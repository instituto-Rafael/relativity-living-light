"""RLL geometric bridge: mathematical and counterexample gates only."""
import importlib.util
import math
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"scripts/rll_pythagoras_geodesic_bridge_v1.py"
sp=importlib.util.spec_from_file_location("geo_bridge",PATH)
geo=importlib.util.module_from_spec(sp)
sp.loader.exec_module(geo)

class TestGeodesicBridge(unittest.TestCase):
    def test_plane(self):
        self.assertAlmostEqual(geo.pythagoras_isosceles(1,1)["height"],math.sqrt(3)/2,places=13)
        self.assertAlmostEqual(geo.pythagoras_isosceles(1,1)["unit_direction_chord_discriminant"],3)
    def test_sphere(self):
        self.assertAlmostEqual(geo.spherical_geodesic_altitude(1,1,1),.907558874685877,places=12)
    def test_flat_limit(self):
        self.assertAlmostEqual(geo.spherical_geodesic_altitude(1,1,1e6),math.sqrt(3)/2,places=10)
    def test_bad_sphere(self):
        with self.assertRaises(ValueError):geo.spherical_geodesic_altitude(1,2.5,1)
    def test_torus_pythagoras(self):
        r=geo.torus_local_pythagoras(3,1,.3,math.pi/3,.2,.1)
        self.assertAlmostEqual(r["ds2"],.5)
        self.assertEqual(r["global_minimizing_geodesic"],"TOKEN_VAZIO_NOT_SOLVED")
    def test_torus_invalid(self):
        with self.assertRaises(ValueError):geo.torus_local_pythagoras(1,2,0,0,.1,.1)
    def test_same_area_distinct_volumes(self):
        a,b=geo.annular_equal_area_counterexample(1)
        self.assertAlmostEqual(a["area_annulus"],b["area_annulus"])
        self.assertAlmostEqual(a["surface_torus"],b["surface_torus"])
        self.assertAlmostEqual(b["volume_torus"]/a["volume_torus"],2*math.sqrt(3)-3)
        self.assertNotAlmostEqual(a["meridian_metric_G"],b["meridian_metric_G"])
    def test_scale_survives_reduction(self):
        self.assertEqual(geo.fraction_index_trace(77,33)["nominal_scale"],11)
        self.assertEqual(geo.fraction_index_trace(7,3)["nominal_scale"],1)
    def test_mod_zero_keeps_winding(self):
        a=geo.modulo_index_trace(77,7)
        self.assertEqual((a["residue"],a["winding"]),(0,11))
    def test_bad_indexes(self):
        with self.assertRaises(ValueError):geo.fraction_index_trace(1,0)
        with self.assertRaises(ValueError):geo.modulo_index_trace(1,0)
    def test_claim_gate_closed(self):
        x=geo.evaluate()
        self.assertFalse(x["claim_allowed"])
        self.assertFalse(x["real_data_processed"])
        self.assertFalse(x["likelihood_modified"])
        self.assertEqual(x["chi2_preserved"],"NOT_RUN_NO_DATA_READ")
if __name__=="__main__":unittest.main()
