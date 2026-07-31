from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CANONICAL_DATA_DIR = Path(
    "data/real/cosmology/pantheon_plus/"
    "Pantheon+_Data/4_DISTANCES_AND_COVAR"
)
CATALOG_FILENAME = "Pantheon+SH0ES.dat"
STAT_SYS_FILENAME = "Pantheon+SH0ES_STAT+SYS.cov"
STAT_ONLY_FILENAME = "Pantheon+SH0ES_STATONLY.cov"
CATALOG_SHA256 = "1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8"
CATALOG_SIZE_BYTES = 579_283
CATALOG_ROWS = 1_701
CATALOG_CALIBRATORS = 77
CATALOG_COSMO_ROWS = 1_624
EXPECTED_COVARIANCE_DIMENSION = 1_701
EXPECTED_COVARIANCE_VALUES = EXPECTED_COVARIANCE_DIMENSION**2
REQUIRED_HEADER_FIELDS = {
    "zHD",
    "MU_SH0ES",
    "MU_SH0ES_ERR_DIAG",
    "IS_CALIBRATOR",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_sha256_sidecar(path: Path) -> str | None:
    if not path.exists():
        return None
    tokens = path.read_text(encoding="utf-8").strip().split()
    if not tokens:
        return None
    value = tokens[0].lower()
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        return None
    return value


def _inspect_catalog(path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "file": CATALOG_FILENAME,
        "description": "Pantheon+SH0ES official distance/redshift table",
        "required_for_diagonal_diagnostic": True,
        "required_for_full_covariance_likelihood": True,
        "expected_size_bytes": CATALOG_SIZE_BYTES,
        "expected_sha256": CATALOG_SHA256,
        "status": "missing",
        "size_bytes": None,
        "sha256": None,
        "header_valid": False,
        "rows": 0,
        "calibrator_rows": 0,
        "cosmology_rows": 0,
    }
    if not path.exists():
        return entry

    entry["size_bytes"] = path.stat().st_size
    entry["sha256"] = _sha256(path)
    if entry["size_bytes"] != CATALOG_SIZE_BYTES:
        entry["status"] = "BLOCKED_CATALOG_SIZE"
        return entry
    if entry["sha256"] != CATALOG_SHA256:
        entry["status"] = "BLOCKED_CATALOG_SHA256"
        return entry

    with path.open(encoding="utf-8") as handle:
        header = handle.readline().split()
        indexes = {name: index for index, name in enumerate(header)}
        entry["header_valid"] = REQUIRED_HEADER_FIELDS.issubset(indexes)
        if not entry["header_valid"]:
            entry["status"] = "BLOCKED_CATALOG_HEADER"
            return entry
        calibrator_index = indexes["IS_CALIBRATOR"]
        rows = 0
        calibrators = 0
        for line in handle:
            if not line.strip():
                continue
            values = line.split()
            if len(values) <= calibrator_index:
                entry["status"] = "BLOCKED_CATALOG_ROW_WIDTH"
                return entry
            rows += 1
            try:
                is_calibrator = int(float(values[calibrator_index]))
            except ValueError:
                entry["status"] = "BLOCKED_CATALOG_CALIBRATOR_FIELD"
                return entry
            if is_calibrator == 1:
                calibrators += 1
            elif is_calibrator != 0:
                entry["status"] = "BLOCKED_CATALOG_CALIBRATOR_DOMAIN"
                return entry

    entry["rows"] = rows
    entry["calibrator_rows"] = calibrators
    entry["cosmology_rows"] = rows - calibrators
    if rows != CATALOG_ROWS:
        entry["status"] = "BLOCKED_CATALOG_ROW_COUNT"
    elif calibrators != CATALOG_CALIBRATORS:
        entry["status"] = "BLOCKED_CATALOG_CALIBRATOR_COUNT"
    elif entry["cosmology_rows"] != CATALOG_COSMO_ROWS:
        entry["status"] = "BLOCKED_CATALOG_COSMOLOGY_COUNT"
    else:
        entry["status"] = "READY_DIAGONAL_DIAGNOSTIC"
    return entry


def _count_covariance_values(path: Path) -> tuple[int | None, int]:
    dimension: int | None = None
    value_count = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle):
            tokens = line.split()
            if not tokens:
                continue
            if dimension is None:
                try:
                    dimension = int(tokens[0])
                except ValueError:
                    return None, 0
                tokens = tokens[1:]
            for token in tokens:
                try:
                    float(token)
                except ValueError:
                    return None, value_count
                value_count += 1
    return dimension, value_count


def _inspect_covariance(path: Path, description: str) -> dict[str, Any]:
    sidecar = path.with_name(path.name + ".sha256")
    entry: dict[str, Any] = {
        "file": path.name,
        "description": description,
        "required_for_diagonal_diagnostic": False,
        "required_for_full_covariance_likelihood": path.name == STAT_SYS_FILENAME,
        "status": "TOKEN_VAZIO_FULL_COVARIANCE" if path.name == STAT_SYS_FILENAME else "TOKEN_VAZIO_STAT_ONLY_COVARIANCE",
        "size_bytes": None,
        "sha256": None,
        "sha256_sidecar": sidecar.name,
        "expected_sha256": None,
        "checksum_verified": False,
        "matrix_dimension": None,
        "matrix_values": None,
    }
    if not path.exists():
        return entry

    entry["size_bytes"] = path.stat().st_size
    entry["sha256"] = _sha256(path)
    expected_sha256 = _read_sha256_sidecar(sidecar)
    entry["expected_sha256"] = expected_sha256
    if expected_sha256 is None:
        entry["status"] = "TOKEN_VAZIO_COVARIANCE_SHA256_POLICY"
        return entry
    if entry["sha256"] != expected_sha256:
        entry["status"] = "BLOCKED_COVARIANCE_SHA256"
        return entry
    entry["checksum_verified"] = True

    dimension, value_count = _count_covariance_values(path)
    entry["matrix_dimension"] = dimension
    entry["matrix_values"] = value_count
    if dimension != EXPECTED_COVARIANCE_DIMENSION:
        entry["status"] = "BLOCKED_COVARIANCE_DIMENSION"
    elif value_count != EXPECTED_COVARIANCE_VALUES:
        entry["status"] = "BLOCKED_COVARIANCE_VALUE_COUNT"
    else:
        entry["status"] = "READY_FULL_COVARIANCE" if path.name == STAT_SYS_FILENAME else "READY_STAT_ONLY_COVARIANCE"
    return entry


def _build_report(data_dir: Path) -> dict[str, Any]:
    catalog = _inspect_catalog(data_dir / CATALOG_FILENAME)
    stat_sys = _inspect_covariance(
        data_dir / STAT_SYS_FILENAME,
        "Pantheon+SH0ES combined statistical+systematic covariance matrix",
    )
    stat_only = _inspect_covariance(
        data_dir / STAT_ONLY_FILENAME,
        "Pantheon+SH0ES statistical-only covariance matrix",
    )
    files = [catalog, stat_sys, stat_only]

    diagonal_ready = catalog["status"] == "READY_DIAGONAL_DIAGNOSTIC"
    full_ready = diagonal_ready and stat_sys["status"] == "READY_FULL_COVARIANCE"
    if full_ready:
        route_state = "FULL_COVARIANCE_LIKELIHOOD_READY"
    elif diagonal_ready:
        route_state = "TOKEN_VAZIO_FULL_COVARIANCE"
    else:
        route_state = "BLOCKED_CATALOG"

    missing = [entry["file"] for entry in files if str(entry["status"]).startswith("TOKEN_VAZIO") or entry["status"] == "missing"]
    all_files_present = all(entry["size_bytes"] is not None for entry in files)
    all_files_verified = all(str(entry["status"]).startswith("READY_") for entry in files)

    return {
        "schema": "rll_pantheon_input_readiness_v2",
        "data_dir": str(data_dir),
        "route_state": route_state,
        "claim_allowed": False,
        "all_required_present": catalog["size_bytes"] is not None,
        "all_present": all_files_present,
        "all_verified": all_files_verified,
        "missing_required": [] if catalog["size_bytes"] is not None else [CATALOG_FILENAME],
        "missing": missing,
        "diagonal_diagnostic_ready": diagonal_ready,
        "full_covariance_likelihood_ready": full_ready,
        "catalog_rows": catalog["rows"],
        "catalog_calibrator_rows": catalog["calibrator_rows"],
        "catalog_cosmology_rows": catalog["cosmology_rows"],
        "files": files,
        "boundaries": {
            "diagonal_diagnostic_is_full_likelihood": False,
            "catalog_presence_is_covariance_presence": False,
            "covariance_requires_pinned_sha256": True,
            "full_likelihood_requires_stat_sys_covariance": True,
            "claim_allowed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify Pantheon+ catalog and full-covariance readiness"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=CANONICAL_DATA_DIR,
        help="Directory containing the official Pantheon+ distance/covariance files",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--require-diagonal-diagnostic",
        action="store_true",
        help="Fail unless the official catalog is hash-verified and structurally valid",
    )
    parser.add_argument(
        "--require-full-covariance",
        action="store_true",
        help="Fail unless STAT+SYS covariance exists, has a pinned sidecar hash, and has the expected shape",
    )
    args = parser.parse_args()

    report = _build_report(args.data_dir)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("[rll] Pantheon+ input readiness V2")
        print(f"data_dir={report['data_dir']}")
        print(f"route_state={report['route_state']}")
        print(f"diagonal_diagnostic_ready={str(report['diagonal_diagnostic_ready']).lower()}")
        print(f"full_covariance_likelihood_ready={str(report['full_covariance_likelihood_ready']).lower()}")
        print(f"claim_allowed={str(report['claim_allowed']).lower()}")
        for entry in report["files"]:
            print(
                f" - {entry['status']}: {entry['file']} "
                f"size={entry['size_bytes']} sha256={entry['sha256']}"
            )

    if not report["all_required_present"]:
        raise SystemExit(2)
    if args.require_full_covariance and not report["full_covariance_likelihood_ready"]:
        raise SystemExit(3)
    if args.require_diagonal_diagnostic and not report["diagonal_diagnostic_ready"]:
        raise SystemExit(4)


if __name__ == "__main__":
    main()
