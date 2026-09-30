#!/usr/bin/env python3
"""Validate RLL watch config with project-local strict stdlib subsets.

Canonical config is JSON. Legacy YAML remains readable only through the
restricted rx.yaml_subset parser; this script does not claim general YAML or
general JSON Schema support.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from rx.schema_subset import validate as validate_schema_subset
from rx.yaml_subset import load as load_yaml_subset


def load_config(path: Path):
    text=path.read_text(encoding="utf-8")
    if path.suffix.lower()==".json":
        return json.loads(text)
    if path.suffix.lower() in {".yml",".yaml"}:
        return load_yaml_subset(path)
    raise ValueError("unsupported config format: "+path.suffix)


def validate_config(config_path: Path, schema_path: Path) -> None:
    payload=load_config(config_path)
    schema=json.loads(schema_path.read_text(encoding="utf-8"))
    validate_schema_subset(payload,schema)


def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("rll_inovacao_tecnologica_watch.json"),
        help="Path to watch config JSON or strict-subset legacy YAML",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/rll_watch.schema.json"),
        help="Path to supported JSON schema subset",
    )
    return parser


def main() -> int:
    args=build_parser().parse_args()
    validate_config(config_path=args.config,schema_path=args.schema)
    print(f"OK: {args.config} is valid against {args.schema}")
    print("third_party_python_dependencies=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
