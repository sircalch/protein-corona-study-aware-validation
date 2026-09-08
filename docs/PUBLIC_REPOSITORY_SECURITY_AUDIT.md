# Public repository security audit

Audited candidate: `reproducibility_repository_candidate/` on 2026-09-07.

| Check | Result |
| --- | --- |
| Raw PC-DB/PROTCROWN directories excluded | PASS |
| Row-level predictions and split manifests excluded | PASS |
| Absolute local paths and user paths | PASS: no matches in public-release content |
| Credential signatures, private-key markers and access-key patterns | PASS: no matches in public-release content |
| Temporary environments, caches and Python bytecode | PASS: ignored by `.gitignore`; no tracked release content |
| Public-safe release tests | PASS: 5 tests in clean environment |

The scan is not a legal rights determination. `DATA_RIGHTS.md` defines the separate third-party-content exclusion boundary.
