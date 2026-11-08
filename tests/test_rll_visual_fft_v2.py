import tempfile
import unittest
from pathlib import Path
from tools.ci.rll_visual_fft_v2 import N,fft1,pgm_bytes,read_pgm,western_five,blank,spectral_entropy,visual_benchmark
class VisualFFT(unittest.TestCase):
 def test_fft_impulse(self):
  v=fft1([1,0,0,0,0,0,0,0]);self.assertTrue(all(abs(c-1)<1e-9 for c in v))
 def test_fft_zero_dc(self):
  e,n=spectral_entropy(blank());self.assertEqual(e,0);self.assertEqual(n,0)
 def test_pgm_size(self):self.assertEqual(len(pgm_bytes(blank())),len(b'P5\n128 128\n255\n')+128*128)
 def test_no_real_libras_fabricated(self):
  with tempfile.TemporaryDirectory() as d:
   r=visual_benchmark(Path(d));self.assertEqual(r['real_libras'],'TOKEN_VAZIO_REAL_LIBRAS_FRAME')
   self.assertTrue(all(z['width']==128 and z['height']==128 for z in r['images']))
   self.assertEqual(len(r['images']),6)
 def test_frame_requires_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   frame=Path(d)/'f.pgm';frame.write_bytes(pgm_bytes(western_five()))
   with self.assertRaises(ValueError):visual_benchmark(Path(d)/'out',frame,None)
 def test_fft_nonconstant(self):
  e,n=spectral_entropy(western_five());self.assertGreater(e,1);self.assertTrue(0<n<=1)
if __name__=='__main__':unittest.main()
