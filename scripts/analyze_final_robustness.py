from pathlib import Path
import json,hashlib,datetime
import pandas as pd,numpy as np
P=Path(__file__).resolve().parents[1];O=P/'runs/final_robustness';T=['APOE','APOB','CO3','CLUS'];MODELS=['PREVALENCE','LR','RF']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ratios(g,keys):
 x=g.pivot(index=keys,columns='model',values='brier').reset_index()
 for m in ['LR','RF']:x['BSS_'+m]=np.where(x.PREVALENCE>0,1-x[m]/x.PREVALENCE,np.nan)
 return x
def summarize(pred,name):
 pred=pred.copy();pred['brier']=(pred.y-pred.p)**2
 sm=pred.groupby(['block','regime','seed','study_id','target','model'],as_index=False).agg(brier=('brier','mean'),n=('y','size'),prevalence=('y','mean'))
 a=sm.groupby(['block','regime','study_id','target','model'],as_index=False).agg(brier=('brier','mean'),n=('n','first'),prevalence=('prevalence','first'));a.to_csv(O/(name+'_study_metrics.csv'),index=False)
 t=a.groupby(['block','regime','target','model'],as_index=False).brier.mean();b=ratios(t,['block','regime','target']);b.to_csv(O/(name+'_target_bss.csv'),index=False)
 z=ratios(t.groupby(['block','regime','model'],as_index=False).brier.mean(),['block','regime']);z.to_csv(O/(name+'_macro_bss.csv'),index=False)
 gaps=a.pivot(index=['block','study_id','target','model'],columns='regime',values='brier').reset_index();gaps['gap']=gaps.LOSO-gaps.RANDOM;gaps.to_csv(O/(name+'_paired_gaps.csv'),index=False)
 rows=[]
 for (block,model),g in gaps.groupby(['block','model']):
  studies=sorted(g.study_id.unique());rng=np.random.default_rng(2026);draw=rng.integers(0,len(studies),(2000,len(studies)))
  for target in T+['OVERALL_MACRO']:
   gg=g[g.target==target] if target in T else g;v=gg.pivot(index='study_id',columns='target',values='gap').reindex(studies).to_numpy();bv=np.nanmean(np.nanmean(v[draw],axis=1),axis=1);ci=np.quantile(bv,[.025,.975]);rows.append(dict(block=block,model=model,target=target,gap=float(gg.groupby('target').gap.mean().mean()),ci_low=ci[0],ci_high=ci[1],n_studies=gg.study_id.nunique()))
 ci=pd.DataFrame(rows);ci.to_csv(O/(name+'_gap_uncertainty.csv'),index=False);return z,b,ci
def verify_structure(d):
 F=json.loads((O/'feature_blocks.json').read_text())['COMBINED'];X=pd.get_dummies(d[F].fillna('MISSING').astype(str),dtype=float);total=between=0.
 for c in X:
  x=X[c];gm=x.groupby(d.study_id).transform('mean');total+=float(((x-x.mean())**2).sum());between+=float(((gm-x.mean())**2).sum())
 cohort=[]
 for (study,g) in d.groupby('study_id'):
  for t in T:
   y=g[t].dropna()
   if len(y):cohort.append(dict(study_id=study,target=t,n=len(y),single_class=y.nunique()==1))
 pd.DataFrame(cohort).to_csv(O/'structure_study_target_cohorts.csv',index=False)
 preds=[]
 for s in json.loads((P/'splits/manifests.json').read_text()):
  if s['regime']!='RANDOM':continue
  for t in T:
   tr=d.loc[s['target_train_ids'][t]];te=d.loc[s['test_ids']];te=te[te[t].notna()];prior=tr[t].mean();by=tr.groupby('study_id')[t].mean()
   for sid,r in te.iterrows():preds.append(dict(sample_id=sid,study_id=r.study_id,target=t,seed=s['seed'],y=int(r[t]),known=float(by.get(r.study_id,prior)),global_prior=float(prior)))
 pp=pd.DataFrame(preds);pp.to_csv(O/'structure_recomputed_prior_predictions.csv',index=False)
 vals={}
 for name in ['known','global_prior']:
  loss=(pp[name]-pp.y)**2;gg=pp.assign(loss=loss).groupby(['target','study_id','seed']).loss.mean().groupby(['target','study_id']).mean().groupby('target').mean().mean();vals[name]=float(gg)
 old=pd.read_csv(P/'runs/confirmatory/covariate_variance_decomposition.csv');k=pd.read_csv(P/'runs/confirmatory/known_study_prior_metrics.csv');prev=pd.read_csv(P/'runs/confirmatory/bss_overall_macro.csv')
 assert np.isclose(between/total,old.between_study_ss.sum()/old.total_ss.sum(),atol=1e-12)
 assert np.isclose(vals['known'],k[k.regime=='RANDOM'].brier.mean(),atol=1e-12)
 assert np.isclose(vals['global_prior'],prev.loc[prev.regime=='RANDOM','PREVALENCE'].iloc[0],atol=1e-12)
 assert sum(x['single_class'] for x in cohort)==177 and len(cohort)==203
 result=dict(between_study_covariate_fraction=between/total,total_covariate_ss=total,between_covariate_ss=between,single_class_cohorts=177,total_cohorts=203,known_study_random_brier=vals['known'],global_prevalence_random_brier=vals['global_prior'],verification='PASS_RECOMPUTED_FROM_FROZEN_COHORT_AND_TRAIN_IDS')
 (O/'study_structure_verification.json').write_text(json.dumps(result,indent=2));return result
def main():
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');d=d[d.partition=='DEVELOPMENT'];clean=pd.read_csv(O/'clean_cohort.csv').set_index('sample_id');cp=pd.read_csv(O/'clean_predictions.csv');bp=pd.read_csv(O/'blocks_predictions.csv')
 old=pd.read_csv(P/'runs/first_split_comparison/predictions.csv');lp=pd.read_csv(P/'runs/confirmatory/loso_predictions.csv');primary=pd.concat([old[lp.columns],lp],ignore_index=True);primary=primary[primary.regime.isin(['RANDOM','LOSO'])]
 prev=primary[primary.model=='PREVALENCE'].copy();ref=[]
 for block in bp.block.unique():ref.append(prev.assign(block=block,analysis='blocks'))
 allblocks=pd.concat([bp,*ref],ignore_index=True);allblocks.to_csv(O/'blocks_predictions_with_reference.csv',index=False)
 checks=[]
 for name,frame,cohort in [('clean',cp,clean),('blocks',allblocks,d)]:
  for (block,regime,seed,t,model),g in frame.groupby(['block','regime','seed','target','model']):
   expected=cohort.loc[cohort[t].notna(),t].sort_index();got=g.set_index('sample_id').y.sort_index();ok=got.index.is_unique and got.index.equals(expected.index) and np.array_equal(got.to_numpy(),expected.to_numpy());checks.append(dict(analysis=name,block=block,regime=regime,seed=int(seed),target=t,model=model,n=len(g),sample_and_label_match=bool(ok)));assert ok
 (O/'SAMPLE_MATCH.json').write_text(json.dumps({'status':'PASS','checks':checks},indent=2))
 combined=bp[bp.block=='COMBINED'];keys=['regime','seed','target','model','sample_id'];matched=combined.merge(primary[primary.model.isin(['LR','RF'])],on=keys,suffixes=('_new','_old'),validate='one_to_one');diff=float(np.max(np.abs(matched.p_new-matched.p_old)));assert len(matched)==len(combined) and diff<1e-10
 (O/'COMBINED_REPRODUCTION.json').write_text(json.dumps(dict(status='PASS',n_predictions=len(matched),max_absolute_probability_difference=diff,tolerance=1e-10),indent=2))
 cm,ct,cg=summarize(cp,'clean');bm,bt,bg=summarize(allblocks,'blocks');structure=verify_structure(d)
 primaryb=pd.read_csv(P/'runs/confirmatory/bss_overall_macro.csv');comparison=primaryb.merge(cm,on='regime',suffixes=('_primary','_clean'));comparison.to_csv(O/'primary_vs_clean_bss.csv',index=False)
 pg=pd.read_csv(P/'runs/confirmatory/gap_uncertainty.csv');oldg=pg[(pg.regime=='LOSO')&(pg.target=='OVERALL_MACRO')].set_index('model');conditions=[]
 for model in ['LR','RF']:
  c=cg[(cg.model==model)&(cg.target=='OVERALL_MACRO')].iloc[0];random=float(cm.loc[cm.regime=='RANDOM','BSS_'+model].iloc[0]);loso=float(cm.loc[cm.regime=='LOSO','BSS_'+model].iloc[0]);conditions.append(dict(model=model,random_bss=random,loso_bss=loso,clean_gap=float(c.gap),ci_low=float(c.ci_low),ci_high=float(c.ci_high),original_gap=float(oldg.loc[model,'gap']),retained_gap_fraction=float(c.gap/oldg.loc[model,'gap'])))
 robust=all(c['random_bss']>0 and c['loso_bss']<0 and c['clean_gap']>0 and c['ci_low']>0 and c['retained_gap_fraction']>=.5 for c in conditions)
 changed=any(c['clean_gap']<=0 or c['random_bss']<=0 or c['loso_bss']>0 for c in conditions)
 status='ROBUST' if robust else 'MATERIALLY_CHANGED' if changed else 'ATTENUATED'
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),log_unit_status=status,conditions=conditions,structure_verification=structure,sample_match='PASS',combined_reproduction='PASS',manuscript_candidate='UNLOCK_PENDING_INTEGRITY' if not changed else 'REMAINS_LOCKED',script_sha256=sha(Path(__file__)))
 (O/'analysis_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));print(bm.to_string(index=False))
if __name__=='__main__':main()
