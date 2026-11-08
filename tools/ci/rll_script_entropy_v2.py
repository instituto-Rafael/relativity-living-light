#!/usr/bin/env python3
"""Byte/code-point entropy and independent lossless compression; stdlib only.

An encoded word, Braille cell and Egyptian/Mayan numeral can denote five but
have different alphabets and coding conventions. No entropy equivalence claimed.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics
import unicodedata
import zlib
import gzip
import lzma

HERE = Path(__file__).resolve().parents[2]
DATA = HERE / 'data/experiments/rll_cross_script_entropy_v2/parallel_quantity_five_v2.json'

def h(items):
    if not items: return None
    count = Counter(items)
    n = len(items)
    return -sum((v/n)*math.log2(v/n) for v in count.values())

def metrics(s):
    if not s or not isinstance(s,str):raise ValueError('TOKEN_VAZIO_INVALID_STRING')
    if s!=unicodedata.normalize('NFC',s): raise ValueError('TOKEN_VAZIO_NOT_NFC')
    raw=s.encode('utf-8')
    compressed={'zlib9':zlib.compress(raw,9),'gzip9':gzip.compress(raw,9,mtime=0),'xz6':lzma.compress(raw,preset=6)}
    if any(zlib.decompress(compressed['zlib9'])!=raw for _ in range(1)):raise AssertionError('ZLIB_LOSS')
    if gzip.decompress(compressed['gzip9'])!=raw or lzma.decompress(compressed['xz6'])!=raw:raise AssertionError('CODEC_LOSS')
    return {
        'text':s,'utf8_bytes':len(raw),'unicode_codepoints':len(s),
        'unique_bytes':len(set(raw)),'unique_codepoints':len(set(s)),
        'H_byte_bits_per_byte':round(h(raw),6),'H_unicode_bits_per_codepoint':round(h(s),6),
        'byte_entropy_estimated_total_bits':round(len(raw)*h(raw),6),
        'zlib9_bytes':len(compressed['zlib9']),'gzip9_bytes':len(compressed['gzip9']),
        'xz6_bytes':len(compressed['xz6']),'zlib9_saving_pct':round(100*(1-len(compressed['zlib9'])/len(raw)),3),
        'sha256_utf8':hashlib.sha256(raw).hexdigest(),
        'estimated_entropy_not_coding_bound_for_single_sample': True
    }

def dot_mask(unicode_braille):
    n=ord(unicode_braille)
    if not (0x2800<=n<=0x28ff):raise ValueError('NOT_BRAILLE_CELL')
    return n-0x2800

def pack6(cells):
    """Tight 6-bit cell stream (5x6 = 30 bits -> 4 bytes), length external."""
    if any(dot_mask(c)>63 for c in cells):raise ValueError('REQUIRE_SIX_DOT')
    n=0
    for i,c in enumerate(cells):n|=dot_mask(c)<<(6*i)
    return n.to_bytes((len(cells)*6+7)//8,'little')

def unpack6(blob, count):
    n=int.from_bytes(blob,'little')
    return ''.join(chr(0x2800+((n>>(6*i))&63)) for i in range(count))

def validate(doc):
    if doc.get('claim_allowed') is not False:raise ValueError('CLAIM_GATE')
    if doc.get('translation_audit') != 'TOKEN_VAZIO_HUMAN_LINGUIST_REVIEW':raise ValueError('TRANSLATION_NOT_AUDITED')
    variants=doc['text_variants']; ids=[v['id'] for v in variants]
    if len(ids)<8 or len(set(ids))!=len(ids):raise ValueError('INSUFFICIENT_LANGUAGES')
    for v in variants:
        for key in ('word','sentence'):
            if not v.get(key) or v[key]!=unicodedata.normalize('NFC',v[key]):raise ValueError('BAD_PARALLEL_TEXT')
    br=doc['braille'];pt=next(v for v in variants if v['id']=='pt')
    if br['source_text']!=pt['word'] or br['source_text']!='cinco': raise ValueError('BRAILLE_NOT_SAME_PT_WORD')
    m={'c':0x2809,'i':0x280a,'n':0x281d,'o':0x2815}
    expected=''.join(chr(m[x]) for x in 'cinco')
    if br['cells_unicode']!=expected or br['digits_five']!='⠼⠑':raise ValueError('BRAILLE_MAP')
    if unpack6(pack6(br['cells_unicode']),len(br['cells_unicode']))!=br['cells_unicode']:raise ValueError('BRAILLE_SIXBIT_ROUNDTRIP')
    other={r['id']:r['text'] for r in doc['other_writing_systems']}
    if other['mayan_numeral_five']!=chr(0x1d2e5) or other['egyptian_hieroglyph_five']!=chr(0x133fe):raise ValueError('UNICODE_REFERENCE_IDENTITY')
    if doc['libras']['real_frame_status']!='TOKEN_VAZIO_NO_LICENSED_ALIGNED_FRAME_MATERIALIZED':raise ValueError('LIBRAS_FALSE_PROMOTION')
    return True

def run(doc):
    validate(doc)
    records=[]
    for v in doc['text_variants']:
        for unit in ('word','sentence'):
            records.append({'id':v['id'],'name':v['name'],'script':v['script'],'unit':unit,'writing_system':'ordinary_unicode',**metrics(v[unit])})
    for key in ('cells_unicode','digits_five'):
        records.append({'id':'pt_braille','name':'Braille português','script':'Braille','unit':('word' if key=='cells_unicode' else 'numeral'),'writing_system':'unicode_6dot',**metrics(doc['braille'][key])})
    for v in doc['other_writing_systems']:
        records.append({'id':v['id'],'name':v['id'],'script':v['class'],'unit':'numeral','writing_system':'unicode_numeral',**metrics(v['text'])})
    blob=pack6(doc['braille']['cells_unicode'])
    return {'schema':'rll.cross_script_entropy_receipt.v2','status':'PASS_SCOPED_PARALLEL_TEXT_BYTES_ONLY',
      'semantic_anchor':doc['semantic_anchor'],'natural_languages':len(doc['text_variants']),
      'proposition_count':1,'records':records,
      'braille_packed_6bit':{'word':'cinco','cells':len(doc['braille']['cells_unicode']),'packed_bytes':len(blob),'packed_hex':blob.hex(),'decoded_cells':unpack6(blob,len(doc['braille']['cells_unicode'])),'length_metadata_included':False,'codebook_metadata_included':False},
      'libras_status':'TOKEN_VAZIO_NO_LICENSED_ALIGNED_FRAME_MATERIALIZED',
      'semantic_translation_verified':'NOT_RUN_HUMAN_REVIEW',
      'visual_fft_status':'SEPARATE_IMAGE_PIPELINE_NOT_LANGUAGE_ENTROPY',
      'caution':'Single short string H is plug-in frequency entropy; zlib/gzip/xz overhead may expand; byte and codepoint H differ, not comparable to full language entropy.',
      'source_sha256':hashlib.sha256(json.dumps(doc,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
      'claim_allowed':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=DATA);p.add_argument('--output',type=Path)
    a=p.parse_args();r=run(json.loads(a.input.read_text(encoding='utf-8')))
    out=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(out,encoding='utf-8')
    print(json.dumps({'status':r['status'],'natural_languages':r['natural_languages'],'records':len(r['records']),'braille_packed_bytes':r['braille_packed_6bit']['packed_bytes'],'libras_status':r['libras_status']}))
if __name__=='__main__':main()
