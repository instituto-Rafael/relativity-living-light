#!/usr/bin/env python3
"""
Carrega um arquivo JSON ou CSV já commitado e calcula estatísticas simples.

Saída esperada:
- n registros;
- colunas numéricas: mean, median, std, min, max;
- pequenas amostras (first/last 5).

Fronteira de claim:
este script só gera artefato de auditoria estatística. Ele não valida RLL,
matéria escura, energia escura ou qualquer hipótese cosmológica.
"""

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


RECORD_KEYS = ("records", "data", "dados", "rows", "items")


def _json_records(payload: Any) -> list[dict[str, Any]]:
    """Normalize common JSON shapes into tabular records."""
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


def load(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    suffix = p.suffix.lower()
    if suffix == ".json":
        with p.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return pd.DataFrame(_json_records(payload))

    return pd.read_csv(p)


def _finite_or_none(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isfinite(number):
        return number
    return None


def _sample(df: pd.DataFrame, n: int, tail: bool = False) -> list[dict[str, Any]]:
    frame = df.tail(n) if tail else df.head(n)
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    stats: dict[str, Any] = {
        "n_records": int(len(df)),
        "n_columns": int(len(df.columns)),
        "numeric_columns": [str(col) for col in numeric.columns],
        "columns": {},
    }

    for col in numeric.columns:
        s = numeric[col].dropna()
        stats["columns"][str(col)] = {
            "mean": _finite_or_none(s.mean()) if len(s) > 0 else None,
            "median": _finite_or_none(s.median()) if len(s) > 0 else None,
            "std": _finite_or_none(s.std()) if len(s) > 1 else None,
            "min": _finite_or_none(s.min()) if len(s) > 0 else None,
            "max": _finite_or_none(s.max()) if len(s) > 0 else None,
            "n_nonnull": int(s.count()),
        }

    stats["sample_head"] = _sample(df, 5, tail=False)
    stats["sample_tail"] = _sample(df, 5, tail=True)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", required=True)
    parser.add_argument("--out", dest="outfile", required=True)
    args = parser.parse_args()

    df = load(args.infile)
    res = summarize(df)
    Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"Resultados gravados em {args.outfile}")


if __name__ == "__main__":
    main()
