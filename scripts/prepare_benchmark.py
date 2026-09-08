from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,re,datetime,sys
from sklearn.model_selection import KFold,GroupKFold,train_test_split
P=Path(__file__).resolve().parents[1]
for n in ['data/derived','splits','audit','runs']:(P/n).mkdir(parents=True,exist_ok=True)
R=P/'data/raw/pcdb/Datasets'
meta=pd.read_csv(R/'PC-DB_for_Meta-Analysis.csv',keep_default_na=False)
profile=pd.read_csv(R/'Dataset-for-protein-freq-analysis-v2.csv',keep_default_na=False)
prepared=pd.read_csv(R/'prediction_model_data_human_only.csv',keep_default_na=False)
assert meta['NP Entry ID'].is_unique and profile['NP Entry ID'].is_unique
assert meta.groupby('Study ID')['Title'].nunique().max()==1
assert meta.groupby('Study ID')['Year'].nunique().max()==1
assert set(meta['NP Entry ID'])==set(profile['NP Entry ID'])
profile=profile.set_index('NP Entry ID').loc[meta['NP Entry ID']].reset_index()
assert profile['Study ID'].tolist()==meta['Study ID'].tolist()
features={'NP Type':'Type','NP Sub-Type':'Subtype','Modification Charge':'Mod_Charge','Size Group':'Size_Group','Zeta Potential Group':'ZP_Group','Zeta Potential Charge':'ZP_Charge','Incubation time Group':'In_Time','Shaking or AgitationDuring Incubation':'Shaking'}
targets={'APOE':'Apolipoprotein E','APOB':'Apolipoprotein B-100','CO3':'Complement C3','CLUS':'Clusterin'}
d=meta[['NP Entry ID','Study ID','Year','Title','DOI']+list(features)].rename(columns={'NP Entry ID':'sample_id','Study ID':'study_id',**features})
d['material_class']=meta['NP Sub-Type'];d['row_index']=np.arange(len(d))
for t,name in targets.items():
 a=pd.to_numeric(profile[name],errors='coerce');original=pd.to_numeric(meta[t],errors='coerce')
 conflict=a.notna() & original.notna() & ((a>0)!=(original>0))
 d[t]=np.where(a.isna() | original.isna() | conflict,np.nan,(a>0).astype(int))
 for c in features.values():d[c]=d[c].astype(str).str.strip().replace({'':'MISSING','na':'MISSING','N/A':'MISSING','Not Reported':'MISSING'})
studies=sorted(d.study_id.unique());parent={s:s for s in studies}
def find(s):
 while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
 return s
def union(a,b):parent[find(max(a,b))]=find(min(a,b))
# Conservative observation identity includes all profile values and eight model inputs.
payload=pd.concat([d[list(features.values())],profile.drop(columns=['NP Entry ID','Study ID'])],axis=1).astype(str)
fingerprints=payload.apply(lambda r:hashlib.sha256('\x1f'.join(r).encode()).hexdigest(),axis=1)
d['observation_hash']=fingerprints
for _,g in d.groupby('observation_hash'):
 for s in g.study_id.iloc[1:]:union(g.study_id.iloc[0],s)
d['component']=d.study_id.map(find)
latest=int(pd.to_numeric(d.Year).max());temporal_components=set(d.loc[pd.to_numeric(d.Year)==latest,'component']);d['partition']=np.where(d.component.isin(temporal_components),'TEMPORAL_RESERVED','DEVELOPMENT')
development=d[d.partition=='DEVELOPMENT'].copy();full_indices=development.index.to_numpy()
assert development.component.nunique()>=5
group_folds=list(GroupKFold(5).split(development,groups=development.component))
cap=min(len(tr) for tr,te in group_folds)
records=[]
def record(regime,seed,fold,tr,te,unused=None):
 tr=list(map(int,tr));te=list(map(int,te));assert not set(tr)&set(te)
 a,b=d.loc[tr],d.loc[te]
 assert regime.startswith('RANDOM') or not set(a.component)&set(b.component)
 records.append({'regime':regime,'seed':seed,'fold':str(fold),'train_ids':a.sample_id.tolist(),'test_ids':b.sample_id.tolist(),'unused_ids':d.loc[list(unused or []),'sample_id'].tolist(),'train_study_overlap_with_test':len(set(a.study_id)&set(b.study_id)),'n_train':len(a),'n_test':len(b)})
for seed in [32,1729,2026]:
 rng=np.random.default_rng(seed)
 for regime,folds in [('RANDOM',list(KFold(5,shuffle=True,random_state=seed).split(development))),('GROUP_STUDY',group_folds)]:
  for k,(tr,te) in enumerate(folds):
   train=full_indices[tr];test=full_indices[te];selected=np.sort(rng.choice(train,size=cap,replace=False))
   record(regime,seed,k,selected,test)
for group in sorted(development.component.unique()):
 record('LEAVE_ONE_STUDY_OUT',32,group,development.index[development.component!=group],development.index[development.component==group])
for material in sorted(development.material_class.unique()):
 test=development[development.material_class==material];comp=set(test.component);train=development[~development.component.isin(comp)]
 if len(train):record('MATERIAL_HOLDOUT',32,material,train.index,test.index)
record('TEMPORAL_HOLDOUT',32,latest,d.index[d.partition=='DEVELOPMENT'],d.index[d.partition=='TEMPORAL_RESERVED'])
# Equalize valid training counts per target, not merely the pre-filter cap.
by_id=d.set_index('sample_id');active=[s for s in records if s['regime'] in ['RANDOM','GROUP_STUDY']]
target_caps={t:min(int(by_id.loc[s['train_ids'],t].notna().sum()) for s in active) for t in targets}
for s in active:
 s['target_train_ids']={}
 for j,t in enumerate(targets):
  pool=by_id.loc[s['train_ids']];eligible=pool.index[pool[t].notna()].to_numpy()
  rng=np.random.default_rng(s['seed']+1000*(j+1)+int(s['fold']))
  s['target_train_ids'][t]=sorted(rng.choice(eligible,target_caps[t],replace=False).tolist())
d.to_csv(P/'data/derived/benchmark.csv',index=False)
(P/'splits/manifests.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
# Independent published reproduction split manifests, frozen before any fit.
repro=[]
for t in targets:
 y=prepared[t].map({'Present':0,'Absent':1});assert y.notna().all()
 tr,te=train_test_split(np.arange(len(prepared)),test_size=.3,random_state=32,stratify=y)
 repro.append({'target':t,'train_indices':tr.tolist(),'test_indices':te.tolist(),'seed':32,'label_convention':'Present=0; Absent=1'})
(P/'splits/published_reproduction.json').write_text(json.dumps(repro,indent=2),encoding='utf-8')
meta.groupby('Study ID').agg(title=('Title','first'),year=('Year','first'),n_samples=('NP Entry ID','size'),doi_distinct=('DOI','nunique'),doi_first=('DOI','first')).to_csv(P/'audit/study_registry.csv')
meta[meta.groupby('Study ID')['DOI'].transform('nunique')>1][['NP Entry ID','Study ID','DOI','Title']].to_csv(P/'audit/doi_anomalies.csv',index=False)
dup=d[d.observation_hash.duplicated(keep=False)];dup[['sample_id','study_id','component','observation_hash']].to_csv(P/'audit/duplicate_observations.csv',index=False)
schema={str(f.relative_to(P)):{'shape':list(pd.read_csv(f,keep_default_na=False).shape),'columns':pd.read_csv(f,nrows=0).columns.tolist()} for f in (P/'data/raw').rglob('*.csv')}
(P/'audit/schema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
tokens={'','na','nan','n/a','not reported','none'}
missing=[]
for f in (P/'data/raw').rglob('*.csv'):
 df=pd.read_csv(f,keep_default_na=False)
 for c in df:missing.append({'file':str(f.relative_to(P)),'column':c,'missing_count':int(df[c].astype(str).str.strip().str.lower().isin(tokens).sum())})
pd.DataFrame(missing).to_csv(P/'audit/missingness.csv',index=False)
summary={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'meta_rows':len(meta),'profile_rows':len(profile),'prepared_rows':len(prepared),'studies':len(studies),'components':d.component.nunique(),'duplicate_observation_rows':len(dup),'cross_study_duplicate_components':sum(d.groupby('component').study_id.nunique()>1),'development_rows':len(development),'temporal_reserved_rows':sum(d.partition=='TEMPORAL_RESERVED'),'latest_year_reserved':latest,'common_training_cap':cap,'split_records':len(records),'target_positive':{t:int(d[t].eq(1).sum()) for t in targets},'target_unknown':{t:int(d[t].isna().sum()) for t in targets},'prepared_positive':{t:int(prepared[t].eq('Present').sum()) for t in targets},'scientific_models_trained':False}
(P/'audit/data_audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
summary['valid_training_caps_by_target']=target_caps
(P/'audit/data_audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
inputs=[P/'MINIMAL_BENCHMARK_LOCK.md',Path(__file__),P/'data/derived/benchmark.csv',P/'splits/manifests.json',P/'splits/published_reproduction.json']+list((P/'data/raw').rglob('*'))
hashes={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs if f.is_file()}
(P/'splits/pretraining_freeze.json').write_text(json.dumps({'utc':summary['utc'],'hashes':hashes},indent=2),encoding='utf-8')
print(json.dumps(summary))
