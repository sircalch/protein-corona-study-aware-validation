"""Fixed models only. Fit LOSO, then gated material and training-bootstrap sensitivities."""
from pathlib import Path
import json,hashlib,time,datetime,sys,platform,importlib.metadata as md,warnings,faulthandler
import numpy as np,pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
P=Path(__file__).resolve().parents[1];O=P/'runs/confirmatory';O.mkdir(parents=True,exist_ok=True)
F=['Type','Subtype','Mod_Charge','Size_Group','ZP_Group','ZP_Charge','In_Time','Shaking'];T=['APOE','APOB','CO3','CLUS'];MODELS=['PREVALENCE','LR','RF'];SEEDS=[32,1729,2026]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit_plan(plan,d,name):
 rows=[];fits=[];start=time.time()
 (O/(name+'_manifest.json')).write_text(json.dumps(plan,indent=2))
 for i,s in enumerate(plan):
  tr0=d.loc[s['train_ids']];te0=d.loc[s['test_ids']]
  assert not set(tr0.study_id)&set(te0.study_id)
  assert not set(tr0.observation_hash)&set(te0.observation_hash)
  for t in s.get('targets',T):
   tr=tr0[tr0[t].notna()];te=te0[te0[t].notna()]
   if not len(te) or not len(tr):continue
   X=tr[F].fillna('MISSING').astype(str);Y=te[F].fillna('MISSING').astype(str);y=tr[t].astype(int)
   for model in MODELS:
    est=DummyClassifier(strategy='prior') if model=='PREVALENCE' or y.nunique()<2 else LogisticRegression(C=1,max_iter=2000,random_state=s['seed']) if model=='LR' else RandomForestClassifier(n_estimators=100,min_samples_leaf=5,n_jobs=1,random_state=s['seed'])
    pipe=Pipeline([('encoder',OneHotEncoder(handle_unknown='ignore',sparse_output=False)),('estimator',est)])
    if i==0:print('first fold fitting',t,model,len(tr),X.shape,flush=True)
    with warnings.catch_warnings(record=True) as caught:
     warnings.simplefilter('always');pipe.fit(X,y)
    assert not any(issubclass(w.category,ConvergenceWarning) for w in caught)
    pp=pipe.predict_proba(Y);prob=pp[:,list(pipe.classes_).index(1)] if 1 in pipe.classes_ else np.zeros(len(te))
    fits.append(dict(regime=s['regime'],fold=s['fold'],seed=s['seed'],target=t,model=model,n_train=len(tr),n_unique_train=tr.index.nunique(),n_train_studies=tr.study_id.nunique(),single_class_fallback=y.nunique()<2,warnings=';'.join(str(w.message) for w in caught)))
    for (sid,r),pr in zip(te.iterrows(),prob):rows.append(dict(sample_id=sid,study_id=r.study_id,regime=s['regime'],fold=s['fold'],seed=s['seed'],target=t,model=model,y=int(r[t]),p=float(pr)))
  if i%10==0:print(name,i+1,'/',len(plan),flush=True)
 pd.DataFrame(rows).to_csv(O/(name+'_predictions.csv'),index=False);pd.DataFrame(fits).to_csv(O/(name+'_fits.csv'),index=False)
 info=dict(name=name,seconds=time.time()-start,n_fits=len(fits),n_predictions=len(rows),manifest_sha256=sha(O/(name+'_manifest.json')))
 (O/(name+'_run.json')).write_text(json.dumps(info,indent=2));return info
def main():
 assert (P/'LABEL_PROVENANCE.md').exists()
 freeze=json.loads((P/'splits/pretraining_freeze.json').read_text());assert all(sha(P/k)==v for k,v in freeze['hashes'].items())
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');d=d[d.partition=='DEVELOPMENT'];studies=sorted(d.study_id.unique())
 locked=[P/'CONFIRMATORY_LOCK.md',P/'LABEL_PROVENANCE.md',Path(__file__),P/'data/derived/benchmark.csv',P/'splits/manifests.json']
 (O/'input_freeze.json').write_text(json.dumps({str(x.relative_to(P)):sha(x) for x in locked},indent=2))
 plan=[dict(regime='LOSO',fold=s,seed=seed,train_ids=d.index[d.study_id!=s].tolist(),test_ids=d.index[d.study_id==s].tolist()) for seed in SEEDS for s in studies]
 runs=[fit_plan(plan,d,'loso')]
 # Sufficiency assessed only after completion of LOSO, under prewritten thresholds.
 suff=[];mp=[]
 for mat,g in d.groupby('material_class'):
  tr=d[~d.study_id.isin(g.study_id)]
  for t in T:
   te=g[g[t].notna()];a=tr[tr[t].notna()];n0=int(te[t].eq(0).sum());n1=int(te[t].eq(1).sum())
   ok=te.study_id.nunique()>=3 and len(te)>=30 and min(n0,n1)>=5 and min(te.loc[te[t].eq(k),'study_id'].nunique() for k in [0,1])>=2 and a.study_id.nunique()>=10 and a[t].nunique()==2
   suff.append(dict(material=mat,target=t,n_test=len(te),n_studies=te.study_id.nunique(),negative=n0,positive=n1,n_train_studies=a.study_id.nunique(),eligible=ok))
   if ok:mp.append(dict(regime='MATERIAL',fold=mat,seed=32,targets=[t],train_ids=tr.index.tolist(),test_ids=g.index.tolist()))
 pd.DataFrame(suff).to_csv(O/'material_sufficiency.csv',index=False)
 if mp:runs.append(fit_plan(mp,d,'material'))
 rng=np.random.default_rng(2026);bp=[]
 for b in range(20):
  picked=rng.choice(studies,len(studies),replace=True);held=sorted(set(studies)-set(picked));train=[sid for s in picked for sid in d.index[d.study_id==s]]
  assert held
  bp.append(dict(regime='TRAIN_BOOTSTRAP_OOB',fold=str(b),seed=2026+b,train_ids=train,test_ids=d.index[d.study_id.isin(held)].tolist()))
 runs.append(fit_plan(bp,d,'training_bootstrap'))
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python scripts/confirmatory_fit.py',python=sys.version,platform=platform.platform(),versions={x:md.version(x) for x in ['numpy','pandas','scipy','scikit-learn']},runs=runs,temporal_status='INSUFFICIENT DATA; untouched',hpo=False,script_sha256=sha(Path(__file__)))
 (O/'run_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':
 faulthandler.dump_traceback_later(45,repeat=True)
 with threadpool_limits(limits=1):main()
 faulthandler.cancel_dump_traceback_later()
