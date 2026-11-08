import copy
import json
import unittest
from pathlib import Path
from tools.ci.rll_script_entropy_v2 import DATA,validate,run,metrics,pack6,unpack6
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.doc=json.loads(DATA.read_text(encoding='utf-8'))
 def test_ten_languages(self):self.assertGreaterEqual(len(self.doc['text_variants']),8)
 def test_all_unicode_nfc(self):self.assertTrue(validate(self.doc))
 def test_braille_same_word(self):self.assertEqual(self.doc['braille']['source_text'],'cinco')
 def test_braille_lossless_packed(self):
  s=self.doc['braille']['cells_unicode'];self.assertEqual(len(pack6(s)),4);self.assertEqual(unpack6(pack6(s),5),s)
 def test_no_semantic_claim(self):self.assertFalse(run(self.doc)['claim_allowed'])
 def test_language_entropy_is_not_fft(self):self.assertIn('SEPARATE_IMAGE',run(self.doc)['visual_fft_status'])
 def test_zlib_roundtrip(self):self.assertGreater(metrics('cinco')['zlib9_bytes'],0)
 def test_short_compress_expands(self):self.assertGreater(metrics('5')['zlib9_bytes'],metrics('5')['utf8_bytes'])
 def test_mayan_is_numeral_not_language(self):self.assertTrue(self.doc['other_writing_systems'][1]['not_full_mayan_language'])
 def test_egyptian_is_numeral_not_sentence(self):self.assertTrue(self.doc['other_writing_systems'][2]['not_full_egyptian_sentence'])
 def test_claim_promotion_rejected(self):
  d=copy.deepcopy(self.doc);d['claim_allowed']=True
  with self.assertRaises(ValueError):run(d)
 def test_braille_mutation_rejected(self):
  d=copy.deepcopy(self.doc);d['braille']['cells_unicode']='⠁⠊⠝⠉⠕'
  with self.assertRaises(ValueError):run(d)
 def test_Libras_false_validation_rejected(self):
  d=copy.deepcopy(self.doc);d['libras']['real_frame_status']='VALIDATED'
  with self.assertRaises(ValueError):run(d)
if __name__=='__main__':unittest.main()
