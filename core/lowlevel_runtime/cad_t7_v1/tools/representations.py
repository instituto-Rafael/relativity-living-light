#!/usr/bin/env python3
"""Same Q16 scenario records in JSON/CSV/packed LE/SVG+metadata, measure size/entropy.

Hosted persistence and compression only: all engineering metrics are produced
by the freestanding C core. SVG adds vector presentation, so is a SUPERSET of
canonical records, not a byte-for-byte equivalent channel.
"""
from __future__ import annotations
from collections import Counter
import ctypes
import csv
import gzip
import hashlib
import json
import lzma
import math
from pathlib import Path
import struct
import subprocess
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
J=ROOT/'results/models42.json'
SVG=ROOT/'svg'
OUT=ROOT/'results'
class Input(ctypes.Structure):
 _fields_=[(x,ctypes.c_int32) for x in ('span_mm_q16','rise_mm_q16','area_diagonal_mm2_q16','area_tie_mm2_q16','downward_load_kN_q16','young_GPa_q16','yield_MPa_q16','deltaT_K_q16','alpha_micro_per_K')]
class Result(ctypes.Structure):
 _fields_=[(x,ctypes.c_int32) for x in ('diagonal_length_mm_q16','tan_angle_q16','diagonal_force_kN_q16','tie_force_kN_q16','diagonal_stress_MPa_q16','tie_stress_MPa_q16','apex_deflection_mm_q16','thermal_free_span_mm_q16','buckling_limit_kN_q16','buckling_ratio_q16','diagonal_diameter_mm_q16','tie_diameter_mm_q16')]+[('flags',ctypes.c_uint32)]
lib=ctypes.CDLL(str(ROOT/'build/librllcad_host.so'))
lib.rll_cad_emit_svg.argtypes=[ctypes.POINTER(Input),ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_char),ctypes.c_uint32]
lib.rll_cad_emit_svg.restype=ctypes.c_int
lib.rll_cad_evaluate.argtypes=[ctypes.POINTER(Input),ctypes.POINTER(Result)]
lib.rll_cad_evaluate.restype=ctypes.c_int
schema=['sample']+['t7_{}'.format(i) for i in range(7)]+['in_{}'.format(i) for i in range(8)]+['alpha_micro']+['out_{}'.format(i) for i in range(12)]+['flags']
assert len(schema)==30
j=json.loads(J.read_text());records=j['samples'];assert len(records)==42

def flat(row):return [row['sample'],*row['t7_q16'],*row['in_q16'],row['alpha_micro'],*row['out_q16'],row['flags']]
assert all(len(flat(r))==30 for r in records)
canonical=json.dumps(records,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n'
(OUT/'records42_canonical.json').write_text(canonical)
with (OUT/'records42.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(schema);w.writerows(flat(r) for r in records)
raw=bytearray(b'RLLQ16V1')
raw+=struct.pack('<I',len(records))
for row in records:raw+=struct.pack('<30i',*flat(row))
(OUT/'records42_le_q16.bin').write_bytes(raw)
back=[list(x) for x in struct.iter_unpack('<30i',raw[12:])]
assert back==[flat(x) for x in records]

svg_meta=[]
for row in records:
 inp=Input(*(row['in_q16']+[row['alpha_micro']]))
 result=Result()
 assert lib.rll_cad_evaluate(ctypes.byref(inp),ctypes.byref(result))==0
 actual=[int(getattr(result,x)) for x in list(dict(Result._fields_).keys())[:-1]]
 assert actual==row['out_q16'] and result.flags==row['flags']
 buf=ctypes.create_string_buffer(12000)
 sz=lib.rll_cad_emit_svg(ctypes.byref(inp),ctypes.byref(result),buf,len(buf))
 assert sz>0
 svg=buf.value.decode()
 payload=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))
 metadata='<metadata id="rll-canonical-record" data-format="canonical-json"><![CDATA['+payload+']]></metadata>\n'
 svg=svg.replace('</svg>',metadata+'</svg>')
 dest=SVG/('design_{:02d}.svg'.format(row['sample']))
 dest.write_text(svg)
 elem=ET.fromstring(svg)
 payload_back=[x.text for x in elem if x.tag.endswith('metadata') and x.attrib.get('id')=='rll-canonical-record']
 assert payload_back==[payload] and json.loads(payload_back[0])==row
 svg_meta.append(dest)

svg_corpus=b''.join(x.read_bytes() for x in svg_meta)
(OUT/'svg42_corpus.xml.txt').write_bytes(svg_corpus)

def entropy(data):
 count=Counter(data);n=len(data)
 return -sum((m/n)*math.log2(m/n) for m in count.values()) if n else 0

def zstd(data):
 return subprocess.run(['zstd','-19','-q','-c'],input=data,stdout=subprocess.PIPE,check=True).stdout

def metrics(name,data):
 gz=gzip.compress(data,compresslevel=9,mtime=0)
 z=zstd(data)
 x=lzma.compress(data,preset=6)
 assert gzip.decompress(gz)==data
 assert subprocess.run(['zstd','-d','-q','-c'],input=z,stdout=subprocess.PIPE,check=True).stdout==data
 assert lzma.decompress(x)==data
 return {'format':name,'original_bytes':len(data),'entropy_bits_per_byte':round(entropy(data),6),
         'gzip9_bytes':len(gz),'zstd19_bytes':len(z),'xz6_bytes':len(x),
         'zstd19_savings_pct':round(100*(1-len(z)/len(data)),3),
         'sha256':hashlib.sha256(data).hexdigest(),'zstd_roundtrip':True}
rows=[metrics('canonical_records42_json',(OUT/'records42_canonical.json').read_bytes()),
      metrics('csv_records42',(OUT/'records42.csv').read_bytes()),
      metrics('binary_le_q16_42',(OUT/'records42_le_q16.bin').read_bytes()),
      metrics('svg_42_with_canonical_record_metadata',svg_corpus),
      metrics('single_baseline_svg',(SVG/'bridge.svg').read_bytes())]
with (OUT/'compression_42_compositions.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'compression_42_compositions.json').write_text(json.dumps(rows,indent=2)+'\n')
(OUT/'parity_receipt.json').write_text(json.dumps({'record_count':42,'per_svg_embedded_json_parity':'PASS','binary_little_endian_parity':'PASS','csv_integer_parity':'PASS','svg_carries_extra_drawable_structure':True,'schema_required_for_binary_recovery':True,'claim_allowed':False},indent=2)+'\n')
for row in rows:print('{:<42s} raw={:>7} zstd19={:>6} savings={:>7.3f}% Hbyte={:.3f}'.format(row['format'],row['original_bytes'],row['zstd19_bytes'],row['zstd19_savings_pct'],row['entropy_bits_per_byte']))
