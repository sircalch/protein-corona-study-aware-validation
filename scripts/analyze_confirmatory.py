from pathlib import Path
import json,hashlib,datetime
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score,average_precision_score,balanced_accuracy_score
P=Path(__file__).resolve().parents[1];O=P/'runs/confirmatory';T=['APOE','APOB','CO3','CLUS'];M=['PREVALENCE','LR','RF']
def metrics(g):
 y=g.y.to_numpy();p=g.p.to_numpy();both=len(np.unique(y))==2;q=np.clip(p,1e-15,1-1e-15);bins=np.minimum((p*5).astype(int),4);cnt=pd.Series(bins).value_counts()
 ok=len(y)>=50 and len(cnt)>=2 and cnt.min()>=10
 return dict(n=len(y),prevalence=float(y.mean()),brier=float(np.mean((y-p)**2)),log_loss=float(np.mean(-y*np.log(q)-(1-y)*np.log(1-q))),auroc=float(roc_auc_score(y,p)) if both else np.nan,average_precision=float(average_precision_score(y,p)) if both else np.nan,balanced_accuracy=float(balanced_accuracy_score(y,p>=.5)) if both else np.nan,ece=float(sum(np.mean(bins==b)*abs(y[bins==b].mean()-p[bins==b].mean()) for b in cnt.index)) if ok else np.nan,calibration_status='DESCRIPTIVE_5_BINS' if ok else 'NA_INSUFFICIENT_BIN_SUPPORT',discrimination_status='DEFINED' if both else 'NA_SINGLE_CLASS')
def metric_table(pred):
 rows=[];keys=['regime','seed','fold','study_id','target','model']
 for k,g in pred.groupby(keys):rows.append(dict(zip(keys,k))|metrics(g))
 return pd.DataFrame(rows)
def ratios(frame,keys):
 wide=frame.pivot(index=keys,columns='model',values='brier').reset_index()
 for m in ['LR','RF']:wide['BSS_'+m]=np.where(wide.PREVALENCE>0,1-wide[m]/wide.PREVALENCE,np.nan)
 return wide
def main():
 old=pd.read_csv(P/'runs/first_split_comparison/predictions.csv');new=pd.read_csv(O/'loso_predictions.csv');pred=pd.concat([old[new.columns],new],ignore_index=True)
 d=pd.read_csv(P/'data/derived/benchmark.csv').set_index('sample_id');dev=d[d.partition=='DEVELOPMENT'];raw=pd.read_csv(P/'data/raw/pcdb/Datasets/PC-DB_for_Meta-Analysis.csv',keep_default_na=False).set_index('NP Entry ID').loc[dev.index]
 checks=[]
 for t in T:
  expected=dev.loc[dev[t].notna(),t].astype(int).sort_index()
  for (reg,seed,model),g in pred[pred.target==t].groupby(['regime','seed','model']):
   got=g.set_index('sample_id').y.sort_index();check=dict(target=t,regime=reg,seed=int(seed),model=model,n=len(g),same_sample_set=set(g.sample_id)==set(expected.index),unique_sample_ids=g.sample_id.is_unique,identical_y=got.index.equals(expected.index) and np.array_equal(got.to_numpy(),expected.to_numpy()),missing_ids=sorted(set(expected.index)-set(g.sample_id)),extra_ids=sorted(set(g.sample_id)-set(expected.index)))
   assert check['same_sample_set'] and check['unique_sample_ids'] and check['identical_y'];checks.append(check)
 (O/'SAMPLE_MATCH_TEST.json').write_text(json.dumps({'status':'PASS','scope':'Exact sample and y equality RANDOM/GROUP_STUDY/LOSO, each target/model/seed','checks':checks},indent=2))
 sm=metric_table(pred);sm.to_csv(O/'study_seed_metrics.csv',index=False)
 # Average per-seed losses, never pool repeated seed predictions as independent samples.
 avg=sm.groupby(['regime','study_id','target','model'],as_index=False).agg(brier=('brier','mean'),log_loss=('log_loss','mean'),n=('n','sum'),prevalence=('prevalence','mean'))
 # RANDOM folds fragment a study; collapse weighted across folds per seed first.
 rr=[]
 for k,g in pred.groupby(['regime','seed','study_id','target','model']):rr.append(dict(zip(['regime','seed','study_id','target','model'],k))|metrics(g))
 sm=pd.DataFrame(rr);sm.to_csv(O/'study_seed_metrics.csv',index=False)
 avg=sm.groupby(['regime','study_id','target','model'],as_index=False).agg(brier=('brier','mean'),log_loss=('log_loss','mean'),n=('n','first'),prevalence=('prevalence','first'))
 avg.to_csv(O/'study_mean_metrics.csv',index=False)
 study=ratios(avg,['regime','study_id','target']);study.to_csv(O/'bss_study_target.csv',index=False)
 target=avg.groupby(['regime','target','model'],as_index=False).brier.mean();bt=ratios(target,['regime','target']);bt.to_csv(O/'bss_target_study_macro.csv',index=False)
 overall=target.groupby(['regime','model'],as_index=False).brier.mean();bo=ratios(overall,['regime']);bo.to_csv(O/'bss_overall_macro.csv',index=False)
 stmacro=avg.groupby(['regime','study_id','model'],as_index=False).brier.mean();ratios(stmacro,['regime','study_id']).to_csv(O/'bss_study_macro_target.csv',index=False)
 sampleloss=pred.assign(brier=(pred.y-pred.p)**2).groupby(['regime','target','model'],as_index=False).brier.mean();ratios(sampleloss,['regime','target']).to_csv(O/'bss_target_sample_weighted.csv',index=False)
 # Paired conditional cluster bootstrap: identical study multiplicities across targets and models.
 gap=avg.pivot(index=['study_id','target','model'],columns='regime',values='brier').reset_index();gap['LOSO_gap']=gap.LOSO-gap.RANDOM;gap['GROUP_gap']=gap.GROUP_STUDY-gap.RANDOM;gap.to_csv(O/'paired_gaps.csv',index=False)
 studies=sorted(dev.study_id.unique());rng=np.random.default_rng(2026);draws=rng.integers(0,len(studies),(2000,len(studies)));summ=[]
 for model in M:
  for targetname in T+['OVERALL_MACRO']:
   g=gap[(gap.model==model)&((gap.target==targetname) if targetname in T else True)]
   for reg,col in [('LOSO','LOSO_gap'),('GROUP_STUDY','GROUP_gap')]:
    v=g.pivot(index='study_id',columns='target',values=col).reindex(studies).to_numpy();boot=np.nanmean(np.nanmean(v[draws],axis=1),axis=1)
    point=float(g.groupby('target')[col].mean().mean());ci=np.quantile(boot,[.025,.975]);w=g.groupby('study_id')[col].mean();positive=w.clip(lower=0);top=positive.nlargest(3).sum()/positive.sum() if positive.sum()>0 else np.nan
    # Equal-study sensitivity, remove each study and recompute original equal-target endpoint.
    loo=[g[g.study_id!=s].groupby('target')[col].mean().mean() for s in g.study_id.unique()]
    summ.append(dict(model=model,target=targetname,regime=reg,gap=point,ci_low=ci[0],ci_high=ci[1],n_studies=len(w),fraction_studies_positive=float(w.gt(0).mean()),median_study_gap=w.median(),q25=w.quantile(.25),q75=w.quantile(.75),min_gap=w.min(),max_gap=w.max(),top3_share_positive_gap=top,leave_one_study_mean_min=min(loo),leave_one_study_mean_max=max(loo)))
 summary=pd.DataFrame(summ);summary.to_csv(O/'gap_uncertainty.csv',index=False)
 # Metadata are descriptive, not model inputs. Full proteomics methodology is not in the source schema.
 cmap={'material_class':'NP Sub-Type','surface_chemistry':'Surface Modification','surface_charge':'Modification Charge','biofluid':'Incubation Protein Source','species':'Species','isolation_protocol':'NP-PC Isolation Method','quantification_unit_proxy':'Protein Composition Units'}
 nmap={'particle_size_nm':'Size (nm)','zeta_potential_mv':'Zeta Potential (mV)','incubation_time_min':'Incubation time (min)','publication_year':'Year'}
 tokens={'','na','n/a','nan','not reported','nd','none'}
 def known(s):return ~s.astype(str).str.strip().str.lower().isin(tokens)
 mdrows=[]
 for s,g in raw.groupby('Study ID'):
  r=dict(study_id=s,study_size=len(g));present=[]
  for key,c in cmap.items():
   good=g.loc[known(g[c]),c];u=good.unique();r[key]=u[0] if len(u)==1 else 'MIXED' if len(u)>1 else 'MISSING';r[key+'_levels']=' | '.join(sorted(map(str,u)));r[key+'_missing_fraction']=1-len(good)/len(g);present.extend(known(g[c]).tolist())
  for key,c in nmap.items():
   v=pd.to_numeric(g[c],errors='coerce');r[key]=v.median() if v.notna().any() else np.nan;r[key+'_missing_fraction']=v.isna().mean();present.extend(v.notna().tolist())
  r['metadata_completeness']=np.mean(present);r['proteomics_methodology']='NOT_AVAILABLE';mdrows.append(r)
 metadata=pd.DataFrame(mdrows);metadata.to_csv(O/'study_metadata.csv',index=False)
 base=study[study.regime=='LOSO'].drop(columns='regime');base=base.merge(avg[(avg.regime=='LOSO')&(avg.model=='PREVALENCE')][['study_id','target','n','prevalence']],on=['study_id','target'])
 for model in ['LR','RF']:
  gg=gap[gap.model==model][['study_id','target','RANDOM','LOSO_gap','GROUP_STUDY']].rename(columns={'RANDOM':'Brier_RANDOM_'+model,'LOSO_gap':'OOD_gap_'+model,'GROUP_STUDY':'Brier_GROUP_'+model});base=base.merge(gg,on=['study_id','target'])
 base=base.rename(columns={'PREVALENCE':'Brier_PREV','LR':'Brier_LR','RF':'Brier_RF'}).merge(metadata,on='study_id');base.to_csv(O/'study_target_table.csv',index=False)
 assoc=[]
 for t in T:
  for model in ['LR','RF']:
   g=base[base.target==t]
   for cov in list(nmap)+['study_size','metadata_completeness']:
    v=g[[cov,'OOD_gap_'+model]].dropna();rho=spearmanr(v.iloc[:,0],v.iloc[:,1]).statistic if len(v)>=10 and v.iloc[:,0].nunique()>1 else np.nan
    assoc.append(dict(target=t,model=model,covariate=cov,n_studies=len(v),spearman_rho=rho,status='EXPLORATORY_NO_CAUSAL_OR_SIGNIFICANCE_CLAIM'))
 pd.DataFrame(assoc).to_csv(O/'heterogeneity_numeric.csv',index=False)
 cats=[]
 for cov in cmap:
  for (level,t),g in base.groupby([cov,'target']):
   for model in ['LR','RF']:cats.append(dict(covariate=cov,level=level,target=t,model=model,n_studies=len(g),mean_gap=g['OOD_gap_'+model].mean(),mean_bss=g['BSS_'+model].mean(),warning='Descriptive; category BSS average differs from aggregated-loss BSS'))
 pd.DataFrame(cats).to_csv(O/'heterogeneity_categorical.csv',index=False)
 # Covariate decomposition: descriptive between-study variance, no supervised refit/test centering.
 F=['Type','Subtype','Mod_Charge','Size_Group','ZP_Group','ZP_Charge','In_Time','Shaking'];X=pd.get_dummies(dev[F].fillna('MISSING').astype(str),dtype=float);vf=[]
 for c in X:
  x=X[c];groupmean=x.groupby(dev.study_id).transform('mean');total=float(((x-x.mean())**2).sum());between=float(((groupmean-x.mean())**2).sum());vf.append(dict(feature=c,total_ss=total,between_study_ss=between,between_fraction=between/total if total else np.nan))
 pd.DataFrame(vf).to_csv(O/'covariate_variance_decomposition.csv',index=False)
 # Known-study prevalence diagnostic, labels drawn ONLY from target-specific training IDs.
 diag=[];manifest=json.loads((P/'splits/manifests.json').read_text())
 for s in manifest:
  if s['regime'] not in ['RANDOM','GROUP_STUDY']:continue
  for t in T:
   tr=d.loc[s['target_train_ids'][t]];te=d.loc[s['test_ids']];te=te[te[t].notna()];prior=tr[t].mean();by=tr.groupby('study_id')[t].mean()
   for sid,r in te.iterrows():diag.append(dict(regime=s['regime'],seed=s['seed'],study_id=r.study_id,target=t,sample_id=sid,y=int(r[t]),p=float(by.get(r.study_id,prior)),seen_study=r.study_id in by.index))
 diagnostic=pd.DataFrame(diag);diagnostic.to_csv(O/'known_study_prior_predictions.csv',index=False)
 diagnostic['brier']=(diagnostic.y-diagnostic.p)**2
 diagnostic.groupby(['regime','target','study_id']).brier.mean().groupby(['regime','target']).mean().to_csv(O/'known_study_prior_metrics.csv')
 # Unit sensitivity on held-out cohorts only, all original fitted predictions retained.
 logstudies=set(raw.loc[raw['Protein Composition Units'].str.contains('Log2',case=False),'Study ID']);sens=gap[~gap.study_id.isin(logstudies)].groupby(['target','model'])[['LOSO_gap','GROUP_gap']].mean();sens.to_csv(O/'log_units_exclusion_sensitivity.csv')
 # Training-fit uncertainty: independent fitting, study-resampled training, common OOB test across models.
 boot=pd.read_csv(O/'training_bootstrap_predictions.csv');bm=metric_table(boot);bm.to_csv(O/'training_bootstrap_study_metrics.csv',index=False)
 br=bm.groupby(['fold','target','model'],as_index=False).brier.mean();br=ratios(br,['fold','target']);br.to_csv(O/'training_bootstrap_bss.csv',index=False)
 ub=[]
 for t in T+['OVERALL_MACRO']:
  z=br[br.target==t] if t in T else ratios(bm.groupby(['fold','target','model'],as_index=False).brier.mean().groupby(['fold','model'],as_index=False).brier.mean(),['fold'])
  for model in ['LR','RF']:
   x=z['BSS_'+model].dropna();ub.append(dict(target=t,model=model,n_refits=len(x),bss_median=x.median(),q05=x.quantile(.05),q95=x.quantile(.95),fraction_bss_positive=x.gt(0).mean(),uncertainty='TRAINING_PERTURBATION_DISTRIBUTION_NOT_CI'))
 pd.DataFrame(ub).to_csv(O/'training_uncertainty_summary.csv',index=False)
 sm[sm.regime=='LOSO'].groupby(['seed','target','model']).brier.mean().to_csv(O/'model_seed_variability.csv')
 if (O/'material_predictions.csv').exists():
  material=metric_table(pd.read_csv(O/'material_predictions.csv'));material.to_csv(O/'material_study_metrics.csv',index=False);ratios(material.groupby(['fold','target','model'],as_index=False).brier.mean(),['fold','target']).to_csv(O/'material_bss.csv',index=False)
 primary=summary[(summary.regime=='LOSO')&summary.model.isin(['LR','RF'])&summary.target.isin(T)]
 counts=primary[primary.ci_low>0].groupby('model').size().to_dict()
 strong=all(counts.get(m,0)>=3 for m in ['LR','RF']) and (primary.median_study_gap>0).all() and (primary.leave_one_study_mean_min>0).all()
 classification='STRONG SIGNAL' if strong else 'HETEROGENEOUS SIGNAL' if (primary.ci_low>0).any() else 'WEAK SIGNAL'
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),signal=classification,positive_ci_targets=counts,log_unit_studies=sorted(logstudies),sample_match='PASS',label_construction='UNKNOWN; audited definition unchanged',temporal='INSUFFICIENT DATA',uncertainty='conditional study-bootstrap CI; training perturbations separately; measurement uncertainty unquantified',script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'analysis_report.json').write_text(json.dumps(report,indent=2));print(bo.to_string(index=False));print(primary[['model','target','gap','ci_low','ci_high','fraction_studies_positive']].to_string(index=False));print(json.dumps(report))
if __name__=='__main__':main()
