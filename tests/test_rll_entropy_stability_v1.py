import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools/rll_entropy_stability.py'
spec=importlib.util.spec_from_file_location('entropy_stability',SCRIPT)
core=importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

class EntropyStabilityTests(unittest.TestCase):
    def test_relabel_invariant(self):
        self.assertAlmostEqual(core.entropy_discrete([0,0,1,1,2]),
                               core.entropy_discrete([10,10,7,7,99]))
    def test_binary_entropy(self):
        self.assertAlmostEqual(core.entropy_discrete([0,1,0,1]),1)
    def test_sample_vs_population(self):
        self.assertAlmostEqual(core.sample_std([1,2,3]),1)
    def test_insufficient_sample(self):
        self.assertIsNone(core.sample_std([5]))
    def test_bad_data_rejected(self):
        with self.assertRaises(ValueError):core.entropy_discrete([1,float('nan')])
    def test_regression(self):
        self.assertAlmostEqual(core.slope([0,1,2,3],[8,9,10,11]),1)
    def test_no_regression_one_point(self):
        self.assertIsNone(core.slope([1],[1]))
    def test_decomposition_identity(self):
        r=core.between_within([[1,2,3],[3,4,5]])
        self.assertAlmostEqual(r['total_sse'],r['within_sse']+r['between_sse'])
    def test_entropy_equal_but_drift(self):
        d=core.compute()
        self.assertAlmostEqual(d['baseline']['H_mean'], d['drifting']['H_mean'])
        self.assertEqual(d['baseline']['H_sample_std'],0)
        self.assertEqual(d['drifting']['H_sample_std'],0)
        self.assertAlmostEqual(d['baseline']['mean_linear_slope_value_per_window'],0)
        self.assertAlmostEqual(d['drifting']['mean_linear_slope_value_per_window'],1)
    def test_between_variance_detects_drift(self):
        d=core.compute()
        self.assertEqual(d['baseline']['variance_decomposition']['between_fraction'],0)
        self.assertGreater(d['drifting']['variance_decomposition']['between_fraction'],0)
    def test_no_physical_claim(self):
        d=core.compute()
        self.assertFalse(d['claim_allowed']);self.assertFalse(d['cosmology_fit_modified'])
        self.assertEqual(d['gates']['lyapunov'],'TOKEN_VAZIO_PHYSICAL_DYNAMICS_AND_PERTURBATION_EVOLUTION')
    def test_all_seven_windows_equal_entropy(self):
        d=core.compute()
        x=[round(r['shannon_empirical_bits_per_symbol'],12) for r in d['drifting']['per_window']]
        self.assertEqual(len(set(x)),1)
        self.assertEqual(len(x),7)

if __name__=='__main__':unittest.main()
