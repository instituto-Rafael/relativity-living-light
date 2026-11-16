#!/usr/bin/env python3
"""Validate the RLL watch config with explicit stdlib-only subsets.

Only JSON and the bounded Rx YAML subset are accepted; unsupported syntax
fails closed. This does not claim general YAML/JSON-Schema conformance.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Direct invocation from scripts/ must work without setting PYTHONPATH.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.schema_subset import validate as validate_schema
from rx.yaml_subset import load as load_yaml_subset


def load_config(config_path: Path) -> dict:
    config_path = Path(config_path)
    suffix = config_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    elif suffix in (".yml", ".yaml"):
        payload = load_yaml_subset(config_path)
    else:
        raise ValueError("unsupported watch config format: " + suffix)
    if not isinstance(payload, dict):
        raise ValueError("watch config must be an object")
    return payload


def validate_config(config_path: Path, schema_path: Path) -> None:
    payload = load_config(config_path)
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validate_schema(payload, schema)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("rll_inovacao_tecnologica_watch.yml"),
        help="Versioned watch config YAML subset or JSON",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/rll_watch.schema.json"),
        help="Strict-subset JSON schema",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    validate_config(config_path=args.config, schema_path=args.schema)
    print(f"OK: {args.config} is valid against {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
