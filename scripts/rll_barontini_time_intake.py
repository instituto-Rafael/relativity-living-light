#!/usr/bin/env python3
"""Reproducible, claim-gated intake of Barontini (2026) Zenodo files.

This module verifies SOURCE integrity and table structure; it does not derive
an entropic clock, fit a physical model, or validate RLL cosmology.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from urllib.request import urlopen

RECORD = "19651064"
PAPER_DOI = "10.1103/1h9j-df4k"
FILES = {
    "Fig2Fig3V0.dat": "3ccd2ee4f076e1d87ddf745f3c5817dc",
    "Fig2Fig3V03.dat": "335fe6bd46b64505a1db5f8096412748",
    "Fig2Fig3V06.dat": "4a26133c0308351324c0943bb81032a5",
    "Fig2Fig3V09.dat": "2acb406c4b5801712cd38bc2e53d98cb",
    "Fig2Fig3V1.dat": "6298f4b3b9990b344713ae513c629435",
    "Fig3numerics.dat": "18823ce15e484770b0ecf981fd55cae4",
    "Fig4.dat": "0ec7c739502163a0d5889fb9a4e23487",
}
LIMIT_BYTES = 6_000_000


def digest(path):
    md5, sha = hashlib.md5(), hashlib.sha256()
    size = 0
    with path.open("rb") as inp:
        for chunk in iter(lambda: inp.read(65536), b""):
            size += len(chunk)
            if size > LIMIT_BYTES:
                raise ValueError("input exceeds per-file safety bound")
            md5.update(chunk)
            sha.update(chunk)
    return {"size_bytes": size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def read_table(path, name):
    # No assumptions about time units, cosmological scale or inferred entropy.
    four = name.startswith("Fig2Fig3V")
    two = name == "Fig3numerics.dat"
    expected_columns = 4 if four else 2 if two else None
    expected_header = ["t", "tau", "phi", "sigma"] if four else ["column", "sigma"] if two else None
    row_count, bad_rows, negative_sigma, zero_sigma = 0, [], 0, 0
    widths = set()
    samples = []
    with path.open("r", encoding="utf-8-sig") as inp:
        for lineno, raw in enumerate(inp, 1):
            line = raw.strip()
            if not line:
                continue
            parts = line.split()
            if expected_header and row_count == 0 and parts == expected_header:
                row_count = -1  # header consumed; -1 means no numeric row yet
                continue
            if expected_header and row_count == 0:
                # first line did not match header; fail rather than infer columns
                raise ValueError("missing or altered header")
            if row_count == -1:
                row_count = 0
            if expected_columns is not None and len(parts) != expected_columns:
                bad_rows.append({"line": lineno, "columns": len(parts)})
                continue
            if expected_columns is None and widths and len(parts) not in widths:
                bad_rows.append({"line": lineno, "columns": len(parts), "reason": "inconsistent_matrix_width"})
                continue
            widths.add(len(parts))
            try:
                nums = [float(v) for v in parts]
            except ValueError as exc:
                raise ValueError(f"invalid numeric token at line {lineno}") from exc
            if any(not math.isfinite(v) for v in nums):
                raise ValueError(f"nonfinite numeric token at line {lineno}")
            if four or two:
                sigma = nums[-1]
                negative_sigma += sigma < 0
                zero_sigma += sigma == 0
                if sigma < 0:
                    bad_rows.append({"line": lineno, "reason": "negative_sigma"})
            if four:
                samples.append((nums[0], nums[1]))
            row_count += 1
    if row_count <= 0:
        raise ValueError("no numeric rows")
    if negative_sigma:
        raise ValueError("negative uncertainty sigma")
    # Source table order is not assumed to be physical-time order. tau ties are valid.
    diagnostics = {}
    if four:
        by_t = sorted(samples)
        diagnostics = {
            "out_of_order_t_pairs": sum(samples[i][0] < samples[i - 1][0] for i in range(1, len(samples))),
            "tau_plateaus_adjacent_by_t": sum(by_t[i][1] == by_t[i - 1][1] for i in range(1, len(by_t))),
            "tau_decreases_adjacent_by_t": sum(by_t[i][1] < by_t[i - 1][1] for i in range(1, len(by_t))),
            "duplicate_t": sum(by_t[i][0] == by_t[i - 1][0] for i in range(1, len(by_t))),
        }
    return {"numeric_rows": row_count, "column_widths": sorted(widths), "malformed_rows": bad_rows,
            "sigma_zeros": zero_sigma, "diagnostics": diagnostics}


def audit(directory, files=FILES):
    directory = Path(directory)
    result = {"schema": "rll.barontini.intake_receipt.v1", "source_record": RECORD,
              "paper_doi": PAPER_DOI, "source_not_model_validation": True,
              "claim_allowed": False, "cosmology_fit_modified": False, "files": {}}
    for name, correct_md5 in files.items():
        path = directory / name
        if not path.is_file():
            result["files"][name] = {"status": "TOKEN_VAZIO_NOT_MATERIALIZED"}
            continue
        try:
            observed = digest(path)
            if observed["md5"] != correct_md5:
                result["files"][name] = {"status": "BLOCKED_DIGEST_MISMATCH", **observed,
                                          "expected_md5": correct_md5}
                continue
            details = read_table(path, name)
            status = "REVIEW_REQUIRED" if details["malformed_rows"] or details["diagnostics"].get("duplicate_t") else "PASS_INTEGRITY_AND_SHAPE"
            result["files"][name] = {"status": status, **observed, **details}
        except (OSError, ValueError, UnicodeError) as exc:
            result["files"][name] = {"status": "BLOCKED_PARSE", "reason": str(exc)}
    statuses = {x["status"] for x in result["files"].values()}
    result["intake_status"] = ("PASS_SCOPED_INTEGRITY" if statuses == {"PASS_INTEGRITY_AND_SHAPE"}
                               else "BLOCKED_OR_REVIEW_REQUIRED")
    result["physical_replication"] = "TOKEN_VAZIO_NOT_EXECUTED"
    result["rll_vs_lcdm"] = "NOT_APPLICABLE"
    return result


def fetch_one(directory, name, correct_md5):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    if path.exists():
        if digest(path)["md5"] != correct_md5:
            raise ValueError(f"existing data differs from pinned source: {name}; not overwritten")
        return
    url = f"https://zenodo.org/records/{RECORD}/files/{name}?download=1"
    tmp_path = None
    try:
        with urlopen(url, timeout=30) as response, tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=".download_", delete=False) as out:
            tmp_path = Path(out.name)
            count = 0
            for chunk in iter(lambda: response.read(65536), b""):
                count += len(chunk)
                if count > LIMIT_BYTES:
                    raise ValueError("source larger than safety bound")
                out.write(chunk)
        if digest(tmp_path)["md5"] != correct_md5:
            raise ValueError(f"source digest mismatch: {name}")
        # Never overwrite pre-existing data; a concurrent writer is a review gap.
        if path.exists():
            raise ValueError(f"destination appeared during fetch; not overwriting: {name}")
        os.replace(tmp_path, path)
        tmp_path = None
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data/real/relational_time/barontini_19651064")
    parser.add_argument("--fetch", action="store_true", help="opt-in external download with pinned integrity")
    parser.add_argument("--receipt", help="write audit JSON to explicit path (never overwrite existing receipt)")
    args = parser.parse_args(argv)
    failures = []
    if args.fetch:
        for name, md5 in FILES.items():
            try:
                fetch_one(args.data_dir, name, md5)
            except (OSError, ValueError, TimeoutError) as exc:
                failures.append({"file": name, "reason": str(exc)})
    report = audit(args.data_dir)
    if failures:
        report["fetch_failures"] = failures
        report["intake_status"] = "BLOCKED_OR_REVIEW_REQUIRED"
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        path = Path(args.receipt)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as out:
            out.write(encoded)
    print(encoded, end="")
    return 0 if report["intake_status"] == "PASS_SCOPED_INTEGRITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
