"""Legacy NumPy/Pandas loader retained only for Bayesian/historical validation routes.

Dependency-free deterministic validation uses validation.load_data.
Do not promote this adapter as the Rx/stdlib route.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_REAL_HZ = Path("data/real/Hz_data_real.csv")


def _numeric_column(df: pd.DataFrame, column: str, source: Path) -> np.ndarray:
    if column not in df.columns:
        raise ValueError(f"missing required column {column!r} in {source}")
    values = pd.to_numeric(df[column], errors="raise").to_numpy(dtype=float)
    if values.size == 0:
        raise ValueError(f"empty required column {column!r} in {source}")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"non-finite values in column {column!r} from {source}")
    return values


def load_real_data(path: str | Path = DEFAULT_REAL_HZ):
    """Load the canonical real H(z) dataset used by validation scripts.

    This loader intentionally avoids globbing arbitrary `data/*.csv` files. The
    scientific validation workflow must use a declared real-data artifact with a
    stable path and schema; it must not silently fall back to synthetic values or
    accidentally pick an unrelated CSV from the repository root.
    """

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(
            f"required real-data file not found: {source}. "
            "Run the documented real-data materialization/audit workflow before validation."
        )

    df = pd.read_csv(source)
    z = _numeric_column(df, "z", source)
    y = _numeric_column(df, "H_obs", source)
    yerr = _numeric_column(df, "sigma_H", source)

    if not (len(z) == len(y) == len(yerr)):
        raise ValueError(f"inconsistent vector lengths in {source}")
    if np.any(yerr <= 0):
        raise ValueError(f"non-positive sigma_H values in {source}")

    print(f"DATA REAL: {source} | N={len(z)}")
    return z, y, yerr
