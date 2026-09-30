#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / 'docs/navigation/README.md'
ROOT_INDEX = ROOT / 'docs/navigation/ROOT_FILES_INDEX.md'
LGPD_DOC = ROOT / 'docs/governance/LGPD_PRIVACY_NAVIGATION_V1.md'
CONTRACT = ROOT / 'data/governance/RLL_LGPD_NAVIGATION_PRIVACY_V1.json'
README = ROOT / 'README.md'
MASTER = ROOT / 'docs/INDICE_MESTRE.md'

TEXT_SUFFIXES = {'.md','.txt','.json','.jsonl','.yml','.yaml','.py','.sh','.toml','.gradle','.properties','.tex','.csv','.tsv'}
LABELED_PII = re.compile(r'(?i)\b(cpf|rg|telefone|phone|celular|endereco|endereço|address)\b[^\n]{0,32}(?:\d[\d .()/-]{5,})')
EMAIL = re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b')

def fail(msg: str) -> None:
    print('FAIL ' + msg)
    raise SystemExit(1)

def tracked_files() -> list[str]:
    cp = subprocess.run(['git','ls-files','-z'], cwd=ROOT, check=True, stdout=subprocess.PIPE)
    return sorted(x for x in cp.stdout.decode('utf-8').split('\0') if x)

def main() -> int:
    for path in (HUB, ROOT_INDEX, LGPD_DOC, CONTRACT, README, MASTER):
        if not path.is_file():
            fail('missing:' + path.relative_to(ROOT).as_posix())

    tracked = tracked_files()
    root_files = sorted(p for p in tracked if '/' not in p)
    index_text = ROOT_INDEX.read_text(encoding='utf-8')
    missing = [p for p in root_files if ('`' + p + '`') not in index_text]
    if missing:
        print('UNINDEXED_ROOT_PATHS=' + ','.join(missing))
        fail('root_index_incomplete')

    if 'docs/navigation/README.md' not in README.read_text(encoding='utf-8'):
        fail('README_missing_navigation_hub')
    if 'navigation/README.md' not in MASTER.read_text(encoding='utf-8'):
        fail('INDICE_MESTRE_missing_navigation_hub')

    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    if contract.get('claim_allowed') is not False:
        fail('claim_allowed_must_be_false')
    if contract.get('compliance_claim') is not False:
        fail('compliance_claim_must_be_false')

    inv = set(contract.get('invariants', []))
    for req in ('PRIVACY_BY_DESIGN != LEGAL_COMPLIANCE_CERTIFICATION','TOKEN_VAZIO != COMPLIANT','INDEX_FIRST_BEFORE_PHYSICAL_MIGRATION'):
        if req not in inv:
            fail('missing_invariant:' + req)

    pii_paths = 0
    email_paths = 0
    for rel in tracked:
        p = ROOT / rel
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if p.stat().st_size > 1000000:
                continue
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if LABELED_PII.search(txt):
            pii_paths += 1
        if EMAIL.search(txt):
            email_paths += 1

    print('ROOT_FILES_INDEXED=' + str(len(root_files)))
    print('PII_LABELED_REVIEW_PATH_COUNT=' + str(pii_paths))
    print('EMAIL_REVIEW_PATH_COUNT=' + str(email_paths))
    print('PII_VALUES_LOGGED=0')
    print('LEGAL_COMPLIANCE_CLAIM=0')
    print('PASS_NAVIGATION_PRIVACY_ENGINEERING_GATE')
    return 0

if __name__ == '__main__':
    sys.exit(main())
