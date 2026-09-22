#!/usr/bin/env python3
"""Strict-JSON normalization for auditable receipts.

Scientific/optimizer diagnostics may contain NaN or +/-Infinity when a bounded
attempt fails. JSON receipts must never emit those non-standard numbers. This
module preserves the failure event and recursively maps only non-finite float
payloads to null; it does not turn them into zero, finite evidence, or PASS.
"""
from __future__ import annotations

import json
import math
from typing import Any


def normalize(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, tuple):
        return [normalize(item) for item in value]
    return value


def dumps(value: Any, **kwargs: Any) -> str:
    options = {"ensure_ascii": False, "allow_nan": False}
    options.update(kwargs)
    options["allow_nan"] = False
    return json.dumps(normalize(value), **options)
