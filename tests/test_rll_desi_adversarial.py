"""Adversarial, fail-closed unit controls for the BAO profiling gate."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('rll_desi_adversarial', ROOT/'scripts'/'rll_desi_adversarial.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DESIAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = MOD.load_inputs(ROOT)

    def test_exact_producer_blob_pins_and_shape(self):
        for key, sha in MOD.SOURCE_BLOBS.items():
            self.assertEqual(self.data['source'][key]['git_blob_sha1'], sha)
        self.assertEqual(self.data['cov'].shape, (13, 13))
        self.assertTrue(np.all(np.linalg.eigvalsh(self.data['cov']) > 0))

    def test_fixed_source_numbers_reproduced(self):
        self.assertAlmostEqual(MOD.chi2(self.data,'LCDM',np.array([67.4,.315])), 28.69374102, delta=2e-7)
        self.assertAlmostEqual(MOD.chi2(self.data,'RLL',np.array([67.4,.315,.02,1.,.3])), 34.52753599, delta=2e-7)

    def test_nested_limits(self):
        z=self.data['z']
        ref=MOD.hubble_ratio_sq('LCDM',np.array([68.,.28]),z)
        self.assertTrue(np.allclose(ref, MOD.hubble_ratio_sq('RLL',np.array([68.,.28,0.,.6,.15]),z), atol=1e-12))
        self.assertTrue(np.allclose(ref, MOD.hubble_ratio_sq('CPL',np.array([68.,.28,-1.,0.]),z), atol=1e-12))
        for model,theta in [('LCDM',[68.,.28]),('CPL',[68.,.28,-.9,.5]),('RLL',[68.,.28,.1,.5,.2])]:
            self.assertAlmostEqual(float(MOD.hubble_ratio_sq(model,np.array(theta),np.array([0.]))[0]),1.,places=13)

    def test_unpinned_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            for source in (MOD.MEAS, MOD.COV):
                (base/source).parent.mkdir(parents=True,exist_ok=True)
                shutil.copy(ROOT/source, base/source)
            target=base/MOD.MEAS
            target.write_bytes(target.read_bytes().replace(b'7.94167639', b'7.94167640'))
            with self.assertRaisesRegex(ValueError, 'UNPINNED_SOURCE'):
                MOD.load_inputs(base)

    def test_covariance_and_observable_corruption_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            for source in (MOD.MEAS, MOD.COV):
                (base/source).parent.mkdir(parents=True,exist_ok=True)
                shutil.copy(ROOT/source, base/source)
            cov=base/MOD.COV
            cov.write_text(cov.read_text().replace('5.78998687e-03','-5.78998687e-03'))
            with self.assertRaises(ValueError): MOD.load_inputs(base,enforce_pins=False)

    def test_model_competition_has_no_preordained_winner(self):
        baseline=MOD.fit(self.data,'LCDM',42,5)
        rll=MOD.fit(self.data,'RLL',42,5,baseline['_theta'])
        cpl=MOD.fit(self.data,'CPL',42,5,baseline['_theta'])
        self.assertLessEqual(rll['chi2'], baseline['chi2'] + 1e-7)
        self.assertLessEqual(cpl['chi2'], baseline['chi2'] + 1e-7)
        self.assertEqual((baseline['k_fit'],cpl['k_fit'],rll['k_fit']),(2,4,5))
        self.assertIn('wt',rll['boundary_parameters'])

    def test_seeded_null_bootstrap_is_reproducible(self):
        baseline=MOD.fit(self.data,'LCDM',42,3)
        rll=MOD.fit(self.data,'RLL',42,3,baseline['_theta'])
        one=MOD.bootstrap_null(self.data,baseline,rll,3,31,3)
        two=MOD.bootstrap_null(self.data,baseline,rll,3,31,3)
        self.assertEqual(one,two)
        self.assertFalse(one['reliable_tail_inference'])
        self.assertFalse(one['critical_values_calibrated'])

    def test_heldout_blocks_do_not_leak_observations(self):
        ix=np.array([0]); train=np.arange(1,13)
        cov_cross=self.data['cov'][np.ix_(ix,train)]
        self.assertTrue(np.all(cov_cross==0.))
        d=MOD.subdata(self.data,train)
        before=MOD.fit(d,'LCDM',42,3)['chi2']
        mutated=self.data['y'].copy(); mutated[ix] += 1000.
        after=MOD.fit(MOD.subdata(self.data,train,mutated),'LCDM',42,3)['chi2']
        self.assertAlmostEqual(before,after,places=10)

    def test_output_no_overwrite_and_claim_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=['--root',str(ROOT),'--output-dir',tmp,'--seed','42','--starts','3','--bootstrap','0']
            self.assertEqual(MOD.main(args),0)
            files=list(Path(tmp).glob('*.json')); self.assertEqual(len(files),1)
            result=json.loads(files[0].read_text())
            self.assertFalse(result['claim_allowed'])
            self.assertEqual(result['null_bootstrap']['state'],'NOT_EXECUTED')
            with self.assertRaises(FileExistsError): MOD.main(args)

    def test_subset_indices_reject_aliasing_and_double_counting(self):
        for indices in ([-1, 0], [0, 13], [0, 0], [True, False], [0., 1.], [], [[0, 1]]):
            with self.subTest(indices=indices), self.assertRaisesRegex(ValueError, 'INVALID_SUBDATA_INDICES'):
                MOD.subdata(self.data, np.asarray(indices))

    def test_valid_permutation_keeps_observations_and_covariance_aligned(self):
        indices = np.array([12, 0, 3, 1])
        result = MOD.subdata(self.data, indices)
        np.testing.assert_array_equal(result['y'], self.data['y'][indices])
        np.testing.assert_array_equal(result['cov'], self.data['cov'][np.ix_(indices, indices)])
        self.assertEqual(result['obs'], [self.data['obs'][i] for i in indices])
        np.testing.assert_allclose(result['chol'] @ result['chol'].T, result['cov'])

    def test_subset_override_requires_complete_finite_vector(self):
        for y in (np.zeros(12), np.zeros((13, 1)), np.full(13, np.nan)):
            with self.assertRaisesRegex(ValueError, 'INVALID_SUBDATA_OBSERVATIONS'):
                MOD.subdata(self.data, np.array([0, 1]), y)

    def test_prediction_rejects_partial_observable_vector(self):
        for obs in (self.data['obs'][:-1], self.data['obs'] + ['DM_over_rd'], ['UNKNOWN'] * 13):
            with self.assertRaisesRegex(ValueError, 'INVALID_PREDICTION_OBSERVABLE_ALIGNMENT'):
                MOD.predict('LCDM', np.array([67.4, .315]), self.data['z'], obs)

    def test_malformed_csv_rows_and_duplicate_columns_fail_closed(self):
        for mutation, expected in (
            (lambda text: text.replace('index,tracer', 'index,index'), 'HEADER_MISMATCH'),
            (lambda text: text.replace('0,BGS,', '0,BGS,EXTRA,'), 'ROW_SHAPE_MISMATCH'),
            (lambda text: text.replace('0,BGS,', '00,BGS,'), 'ORDERED_BAO_ROWS'),
        ):
            with tempfile.TemporaryDirectory() as td:
                base = Path(td)
                for source in (MOD.MEAS, MOD.COV):
                    (base/source).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(ROOT/source, base/source)
                target = base/MOD.MEAS
                target.write_text(mutation(target.read_text()))
                with self.assertRaisesRegex(ValueError, expected):
                    MOD.load_inputs(base, enforce_pins=False)


if __name__=='__main__':
    unittest.main()
