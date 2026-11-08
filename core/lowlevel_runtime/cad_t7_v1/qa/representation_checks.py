import csv,json,struct,unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class TestRepresentationParity(unittest.TestCase):
 def test_all42_svg_embedded_exact_records(self):
  records=json.loads((ROOT/'results/records42_canonical.json').read_text())
  for r in records:
   p=ROOT/'svg'/f"design_{r['sample']:02}.svg"
   svg=ET.parse(p).getroot()
   meta=[x for x in svg if x.tag.endswith('metadata')]
   self.assertEqual(len(meta),1)
   self.assertEqual(json.loads(meta[0].text),r)
 def test_binary_exact_ints(self):
  data=(ROOT/'results/records42_le_q16.bin').read_bytes();self.assertEqual(data[:8],b'RLLQ16V1')
  n=struct.unpack('<I',data[8:12])[0];self.assertEqual(n,42);self.assertEqual(len(data),12+42*30*4)
  j=json.loads((ROOT/'results/records42_canonical.json').read_text())
  for k,ints in enumerate(struct.iter_unpack('<30i',data[12:])):
   r=j[k];self.assertEqual(list(ints),[r['sample'],*r['t7_q16'],*r['in_q16'],r['alpha_micro'],*r['out_q16'],r['flags']])
 def test_csv_exact_ints(self):
  with (ROOT/'results/records42.csv').open() as f: rows=list(csv.reader(f))
  self.assertEqual(len(rows),43);self.assertEqual(len(rows[0]),30)
  data=json.loads((ROOT/'results/records42_canonical.json').read_text())
  for row,v in zip(rows[1:],data):self.assertEqual(list(map(int,row)),[v['sample'],*v['t7_q16'],*v['in_q16'],v['alpha_micro'],*v['out_q16'],v['flags']])
 def test_no_false_physical_compliance_claim(self):
  a=json.loads((ROOT/'spec/architecture.json').read_text());self.assertFalse(a['claim_allowed']);self.assertFalse(a['certified_for_construction'])
  a=json.loads((ROOT/'results/parity_receipt.json').read_text());self.assertTrue(a['svg_carries_extra_drawable_structure'])
if __name__=='__main__':unittest.main()
