from pathlib import Path
import hashlib,json,numpy as np,pandas as pd
P=Path(__file__).resolve().parents[1];O=P/'runs/final_robustness'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks={};f=json.loads((P/'splits/pretraining_freeze.json').read_text());checks['original_frozen_inputs_preserved']=all(sha(P/k)==v for k,v in f['hashes'].items());f=json.loads((O/'input_freeze.json').read_text());checks['final_lock_inputs_and_fit_script_preserved']=all(sha(P/k)==v for k,v in f.items())
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');reserved=set(d.index[d.partition=='TEMPORAL_RESERVED']);excluded=set(d.index[d.study_id.isin(['A10','A38'])]);clean=pd.read_csv(O/'clean_cohort.csv').set_index('sample_id');checks['entire_affected_studies_excluded']=set(clean.index)==set(d.index[d.partition=='DEVELOPMENT'])-excluded
 for name in ['clean','blocks']:
  pred=pd.read_csv(O/(name+'_predictions.csv'));fit=pd.read_csv(O/(name+'_fit_log.csv'));plan=json.loads((O/(name+'_manifest.json')).read_text());cohort=clean if name=='clean' else d[d.partition=='DEVELOPMENT'];blocks=sorted(pred.block.unique());caps={}
  checks[name+'_no_duplicate_predictions']=not pred.duplicated(['block','regime','seed','fold','target','model','sample_id']).any();checks[name+'_valid_probabilities']=pred.p.between(0,1).all();checks[name+'_frozen_labels']=all(np.array_equal(g.y,cohort.loc[g.sample_id,t]) for t,g in pred.groupby('target'));checks[name+'_temporal_untouched']=not set(pred.sample_id)&reserved
  checks[name+'_models_only_authorized']=set(pred.model)==({'PREVALENCE','LR','RF'} if name=='clean' else {'LR','RF'})
  for s in plan:
   train=cohort.loc[s['train_ids']];test=cohort.loc[s['test_ids']];assert not set(train.index)&set(test.index);assert not (set(train.index)|set(test.index))&reserved
   if name=='clean':assert not (set(train.index)|set(test.index))&excluded
   if s['regime']!='RANDOM':assert not set(train.study_id)&set(test.study_id) and not set(train.observation_hash)&set(test.observation_hash)
   if s['regime']=='LOSO':assert test.study_id.nunique()==1 and set(train.index)==set(cohort.index)-set(test.index)
   for t in ['APOE','APOB','CO3','CLUS']:
    tr=cohort.loc[s['target_train_ids'][t]] if 'target_train_ids' in s else train[train[t].notna()];te=test[test[t].notna()];assert tr[t].notna().all() and set(tr.index)<=set(train.index)
    if not len(te):continue
    if s['regime'] in ['RANDOM','GROUP_STUDY']:caps.setdefault(t,[]).append(len(tr))
    for block in blocks:
     g=pred[(pred.block==block)&(pred.regime==s['regime'])&(pred.seed==s['seed'])&(pred.fold.astype(str)==str(s['fold']))&(pred.target==t)]
     for model,gg in g.groupby('model'):
      assert set(gg.sample_id)==set(te.index)
      if model=='PREVALENCE':assert np.allclose(gg.p,tr[t].mean())
     log=fit[(fit.block==block)&(fit.regime==s['regime'])&(fit.seed==s['seed'])&(fit.fold.astype(str)==str(s['fold']))&(fit.target==t)];assert log.n_train.eq(len(tr)).all()
  checks[name+'_manifests_disjoint_all_training_rows_accounted']=True;checks[name+'_no_convergence_warning']=not fit.warnings.fillna('').str.contains('converg',case=False).any()
  if name=='clean':checks['clean_random_group_equal_eligible_training_n']=all(len(set(v))==1 for v in caps.values())
 checks['exact_sample_and_label_match']=json.loads((O/'SAMPLE_MATCH.json').read_text())['status']=='PASS';checks['combined_reproduced']=json.loads((O/'COMBINED_REPRODUCTION.json').read_text())['status']=='PASS';checks['study_structure_recomputed']=json.loads((O/'study_structure_verification.json').read_text())['verification'].startswith('PASS')
 for name in ['clean','blocks']:
  x=pd.read_csv(O/(name+'_macro_bss.csv'));checks[name+'_bss_formula']=all(np.allclose(x['BSS_'+m],1-x[m]/x.PREVALENCE) for m in ['LR','RF'])
 out=dict(status='PASS' if all(checks.values()) else 'FAIL',checks={k:bool(v) for k,v in checks.items()},script_sha256=sha(Path(__file__)));(O/'INTEGRITY_CHECKS.json').write_text(json.dumps(out,indent=2));assert all(checks.values());print(json.dumps(out))
if __name__=='__main__':main()
