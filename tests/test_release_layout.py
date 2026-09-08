import csv
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class ReleaseLayoutTest(unittest.TestCase):
    def test_required_outputs_exist(self):
        for rel in ['README.md','requirements.lock.txt','aggregate_results/bss_overall_macro.csv','figures/Figure_1.pdf','docs/DATA_RIGHTS.md']:
            self.assertTrue((ROOT / rel).is_file(), rel)
    def test_headline_metrics_match_frozen_aggregate(self):
        with (ROOT / 'aggregate_results/bss_overall_macro.csv').open(newline='', encoding='utf-8') as handle:
            rows = {row['regime']: row for row in csv.DictReader(handle)}
        self.assertAlmostEqual(float(rows['RANDOM']['BSS_LR']), .089006, places=6)
        self.assertAlmostEqual(float(rows['RANDOM']['BSS_RF']), .145968, places=6)
        self.assertAlmostEqual(float(rows['GROUP_STUDY']['BSS_LR']), -.211966, places=6)
        self.assertAlmostEqual(float(rows['GROUP_STUDY']['BSS_RF']), -.079104, places=6)
if __name__ == '__main__':
    unittest.main()
