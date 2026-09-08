# Frozen configuration

Targets: APOE, APOB, C3/CO3, CLUS. Predictors: Type, Subtype, Mod_Charge, Size_Group, ZP_Group, ZP_Charge, In_Time, Shaking. LR: C=1; max_iter=2000. RF: 100 trees; min_samples_leaf=5; n_jobs=1. Seeds: 32, 1729, 2026. Primary contrast: matched-size GROUP_STUDY minus RANDOM. Complementary contrast: LOSO minus RANDOM. Bootstrap: paired conditional study bootstrap; 2,000 draws; seed 2026.
