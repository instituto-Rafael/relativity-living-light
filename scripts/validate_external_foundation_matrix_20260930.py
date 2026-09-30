#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

RELATIONS = {'SUPPORTS_METHOD','SUPPORTS_BOUNDED_BRIDGE','CONTRADICTS_STRONG_FORM','DOES_NOT_RESOLVE','TRANSVERSAL_CASE_STUDY','PARTIAL_SUPPORT_WITH_CORRECTION','PARTIAL_SUPPORT_WITH_CONTRADICTION'}
REQ_BOUNDARIES = {
  'MATHEMATICAL_REPRESENTATION != PHYSICAL_MECHANISM',
  'HOLOGRAPHIC_INFORMATION_GEOMETRY != GENERIC_SPACETIME_IS_INFORMATION',
  'CROSS_LINGUAL_ALIGNMENT != UNIVERSAL_SEMANTIC_LAW',
  'TRANSVERSAL_NUTRITION_CASE != RLL_COSMOLOGY_EVIDENCE',
}

def main():
    p = Path(sys.argv[1] if len(sys.argv) > 1 else 'data/evidence/RLL_EXTERNAL_FOUNDATION_MATRIX_20260930.json')
    d = json.loads(p.read_text(encoding='utf-8'))
    e = []
    if d.get('schema') != 'rll.external-foundation-matrix.v1': e.append('schema')
    if d.get('claim_allowed') is not False: e.append('root_claim_allowed')
    if not re.fullmatch(r'[0-9a-f]{40}', str(d.get('base_commit',''))): e.append('base_commit')
    if not REQ_BOUNDARIES.issubset(set(d.get('boundaries',[]))): e.append('boundaries')
    ids=set()
    for r in d.get('records',[]):
        if r.get('id') in ids: e.append('duplicate:'+str(r.get('id')))
        ids.add(r.get('id'))
        if r.get('relation') not in RELATIONS: e.append('relation:'+str(r.get('id')))
        if r.get('claim_allowed') is not False: e.append('promotion:'+str(r.get('id')))
        if r.get('scope') == 'OUTSIDE_RLL_COSMOLOGY' and r.get('state') == 'PHYSICAL_EVIDENCE': e.append('scope:'+str(r.get('id')))
    out={'schema':'rll.external-foundation-matrix.validation.v1','records':len(d.get('records',[])),'status':'PASS' if not e else 'FAIL','errors':e,'claim_allowed':False}
    print(json.dumps(out,sort_keys=True))
    return 0 if not e else 2

if __name__ == '__main__': raise SystemExit(main())
