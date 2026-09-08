# Reproducibility release plan

**PLAN — no upload, license assignment or fresh scientific execution performed.** RELEASE_FILE_CLASSIFICATION.csv inventories every file currently present, including environment/development files, with an explicit proposed release class. The inventory is an editorial screening, not legal permission or an assertion of author ownership. Source-dependent rows are conservatively excluded until terms are established. Nothing is deleted.

| Class | Meaning |
|---|---|
| INCLUDE | Author-created code/docs/configuration eligible for release after author ownership/declaration review |
| INCLUDE GENERATED | Existing aggregate metrics, figures and author-generated provenance; not new results |
| DO NOT REDISTRIBUTE | Third-party downloads, source data, source-row derivatives or source-bearing predictions/manifests without established redistribution rights |
| REFERENCE ONLY | Preserve locally and cite origin/version/hash; do not package the content by default |
| PRIVATE/DEVELOPMENT | Environment, caches, prompts, internal editorial/review material and superseded development files |

## Proposed public structure

```text
README.md                 # study scope, limitations, execution order and expected outputs
LICENSE                   # chosen only for confirmed author-owned code
CITATION.cff              # real authors/version; DOI only after deposit exists
environment/              # requirements.lock.txt, requirements.confirmatory.lock.txt
scripts/                  # frozen author-owned fitting/analysis/display code
configs/                  # effective model parameters, seeds and preprocessing definitions
manifests/                # hashes and source acquisition records; restricted row lists rebuilt locally
derived_data/             # aggregate figure sources only; source-bearing rows rebuilt locally
results/                  # primary and final-robustness aggregate tables, labeled separately
figures/                  # six final PNG/SVG assets and provenance
docs/                     # methods/endpoint limits, numerical traceability, source-access guide
```

Use GitHub for reviewed author-owned code and Zenodo/OSF for a fixed archival version if selected by the authors. A local-only plan is not deposition. No DOI, author list, account, license or reviewer-access URL is invented. Do not use a root license that appears to cover PC-DB, PROTCROWN, publisher PDFs, third-party scripts or their underlying records.

## Acquisition and execution specification

The PC-DB source commit is `761dc04a9a5815684ea8923fa86f9aac262c4a6a`. Preserve the original source URLs and expected hashes from evidence/data_download_manifest.json, DATA_PROVENANCE.md and SHA256_MANIFEST.json. The source repository is https://github.com/choulab210/Meta-Analysis-of-Nanoparticle-and-Protein-Corona-Interactions-in-Biological-Media. Required inputs include PC-DB_for_Meta-Analysis.csv, Dataset-for-protein-freq-analysis-v2.csv and prediction_model_data_human_only.csv under data/raw/pcdb/Datasets/. Obtain them lawfully from that original repository at the frozen commit. Public availability alone is not a blanket redistribution license.

A reproducibility run in a **separate fresh directory** should acquire sources, check hashes, install the exact pinned environment, and follow the frozen pipeline: prepare_benchmark.py; compare_splits.py; confirmatory_fit.py and analyze_confirmatory.py; final_robustness_fit.py and analyze_final_robustness.py; the corresponding verify scripts; manuscript_displays.py. Read the frozen locks/run logs before invoking scripts: preserve parameters, seeds and split IDs, and do not substitute new defaults. The release README must copy actual recorded command arguments from run manifests. Some reporting scripts write project documents and should not be run inside the canonical archive. This ordered specification is not a claim that a clean external reproduction was executed here.

Published-label numerical reproduction is separate from the audited-endpoint benchmark and must remain labeled accordingly. PROTCROWN acquisition/schema audit is a separate feasibility path (fetch_protcrown.py and audit_protcrown_feasibility.py), never external scoring. Do not run any positional RPA join. Freeze the source release and supply its original download records; changes at live websites are not silently accepted.

## Rights-sensitive boundary

Raw PC-DB/PROTCROWN files, prepared labels, downloaded SI/PDFs/HTML and copied upstream code are DO NOT REDISTRIBUTE. The separate article-SI license does not establish rights in website XLSX files. Row-level cohort tables, per-record predictions containing outcomes, target labels and sample-bearing split JSON can reconstruct source observations and are also excluded by default. Supply deterministic reconstruction code and expected hashes instead. Aggregate study/model metrics and original visualizations may be proposed for release, but perform the documented author ownership/source-content review before deposition. The conservative default may omit releasable files; this is preferable to claiming permissions not established.

Reviewers need usable access before submission: code, allowed aggregate outputs, explicit input-source instructions and source terms. If a required source becomes unavailable or cannot lawfully be obtained, document that reproducibility limitation; do not claim a self-contained release. Source reproducibility does not repair unresolved upstream semantic labels. All local originals, history and downloads remain preserved regardless of release class.
