"""Real-data integrity checks; failure blocks audited delivery."""
from pathlib import Path
import hashlib,json,numpy as np,pandas as pd
P=Path(__file__).resolve().parents[1];O=P/'runs/confirmatory'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks={};freeze=json.loads((P/'splits/pretraining_freeze.json').read_text());checks['original_inputs_preserved']=all(sha(P/k)==v for k,v in freeze['hashes'].items())
 inputs=json.loads((O/'input_freeze.json').read_text());checks['confirmatory_inputs_and_fit_script_preserved']=all(sha(P/k)==v for k,v in inputs.items())
 checks['exact_sample_and_label_matching']=json.loads((O/'SAMPLE_MATCH_TEST.json').read_text())['status']=='PASS'
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');dev=d[d.partition=='DEVELOPMENT'];reserved=set(d.index[d.partition=='TEMPORAL_RESERVED'])
 nfits=0
 for name in ['loso','material','training_bootstrap']:
  if not (O/(name+'_predictions.csv')).exists():continue
  pred=pd.read_csv(O/(name+'_predictions.csv'));fit=pd.read_csv(O/(name+'_fits.csv'));manifest=json.loads((O/(name+'_manifest.json')).read_text());nfits+=len(fit)
  checks[name+'_models_frozen']=set(pred.model)=={'PREVALENCE','LR','RF'}
  checks[name+'_valid_probabilities']=pred.p.between(0,1).all() and pred.p.notna().all()
  checks[name+'_temporal_untouched']=not set(pred.sample_id)&reserved
  checks[name+'_no_duplicate_predictions']=not pred.duplicated(['fold','seed','target','model','sample_id']).any()
  checks[name+'_audited_labels']=all(np.array_equal(g.y.to_numpy(),d.loc[g.sample_id,t].to_numpy()) for t,g in pred.groupby('target'))
  for s in manifest:
   tr=d.loc[s['train_ids']];te=d.loc[s['test_ids']]
   assert not set(tr.index)&set(te.index) and not set(tr.study_id)&set(te.study_id) and not set(tr.observation_hash)&set(te.observation_hash)
   assert not (set(tr.index)|set(te.index))&reserved
   if name=='loso':assert set(tr.index)==set(dev.index)-set(te.index) and te.study_id.nunique()==1
   for t in s.get('targets',['APOE','APOB','CO3','CLUS']):
    train=tr[tr[t].notna()];test=te[te[t].notna()]
    if not len(test):continue
    p=pred[(pred.fold.astype(str)==str(s['fold']))&(pred.seed==s['seed'])&(pred.target==t)&(pred.model=='PREVALENCE')]
    assert set(p.sample_id)==set(test.index)
    assert np.allclose(p.p,train[t].mean())
    recorded=fit[(fit.fold.astype(str)==str(s['fold']))&(fit.seed==s['seed'])&(fit.target==t)]
    assert len(recorded)==3 and recorded.n_train.eq(len(train)).all()
  checks[name+'_study_observation_disjoint_and_prior_train_only']=True
  checks[name+'_fit_counts_match_manifest']=True
  checks[name+'_no_convergence_warning']=not fit.warnings.fillna('').str.contains('converg',case=False).any()
 sm=pd.read_csv(O/'study_seed_metrics.csv');single=sm[sm.discrimination_status=='NA_SINGLE_CLASS'];checks['undefined_discrimination_is_na']=single[['auroc','average_precision','balanced_accuracy']].isna().all().all()
 checks['proper_losses_defined']=sm[['brier','log_loss']].notna().all().all()
 b=pd.read_csv(O/'bss_overall_macro.csv');checks['bss_formula']=all(np.allclose(b['BSS_'+m],1-b[m]/b.PREVALENCE) for m in ['LR','RF'])
 audit={'status':'PASS' if all(checks.values()) else 'FAIL','checks':{k:bool(v) for k,v in checks.items()},'n_fits':nfits,'n_temporal_reserved':len(reserved),'scope':'Implementation/data integrity, not validation of unknown published label derivation'}
 (O/'INTEGRITY_CHECKS.json').write_text(json.dumps(audit,indent=2));assert all(checks.values());print(json.dumps(audit,indent=2))
 # Preserve prior portfolio manifest and write this project-only current audit manifest.
 (O/'ARTIFACT_SHA256.json').write_text(json.dumps({str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and '.venv' not in f.parts and '__pycache__' not in f.parts and f.name!='ARTIFACT_SHA256.json'},indent=2))
if __name__=='__main__':main()
