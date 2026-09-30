#!/usr/bin/env python3
"""Reconcile the existing external formal manifest; never promote physics."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rp-root', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = {
        'manifest': args.rp_root / 'examples/rll_formal_experiment_manifest.v1.json',
        'schema': args.rp_root / 'schemas/formal_experiment_manifest.v1.schema.json',
        'registry': root / 'knowledge_ecosystem/rll_cross_repo_entrelaces_v2.json',
    }
    content = {key: json.loads(path.read_text()) for key, path in paths.items()}
    Draft202012Validator.check_schema(content['schema'])
    Draft202012Validator(content['schema']).validate(content['manifest'])
    relation = next(x for x in content['registry']['relationships'] if x['id'] == 'RLL-RP-FORMAL-001')
    manifest = content['manifest']
    if manifest['claim_allowed'] is not False or manifest['manifest_id'] != relation['id']:
        raise ValueError('identity or claim boundary mismatch')
    report = {
        'receipt_id': 'RLL-RP-FORMAL-RECONCILIATION-20260914',
        'parent': relation['id'],
        'state': 'STRUCTURAL_SCHEMA_PASS_SCIENTIFIC_BLOCKED',
        'claim_allowed': False,
        'source_commits': {
            name: subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
            for name, directory in [('RLL', root), ('RafPolimata', args.rp_root)]
        },
        'sources': {key: {'path': str(path.relative_to(args.rp_root if key != 'registry' else root)),
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    for key, path in paths.items()},
        'contract_comparison': {
            'requested': relation['required_artifact']['schema'],
            'observed': manifest['schema'],
            'equal': relation['required_artifact']['schema'] == manifest['schema'],
        },
        'scientific_evidence': manifest['evidence'],
        'routes': {'L': 'historical registry preserved; successor receipt',
                   'O': 'RLL observational owner to RafPolimata formal owner',
                   'C': 'recover existing contract before implementing a duplicate',
                   'P': 'commit and byte hashes above'},
        'gap': ['schema namespace/ownership reconciliation', 'stable equation IDs',
                'canonical experiment command and frozen data', 'scientific execution and independent reproduction'],
        'next': 'Resolve schema identity explicitly before emitting a real experiment manifest; retain existing example as an example.',
        'rollback': 'Revert this additive reconciliation script and receipt only; preserve both source documents and all negative evidence.',
        'boundary': 'JSON Schema validation is not execution of the scientific experiment or dual repository scientific approval.',
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(report['state'])


if __name__ == '__main__':
    main()
