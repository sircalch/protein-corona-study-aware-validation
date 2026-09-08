# Protein corona study aware validation

This public repository is the reproducibility release for the frozen analysis, **Study-aware validation of cross-study transportability in protein-corona detection models**. It contains only project-authored code, aggregate outputs, figures, checksums and documentation. Raw PC-DB/PROTCROWN files, row-level derivatives, split manifests with sample identifiers, source downloads, manuscript files and credentials are excluded.

## Scope

The primary comparison is **Study-grouped** versus RANDOM with the same target-specific training-size cap. LOSO is complementary. The endpoint is audited reported quantitative-positive detection; it is not a physical-binding measurement or semantic reconstruction of upstream labels.

## Reproducibility workflow

1. Review `docs/DATA_RIGHTS.md` and the upstream terms.
2. Acquire upstream files to an ignored local directory: `python scripts/acquire_sources.py --accept-source-terms`.
3. Verify checksums: `python scripts/verify_sources.py`.
4. Inspect the frozen configuration in `configs/frozen_configuration.md` and `manifests/cohort_summary.json`.
5. Verify public aggregate results and figure sources: `python scripts/release_checks.py`.
6. Regenerate the public Figure 2 and Figure 4 displays from aggregate outputs: `python scripts/generate_figures.py`.

The public release does **not** claim one-command, end-to-end rerunning of cohort construction, split generation or model fitting. Those steps require lawful source acquisition and an explicitly authorized independent reproduction exercise. No new fit, target, result or analysis is created by the static checks or figure regeneration shipped here.

## Layout

- `aggregate_results/`: frozen aggregate metrics and source tables
- `configs/`: effective fixed settings
- `docs/`: data rights, provenance and scientific limits
- `figures/`: publication assets in SVG, PDF, PNG and TIFF
- `manifests/`: public-safe cohort and source-checksum manifests
- `scripts/`: acquisition, verification, release checks and figure regeneration
- `tests/`: static integrity and security tests

## License and citation

The project-authored material is released under [CC BY-NC 4.0](LICENSE). See `CITATION.cff`. Creator metadata is intentionally omitted until author information is confirmed for this specific manuscript.
