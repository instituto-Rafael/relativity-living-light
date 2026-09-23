from __future__ import annotations

import csv
import math
from pathlib import Path

DEFAULT_REAL_HZ = Path("data/real/Hz_data_real.csv")


def _numeric_column(rows: list[dict[str, str]], column: str, source: Path) -> list[float]:
    if not rows:
        raise ValueError(f"empty dataset in {source}")
    if column not in rows[0]:
        raise ValueError(f"missing required column {column!r} in {source}")
    values: list[float] = []
    for index, row in enumerate(rows, start=2):
        raw = row.get(column)
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"non-numeric value in column {column!r} at CSV line {index} from {source}"
            ) from exc
        if not math.isfinite(value):
            raise ValueError(
                f"non-finite value in column {column!r} at CSV line {index} from {source}"
            )
        values.append(value)
    if not values:
        raise ValueError(f"empty required column {column!r} in {source}")
    return values


def load_real_data(path: str | Path = DEFAULT_REAL_HZ):
    """Load the canonical real H(z) dataset with Python stdlib only.

    Returns three lists of floats: z, H_obs and sigma_H. The deterministic
    validation route consumes these lists directly. Bayesian legacy consumers
    that still require ndarray semantics use load_data_numpy_legacy.py.
    """

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(
            f"required real-data file not found: {source}. "
            "Run the documented real-data materialization/audit workflow before validation."
        )

    with source.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    z = _numeric_column(rows, "z", source)
    y = _numeric_column(rows, "H_obs", source)
    yerr = _numeric_column(rows, "sigma_H", source)

    if not (len(z) == len(y) == len(yerr)):
        raise ValueError(f"inconsistent vector lengths in {source}")
    if any(value <= 0.0 for value in yerr):
        raise ValueError(f"non-positive sigma_H values in {source}")

    print(f"DATA REAL: {source} | N={len(z)}")
    return z, y, yerr


def main() -> int:
    z, y, yerr = load_real_data()
    print(
        "VALIDATION_STDLIB_DATA=PASS",
        f"N={len(z)}",
        f"z=[{min(z):.6g},{max(z):.6g}]",
        f"H=[{min(y):.6g},{max(y):.6g}]",
        f"sigma_min={min(yerr):.6g}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
