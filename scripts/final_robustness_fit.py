from pathlib import Path
import json,hashlib,time,datetime,sys,platform,importlib.metadata as md,warnings
import numpy as np,pandas as pd
from sklearn.model_selection import KFold,GroupKFold
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
P=Path(__file__).resolve().parents[1];O=P/'runs/final_robustness';O.mkdir(parents=True,exist_ok=True)
T=['APOE','APOB','CO3','CLUS'];SEEDS=[32,1729,2026];BLOCKS={'NP_INTRINSIC':['Type','Subtype','Mod_Charge','Size_Group','ZP_Group','ZP_Charge'],'EXPERIMENTAL_CONTEXT':['In_Time','Shaking'],'COMBINED':['Type','Subtype','Mod_Charge','Size_Group','ZP_Group','ZP_Charge','In_Time','Shaking']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj):(O/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
def clean_manifests(d):
 idx=d.index.to_numpy();group=list(GroupKFold(5).split(d,groups=d.component));cap=min(len(a) for a,b in group);records=[]
 for seed in SEEDS:
  rng=np.random.default_rng(seed)
  for regime,folds in [('RANDOM',list(KFold(5,shuffle=True,random_state=seed).split(d))),('GROUP_STUDY',group)]:
   for k,(tr,te) in enumerate(folds):
    selected=np.sort(rng.choice(tr,cap,replace=False));records.append(dict(regime=regime,seed=seed,fold=str(k),train_ids=idx[selected].tolist(),test_ids=idx[te].tolist()))
 caps={t:min(int(d.loc[s['train_ids'],t].notna().sum()) for s in records) for t in T}
 for s in records:
  s['target_train_ids']={}
  for j,t in enumerate(T):
   pool=d.loc[s['train_ids']];eligible=pool.index[pool[t].notna()].to_numpy();rng=np.random.default_rng(s['seed']+1000*(j+1)+int(s['fold']));s['target_train_ids'][t]=sorted(rng.choice(eligible,caps[t],replace=False).tolist())
 for seed in SEEDS:
  for study in sorted(d.study_id.unique()):records.append(dict(regime='LOSO',seed=seed,fold=study,train_ids=d.index[d.study_id!=study].tolist(),test_ids=d.index[d.study_id==study].tolist()))
 return records,caps
def fit(name,plan,d,blocks,models):
 rows=[];fits=[];start=time.time()
 for block in blocks:
  for i,s in enumerate(plan):
   tr0=d.loc[s['train_ids']];te0=d.loc[s['test_ids']]
   assert not set(tr0.index)&set(te0.index)
   if s['regime']!='RANDOM':assert not set(tr0.study_id)&set(te0.study_id) and not set(tr0.observation_hash)&set(te0.observation_hash)
   for t in T:
    tr=d.loc[s['target_train_ids'][t]] if 'target_train_ids' in s else tr0[tr0[t].notna()];te=te0[te0[t].notna()]
    if not len(te):continue
    X=tr[BLOCKS[block]].fillna('MISSING').astype(str);Y=te[BLOCKS[block]].fillna('MISSING').astype(str);y=tr[t].astype(int)
    for model in models:
     est=DummyClassifier(strategy='prior') if model=='PREVALENCE' or y.nunique()<2 else LogisticRegression(C=1,max_iter=2000,random_state=s['seed']) if model=='LR' else RandomForestClassifier(n_estimators=100,min_samples_leaf=5,n_jobs=1,random_state=s['seed'])
     pipe=Pipeline([('encoder',OneHotEncoder(handle_unknown='ignore',sparse_output=False)),('estimator',est)])
     with warnings.catch_warnings(record=True) as caught:
      warnings.simplefilter('always');pipe.fit(X,y)
     assert not any(issubclass(w.category,ConvergenceWarning) for w in caught)
     pp=pipe.predict_proba(Y);prob=pp[:,list(pipe.classes_).index(1)] if 1 in pipe.classes_ else np.zeros(len(te))
     fits.append(dict(analysis=name,block=block,regime=s['regime'],seed=s['seed'],fold=s['fold'],target=t,model=model,n_train=len(tr),n_train_studies=tr.study_id.nunique(),single_class_fallback=y.nunique()<2,warnings=';'.join(str(w.message) for w in caught)))
     for (sid,r),pr in zip(te.iterrows(),prob):rows.append(dict(analysis=name,block=block,regime=s['regime'],seed=s['seed'],fold=s['fold'],target=t,model=model,sample_id=sid,study_id=r.study_id,y=int(r[t]),p=float(pr)))
   if i%10==0:write('progress.json',dict(analysis=name,block=block,completed_plan_entries=i+1,total=len(plan),fits=len(fits),elapsed_seconds=time.time()-start))
 pd.DataFrame(rows).to_csv(O/(name+'_predictions.csv'),index=False);pd.DataFrame(fits).to_csv(O/(name+'_fit_log.csv'),index=False)
 info=dict(analysis=name,n_fits=len(fits),n_predictions=len(rows),seconds=time.time()-start);write(name+'_run.json',info);return info
def main():
 original=json.loads((P/'splits/pretraining_freeze.json').read_text());assert all(sha(P/k)==v for k,v in original['hashes'].items())
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');dev=d[d.partition=='DEVELOPMENT'];raw=pd.read_csv(P/'data/raw/pcdb/Datasets/PC-DB_for_Meta-Analysis.csv',keep_default_na=False)
 affected=sorted(raw.loc[raw['Protein Composition Units'].str.contains('log',case=False),'Study ID'].unique());assert affected==['A10','A38'];clean=dev[~dev.study_id.isin(affected)].copy();clean.to_csv(O/'clean_cohort.csv');dev[dev.study_id.isin(affected)].to_csv(O/'excluded_log_study_rows.csv')
 cp,caps=clean_manifests(clean);write('clean_manifest.json',cp)
 rp=[s for s in json.loads((P/'splits/manifests.json').read_text()) if s['regime']=='RANDOM'];lp=json.loads((P/'runs/confirmatory/loso_manifest.json').read_text());bp=rp+lp;write('blocks_manifest.json',bp);write('feature_blocks.json',BLOCKS)
 fixed=[Path(__file__),P/'FINAL_ROBUSTNESS_LOCK.md',P/'LABEL_PROVENANCE.md',P/'data/derived/benchmark.csv',P/'splits/manifests.json',P/'runs/confirmatory/loso_manifest.json',O/'clean_manifest.json',O/'blocks_manifest.json',O/'feature_blocks.json',O/'clean_cohort.csv']
 write('input_freeze.json',{str(f.relative_to(P)):sha(f) for f in fixed})
 write('design_summary.json',dict(excluded_studies=affected,excluded_rows=len(dev)-len(clean),clean_n=len(clean),clean_studies=clean.study_id.nunique(),original_n=len(dev),original_studies=dev.study_id.nunique(),clean_target_training_caps=caps,temporal_reserved_n=int(d.partition.eq('TEMPORAL_RESERVED').sum()),external_models_fit=False))
 runs=[fit('clean',cp,clean,['COMBINED'],['PREVALENCE','LR','RF']),fit('blocks',bp,dev,list(BLOCKS),['LR','RF'])]
 write('run_report.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python scripts/final_robustness_fit.py',python=sys.version,platform=platform.platform(),versions={x:md.version(x) for x in ['numpy','pandas','scipy','scikit-learn','threadpoolctl']},runs=runs,script_sha256=sha(Path(__file__)),hpo=False,external_training=False))
 write('progress.json',dict(status='COMPLETED'));print(json.dumps(runs))
if __name__=='__main__':
 with threadpool_limits(limits=1):main()
