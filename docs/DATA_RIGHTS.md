# Data and rights audit

Public download availability is not evidence that third-party rows, source code, publisher files, or derived row-level artifacts may be redistributed. The public repository excludes all such material.

| Resource | Owner/source | Access URL | License | Redistribution clearly allowed? | Derived-data implications | Repository action |
| --- | --- | --- | --- | --- | --- |
| PC-DB supporting datasets and metadata | Chou laboratory / ACS Figshare supporting record | `https://acs.figshare.com/articles/journal_contribution/Meta-Analysis_and_Machine_Learning_Prediction_of_Protein_Corona_Composition_across_Nanoparticle_Systems_in_Biological_Media/30256369` | Article XML records CC BY-NC 4.0; independent file-level terms not verified | No for row-level copies | Cohorts, splits, labels and predictions can reconstruct source rows | Exclude; provide source URL, pinned upstream revision, hashes and acquisition instructions only |
| PC-DB upstream GitHub files | `choulab210/Meta-Analysis-of-Nanoparticle-and-Protein-Corona-Interactions-in-Biological-Media` | URL recorded in `evidence/data_download_manifest.json` | Repository inspected with no explicit LICENSE | No | Copied notebooks/code and modified derivatives require separate review | Exclude upstream copies; cite and link only |
| PROTCROWN metadata and abundance workbooks | PROTCROWN authors / publisher resource | DOI `10.1021/acs.nanolett.4c05955` and official supporting-information route | Supporting-information record observed as CC BY-NC 4.0; workbook-level redistribution not independently cleared | No for workbooks/rows | Row-level feasibility linkage is not verified and should not be published | Exclude raw workbooks and rows; retain aggregate feasibility counts and acquisition instructions |
| Publisher PDFs, HTML and supplementary evidence | Publishers and article authors | URLs retained in evidence and reference audit | Varies; not independently cleared for redistribution | No | Extracted evidence is sufficient locally; file copies are not required publicly | Exclude |
| Project-authored release wrapper, tests and documentation | This project, under user-authorized release | Local work product | CC BY-NC 4.0 chosen for the public repository release | Yes, for these files only | Must not contain copied third-party rows or source-code fragments | Publish after security scan |
| Aggregate metrics, figure source tables and frozen figures | Derived project outputs | Generated locally from frozen outputs | CC BY-NC 4.0 for the released aggregate artifacts, subject to the exclusion above | Yes, after row-level disclosure check | Aggregate values cannot include sample IDs, row-level predictions or reconstructable manifests | Publish only aggregate-safe files checked by release tests |
| Manuscript and editorial files | Project authors | Local submission package | Author/journal rights pending | No public manuscript deposit at this stage | Authorship and publisher route remain incomplete | Keep out of the public repository and Zenodo archive until authors approve |

## Public-release boundary

The repository may publish project-authored code, static tests, configuration, source-acquisition instructions, checksums, aggregate outputs, figure assets and documentation. It must not publish raw PC-DB or PROTCROWN files, source-derived row-level CSVs, sample identifiers, split manifests containing sample IDs, row-level predictions, publisher PDFs/HTML, credentials, or local paths.

This audit does not grant rights over third-party material. It records the conservative release boundary applied to the public repository.
