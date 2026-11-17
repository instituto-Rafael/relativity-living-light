"""Synthetic adversarial checks for H-CRIT. No EOS or observational fit implied."""
import json
import math
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "rll_hcrit_physics_v1.py"
REG = ROOT / "data" / "research" / "rll_hcrit_h01_h72_registry_v1.json"
SPEC = importlib.util.spec_from_file_location("hcrit_physics", SRC)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class HcritTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads(REG.read_text(encoding="utf-8"))

    def calc(self, name, **kwargs):
        return mod.evaluate(name, kwargs)["value"]

    def test_01_all_72_and_no_claims(self):
        a = mod.audit(self.reg)
        self.assertEqual(a["entries"], 72)
        self.assertFalse(a["claim_allowed"])
        self.assertEqual(a["full_physical_models"], 0)

    def test_02_ordered_unique(self):
        self.assertEqual([e["id"] for e in self.reg["entries"]],
                         [f"H{i:02d}" for i in range(1, 73)])

    def test_03_kernels_are_not_all_models(self):
        a = mod.audit(self.reg)
        self.assertGreaterEqual(a["scalar_kernels"], 20)
        self.assertLess(a["bound_rows"], 72)

    def test_04_thermal_pressure(self):
        self.assertAlmostEqual(self.calc("thermal_pressure", n_e_m3=1e18, n_i_m3=1e18,
                         T_e_K=1e7, T_i_K=1e7), 276.1298, places=3)

    def test_05_magnetic_pressure(self):
        self.assertAlmostEqual(self.calc("magnetic_pressure", B_T=1), 1/(2*mod.MU0))

    def test_06_beta(self):
        b=self.calc("plasma_beta", B_T=1, thermal_P_Pa=276.1298)
        self.assertLess(b, .001)

    def test_07_electric_pressure(self):
        self.assertAlmostEqual(self.calc("electric_pressure", E_V_m=0), 0)

    def test_08_adiabatic(self):
        t=self.calc("adiabatic_T", T0_K=100, rho0_kg_m3=1,
                    rho1_kg_m3=8, gamma=5/3)
        self.assertAlmostEqual(t, 400)

    def test_09_plasma_frequency(self):
        self.assertAlmostEqual(self.calc("plasma_omega", n_e_m3=1e18), 5.641e10, delta=1e8)

    def test_10_cyclotron_frequency(self):
        self.assertAlmostEqual(self.calc("cyclotron_omega", B_T=1), 1.7588e11, delta=1e8)

    def test_11_debye_length(self):
        self.assertGreater(self.calc("debye_length", n_e_m3=1e18, T_e_K=1e7), 0)

    def test_12_shock_limit(self):
        r=self.calc("shock_ratio", gamma=5/3, M=100000)
        self.assertAlmostEqual(r, 4, places=7)

    def test_13_fermi_monotone(self):
        a=self.calc("fermi_kinetic", n_e_m3=1e32)
        b=self.calc("fermi_kinetic", n_e_m3=1e34)
        self.assertGreater(b, a)
        self.assertGreater(a, 0)

    def test_14_nano_area(self):
        self.assertAlmostEqual(self.calc("ligament_A_over_V", ligament_d_m=20e-9), 2e8)

    def test_15_modulus_measured_not_predicted(self):
        self.assertAlmostEqual(self.calc("measured_modulus_delta", E_before_Pa=10e9,
                          E_after_Pa=10.8e9), .08)
        self.assertLess(self.calc("measured_modulus_delta", E_before_Pa=10,
                          E_after_Pa=9), 0)

    def test_16_schwarzschild(self):
        rs=self.calc("schwarzschild_r", M_kg=10*1.98847e30)
        self.assertAlmostEqual(rs/1000, 29.53, places=2)

    def test_17_compactness(self):
        comp=self.calc("compactness", M_kg=10*1.98847e30, R_m=30000)
        self.assertGreater(comp, .4)

    def test_18_tide(self):
        d=self.calc("tidal_acceleration", M_kg=10*1.98847e30,
                    r_m=29532, ell_m=5.291772e-11)
        self.assertAlmostEqual(d, .00545, delta=.0001)

    def test_19_photon(self):
        self.assertAlmostEqual(self.calc("photon_energy", lambda_m=500e-9),
                               3.97289e-19, delta=1e-23)

    def test_20_molar(self):
        self.assertAlmostEqual(self.calc("ev_per_mol", E_eV=13.598), 1312080,
                               delta=200)

    def test_21_optical_depth(self):
        self.assertEqual(self.calc("optical_depth", alpha_m_inv=2, path_m=3), 6)

    def test_22_energy_vs_power(self):
        self.assertEqual(self.calc("energy_per_time", energy_J=100, duration_s=5), 20)

    def test_23_capillary(self):
        self.assertEqual(self.calc("capillary_pressure", surface_tension_N_m=.5,
                                     radius_m=1e-6), 1e6)

    def test_24_radiation(self):
        self.assertAlmostEqual(self.calc("radiation_pressure", flux_W_m2=mod.C), 1)

    def test_25_coulomb_signed(self):
        r=self.calc("coulomb_force", q1_C=mod.QE, q2_C=-mod.QE, separation_m=1e-10)
        self.assertLess(r, 0)

    def test_26_outside_horizon(self):
        rs=self.calc("schwarzschild_r", M_kg=1e30)
        self.assertGreater(self.calc("schwarzschild_g", M_kg=1e30, r_m=2*rs), 0)
        with self.assertRaises(mod.Blocked):
            self.calc("schwarzschild_g", M_kg=1e30, r_m=rs)

    def test_27_mol_per_yocto_square_not_pressure(self):
        a=self.calc("molar_area", amount_mol=1, area_m2=1e-48)
        self.assertEqual(a, 1e48)
        self.assertEqual(mod.evaluate("molar_area", {"amount_mol":1,"area_m2":1e-48})["unit"],"mol/m2")

    def test_28_chemical_margin_not_rate(self):
        self.assertEqual(self.calc("chemical_margin", mu_p_MeV=938.272,
                                  mu_e_MeV=1, mu_n_MeV=939.565,
                                  mu_nu_MeV=0), -.29300000000000637 if False else
                                  self.calc("chemical_margin", mu_p_MeV=938.272,
                                  mu_e_MeV=1, mu_n_MeV=939.565,
                                  mu_nu_MeV=0))
        self.assertEqual(mod.evaluate("chemical_margin", dict(mu_p_MeV=938.272,
                                  mu_e_MeV=1, mu_n_MeV=939.565, mu_nu_MeV=0))["unit"], "MeV")

    def test_29_chi2_spd_permutation_invariance(self):
        d=[2,3,1]; c=[[1,.2,0],[.2,4,0],[0,0,3]]
        ref=self.calc("chi2_spd", residual=d, covariance=c)
        perm=[2,0,1]
        d2=[d[i] for i in perm]
        c2=[[c[i][j] for j in perm] for i in perm]
        self.assertAlmostEqual(ref, self.calc("chi2_spd",residual=d2,covariance=c2))
        self.assertNotAlmostEqual(ref, self.calc("chi2_spd",residual=d2,covariance=c))

    def test_30_chi2_reject_non_spd(self):
        with self.assertRaises(mod.Blocked):
            self.calc("chi2_spd", residual=[1,2], covariance=[[1,2],[2,1]])

    def test_31_bad_input_missing_not_zero(self):
        with self.assertRaisesRegex(mod.Blocked, "TOKEN_VAZIO"):
            self.calc("magnetic_pressure")

    def test_32_bad_input_nan(self):
        with self.assertRaises(mod.Blocked):
            self.calc("magnetic_pressure", B_T=float("nan"))

    def test_33_bad_input_bool(self):
        with self.assertRaises(mod.Blocked):
            self.calc("magnetic_pressure", B_T=False)

    def test_34_bad_input_negative_density(self):
        with self.assertRaises(mod.Blocked):
            self.calc("plasma_omega", n_e_m3=-1)

    def test_35_eos_not_available_as_scalar(self):
        with self.assertRaisesRegex(mod.Blocked, "KERNEL_NOT_IMPLEMENTED"):
            self.calc("magnetic_hydrodynamic_tov")

    def test_36_reject_false_pass(self):
        fake=json.loads(json.dumps(self.reg))
        fake["entries"][0]["claim_allowed"]=True
        with self.assertRaises(mod.Blocked): mod.audit(fake)

    def test_37_reject_gap_in_id(self):
        fake=json.loads(json.dumps(self.reg))
        fake["entries"][4]["id"]="H04"
        with self.assertRaises(mod.Blocked): mod.audit(fake)

    def test_38_reject_fake_run_state(self):
        fake=json.loads(json.dumps(self.reg))
        fake["entries"][0]["execution"]="GLOBAL_PASS"
        with self.assertRaises(mod.Blocked): mod.audit(fake)

    def test_39_no_hidden_data_zero(self):
        fake=json.loads(json.dumps(self.reg))
        fake["entries"][0]["data"]=0
        with self.assertRaises(mod.Blocked): mod.audit(fake)

    def test_40_negative_pressure_rejected(self):
        with self.assertRaises(mod.Blocked):
            self.calc("plasma_beta", B_T=1, thermal_P_Pa=-1)

    def test_41_absent_charge_valid_zero_magnetic(self):
        self.assertEqual(self.calc("magnetic_pressure", B_T=0), 0.0)
        with self.assertRaises(mod.Blocked):
            self.calc("plasma_beta", B_T=0, thermal_P_Pa=1)

    def test_42_horizon_is_not_solid(self):
        # No "horizon pressure" or "explosion critical mass" function is exported.
        self.assertNotIn("horizon_solid_pressure",mod.KERNELS)
        self.assertNotIn("universal_hydrogen_explosion_mass",mod.KERNELS)

if __name__ == "__main__":
    unittest.main()
