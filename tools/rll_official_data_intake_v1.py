#!/usr/bin/env python3
"""Bounded read-only intake of official public climate data and cosmology *index*.
No credentials, writes only caller-supplied local artifact dir, and no RLL fit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCHEMA = "rll.official_source_intake.v1"
POWER = "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PS&community=AG&longitude=0&latitude=0&start=20250101&end=20250107&format=JSON&time-standard=UTC"
DESI = "https://data.desi.lbl.gov/doc/papers/dr2/"
SOURCES = {
    "nasa_power_daily": {"url": POWER, "host": "power.larc.nasa.gov", "kind": "CLIMATE_GRIDDED_DAILY", "max_bytes": 512_000, "ext": "json"},
    "desi_dr2_publications": {"url": DESI, "host": "data.desi.lbl.gov", "kind": "COSMOLOGY_OFFICIAL_INDEX_NOT_NUMERIC_DATA", "max_bytes": 768_000, "ext": "html"},
}

class IntakeError(ValueError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise IntakeError("REDIRECT_BLOCKED")


def _canonical(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _safe_profile(source: str) -> dict:
    if source not in SOURCES:
        raise IntakeError("SOURCE_NOT_ALLOWLISTED")
    profile = SOURCES[source]
    parsed = urllib.parse.urlsplit(profile["url"])
    if parsed.scheme != "https" or parsed.hostname != profile["host"] or parsed.username or parsed.password:
        raise IntakeError("SOURCE_HOST_OR_SCHEME_INVALID")
    return profile


def fetch_bounded(source: str) -> bytes:
    profile = _safe_profile(source)
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(profile["url"], headers={"User-Agent": "RLL-official-intake/1.0 (read-only)", "Accept": "application/json" if source == "nasa_power_daily" else "text/html"}, method="GET")
    try:
        with opener.open(request, timeout=20) as response:
            if response.status != 200:
                raise IntakeError("HTTP_NOT_200")
            final = urllib.parse.urlsplit(response.geturl())
            if final.scheme != "https" or final.hostname != profile["host"]:
                raise IntakeError("UNEXPECTED_RESPONSE_ORIGIN")
            data = response.read(profile["max_bytes"] + 1)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise IntakeError("REMOTE_FETCH_FAILED") from exc
    if not data or len(data) > profile["max_bytes"]:
        raise IntakeError("EMPTY_OR_OVERSIZE")
    return data


def inspect_power(payload: bytes) -> dict:
    try:
        obj = json.loads(payload)
    except (ValueError, UnicodeDecodeError) as exc:
        raise IntakeError("INVALID_JSON") from exc
    if not isinstance(obj, dict) or obj.get("type") != "Feature":
        raise IntakeError("POWER_FEATURE_MISSING")
    properties = obj.get("properties") or {}
    parameter = properties.get("parameter") or {}
    if not isinstance(parameter, dict) or not all(p in parameter for p in ("T2M", "PS")):
        raise IntakeError("REQUIRED_PARAMETERS_MISSING")
    fill = (obj.get("header") or {}).get("fill_value", -999)
    valid = {}
    missing = {}
    for name in ("T2M", "PS"):
        series = parameter[name]
        if not isinstance(series, dict):
            raise IntakeError("SERIES_NOT_DICT")
        actual = 0
        absent = 0
        for day, val in series.items():
            if not re.fullmatch(r"2025010[1-7]", day):
                raise IntakeError("DATE_OUTSIDE_PINNED_WINDOW")
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise IntakeError("NON_FINITE_VALUE")
            if val == fill or val == -999:
                absent += 1
            else:
                actual += 1
        if len(series) != 7:
            raise IntakeError("INCOMPLETE_TIME_WINDOW")
        valid[name], missing[name] = actual, absent
    if any(v == 0 for v in valid.values()):
        raise IntakeError("NO_VALID_SAMPLES")
    return {"variables": ["T2M", "PS"], "observed_day_count": 7, "non_missing_per_variable": valid, "missing_per_variable": missing, "spatial_domain": "SINGLE_POINT_GRID_CELL", "coordinates_lon_lat": [0, 0], "time_standard": "UTC", "time_window": "2025-01-01/2025-01-07", "confidence": "SCHEMA_CHECK_ONLY", "note": "NASA POWER gridded analysis-ready product, not direct station measurements"}


def inspect_desi(payload: bytes) -> dict:
    try:
        txt = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IntakeError("HTML_NOT_UTF8") from exc
    lower = txt.lower()
    if not all(term in lower for term in ("desi dr2", "baryon acoustic oscillations", "cosmology")):
        raise IntakeError("DESI_RELEASE_MARKERS_NOT_FOUND")
    return {"catalog": "DESI_DR2_PUBLICATIONS", "recognized_release_markers": True, "measurement_count": "TOKEN_VAZIO", "covariance": "TOKEN_VAZIO", "is_numeric_ingestion": False, "data_state": "OFFICIAL_REFERENCE_INDEX_ONLY", "note": "Publication HTML is not a data release table, posterior chain or covariance matrix"}


def make_receipt(source: str, mode: str, data: bytes | None = None, *, run_ref: str = "LOCAL") -> dict:
    profile = _safe_profile(source)
    if mode not in ("metadata_only", "fetch"):
        raise IntakeError("MODE_INVALID")
    if mode == "fetch" and data is None:
        raise IntakeError("FETCH_PAYLOAD_REQUIRED")
    if mode == "metadata_only" and data is not None:
        raise IntakeError("DRY_RUN_HAS_PAYLOAD")
    data_info = None
    if data is not None:
        if not data or len(data) > profile["max_bytes"]:
            raise IntakeError("EMPTY_OR_OVERSIZE")
        data_info = inspect_power(data) if source == "nasa_power_daily" else inspect_desi(data)
    return {
        "schema": SCHEMA,
        "source": source,
        "source_authority": "NASA_POWER" if source == "nasa_power_daily" else "DESI_COLLABORATION_LBL",
        "source_url": profile["url"],
        "type": profile["kind"],
        "mode": mode,
        "execution_state": "SCHEMA_VALIDATED_REMOTE_BYTES" if data is not None else "NOT_FETCHED",
        "bytes_sha256": hashlib.sha256(data).hexdigest() if data is not None else "TOKEN_VAZIO",
        "bytes_length": len(data) if data is not None else "TOKEN_VAZIO",
        "inspection": data_info if data_info is not None else "TOKEN_VAZIO",
        "raw_data_in_repository": False,
        "model_fit_executed": False,
        "physical_validation": "NOT_RUN",
        "claim_allowed": False,
        "publication_effect": "NONE",
        "secrets_required": False,
        "execution_ref": run_ref,
        "next": "PIN_PROVIDER_VERSION_LICENSE_AND_COVARIANCE_THEN_INDEPENDENT_VALIDATION"
    }


def run(source: str, mode: str, destination: Path, *, run_ref: str = "LOCAL") -> dict:
    profile = _safe_profile(source)
    if not destination.name or destination.is_symlink():
        raise IntakeError("DESTINATION_INVALID")
    data = fetch_bounded(source) if mode == "fetch" else None
    receipt = make_receipt(source, mode, data, run_ref=run_ref)
    destination.mkdir(parents=True, exist_ok=True)
    if data is not None:
        # Raw bytes preserved only in ephemeral Actions artifact or explicitly chosen local dir.
        (destination / (source + "." + profile["ext"])).write_bytes(data)
    (destination / "RECEIPT.json").write_bytes(_canonical(receipt))
    (destination / "CHECKSUMS.sha256").write_text(
        hashlib.sha256((destination / "RECEIPT.json").read_bytes()).hexdigest() + "  RECEIPT.json\n"
        + (hashlib.sha256(data).hexdigest() + "  " + source + "." + profile["ext"] + "\n" if data is not None else ""),
        encoding="utf-8")
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", choices=sorted(SOURCES), required=True)
    ap.add_argument("--mode", choices=("metadata_only", "fetch"), default="metadata_only")
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--run-ref", default="LOCAL")
    args = ap.parse_args()
    result = run(args.source, args.mode, args.output_dir, run_ref=args.run_ref)
    print(json.dumps({"source": result["source"], "execution_state": result["execution_state"], "claim_allowed": False}, sort_keys=True))

if __name__ == "__main__":
    main()
