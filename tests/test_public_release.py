import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReleaseTest(unittest.TestCase):
    def test_public_safe_structure(self):
        for name in ["README.md", "LICENSE", "CITATION.cff", ".zenodo.json", "environment.yml", "manifests/source_manifest.json", "manifests/cohort_summary.json"]:
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertFalse((ROOT / "data" / "raw").exists())

    def test_frozen_counts_and_headline_metrics(self):
        summary = json.loads((ROOT / "manifests/cohort_summary.json").read_text(encoding="utf-8"))
        self.assertEqual((summary["source_records"], summary["source_studies"], summary["reserved_records"]), (597, 52, 2))
        self.assertEqual((summary["development_records"], summary["development_studies"]), (595, 51))
        self.assertEqual(summary["targets"]["C3"]["unknown"], 4)
        with (ROOT / "aggregate_results" / "bss_overall_macro.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["regime"]: row for row in csv.DictReader(handle)}
        self.assertAlmostEqual(float(rows["RANDOM"]["BSS_LR"]), .089006, places=6)
        self.assertAlmostEqual(float(rows["GROUP_STUDY"]["BSS_RF"]), -.079104, places=6)
        self.assertAlmostEqual(float(rows["LOSO"]["BSS_LR"]), -.241715, places=6)

    def test_security_audit(self):
        result = subprocess.run([sys.executable, "scripts/security_audit.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
