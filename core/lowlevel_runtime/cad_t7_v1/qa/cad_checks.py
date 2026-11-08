"""Independent double reference oracle for 2D pin-jointed 3-bar analytic truss.

Do not interpret these as physical validation or safety certification.
"""
import ctypes, json, math, subprocess, unittest, pathlib, zlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
Q=65536
class Input(ctypes.Structure):
 _fields_=[(x,ctypes.c_int32) for x in ('span_mm_q16','rise_mm_q16','area_diagonal_mm2_q16','area_tie_mm2_q16','downward_load_kN_q16','young_GPa_q16','yield_MPa_q16','deltaT_K_q16','alpha_micro_per_K')]
class Result(ctypes.Structure):
 _fields_=[(x,ctypes.c_int32) for x in ('diagonal_length_mm_q16','tan_angle_q16','diagonal_force_kN_q16','tie_force_kN_q16','diagonal_stress_MPa_q16','tie_stress_MPa_q16','apex_deflection_mm_q16','thermal_free_span_mm_q16','buckling_limit_kN_q16','buckling_ratio_q16','diagonal_diameter_mm_q16','tie_diameter_mm_q16')]+[('flags',ctypes.c_uint32)]
class T7(ctypes.Structure):
 _fields_=[('coord_q16',ctypes.c_int32*7),('sample_index',ctypes.c_uint32)]
lib=ctypes.CDLL(str(ROOT/'build/librllcad_host.so'))
lib.rll_cad_baseline.argtypes=[ctypes.POINTER(Input)]
lib.rll_cad_evaluate.argtypes=[ctypes.POINTER(Input),ctypes.POINTER(Result)]
lib.rll_cad_t7_sample.argtypes=[ctypes.POINTER(Input),ctypes.c_uint32,ctypes.POINTER(T7),ctypes.POINTER(Input)]
lib.rll_crc32_sw.argtypes=[ctypes.c_char_p,ctypes.c_uint32];lib.rll_crc32_sw.restype=ctypes.c_uint32
lib.rll_add4_scalar.argtypes=[ctypes.POINTER(ctypes.c_int32)]*3
lib.rll_add4_neon.argtypes=[ctypes.POINTER(ctypes.c_int32)]*3

def f(x):return x/Q

def oracle(a):
 L,H,Ad,At,P,E,Y,T=f(a.span_mm_q16),f(a.rise_mm_q16),f(a.area_diagonal_mm2_q16),f(a.area_tie_mm2_q16),f(a.downward_load_kN_q16),f(a.young_GPa_q16),f(a.yield_MPa_q16),f(a.deltaT_K_q16)
 D=math.hypot(L/2,H);N=P*D/(2*H);tie=P*L/(4*H)
 return {'D':D,'N':N,'tie':tie,'stress':1000*N/Ad,'delta':(2*N*N*D/(E*Ad)+tie*tie*L/(E*At))/P,
         'free':L*a.alpha_micro_per_K*T/1e6,'euler':math.pi/4*E*(Ad/D)**2,'diameter':math.sqrt(4*Ad/math.pi)}
class TestFreestanding(unittest.TestCase):
 def baseline(self):
  a=Input();r=Result();self.assertEqual(lib.rll_cad_baseline(ctypes.byref(a)),0);self.assertEqual(lib.rll_cad_evaluate(ctypes.byref(a),ctypes.byref(r)),0);return a,r
 def test_baseline_against_analytic_reference(self):
  a,r=self.baseline();v=oracle(a)
  for field,key,delta in [('diagonal_length_mm_q16','D',0.0001),('diagonal_force_kN_q16','N',0.0001),('tie_force_kN_q16','tie',0.0001),('diagonal_stress_MPa_q16','stress',0.001),('apex_deflection_mm_q16','delta',0.0002),('thermal_free_span_mm_q16','free',0.0001),('buckling_limit_kN_q16','euler',0.02),('diagonal_diameter_mm_q16','diameter',0.001)]:
   self.assertAlmostEqual(f(getattr(r,field)),v[key],delta=delta,msg=field)
 def test_strength_flags_are_not_certification(self):
  a,r=self.baseline();self.assertEqual(r.flags&32,32)
 def test_material_and_force_monotonicity(self):
  a,r=self.baseline();v0=r.apex_deflection_mm_q16
  a.downward_load_kN_q16*=2;s=Result();self.assertEqual(lib.rll_cad_evaluate(ctypes.byref(a),ctypes.byref(s)),0)
  self.assertGreater(s.apex_deflection_mm_q16,v0)
  a.young_GPa_q16//=2;t=Result();self.assertEqual(lib.rll_cad_evaluate(ctypes.byref(a),ctypes.byref(t)),0)
  self.assertGreater(t.apex_deflection_mm_q16,s.apex_deflection_mm_q16)
 def test_independent_double_reference_all_42_compositions(self):
  rows=json.loads((ROOT/'results/models42.json').read_text())['samples']
  for row in rows:
   inp=Input(*(row['in_q16']+[row['alpha_micro']]))
   got=Result();self.assertEqual(lib.rll_cad_evaluate(ctypes.byref(inp),ctypes.byref(got)),0)
   target=oracle(inp)
   for name,key,epsilon in [
    ('diagonal_length_mm_q16','D',0.0001),('diagonal_force_kN_q16','N',0.0001),
    ('tie_force_kN_q16','tie',0.0001),('diagonal_stress_MPa_q16','stress',0.002),
    ('apex_deflection_mm_q16','delta',0.0003),('thermal_free_span_mm_q16','free',0.0001),
    ('buckling_limit_kN_q16','euler',0.03),('diagonal_diameter_mm_q16','diameter',0.001)]:
    self.assertAlmostEqual(f(getattr(got,name)),target[key],delta=epsilon,msg=f"sample={row['sample']} metric={name}")
 def test_zero_area_and_excessive_span_rejected(self):
  inp,got=self.baseline()
  inp.area_diagonal_mm2_q16=0;self.assertNotEqual(lib.rll_cad_evaluate(ctypes.byref(inp),ctypes.byref(got)),0)
  inp.area_diagonal_mm2_q16=500*Q;inp.span_mm_q16=5000*Q
  self.assertNotEqual(lib.rll_cad_evaluate(ctypes.byref(inp),ctypes.byref(got)),0)
 def test_42_t7_samples(self):
  a,_=self.baseline();st=T7();s=Input();r=Result();seen=set()
  for i in range(42):
   self.assertEqual(lib.rll_cad_t7_sample(ctypes.byref(a),i,ctypes.byref(st),ctypes.byref(s)),0)
   self.assertEqual(lib.rll_cad_evaluate(ctypes.byref(s),ctypes.byref(r)),0)
   seen.add(tuple(st.coord_q16))
  self.assertEqual(len(seen),42)
 def test_bounded_fail_closed(self):
  a,_=self.baseline();a.rise_mm_q16=0;r=Result();self.assertNotEqual(lib.rll_cad_evaluate(ctypes.byref(a),ctypes.byref(r)),0)
 def test_crc32_ieee_vector(self):
  self.assertEqual(lib.rll_crc32_sw(b'123456789',9),0xcbf43926)
 def test_scalar_neon_equivalence(self):
  v=(ctypes.c_int32*4)(10,20,30,40);w=(ctypes.c_int32*4)(100,200,300,400);a=(ctypes.c_int32*4)();b=(ctypes.c_int32*4)()
  lib.rll_add4_scalar(v,w,a);lib.rll_add4_neon(v,w,b)
  self.assertEqual(list(a),list(b))
 def test_svg_valid_and_unit_attributes(self):
  import xml.etree.ElementTree as ET
  data=(ROOT/'svg/bridge.svg').read_text();svg=ET.fromstring(data)
  self.assertEqual(svg.attrib['data-unit'],'mm');self.assertTrue(svg.attrib['width'].endswith('mm'))
  lines=[x for x in svg.iter() if x.tag.endswith('line')];self.assertEqual(len(lines),3)
  self.assertTrue(all(float(x.attrib['stroke-width'])>0 for x in lines))
  self.assertTrue(all('data-area-mm2' in x.attrib for x in lines))
 def test_42_sample_json_exclusions(self):
  j=json.loads((ROOT/'results/models42.json').read_text())
  self.assertEqual(len(j['samples']),42)
  self.assertFalse(j['claim_allowed']);self.assertFalse(j['certified']);self.assertIn('torsion',j['missing'])
if __name__=='__main__':unittest.main()
