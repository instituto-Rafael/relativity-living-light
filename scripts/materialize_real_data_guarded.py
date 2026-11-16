#!/usr/bin/env python3
"""Governed entrypoint for bounded public real-data materialization.

The underlying materializer enforces HTTPS/host/path/size and explicit network
opt-in. This wrapper adds the repository development authority contract before
any materialization call.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from internal.governance.development_guard import evaluate_operation
from scripts import materialize_real_data as base

POLICY=ROOT/"data/governance/RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"
OPERATION=ROOT/"configs/real_data_materialization_operation.json"


def preflight(authority_mode=None):
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    operation=json.loads(OPERATION.read_text(encoding="utf-8"))
    mode=(
        authority_mode
        or os.environ.get("RLL_AUTHORITY_MODE")
        or operation.get("authority",{}).get("default_runtime_mode")
    )
    receipt=evaluate_operation(
        policy,
        operation,
        runtime_authority_mode=mode,
    )
    if receipt.get("decision")!="ALLOW":
        raise PermissionError(
            "materialization governance blocked: "
            +str(receipt.get("decision"))
            +" "
            +"; ".join(receipt.get("reasons",[]))
        )
    return receipt


def main():
    parser=argparse.ArgumentParser(
        description="Governed bounded real-data materialization entrypoint."
    )
    parser.add_argument("--dataset",default=None)
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--authorize-network-materialization",action="store_true")
    args=parser.parse_args()

    if args.dry_run and args.authorize_network_materialization:
        raise SystemExit("--dry-run and --authorize-network-materialization are mutually exclusive")

    try:
        receipt=preflight()
    except PermissionError as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(4)

    if not args.dry_run and not args.authorize_network_materialization:
        print(
            "network materialization requires explicit "
            "--authorize-network-materialization",
            file=sys.stderr,
        )
        raise SystemExit(3)

    manifest=base.materialize(
        dataset_id=args.dataset,
        dry_run=args.dry_run,
        authorize_network_materialization=args.authorize_network_materialization,
    )
    manifest["governance_preflight"]=receipt
    base.MANIFEST.write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
    failed=[row for row in manifest.get("results",[]) if row.get("ok") is False]
    return 2 if failed else 0


if __name__=="__main__":
    raise SystemExit(main())
