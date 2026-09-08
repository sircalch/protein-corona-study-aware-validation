# Reproduction test report

Status: **PASS for the public static release; end-to-end refitting NOT RUN by the scientific freeze.**

| Field | Value |
| --- | --- |
| OS | Windows NT 10.0.26200.0, 64-bit |
| Python | 3.12.10 in a new virtual environment |
| Dependencies | Installed from public `requirements.lock.txt`; includes numpy 1.26.4, pandas 2.2.3, scikit-learn 1.5.2 and matplotlib 3.11.1 |
| Commands | `python -m unittest discover -s tests`; `python scripts/release_checks.py`; `python scripts/security_audit.py`; `python scripts/generate_figures.py` |
| Static test result | 5 tests passed |
| Release checks | PASS: public-safe layout, numerical audit, reference audit and raw-data exclusion |
| Security audit | PASS: no absolute Windows-drive paths, user paths, credential signatures or raw-data directory in the public candidate |
| Figures | Figure 2 and Figure 4 regenerated from frozen aggregate CSV files in the clean environment |

| Reference item | Reference value | Reproduced value | Tolerance | Status |
| --- | ---: | ---: | ---: | --- |
| Source / development cohort | 597 / 595 records | 597 / 595 records | exact | PASS |
| Studies / reserved records | 52 / 51 / 2 | 52 / 51 / 2 | exact | PASS |
| C3 unknown labels | 4 | 4 | exact | PASS |
| RANDOM macro BSS, LR / RF | 0.089006 / 0.145968 | 0.089006 / 0.145968 | 1e-6 | PASS |
| Study-grouped macro BSS, LR / RF | -0.211966 / -0.079104 | -0.211966 / -0.079104 | 1e-6 | PASS |
| LOSO macro BSS, LR | -0.241715 | -0.241715 | 1e-6 | PASS |
| Figure 2 / Figure 4 | Generated from frozen aggregate outputs | Generated in clean environment | source values exact | PASS |

No source acquisition, cohort reconstruction, split creation, or model fitting was run in this test. The manuscript freeze explicitly prohibits new scientific analyses and training. Accordingly, this report does not present an end-to-end refit as completed.
