import importlib.util, json, math, pathlib, tempfile, unittest, wave, struct

ROOT=pathlib.Path(__file__).resolve().parents[1]

def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

ING=load('ing','scripts/bible10_ingest.py')
ANA=load('ana','scripts/bible10_analyze.py')
ACO=load('aco','scripts/bible10_acoustics.py')

class Bible10Tests(unittest.TestCase):
    def test_registry_ten_public_domain(self):
        r=json.loads((ROOT/'configs/bible10-public-domain.v1.json').read_text(encoding='utf-8'))
        self.assertEqual(len(r['languages']),10)
        self.assertTrue(all(x['license']=='Public Domain' for x in r['languages']))

    def test_usfm_parse(self):
        t='\\id JHN\n\\c 1\n\\v 1 In the beginning was the Word.\n\\v 2 He was in the beginning.\n'
        v=ING.parse_usfm(t,'JHN')
        self.assertEqual(len(v),2)
        self.assertIn('Word',v[0]['text'])

    def test_entropy_not_hardcoded(self):
        rows=[
          {'text':'aaaa bbbb','verse':'2','chapter':2},
          {'text':'abab abab','verse':'3','chapter':3}
        ]
        m=ANA.book_metrics(rows)
        self.assertIn('conditional_char_entropy_order1',m)
        self.assertEqual(m['number_structure']['interpretation'],'INDEX_STRUCTURE_ONLY_NOT_CAUSATION')

    def test_poincare_distance_finite(self):
        self.assertGreater(ANA.poincare_distance((0.1,0.0),(0.2,0.0)),0)

    def test_uncalibrated_audio_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'x.wav'; rate=8000
            with wave.open(str(p),'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
                vals=[int(10000*math.sin(2*math.pi*1000*i/rate)) for i in range(rate//10)]
                w.writeframes(b''.join(struct.pack('<h',x) for x in vals))
            r=ACO.analyze(p)
            self.assertEqual(r['physical']['state'],'TOKEN_VAZIO_NO_PRESSURE_CALIBRATION')
            self.assertAlmostEqual(r['wav']['zero_crossing_frequency_estimate_hz'],1000,delta=30)

    def test_calibrated_audio_equations(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'x.wav'; rate=8000
            with wave.open(str(p),'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
                w.writeframes(b''.join(struct.pack('<h',1000) for _ in range(100)))
            r=ACO.analyze(p,2.0)
            self.assertEqual(r['physical']['state'],'CALIBRATED_UNDER_DECLARED_PLANE_WAVE_ASSUMPTION')
            self.assertGreater(r['physical']['intensity_w_m2'],0)
            self.assertGreater(r['physical']['mass_equivalent_density_kg_m3'],0)

if __name__=='__main__':
    unittest.main()
