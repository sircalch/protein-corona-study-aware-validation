# Final claim evidence ledger

| Claim ID | Claim | Class | Evidence | Status |
| --- | --- | --- | --- | --- |
| C01 | Public source: 597 records and 52 studies | COMPUTED | `audit/data_audit.json`; `FINAL_NUMBER_AUDIT.csv` N01-N02 | VERIFIED |
| C02 | Development cohort: 595 records and 51 studies; two reserved records unscored | COMPUTED | `design_summary.json`; number audit N03-N05 | VERIFIED |
| C03 | Random macro BSS is positive for fixed LR and RF | COMPUTED | `bss_overall_macro.csv`; number audit | VERIFIED |
| C04 | Matched-size GROUP_STUDY macro BSS is negative for fixed LR and RF | COMPUTED | `bss_overall_macro.csv`; number audit | VERIFIED |
| C05 | Conditional GROUP_STUDY minus RANDOM Brier intervals exclude zero under the stated fixed-prediction bootstrap | DERIVED | `gap_uncertainty.csv`; number audit | VERIFIED |
| C06 | LOSO shows the same qualitative macro direction | COMPUTED | `bss_overall_macro.csv`; number audit | VERIFIED |
| C07 | C3 has heterogeneous study-level behavior and remains in the analysis | COMPUTED | `gap_uncertainty.csv`; target outputs | VERIFIED |
| C08 | A10/A38 clean exclusion preserves the qualitative macro pattern | COMPUTED | `clean_macro_bss.csv`; number audit | VERIFIED |
| C09 | The feature blocks are descriptive rather than causal | PLAN | Frozen analysis specification and manuscript interpretation boundary | VERIFIED |
| C10 | 60.392% is a descriptive between-study one-hot covariate sum-of-squares fraction | DERIVED | `covariate_variance_decomposition.csv`; number audit | VERIFIED |
| C11 | No compatible PROTCROWN external validation set is currently verified | COMPUTED | `protcrown_feasibility.json`; Figure S1 audit | VERIFIED |
| C12 | The upstream published label construction cannot be reconstructed from available public artifacts | UNKNOWN | `LABEL_PROVENANCE.md`; audit records | RETAINED AS UNKNOWN |
| C13 | Protein coronas contribute to nanoparticle biological identity | LITERATURE | References 1-3; reference audit | VERIFIED |
| C14 | Harmonized reporting/data provenance support reproducible comparison | LITERATURE | References 4,12,13,17,18; reference audit | VERIFIED |
| C15 | A public archive with DOI will be provided before submission | PLAN | `FINAL_SUBMISSION_CHECKLIST.md` | BLOCKED |
