#!/usr/bin/env python3
"""Fail-closed academic-intake validator for the Giza continuous research package.

This script inventories local RLL artifacts, validates citation/governance invariants,
and can optionally resolve DOI metadata through Crossref. It never promotes a
scientific or historical claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PACKAGE = Path("PapersPub/11_giza_continuous_archaeoastronomy")
REQUIRED_PACKAGE_FILES = [
    "draft.md",
    "references.md",
    "references.bib",
    "claim_state_ledger.md",
    "data_manifest.md",
    "reproducibility.md",
    "metadata/author_correspondence.yml",
]
REQUIRED_DOIS = {
    "10.1038/35042510",
    "10.1038/35089138",
    "10.1038/35089140",
    "10.1177/002182860103202601",
    "10.1177/002182860703800204",
    "10.1002/rob.21451",
    "10.5913/jarce.56.2020.a008",
    "10.1051/0004-6361:20031539",
    "10.1051/0004-6361/201117274",
    "10.1051/0004-6361/201117274e",
}
MANDATORY_ADVERSARIES = {
    "Rawlins",
    "Pickering",
    "Belmonte",
    "Wall",
    "Sakovich",
}
KEYWORDS = {
    "giza",
    "khufu",
    "shaft",
    "precession",
    "toro",
    "torus",
    "toroidal",
    "geodesic",
    "icosphere",
    "poincare",
    "poincaré",
}
SCAN_ROOTS = [Path("PapersPub"), Path("docs"), Path("data"), Path("results")]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".yml", ".yaml", ".csv", ".bib", ".cff", ".py"}
MAX_SCAN_BYTES = 2_000_000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_doi(value: str) -> str:
    return value.strip().rstrip(".,;)").lower()


def extract_dois(text: str) -> set[str]:
    pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.I)
    return {normalize_doi(m.group(0)) for m in pattern.finditer(text)}


def scan_artifacts(root: Path) -> list[dict]:
    rows: list[dict] = []
    for relroot in SCAN_ROOTS:
        base = root / relroot
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                size = path.stat().st_size
                if size > MAX_SCAN_BYTES:
                    continue
                text = read_text(path)
            except OSError:
                continue
            lowered = text.lower()
            hits = sorted(k for k in KEYWORDS if k in lowered)
            if hits:
                rows.append(
                    {
                        "path": str(path.relative_to(root)),
                        "bytes": size,
                        "sha256": sha256_file(path),
                        "keywords": hits,
                    }
                )
    rows.sort(key=lambda x: x["path"])
    return rows


def crossref_lookup(doi: str) -> dict:
    encoded = urllib.parse.quote(doi, safe="")
    url = f"https://api.crossref.org/works/{encoded}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "RLLAcademicIntake/1.0 (mailto:repository-maintainer@example.invalid)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        msg = payload.get("message", {})
        authors = []
        for a in msg.get("author", []) or []:
            authors.append(
                {
                    "given": a.get("given"),
                    "family": a.get("family"),
                    "orcid": a.get("ORCID"),
                }
            )
        return {
            "state": "RESOLVED",
            "doi": msg.get("DOI", doi),
            "title": (msg.get("title") or [None])[0],
            "container_title": (msg.get("container-title") or [None])[0],
            "publisher": msg.get("publisher"),
            "type": msg.get("type"),
            "authors": authors,
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "state": "TOKEN_VAZIO_NETWORK_METADATA",
            "doi": doi,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--online-crossref", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    package = root / PACKAGE
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    warnings: list[str] = []
    inventory: list[dict] = []

    for rel in REQUIRED_PACKAGE_FILES:
        path = package / rel
        if not path.is_file():
            errors.append(f"missing_required_file:{PACKAGE / rel}")
            continue
        inventory.append(
            {
                "path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    package_text = "\n".join(read_text(package / f) for f in REQUIRED_PACKAGE_FILES if (package / f).is_file())
    found_dois = extract_dois(package_text)
    missing_dois = sorted(d for d in REQUIRED_DOIS if d.lower() not in found_dois)
    if missing_dois:
        errors.append("missing_required_dois:" + ",".join(missing_dois))

    refs_text = read_text(package / "references.md") if (package / "references.md").is_file() else ""
    missing_adversaries = sorted(a for a in MANDATORY_ADVERSARIES if a.lower() not in refs_text.lower())
    if missing_adversaries:
        errors.append("missing_mandatory_adversaries:" + ",".join(missing_adversaries))

    compact = re.sub(r"\s+", "", package_text).lower()
    if "claim_allowed=true" in compact:
        errors.append("claim_inflation:claim_allowed=true")
    if "publication_allowed=true" in compact:
        errors.append("claim_inflation:publication_allowed=true")

    required_boundaries = [
        "preprint != peer_review",
        "same_number != same_object",
        "4 physical != 8 projected",
    ]
    for boundary in required_boundaries:
        if boundary.lower().replace(" ", "") not in compact:
            warnings.append(f"boundary_not_literal:{boundary}")

    local_artifacts = scan_artifacts(root)

    crossref = []
    if args.online_crossref:
        for doi in sorted(REQUIRED_DOIS):
            crossref.append(crossref_lookup(doi))
            time.sleep(0.15)

    report = {
        "schema": "rll.giza_academic_intake.report.v1",
        "claim_allowed": False,
        "scientific_validation": False,
        "package": str(PACKAGE),
        "status": "PASS_GOVERNANCE" if not errors else "FAIL_GOVERNANCE",
        "errors": errors,
        "warnings": warnings,
        "required_file_inventory": inventory,
        "required_dois": sorted(REQUIRED_DOIS),
        "found_dois": sorted(found_dois),
        "local_related_artifacts": local_artifacts,
        "online_crossref": crossref,
        "boundaries": [
            "workflow PASS != archaeological validation",
            "DOI resolved != paper claim correct",
            "preprint != peer review",
            "citation != endorsement",
            "same number != same object",
            "four physical shafts != eight projected rays",
        ],
        "f_gap": [
            "TOKEN_VAZIO_GIZA_4SHAFT_CENTERLINES",
            "TOKEN_VAZIO_GIZA_SURVEY_UNCERTAINTY",
            "TOKEN_VAZIO_VIXRA_SOURCE_BINDING",
            "TOKEN_VAZIO_HISTORICAL_SKY_EXECUTION",
            "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
        ],
        "f_next": "source-bind shaft geometry -> historical astrometry -> full-star control -> adversarial comparison -> independent replication",
    }

    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings), "related_artifacts": len(local_artifacts)}))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
