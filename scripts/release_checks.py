from pathlib import Path
import csv
ROOT = Path(__file__).resolve().parents[1]
required = ['README.md','LICENSE','CITATION.cff','.zenodo.json','requirements.lock.txt','environment.yml','aggregate_results/bss_overall_macro.csv','aggregate_results/FINAL_NUMBER_AUDIT.csv','aggregate_results/FINAL_REFERENCES_AUDIT.csv','figures/Figure_1.pdf','docs/DATA_RIGHTS.md','manifests/source_manifest.json','manifests/cohort_summary.json']
missing = [item for item in required if not (ROOT / item).is_file()]
with (ROOT / 'aggregate_results/FINAL_NUMBER_AUDIT.csv').open(newline='', encoding='utf-8') as h: numeric_ok = all(row['Status'] == 'VERIFIED' for row in csv.DictReader(h))
with (ROOT / 'aggregate_results/FINAL_REFERENCES_AUDIT.csv').open(newline='', encoding='utf-8') as h: refs_ok = all(row['Verified'] == 'YES' for row in csv.DictReader(h))
raw_present = (ROOT / 'data' / 'raw').exists()
if missing or not numeric_ok or not refs_ok or raw_present: raise SystemExit(f'FAIL missing={missing} numeric={numeric_ok} refs={refs_ok} raw_present={raw_present}')
print('PASS: public-safe layout, numeric audit, reference audit and raw-data exclusion')
