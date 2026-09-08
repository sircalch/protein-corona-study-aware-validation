# Final reproducibility checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Frozen canonical inputs preserved | PASS | `manuscript_audit/canonical_input_hashes.json` |
| Number claims audited | PASS | `FINAL_NUMBER_AUDIT.csv`; all rows VERIFIED |
| DOI metadata checked | PASS | `FINAL_REFERENCES_AUDIT.csv` |
| Fixed-output Study-grouped−RANDOM contrast used | PASS | `runs/confirmatory/gap_uncertainty.csv` |
| No model retraining during final revision | PASS | Figure, document and release scripts do not fit models |
| Figure source data copied and hashed | PASS | Figure `source_data/`; `FINAL_FIGURE_SOURCE_HASHES.json` |
| Figure visual QC completed | PASS | `FIGURE_QC_REPORT.md`; final PDF render inspected |
| Manuscript and supplement rendering inspected | PASS | LibreOffice PDF render: 11 main-text pages and 4 supplementary pages |
| Public static reproducibility package | PASS | https://github.com/sircalch/protein-corona-study-aware-validation; source manifests, frozen aggregates, tests and regeneration of Figures 2 and 4 |
| Clean-environment static reproduction | PASS | `REPRODUCTION_TEST_REPORT.md`; five tests, release checks and aggregate-figure regeneration passed |
| Independent end-to-end source acquisition and refit | NOT RUN | The scientific freeze forbids new model training; restricted source rows were deliberately not acquired |
| Immutable tag and archival DOI | BLOCKED | Tag and archive are deferred until verified creators and Zenodo authorization are available |

