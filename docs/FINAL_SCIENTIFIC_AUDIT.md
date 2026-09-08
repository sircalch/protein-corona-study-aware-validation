# Final scientific audit

## Freeze status

**SCIENTIFIC RESULTS FROZEN.** The audit verified that no editorial work changed labels, cohort, targets, split logic, models, hyperparameters, endpoint, exclusions, bootstrap procedure, or frozen numerical results. Permitted operations were source re-reads, provenance checks, manuscript editing, table composition, figure regeneration from frozen outputs, and format conversion.

## Traceability chain

| Link | Evidence | Status |
| --- | --- | --- |
| Source data to audited cohort | `DATA_PROVENANCE.md`; `audit/data_audit.json`; canonical hashes | PASS |
| Cohort to targets/endpoint | `MINIMAL_BENCHMARK_LOCK.md`; `LABEL_PROVENANCE.md`; `manuscript_audit/cohort_targets.csv` | PASS |
| Cohort to splits | `splits/manifests.json`; `runs/confirmatory/loso_manifest.json` | PASS |
| Splits to fixed predictions | fit logs, manifests, `runs/confirmatory/` | PASS |
| Predictions to metrics/intervals | `scripts/analyze_confirmatory.py`; `bss_overall_macro.csv`; `gap_uncertainty.csv` | PASS |
| Metrics to figures/tables/manuscript | `FINAL_NUMBER_AUDIT.csv`; `FIGURE_PROVENANCE.csv`; `FINAL_CLAIM_EVIDENCE_LEDGER.md` | PASS |

## Number audit

`FINAL_NUMBER_AUDIT.csv` records each displayed scientific quantity with a claim identifier, source file, selector, calculation description, checking script, recomputed value, match flag and status. The audit contains only `VERIFIED` rows. The audit is not a new statistical analysis: it re-reads frozen source values or fixed configuration constants.

## Scope limits retained

The published classification-label transformation is unresolved. The benchmark endpoint is the audited quantitative-positive detection rule, not semantic reproduction of the source labels or a direct physical-binding measurement. Conditional study-bootstrap intervals are conditional on frozen predictions. PROTCROWN remains an external-feasibility audit only; no compatible external score was produced. These limitations are stated in the main manuscript and supplement.
