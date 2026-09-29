#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = [
    ROOT / 'data/governance/RLL_ROOT_PHYSICAL_REFACTOR_WAVE2A_V1.json',
    ROOT / 'data/governance/RLL_ROOT_PHYSICAL_REFACTOR_WAVE2B_V1.json',
]
START = ROOT / 'docs/presentation/00_START_HERE_RLL.md'
STATE = ROOT / 'docs/presentation/05_CURRENT_STATE_RLL.md'
ROOT_INDEX = ROOT / 'docs/navigation/ROOT_FILES_INDEX.md'
README = ROOT / 'README.md'

IGNORE_BACKLINK_PREFIXES = (
    'results/pipeline-runs/',
    'to_Add/',
    'ANALISE_COMPLETA/',
    'docs/DOCUMENTATION_FULL_INVENTORY.md',
)
IGNORE_BACKLINK_EXACT = {
    'docs/navigation/ROOT_FILES_INDEX.md',
    'schemas/EVOLUTION_ROADMAP.md',
    'docs/legacy/root/README.md',
    'docs/presentation/05_CURRENT_STATE_RLL.md',
    'receipts/2026-09-29_START_HERE_V2_1_ROOT_WAVE2.md',
}

TEXT_SUFFIXES = {'.md','.txt','.json','.jsonl','.yml','.yaml','.py','.sh','.toml','.html','.tex','.csv','.tsv'}

def fail(msg: str) -> None:
    print('FAIL ' + msg)
    raise SystemExit(1)

def git_blob(path: Path) -> str:
    cp = subprocess.run(['git','hash-object',str(path)], cwd=ROOT, check=True, stdout=subprocess.PIPE, text=True)
    return cp.stdout.strip()

def tracked() -> list[str]:
    cp = subprocess.run(['git','ls-files','-z'], cwd=ROOT, check=True, stdout=subprocess.PIPE)
    return sorted(x for x in cp.stdout.decode('utf-8').split('\0') if x)

def main() -> int:
    start = START.read_text(encoding='utf-8')
    state = STATE.read_text(encoding='utf-8')
    root_index = ROOT_INDEX.read_text(encoding='utf-8')
    readme = README.read_text(encoding='utf-8')

    for token in ('START HERE Ω V2.1','INTENT','CURRENT_STATE','μREAD','SOURCE_MIN','AUTHORITY','ACT','EVIDENCE','μWRITE','R3'):
        if token not in start:
            fail('start_here_missing:' + token)

    if len(start.splitlines()) > 140:
        fail('start_here_router_too_large')
    if len(state.splitlines()) > 80:
        fail('current_state_too_large')
    if 'docs/presentation/00_START_HERE_RLL.md' not in readme:
        fail('README_not_routed_to_v2_1')

    migrations = []
    for mp in MANIFESTS:
        if not mp.is_file():
            fail('missing_manifest:' + mp.name)
        data = json.loads(mp.read_text(encoding='utf-8'))
        migrations.extend(data.get('migrations', []))

    for row in migrations:
        src = ROOT / row['source']
        dst = ROOT / row['destination']
        if not src.is_file():
            fail('missing_stub:' + row['source'])
        if not dst.is_file():
            fail('missing_destination:' + row['destination'])
        observed = git_blob(dst)
        expected = row['original_git_blob']
        if observed != expected:
            fail('blob_mismatch:' + row['destination'] + ':' + observed + '!=' + expected)
        stub = src.read_text(encoding='utf-8', errors='ignore')
        if row['destination'] not in stub:
            fail('stub_missing_destination:' + row['source'])
        if row['destination'] not in root_index:
            fail('root_index_missing_destination:' + row['destination'])
        if src.stat().st_size > 2048:
            fail('stub_too_large:' + row['source'])

    rs = [x for x in migrations if x['source'] == 'Rsfael']
    if len(rs) != 1 or rs[0].get('identified_type') != 'text/plain' or not rs[0]['destination'].endswith('.txt'):
        fail('Rsfael_text_identification_incomplete')

    files = tracked()
    unexpected = []
    for row in migrations:
        needle = row['source']
        for rel in files:
            if rel == row['source'] or rel == row['destination']:
                continue
            if rel in IGNORE_BACKLINK_EXACT or rel.startswith(IGNORE_BACKLINK_PREFIXES):
                continue
            p = ROOT / rel
            if p.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if p.stat().st_size > 1000000:
                    continue
                txt = p.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            if needle in txt:
                unexpected.append((needle, rel))

    print('MIGRATIONS_VERIFIED=' + str(len(migrations)))
    print('START_HERE_LINES=' + str(len(start.splitlines())))
    print('CURRENT_STATE_LINES=' + str(len(state.splitlines())))
    print('DESTINATION_BLOB_PRESERVATION=PASS')
    print('STUB_ROUTING=PASS')
    print('RSFAEL_TYPE=text/plain')
    print('UNEXPECTED_ACTIVE_BACKLINKS=' + str(len(unexpected)))
    if unexpected:
        for needle, rel in unexpected[:20]:
            print('BACKLINK_REVIEW=' + needle + ' <- ' + rel)
        fail('unexpected_active_backlinks')

    print('PASS_START_HERE_V2_1_ROOT_WAVE2_GATE')
    return 0

if __name__ == '__main__':
    sys.exit(main())
