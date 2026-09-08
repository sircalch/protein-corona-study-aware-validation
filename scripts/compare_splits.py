from pathlib import Path
import json,hashlib,datetime,sys,platform,importlib.metadata as md,warnings,time
import numpy as np,pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import brier_score_loss,roc_auc_score,average_precision_score,balanced_accuracy_score
P=Path(__file__).resolve().parents[1];O=P/'runs/first_split_comparison';O.mkdir(parents=True,exist_ok=True)
assert json.loads((P/'runs/baseline_reproduction/report.json').read_text())['status']=='PASS','Baseline reproduction must pass first'
freeze=json.loads((P/'splits/pretraining_freeze.json').read_text());assert all(hashlib.sha256((P/k).read_bytes()).hexdigest()==v for k,v in freeze['hashes'].items())
start=time.time();data=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');features=['Type','Subtype','Mod_Charge','Size_Group','ZP_Group','ZP_Charge','In_Time','Shaking'];targets=['APOE','APOB','CO3','CLUS']
manifest=json.loads((P/'splits/manifests.json').read_text());selected=[s for s in manifest if s['regime'] in ['RANDOM','GROUP_STUDY']];rows=[];fits=[]
for s in selected:
 train=data.loc[s['train_ids']];test=data.loc[s['test_ids']];assert set(train.partition)==set(test.partition)=={'DEVELOPMENT'}
 if s['regime']=='GROUP_STUDY':assert not set(train.component)&set(test.component)
 for t in targets:
  tr=data.loc[s['target_train_ids'][t]];te=test[test[t].notna()];X=tr[features].fillna('MISSING').astype(str);Y=te[features].fillna('MISSING').astype(str);y=tr[t].astype(int)
  assert set(tr.index)<=set(train.index) and tr[t].notna().all()
  if not len(tr) or not len(te):continue
  novelty=np.mean(np.stack([~Y[c].isin(set(X[c])) for c in features],axis=1),axis=1)
  for name in ['LR','RF','PREVALENCE']:
   if name=='LR':est=LogisticRegression(C=1,max_iter=2000,random_state=s['seed'])
   elif name=='RF':est=RandomForestClassifier(n_estimators=100,min_samples_leaf=5,n_jobs=1,random_state=s['seed'])
   else:est=DummyClassifier(strategy='prior')
   fallback=y.nunique()<2
   if fallback:est=DummyClassifier(strategy='prior')
   model=Pipeline([('encoder',OneHotEncoder(handle_unknown='ignore',sparse_output=False)),('estimator',est)])
   with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always');model.fit(X,y)
   cv=[str(w.message) for w in caught if issubclass(w.category,ConvergenceWarning)]
   if cv:raise RuntimeError('Convergence failure: '+str(cv))
   classes=model.classes_;pp=model.predict_proba(Y);prob=pp[:,list(classes).index(1)] if 1 in classes else np.zeros(len(te))
   fits.append({'regime':s['regime'],'seed':s['seed'],'fold':s['fold'],'target':t,'model':name,'n_train':len(tr),'n_train_positive':int(y.sum()),'fallback_single_class':fallback,'warnings':[str(w.message) for w in caught]})
   for (sid,rr),pr,nov in zip(te.iterrows(),prob,novelty):rows.append({'sample_id':sid,'study_id':rr.study_id,'component':rr.component,'material_class':rr.material_class,'regime':s['regime'],'seed':s['seed'],'fold':s['fold'],'target':t,'model':name,'y':int(rr[t]),'p':float(pr),'novel_category_fraction':float(nov)})
pred=pd.DataFrame(rows);pred.to_csv(O/'predictions.csv',index=False);pd.DataFrame(fits).to_csv(O/'fit_log.csv',index=False)
for keys,g in pred.groupby(['regime','seed','target','model']):
 assert g.sample_id.is_unique
 expected=set(data.index[(data.partition=='DEVELOPMENT') & data[keys[2]].notna()]);assert set(g.sample_id)==expected
metrics=[]
for keys,g in pred.groupby(['regime','seed','target','model','study_id','component']):
 met=dict(zip(['regime','seed','target','model','study_id','component'],keys));y=g.y;p=g.p;both=y.nunique()==2
 met.update(n=len(g),positives=int(y.sum()),brier=float(brier_score_loss(y,p)),auc=float(roc_auc_score(y,p)) if both else None,average_precision=float(average_precision_score(y,p)) if both else None,balanced_accuracy=float(balanced_accuracy_score(y,p>=.5)) if both else None,novel_category_fraction=float(g.novel_category_fraction.mean()));metrics.append(met)
sm=pd.DataFrame(metrics);sm.to_csv(O/'study_metrics.csv',index=False)
cal=pred.copy();cal['bin']=np.minimum((cal.p*10).astype(int),9);cal.groupby(['regime','target','model','bin']).agg(n=('y','size'),mean_predicted=('p','mean'),observed_frequency=('y','mean')).to_csv(O/'calibration_bins.csv')
avg=sm.groupby(['regime','target','model','study_id','component']).brier.mean().unstack('regime').reset_index();avg['gap']=avg.GROUP_STUDY-avg.RANDOM;avg.to_csv(O/'paired_study_gaps.csv',index=False)
summaries=[]
for name,g in avg.groupby('model'):
 components=sorted(g.component.unique());rng=np.random.default_rng(2026)
 boots=[]
 for _ in range(2000):
  picks=rng.choice(components,len(components),replace=True);multiplicity=pd.Series(picks).value_counts();w=g.component.map(multiplicity).fillna(0).to_numpy();v=[]
  for t,h in g.groupby('target'):
   ww=w[g.index.get_indexer(h.index)] if False else h.component.map(multiplicity).fillna(0).to_numpy()
   if ww.sum():v.append(float(np.average(h.gap,weights=ww)))
  boots.append(float(np.mean(v)))
 summary={'model':name,'random_study_macro_brier':float(g.groupby('target').RANDOM.mean().mean()),'group_study_macro_brier':float(g.groupby('target').GROUP_STUDY.mean().mean()),'gap_group_minus_random':float(g.groupby('target').gap.mean().mean()),'gap_ci95':np.quantile(boots,[.025,.975]).tolist(),'n_components':len(components),'n_targets':g.target.nunique()};summaries.append(summary)
report={'status':'COMPLETED','primary_endpoint':'study-macro Brier averaged equally across fixed targets; gap = OOD minus random','results':summaries,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.time()-start,'n_fits':len(fits),'n_predictions':len(pred),'temporal_holdout_evaluated':False,'hyperparameter_optimization':False,'interpretation_limit':'Reported detection only. Conditional study bootstrap; three seeds are not independent experiments. No inference of universal binding or causal batch mechanism.','command':'python scripts/compare_splits.py','python':sys.version,'platform':platform.platform(),'packages':{x:md.version(x) for x in ['numpy','pandas','scipy','scikit-learn']},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'freeze_sha256':hashlib.sha256((P/'splits/pretraining_freeze.json').read_bytes()).hexdigest()}
(O/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
