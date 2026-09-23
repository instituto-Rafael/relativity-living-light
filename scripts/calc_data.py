#!/usr/bin/env python3
"""Compute simple audit statistics from a committed JSON or CSV input.

Python stdlib only. This is an audit/statistics utility, not a scientific
validation engine. Output contract preserves the historical keys produced by
the former Pandas/NumPy implementation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

RECORD_KEYS = ("records", "data", "dados", "rows", "items")


def _json_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return payload
        return [{"index": idx, "value": item} for idx, item in enumerate(payload)]

    if isinstance(payload, dict):
        for key in RECORD_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                if all(isinstance(item, dict) for item in value):
                    return value
                return [{"index": idx, key: item} for idx, item in enumerate(value)]

        row: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                row[f"{key}_type"] = type(value).__name__
                row[f"{key}_len"] = len(value)
            else:
                row[key] = value
        return [row]

    return [{"value": payload}]


def _csv_scalar(value: str | None) -> Any:
    if value is None:
        return None
    text = value.strip()
    if text.lower() in {"", "na", "nan", "null", "none"}:
        return None
    try:
        if text.isdigit() or (text.startswith(("+", "-")) and text[1:].isdigit()):
            return int(text)
        number = float(text)
        return number if math.isfinite(number) else text
    except ValueError:
        return text


def load(path: str) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(path)

    if source.suffix.lower() == ".json":
        with source.open("r", encoding="utf-8") as handle:
            return _json_records(json.load(handle))

    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV sem cabeçalho: {source}")
        return [
            {str(key): _csv_scalar(value) for key, value in row.items()}
            for row in reader
        ]


def _columns(records: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in records:
        for key in row:
            if key not in columns:
                columns.append(str(key))
    return columns


def _numeric_values(records: list[dict[str, Any]], column: str) -> list[float] | None:
    present = []
    for row in records:
        value = row.get(column)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        number = float(value)
        if not math.isfinite(number):
            return None
        present.append(number)
    return present if present else None


def _json_safe_row(row: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for column in columns:
        value = row.get(column)
        if isinstance(value, float) and not math.isfinite(value):
            value = None
        out[column] = value
    return out


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    columns = _columns(records)
    numeric: dict[str, list[float]] = {}
    for column in columns:
        values = _numeric_values(records, column)
        if values is not None:
            numeric[column] = values

    stats: dict[str, Any] = {
        "n_records": len(records),
        "n_columns": len(columns),
        "numeric_columns": list(numeric),
        "columns": {},
    }

    for column, values in numeric.items():
        stats["columns"][column] = {
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else None,
            "min": min(values),
            "max": max(values),
            "n_nonnull": len(values),
        }

    stats["sample_head"] = [
        _json_safe_row(row, columns) for row in records[:5]
    ]
    stats["sample_tail"] = [
        _json_safe_row(row, columns) for row in records[-5:]
    ]
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", required=True)
    parser.add_argument("--out", dest="outfile", required=True)
    args = parser.parse_args()

    records = load(args.infile)
    result = summarize(records)
    output = Path(args.outfile)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Resultados gravados em {args.outfile}")


if __name__ == "__main__":
    main()
