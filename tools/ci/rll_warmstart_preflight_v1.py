#!/usr/bin/env python3
"""RLL G4->G5 baseline preflight: audit-only unless official covariance is pinned.

No cosmological likelihood is evaluated here; G4/G5 own the actual calculation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = "NOVOexport/legacy-workflows/20261107/workflows_index.json"
CONTRACT = "data/contracts/rll_baseline_warmstart.v1.json"
G4 = "data/contracts/rll_g4_background_tournament.v1.json"
PARAMS = "data/inputs/cosmology_joint/parameter_origin_registry.json"
DESI = "data/real/cosmology/desi_bao_dr2_cobaya/MANIFEST.json"
PANTHEON = "data/real/cosmology/pantheon_plus/MANIFEST.json"
COV = "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov"
MATERIALIZED = "results/audit/warmstart_pantheon_cov_receipt.json"
SEVEN = ("omega_b", "omega_c", "theta_star", "ln10As", "ns", "tau", "w")
SIX = ("LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL")


def load(root, path):
    return json.loads((root / path).read_text(encoding="utf8"))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_sha1(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def archive_gate(root):
    archive = load(root, INDEX)
    entries = archive.get("entries", [])
    errors = []
    if archive.get("workflow_count") != 133 or len(entries) != 133:
        errors.append("ARCHIVE_COUNT_NOT_133")
    if len({e["original_path"] for e in entries}) != len(entries):
        errors.append("ARCHIVE_PATH_DUPLICATED")
    for e in entries:
        path = root / e["archive_path"]
        if not path.is_file():
            errors.append("ARCHIVE_MISSING:" + e["archive_path"])
        elif path.stat().st_size != e["size_bytes"] or blob_sha1(path) != e["blob_sha1"]:
            errors.append("ARCHIVE_GIT_BLOB_MISMATCH:" + e["archive_path"])
    return len(entries), errors


def check_covariance(cov):
    if len(cov) != 13 or any(len(row) != 13 for row in cov):
        raise ValueError("covariance must be 13x13")
    lower = [[0.0] * 13 for _ in range(13)]
    for i in range(13):
        for j in range(i + 1):
            v = cov[i][j]
            if not math.isfinite(v) or abs(v - cov[j][i]) > 1e-10:
                raise ValueError("covariance not symmetric finite")
            tmp = v - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if tmp <= 0:
                    raise ValueError("covariance not positive-definite")
                lower[i][j] = math.sqrt(tmp)
            else:
                lower[i][j] = tmp / lower[j][j]


def preflight(root=ROOT, require_materialized=False):
    errors = []
    gaps = []
    hashes = {}
    _, archive_errors = archive_gate(root)
    errors.extend(archive_errors)
    config, g4 = load(root, CONTRACT), load(root, G4)
    desi, pantheon = load(root, DESI), load(root, PANTHEON)
    params = load(root, PARAMS)
    if config["claim_allowed"] is not False or config["merge_allowed"] is not False:
        errors.append("POLICY_CLAIM_OR_MERGE_PROMOTION")
    spec = config["existing_execution"]
    if list(g4["models"]) != list(SIX) or g4["claim_allowed"] is not False:
        errors.append("G4_MODEL_OR_POLICY_MISMATCH")
    if spec["models"] != list(SIX) or spec["seeds"] != g4["seeds"]:
        errors.append("G4_SEEDS_OR_MODELS_REWRITTEN")
    if config["parameters"]["wCDM_seven_standard"] != list(SEVEN):
        errors.append("SEVEN_PARAM_DEFINITION_CHANGED")
    if set(SEVEN) - {p["name"] for p in params["parameters"]}:
        errors.append("PARAMETER_SOURCE_MISSING")
    if config["parameters"]["seven_parameter_fit"] != "TOKEN_VAZIO_FULL_CMB_LIKELIHOOD_REQUIRED":
        errors.append("CMB_SEVEN_PARAM_FALSE_PROMOTION")

    official = [p for p in desi.get("files", []) if p.get("subset") == "ALL"]
    if len(official) != 2:
        errors.append("DESI_REQUIRED_TWO_ALL_FILES")
    for entry in official:
        path = root / entry["local_file"]
        if not path.is_file():
            errors.append("DESI_FILE_MISSING:" + entry["local_file"])
        elif (path.stat().st_size != entry["local_bytes"]
              or digest(path) != entry["local_sha256"]):
            errors.append("DESI_FILE_HASH_MISMATCH:" + entry["local_file"])
        else:
            hashes[entry["local_file"]] = entry["local_sha256"]

    mean_path = root / "data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_mean.tsv"
    cov_path = root / "data/real/cosmology/desi_bao_dr2_cobaya/desi_gaussian_bao_ALL_GCcomb_cov.tsv"
    if mean_path.is_file() and cov_path.is_file():
        try:
            dat = [x.split() for x in mean_path.read_text().splitlines()[1:] if x.strip()]
            if len(dat) != 13 or any(len(row) != 3 for row in dat):
                raise ValueError("not 13 observed quantities")
            if any(x[2] not in {"DH_over_rs", "DM_over_rs", "DV_over_rs"} for x in dat):
                raise ValueError("unexpected BAO observable")
            matrix = [[float(w) for w in ln.split()] for ln in cov_path.read_text().splitlines() if ln.strip()]
            check_covariance(matrix)
        except ValueError as ex:
            errors.append("DESI_13X13_COVARIANCE:" + str(ex))
    else:
        errors.append("DESI_DATA_INCOMPLETE")

    catalog_relative = "Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"
    item = next((e for e in pantheon.get("files", []) if e["path"] == catalog_relative), None)
    cat_path = root / "data/real/cosmology/pantheon_plus" / catalog_relative
    if item is None or not cat_path.is_file():
        errors.append("PANTHEON_CATALOG_NOT_MATERIALIZED")
    elif cat_path.stat().st_size != item["size_bytes"] or digest(cat_path) != item["sha256"]:
        errors.append("PANTHEON_CATALOG_HASH_MISMATCH")
    else:
        hashes[str(cat_path.relative_to(root))] = item["sha256"]

    cov = root / COV
    receipt_path = root / MATERIALIZED
    if require_materialized:
        if not cov.is_file() or not receipt_path.is_file():
            errors.append("PANTHEON_FULL_COVARIANCE_RECEIPT_REQUIRED")
        else:
            receipt = load(root, MATERIALIZED)
            if (receipt.get("status") != "PASS"
                or receipt.get("artifact", {}).get("sha256") != digest(cov)
                or receipt.get("policy", {}).get("full_covariance_likelihood_ready") is not True):
                errors.append("PANTHEON_FULL_COVARIANCE_PINNED_GATE")
            else:
                hashes[COV] = digest(cov)
    elif not cov.is_file():
        gaps.append("TOKEN_VAZIO_PANTHEON_FULL_COVARIANCE_PENDING_MANUAL")
    else:
        gaps.append("PANTHEON_COV_PRESENT_PINNED_VERIFICATION_NOT_RUN")

    for key in (CONTRACT, G4, DESI, PANTHEON, PARAMS):
        hashes[key] = digest(root / key)

    return {"schema": "rll.baseline_warmstart_preflight_receipt.v1",
            "state": "PASS_SCOPED_DATA_PREFLIGHT" if not errors else "BLOCKED_PREWARM_INPUT",
            "archive_checked": 133,
            "models": list(SIX), "seven_parameter_names": list(SEVEN),
            "seven_parameter_fit": "NOT_RUN_REQUIRES_FULL_CMB",
            "cosmology_fitting_executed": False, "claim_allowed": False,
            "sources_sha256": hashes, "gaps": gaps, "errors": errors}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--output", type=Path)
    p.add_argument("--archive-only", action="store_true")
    p.add_argument("--require-materialized", action="store_true")
    args = p.parse_args()
    if args.archive_only:
        n, failures = archive_gate(args.root)
        result = {"schema": "rll.archive_check.v1", "count": n, "errors": failures,
                  "claim_allowed": False,
                  "state": "PASS_SCOPED_ARCHIVE" if not failures else "BLOCKED_ARCHIVE"}
    else:
        result = preflight(args.root, args.require_materialized)
    data = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf8")
    print(data)
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
