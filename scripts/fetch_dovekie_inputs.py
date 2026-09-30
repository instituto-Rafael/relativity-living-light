#!/usr/bin/env python3
"""Materialize and verify the official DES-Dovekie Hubble diagram + precision matrix.

The DES-Dovekie release stores STAT+SYS.npz as the *inverse covariance* (precision)
matrix in packed upper-triangular form.  This script preserves that semantic
boundary explicitly and never relabels the object as a covariance matrix.

Source objects are pinned by repository, immutable commit and Git blob SHA-1.
Runtime SHA-256 digests are recorded in the receipt and sidecars.  The large
scientific inputs are intended to stay outside Git; only compact receipts belong
in repository history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np

UPSTREAM_REPOSITORY = "des-science/DES-SN5YR"
UPSTREAM_COMMIT = "c9a4fcafc4cbd19bd750dee47fc76194a45c181f"
HD_PATH = "4_DISTANCES_COVMAT/DES-Dovekie_HD.csv"
PRECISION_PATH = "4_DISTANCES_COVMAT/STAT+SYS.npz"
OFFICIAL_LIKELIHOOD_PATH = "4_DISTANCES_COVMAT/DES-Dovekie-SN_Likelihood.py"
HD_GIT_BLOB_SHA1 = "f80ec4e2795edcbf3442f460c539bea56226027a"
PRECISION_GIT_BLOB_SHA1 = "4289666487f427782ec81c327ae7f7741f0f5fe5"
OFFICIAL_LIKELIHOOD_GIT_BLOB_SHA1 = "b7142093d633bf62281a2253d85ccc54db48431a"
EXPECTED_N = 1820
EXPECTED_PACKED_VALUES = EXPECTED_N * (EXPECTED_N + 1) // 2
HD_FILENAME = "DES-Dovekie_HD.csv"
PRECISION_FILENAME = "STAT+SYS.npz"
DEFAULT_OUTPUT_DIR = Path("data/real/cosmology/des_dovekie")
DEFAULT_RECEIPT = Path("artifacts/science/sn_modern/dovekie_materialization_receipt.json")


def raw_url(path: str) -> str:
    quoted = urllib.parse.quote(path, safe="/")
    return f"https://raw.githubusercontent.com/{UPSTREAM_REPOSITORY}/{UPSTREAM_COMMIT}/{quoted}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    size = path.stat().st_size
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".part", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def download_to(url: str, destination: Path, timeout: float = 180.0) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "RLL-Dovekie-Materializer/1",
            "Accept": "application/octet-stream",
        },
    )
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
        declared = response.headers.get("Content-Length")
        declared_bytes = int(declared) if declared else None
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            digest.update(chunk)
            total += len(chunk)
        output.flush()
        os.fsync(output.fileno())
    if declared_bytes is not None and declared_bytes != total:
        raise ValueError(f"download length mismatch: declared={declared_bytes} actual={total}")
    return {"bytes": total, "sha256": digest.hexdigest(), "declared_bytes": declared_bytes}


def inspect_hd(path: Path) -> dict[str, Any]:
    names: list[str] | None = None
    rows = 0
    zhd_index = zhel_index = mu_index = muerr_index = None
    min_z = math.inf
    max_z = -math.inf

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("VARNAMES:"):
                names = line.split()[1:]
                required = {"CID", "zHD", "zHEL", "MU", "MUERR"}
                missing = sorted(required.difference(names))
                if missing:
                    raise ValueError(f"HD VARNAMES missing columns: {missing}")
                zhd_index = names.index("zHD")
                zhel_index = names.index("zHEL")
                mu_index = names.index("MU")
                muerr_index = names.index("MUERR")
                continue
            if line.startswith("SN:"):
                if names is None:
                    raise ValueError(f"SN row before VARNAMES at line {line_number}")
                values = line.split()[1:]
                if len(values) != len(names):
                    raise ValueError(
                        f"HD row width mismatch at line {line_number}: {len(values)} != {len(names)}"
                    )
                zhd = float(values[int(zhd_index)])
                zhel = float(values[int(zhel_index)])
                mu = float(values[int(mu_index)])
                muerr = float(values[int(muerr_index)])
                if not all(math.isfinite(value) for value in (zhd, zhel, mu, muerr)):
                    raise ValueError(f"non-finite HD value at line {line_number}")
                if zhd <= 0.0 or zhel <= -1.0 or muerr <= 0.0:
                    raise ValueError(f"HD domain violation at line {line_number}")
                rows += 1
                min_z = min(min_z, zhd)
                max_z = max(max_z, zhd)
                continue
            raise ValueError(f"unsupported HD record at line {line_number}: {line[:32]!r}")

    if names is None:
        raise ValueError("HD file has no VARNAMES record")
    if rows != EXPECTED_N:
        raise ValueError(f"HD row count mismatch: {rows} != {EXPECTED_N}")
    return {
        "rows": rows,
        "columns": names,
        "zHD_min": min_z,
        "zHD_max": max_z,
        "ordering_semantics": "precision matrix order MUST follow this HD file",
    }


def load_precision(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with np.load(path, allow_pickle=False) as archive:
        files = list(archive.files)
        if len(files) < 2:
            raise ValueError(f"precision NPZ requires >=2 arrays, found {files}")
        n_array = np.asarray(archive[files[0]]).ravel()
        packed = np.asarray(archive[files[1]], dtype=float).ravel()
        if n_array.size < 1:
            raise ValueError("precision NPZ dimension array is empty")
        n = int(n_array[0])

    if n != EXPECTED_N:
        raise ValueError(f"precision dimension mismatch: {n} != {EXPECTED_N}")
    if packed.size != EXPECTED_PACKED_VALUES:
        raise ValueError(
            f"precision packed count mismatch: {packed.size} != {EXPECTED_PACKED_VALUES}"
        )
    if np.any(~np.isfinite(packed)):
        raise ValueError("precision matrix contains non-finite packed values")

    precision = np.zeros((n, n), dtype=float)
    upper = np.triu_indices(n)
    precision[upper] = packed
    lower = np.tril_indices(n, -1)
    precision[lower] = precision.T[lower]
    if np.any(np.diag(precision) <= 0.0):
        raise ValueError("precision diagonal must be strictly positive")
    try:
        np.linalg.cholesky(precision)
    except np.linalg.LinAlgError as exc:
        raise ValueError("precision matrix is not positive definite") from exc

    return precision, {
        "npz_arrays": files,
        "dimension": n,
        "packed_values": int(packed.size),
        "full_values": int(n * n),
        "finite_values": int(packed.size),
        "positive_diagonal": int(np.count_nonzero(np.diag(precision) > 0.0)),
        "matrix_semantics": "inverse_covariance_precision",
        "storage_semantics": "packed_upper_triangle",
        "symmetric_reconstruction": True,
        "positive_definite": True,
    }


def inspect_precision(path: Path) -> dict[str, Any]:
    _, diagnostics = load_precision(path)
    return diagnostics


def _materialize_one(url: str, final_path: Path, expected_blob_sha1: str) -> dict[str, Any]:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "wb", dir=final_path.parent, prefix=f".{final_path.name}.", suffix=".part", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        transfer = download_to(url, temporary)
        blob = git_blob_sha1(temporary)
        if blob != expected_blob_sha1:
            raise ValueError(
                f"Git blob SHA-1 mismatch for {final_path.name}: {blob} != {expected_blob_sha1}"
            )
        os.replace(temporary, final_path)
        _atomic_text(
            final_path.with_name(final_path.name + ".sha256"),
            f"{transfer['sha256']}  {final_path.name}\n",
        )
        return {**transfer, "git_blob_sha1": blob}
    finally:
        temporary.unlink(missing_ok=True)


def materialize(output_dir: Path, receipt_path: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    hd_path = output_dir / HD_FILENAME
    precision_path = output_dir / PRECISION_FILENAME
    errors: list[str] = []
    try:
        hd_transfer = _materialize_one(raw_url(HD_PATH), hd_path, HD_GIT_BLOB_SHA1)
        precision_transfer = _materialize_one(
            raw_url(PRECISION_PATH), precision_path, PRECISION_GIT_BLOB_SHA1
        )
        hd = inspect_hd(hd_path)
        precision = inspect_precision(precision_path)
        status = "PASS"
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
        status = "FAIL"
        hd_transfer = locals().get("hd_transfer", {})
        precision_transfer = locals().get("precision_transfer", {})
        hd = locals().get("hd", {})
        precision = locals().get("precision", {})

    receipt: dict[str, Any] = {
        "schema": "rll_dovekie_materialization_receipt_v1",
        "status": status,
        "state": "VERIFIED_INPUTS" if status == "PASS" else "BLOCKED_INPUTS",
        "claim_allowed": False,
        "publication_ready": False,
        "calibration_variant": "DES-Dovekie",
        "source": {
            "repository": UPSTREAM_REPOSITORY,
            "commit": UPSTREAM_COMMIT,
            "official_likelihood_path": OFFICIAL_LIKELIHOOD_PATH,
            "official_likelihood_git_blob_sha1": OFFICIAL_LIKELIHOOD_GIT_BLOB_SHA1,
            "license_status": "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND",
        },
        "hubble_diagram": {
            "path": HD_PATH,
            "url": raw_url(HD_PATH),
            "git_blob_sha1_expected": HD_GIT_BLOB_SHA1,
            "sha256": hd_transfer.get("sha256"),
            "bytes": hd_transfer.get("bytes"),
            **hd,
        },
        "precision_matrix": {
            "path": PRECISION_PATH,
            "url": raw_url(PRECISION_PATH),
            "git_blob_sha1_expected": PRECISION_GIT_BLOB_SHA1,
            "sha256": precision_transfer.get("sha256"),
            "bytes": precision_transfer.get("bytes"),
            **precision,
        },
        "policy": {
            "precision_is_covariance": False,
            "precision_is_inverse_covariance": True,
            "metadata_order_can_replace_hd_order": False,
            "large_inputs_committed_to_git": False,
            "runtime_sha256_sidecars_written": status == "PASS",
            "paper_or_repository_name_closes_likelihood_gate": False,
            "claim_allowed": False,
        },
        "token_vazio": [
            "TOKEN_VAZIO_EXPLICIT_REPOSITORY_LICENSE_NOT_FOUND",
            "TOKEN_VAZIO_DOVEKIE_THREE_MODEL_FIT" if status == "PASS" else "TOKEN_VAZIO_DOVEKIE_INPUTS",
        ],
        "errors": errors,
    }
    _atomic_text(receipt_path, json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if status != "PASS":
        raise RuntimeError("; ".join(errors))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()

    try:
        if args.verify_existing:
            hd_path = args.output_dir / HD_FILENAME
            precision_path = args.output_dir / PRECISION_FILENAME
            if git_blob_sha1(hd_path) != HD_GIT_BLOB_SHA1:
                raise ValueError("existing HD Git blob SHA-1 mismatch")
            if git_blob_sha1(precision_path) != PRECISION_GIT_BLOB_SHA1:
                raise ValueError("existing precision Git blob SHA-1 mismatch")
            hd = inspect_hd(hd_path)
            precision = inspect_precision(precision_path)
            result = {
                "schema": "rll_dovekie_existing_input_verification_v1",
                "status": "PASS",
                "claim_allowed": False,
                "hubble_diagram": {"sha256": sha256_file(hd_path), **hd},
                "precision_matrix": {"sha256": sha256_file(precision_path), **precision},
            }
            _atomic_text(args.receipt, json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            result = materialize(args.output_dir, args.receipt)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        f"PASS Dovekie n={result.get('hubble_diagram', {}).get('rows', EXPECTED_N)} "
        "matrix_semantics=inverse_covariance_precision claim_allowed=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
