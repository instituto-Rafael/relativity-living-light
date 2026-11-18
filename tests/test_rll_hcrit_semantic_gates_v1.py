"""Adversarial, synthetic, deterministic. Not a physical validation or provider CI."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'tools' / 'rll_hcrit_semantic_gates_v1.py'
SPEC = importlib.util.spec_from_file_location('hcrit_s3', P)
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)

A = 'a' * 64
B = 'b' * 64

def cov_packet():
    return {'vector': {'source_ref':'synthetic-vector', 'sha256':A,
                       'rows':[{'id':'DR2|BGS|0.29|DV', 'unit':'1', 'residual':2},
                               {'id':'DR2|LRG|0.51|DM', 'unit':'1', 'residual':3}]},
            'covariance':{'source_ref':'synthetic-cov', 'sha256':B,
                          'axis':[{'id':'DR2|BGS|0.29|DV','unit':'1'},
                                  {'id':'DR2|LRG|0.51|DM','unit':'1'}],
                          'matrix':[[4., 0.5], [0.5, 9.]]}}

def capture():
    return {'reaction':'p+e->n+nu_e', 'mu_convention':'FULL_INCLUDES_REST_ENERGY',
            'mu_p_MeV':938.272, 'mu_e_MeV':1.0,
            'mu_n_MeV':939.565, 'mu_nu_e_MeV':0.0}

def generic():
    return {'mu_convention':'SAME_ZERO_AND_REST_ENERGY',
            'terms':[{'species':'p','nu':-1,'charge_e':1,'baryon_number':1,'mu_MeV':938.272},
                     {'species':'e-','nu':-1,'charge_e':-1,'baryon_number':0,'mu_MeV':1},
                     {'species':'n','nu':1,'charge_e':0,'baryon_number':1,'mu_MeV':939.565},
                     {'species':'nu_e','nu':1,'charge_e':0,'baryon_number':0,'mu_MeV':0}]}

def opacity(carrier='neutrino'):
    obj={'carrier':carrier,'opacity_model_ref':'synthetic-opacity',
         'segments':[{'length_m':2,'attenuation_per_m':.25},
                     {'length_m':3,'attenuation_per_m':.5}]}
    if carrier=='neutrino':
        obj.update(neutrino_species='nu_e',energy_MeV=3,
                   composition_ref='synthetic-comp',eos_ref='synthetic-eos')
    else:obj.update(wavelength_m=500e-9)
    return obj

def material():
    return {'material':'AuAg_dealloyed_Au','sample_ref':'synthetic-nanogold',
            'ligament_d_m':20e-9,
            'before':{'modulus_Pa':10e9,'potential_V':0,
                      'surface_charge_C_m2':.01,'temperature_K':300,'adsorbate_fraction':.1},
            'after':{'modulus_Pa':10.8e9,'potential_V':.5,
                     'surface_charge_C_m2':.02,'temperature_K':301,'adsorbate_fraction':.12}}

class Tests(unittest.TestCase):
    def test_01_cov_chi2_known(self):
        out=g.run('H40',cov_packet())
        self.assertAlmostEqual(out['chi2'],2.0**2/4+(3-.5*2/4)**2/(9-.5**2/4),places=12)
        self.assertFalse(out['claim_allowed'])

    def test_02_cov_permutation_invariance(self):
        orig=cov_packet(); x=g.run('H40',orig)['chi2']
        orig['covariance']['axis'].reverse()
        orig['covariance']['matrix']=[list(reversed(row)) for row in reversed(orig['covariance']['matrix'])]
        y=g.run('H40',orig)
        self.assertAlmostEqual(x,y['chi2'],places=12)
        self.assertTrue(y['reordered'])

    def test_03_cov_reordered_one_axis_not_equivalent(self):
        p=cov_packet(); p['covariance']['axis'].reverse()
        # This shape is SPD but pairs wrong without both axes properly moved.
        self.assertNotAlmostEqual(g.run('H40',cov_packet())['chi2'],g.run('H40',p)['chi2'])

    def test_04_cov_wrong_unit(self):
        p=cov_packet();p['covariance']['axis'][0]['unit']='Mpc'
        with self.assertRaisesRegex(g.Blocked,'IDENTITY_MISMATCH'):g.run('H40',p)

    def test_05_cov_wrong_id(self):
        p=cov_packet();p['covariance']['axis'][0]['id']='DR2|BGS|0.29|DH'
        with self.assertRaises(g.Blocked):g.run('H40',p)

    def test_06_cov_duplicate(self):
        p=cov_packet();p['covariance']['axis'][1]=dict(p['covariance']['axis'][0])
        with self.assertRaises(g.Blocked):g.run('H40',p)

    def test_07_cov_missing_provenance(self):
        p=cov_packet();del p['covariance']['sha256']
        with self.assertRaisesRegex(g.Blocked,'TOKEN_VAZIO'):g.run('H40',p)

    def test_08_cov_fabricated_hash_shape(self):
        p=cov_packet();p['covariance']['sha256']='xyz'
        with self.assertRaisesRegex(g.Blocked,'INVALID_SHA256'):g.run('H40',p)

    def test_09_cov_nonspd(self):
        p=cov_packet();p['covariance']['matrix']=[[1,2],[2,1]]
        with self.assertRaisesRegex(g.Blocked,'NOT_SPD'):g.run('H40',p)

    def test_10_cov_not_symmetric(self):
        p=cov_packet();p['covariance']['matrix'][1][0]=.6
        with self.assertRaisesRegex(g.Blocked,'NOT_SYMMETRIC'):g.run('H40',p)

    def test_11_cov_nan_reject(self):
        p=cov_packet();p['vector']['rows'][0]['residual']=float('nan')
        with self.assertRaisesRegex(g.Blocked,'INVALID_FINITE_NUMBER'):g.run('H40',p)

    def test_12_cov_bool_reject(self):
        p=cov_packet();p['vector']['rows'][0]['residual']=False
        with self.assertRaises(g.Blocked):g.run('H40',p)

    def test_13_cov_unlabelled_index_reject(self):
        p=cov_packet();p['vector']['rows'][0]['id']='0'
        with self.assertRaises(g.Blocked):g.run('H40',p)

    def test_14_capture_independent_expected(self):
        self.assertAlmostEqual(g.run('H18',capture())['affinity_MeV'],-.293,places=10)

    def test_15_capture_convention_reject(self):
        p=capture();p['mu_convention']='KINETIC_ONLY'
        with self.assertRaisesRegex(g.Blocked,'CONVENTION'):g.run('H18',p)

    def test_16_capture_wrong_reaction_reject(self):
        p=capture();p['reaction']='fission'
        with self.assertRaises(g.Blocked):g.run('H18',p)

    def test_17_capture_rate_unknown(self):
        self.assertEqual(g.run('H18',capture())['rate'],'TOKEN_VAZIO')

    def test_18_general_affinity_conserved(self):
        o=g.run('H63',generic())
        self.assertAlmostEqual(o['affinity_MeV'],-.293,places=10)
        self.assertFalse(o['claim_allowed'])

    def test_19_general_affinity_charge_reject(self):
        p=generic();p['terms'][1]['charge_e']=0
        with self.assertRaisesRegex(g.Blocked,'NONCONSERVATION'):g.run('H63',p)

    def test_20_general_affinity_duplicate_species(self):
        p=generic();p['terms'][3]['species']='n'
        with self.assertRaises(g.Blocked):g.run('H63',p)

    def test_21_general_affinity_fractional_nu(self):
        p=generic();p['terms'][0]['nu']=-.5
        with self.assertRaises(g.Blocked):g.run('H63',p)

    def test_22_general_affinity_convention(self):
        p=generic();p['mu_convention']='UNKNOWN'
        with self.assertRaises(g.Blocked):g.run('H63',p)

    def test_23_neutrino_opacity_scoped(self):
        x=g.run('H70',opacity())
        self.assertEqual(x['tau'],2.)
        self.assertFalse(x['transport_solved'])

    def test_24_neutrino_species_reject(self):
        p=opacity();p['neutrino_species']='photon'
        with self.assertRaises(g.Blocked):g.run('H70',p)

    def test_25_neutrino_eos_missing(self):
        p=opacity();del p['eos_ref']
        with self.assertRaisesRegex(g.Blocked,'TOKEN_VAZIO'):g.run('H70',p)

    def test_26_neutrino_energy_missing(self):
        p=opacity();del p['energy_MeV']
        with self.assertRaises(g.Blocked):g.run('H70',p)

    def test_27_photon_scoped(self):
        x=g.run('H34',opacity('photon'))
        self.assertEqual(x['tau'],2.)
        self.assertEqual(x['carrier'],'photon')

    def test_28_photon_wavelength_invalid(self):
        p=opacity('photon');p['wavelength_m']=0
        with self.assertRaises(g.Blocked):g.run('H34',p)

    def test_29_optical_negative_attenuation(self):
        p=opacity();p['segments'][0]['attenuation_per_m']=-.1
        with self.assertRaises(g.Blocked):g.run('H70',p)

    def test_30_gold_delta_measured(self):
        x=g.run('H46',material())
        self.assertAlmostEqual(x['relative_modulus_change'], .08)
        self.assertAlmostEqual(x['ideal_cylindrical_area_over_volume_m_inv'], 2e8)
        self.assertFalse(x['charge_vs_adsorbate_causality_established'])

    def test_31_gold_missing_adsorbate_blocks(self):
        p=material();del p['before']['adsorbate_fraction']
        with self.assertRaisesRegex(g.Blocked,'TOKEN_VAZIO'):g.run('H46',p)

    def test_32_gold_missing_charge_blocks(self):
        p=material();del p['after']['surface_charge_C_m2']
        with self.assertRaises(g.Blocked):g.run('H46',p)

    def test_33_gold_false_material(self):
        p=material();p['material']='bulk_Ag'
        with self.assertRaises(g.Blocked):g.run('H46',p)

    def test_34_gold_invalid_coverage(self):
        p=material();p['after']['adsorbate_fraction']=1.1
        with self.assertRaises(g.Blocked):g.run('H46',p)

    def test_35_gold_negative_temperature(self):
        p=material();p['after']['temperature_K']=-5
        with self.assertRaises(g.Blocked):g.run('H46',p)

    def test_36_gold_geometry_not_3d_verified(self):
        self.assertFalse(g.run('H45',material())['geometry_measured_3d'])

    def test_37_magnetic_tensor_z(self):
        x=g.run('H48', {'B_T':[0,0,1]})
        pressure=1/(2*g.MU0)
        self.assertAlmostEqual(x['tensor_Pa'][2][2], pressure)
        self.assertAlmostEqual(x['tensor_Pa'][0][0],-pressure)
        self.assertEqual(x['tensor_Pa'][0][2],0)

    def test_38_magnetic_tensor_rotation(self):
        x=g.run('H48',{'B_T':[1,0,0]})
        y=g.run('H48',{'B_T':[0,0,1]})
        self.assertAlmostEqual(x['scalar_magnetic_pressure_Pa'],y['scalar_magnetic_pressure_Pa'])
        self.assertNotEqual(x['tensor_Pa'],y['tensor_Pa'])

    def test_39_magnetic_nan_reject(self):
        with self.assertRaises(g.Blocked):g.run('H48',{'B_T':[0,0,float('inf')]})

    def test_40_magnetic_dimension_reject(self):
        with self.assertRaises(g.Blocked):g.run('H48',{'B_T':[0,1]})

    def test_41_magnetic_force_not_predicted(self):
        self.assertEqual(g.run('H48',{'B_T':[0,0,1]})['force_density'],'TOKEN_VAZIO')

    def test_42_wrong_gate_reject(self):
        with self.assertRaisesRegex(g.Blocked,'GATE_NOT_IMPLEMENTED'):g.run('H24',{})

    def test_43_missing_null_vs_zero(self):
        with self.assertRaisesRegex(g.Blocked,'TOKEN_VAZIO'):g.run('H48',{})
        self.assertEqual(g.run('H48',{'B_T':[0,0,0]})['scalar_magnetic_pressure_Pa'],0)

    def test_44_scalar_string_reject(self):
        with self.assertRaises(g.Blocked):g.scalar('1','val')

    def test_45_synthetic_no_claim(self):
        self.assertTrue(all(g.run(k, p)['claim_allowed'] is False for k,p in
            [('H18',capture()),('H63',generic()),('H34',opacity('photon')),
             ('H70',opacity()),('H46',material()),('H48',{'B_T':[1,2,3]}),
             ('H40',cov_packet())]))


    def test_46_registry_72_synthetic(self):
        r={'schema':'RLL_HCRIT_H01_H72_SCOPED_V1',
           'entries':[{'id':f'H{i:02d}','claim_allowed':False,
                       'data':'TOKEN_VAZIO','kernel':None,
                       'execution':'MODEL_REQUIRED'} for i in range(1,73)]}
        self.assertEqual(g.audit_h01_h72_registry(r)['ids'],72)
        self.assertFalse(g.audit_h01_h72_registry(r)['claim_allowed'])

    def test_47_registry_reject_gap(self):
        r={'schema':'RLL_HCRIT_H01_H72_SCOPED_V1',
           'entries':[{'id':f'H{i:02d}','claim_allowed':False,
                       'data':'TOKEN_VAZIO','kernel':None,
                       'execution':'MODEL_REQUIRED'} for i in range(1,73)]}
        r['entries'][41]['id']='H41'
        with self.assertRaisesRegex(g.Blocked,'REGISTRY_DUPLICATE_OR_ID_GAP'):
            g.audit_h01_h72_registry(r)

    def test_48_registry_reject_faked_observation(self):
        r={'schema':'RLL_HCRIT_H01_H72_SCOPED_V1',
           'entries':[{'id':f'H{i:02d}','claim_allowed':False,
                       'data':'TOKEN_VAZIO','kernel':None,
                       'execution':'MODEL_REQUIRED'} for i in range(1,73)]}
        r['entries'][3]['data']=0
        with self.assertRaisesRegex(g.Blocked,'FALSE_CLAIM_OR_DATA'):
            g.audit_h01_h72_registry(r)

    def test_49_registry_reject_fake_pass(self):
        r={'schema':'RLL_HCRIT_H01_H72_SCOPED_V1',
           'entries':[{'id':f'H{i:02d}','claim_allowed':False,
                       'data':'TOKEN_VAZIO','kernel':None,
                       'execution':'MODEL_REQUIRED'} for i in range(1,73)]}
        r['entries'][3]['execution']='PASS'
        with self.assertRaisesRegex(g.Blocked,'FALSE_EXECUTION'):
            g.audit_h01_h72_registry(r)

    def test_50_registry_reject_claim_promote(self):
        r={'schema':'RLL_HCRIT_H01_H72_SCOPED_V1',
           'entries':[{'id':f'H{i:02d}','claim_allowed':False,
                       'data':'TOKEN_VAZIO','kernel':None,
                       'execution':'MODEL_REQUIRED'} for i in range(1,73)]}
        r['entries'][10]['claim_allowed']=True
        with self.assertRaises(g.Blocked):g.audit_h01_h72_registry(r)


    def test_51_selector_permutation_invariant(self):
        controls=[{'id':'Z','covers':['A','B'],'relative_cost':2},
                  {'id':'A','covers':['A','B'],'relative_cost':1},
                  {'id':'B','covers':['C'],'relative_cost':1}]
        a=g.select_falsifiers(controls,['A','B','C'])
        b=g.select_falsifiers(list(reversed(controls)),['C','B','A'])
        self.assertEqual(a,b)
        self.assertEqual([s['id'] for s in a['selected']], ['A','B'])
        self.assertFalse(a['claim_allowed'])

    def test_52_selector_unknown_coverage(self):
        out=g.select_falsifiers([{'id':'A','covers':['X'],'relative_cost':1}],['X','Y'])
        self.assertEqual(out['uncovered'],['Y'])

    def test_53_selector_duplicate_rejected(self):
        with self.assertRaises(g.Blocked):
            g.select_falsifiers([{'id':'X','covers':['A'],'relative_cost':1},
                                 {'id':'X','covers':['A'],'relative_cost':1}],['A'])

    def test_54_selector_no_zero_cost(self):
        with self.assertRaises(g.Blocked):
            g.select_falsifiers([{'id':'X','covers':['A'],'relative_cost':0}],['A'])

if __name__ == '__main__':unittest.main()
