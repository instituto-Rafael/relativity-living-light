#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import requests

DEFAULT_OUTPUT_DIR = "artifacts/rll-real-run"
LATENTES_OUTPUT_DIR = "artifacts/rll_latentes"

# These are the committed real inputs consumed by the joint cosmology route.
# Keep observables separate: IML receives H(z) only, while Structure-D consumes
# the complete set through data/real/cosmology/real_cosmology_inputs.yml.
CURATED_LOCAL_REAL: dict[str, Path] = {
    "Hz_data_real.csv": Path("data/real/Hz_data_real.csv"),
    "desi_dr2_bao_primary_points.csv": Path(
        "data/real/cosmology/desi_dr2_bao_primary_points.csv"
    ),
    "desi_dr2_bao_covariance_summary.csv": Path(
        "data/real/cosmology/desi_dr2_bao_covariance_summary.csv"
    ),
    "fsigma8_growth_real.csv": Path(
        "data/real/cosmology/fsigma8_growth_real.csv"
    ),
    "CMB_shift_real.json": Path("data/real/CMB_shift_real.json"),
}

SOURCES: dict[str, dict[str, Any]] = {
    "igrf14": {
        "group": "geomagnetic",
        "url": "https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field",
        "license": "NOAA public data",
        "version": "IGRF14",
        "heavy": False,
    },
    "wmm2025": {
        "group": "geomagnetic",
        "url": "https://www.ncei.noaa.gov/index.php/products/world-magnetic-model/wmm-coefficients",
        "license": "NOAA public data",
        "version": "WMM2025",
        "heavy": False,
    },
    "omni": {
        "group": "heliophysics",
        "url": "https://omniweb.gsfc.nasa.gov/",
        "license": "NASA open data",
        "version": "OMNI/SPDF",
        "heavy": False,
    },
    "nmdb": {
        "group": "heliophysics",
        "url": "https://www.nmdb.eu/",
        "license": "NMDB terms",
        "version": "current",
        "heavy": False,
    },
    "desi": {
        "group": "cosmology",
        "url": "https://data.desi.lbl.gov/",
        "license": "DESI data policy",
        "version": "DR2",
        "heavy": True,
        "manual_reason": "DESI bulk data are large and should be selected from the data portal before materialization.",
    },
    "pantheon": {
        "group": "cosmology",
        "url": "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/README.md",
        "license": "repository license",
        "version": "DataRelease",
        "heavy": False,
    },
    "planck": {
        "group": "cosmology",
        "url": "https://pla.esac.esa.int/",
        "license": "ESA PLA terms",
        "version": "Planck Legacy",
        "heavy": True,
        "manual_reason": "Planck archive products are large and product-specific; select products in ESA PLA before download.",
    },
    "spenvis_reference": {
        "group": "heliophysics",
        "url": "https://www.spenvis.oma.be/",
        "license": "SPENVIS terms",
        "version": "reference",
        "heavy": True,
        "manual_reason": "SPENVIS workflows require portal/session configuration before exporting data.",
    },
    "desi_dr2_bao_supplement_2025": {
        "group": "cosmology",
        "url": "https://data.desi.lbl.gov/doc/releases/dr2/",
        "license": "DESI data policy",
        "version": "DR2 BAO 2025",
        "heavy": True,
        "manual_reason": "DESI DR2 supplemental products are large and analysis-specific; select the required release files before materialization.",
    },
    "desi_dr2_publications_2025_2026": {
        "group": "cosmology",
        "url": "https://data.desi.lbl.gov/doc/releases/dr2/",
        "license": "DESI data policy",
        "version": "DR2 publications 2025-2026",
        "heavy": True,
        "manual_reason": "Publication-specific DESI DR2 products should be selected from the release documentation before materialization.",
    },
    "atlas_13tev_education_2020": {
        "group": "particle_physics",
        "url": "https://opendata.atlas.cern/docs/data/for_education/13TeV_details",
        "license": "ATLAS Open Data terms",
        "version": "13 TeV education 2020",
        "heavy": True,
        "manual_reason": "ATLAS Open Data ROOT samples are large; choose datasets with CERN Open Data tooling before download.",
    },
    "lvk_gwtc_5_2026": {
        "group": "gravitational_wave_physics",
        "url": "https://ligo.org/gwtc-5-0-updated-ligo-virgo-kagra-catalog-sets-new-records-in-precision-gravitational-wave-astronomy/",
        "license": "GWOSC/LVK terms for associated data products",
        "version": "GWTC-5.0 2026 announcement",
        "heavy": True,
        "manual_reason": "GWTC-5 data products should be materialized from the linked GWOSC/LVK release assets once the desired files are selected.",
    },
    "euclid_q1_data_release_2025": {
        "group": "cosmology",
        "url": "https://www.euclid-ec.org/science/q1/",
        "access_url": "https://eas.esac.esa.int/sas",
        "license": "ESA/Euclid/NASA-IPAC archive terms",
        "version": "Euclid Q1 2025",
        "heavy": True,
        "manual_reason": "Euclid Q1 products are exposed through ESA Euclid Science Archive/IPAC selection workflows; choose catalogues, cutouts or files in the portal before local materialization.",
    },
    "human_cell_atlas_portal_2026": {
        "group": "biology_biomedicine",
        "url": "https://data.humancellatlas.org/",
        "license": "HCA portal/project-specific terms",
        "version": "portal snapshot 2026",
        "heavy": True,
        "manual_reason": "HCA datasets are project-specific and large; select projects/files and honor per-project terms before download.",
    },
    "wwpdb_core_archive_2026": {
        "group": "chemistry_structural_biology",
        "url": "https://www.wwpdb.org/",
        "license": "wwPDB public archive terms",
        "version": "core archive 2026",
        "heavy": True,
        "manual_reason": "wwPDB bulk archive materialization should be scoped to selected structures or mirrors before download.",
    },
    "openneuro_bids_portal_2026": {
        "group": "neuroscience",
        "url": "https://docs.openneuro.org/",
        "license": "dataset-specific OpenNeuro terms",
        "version": "portal snapshot 2026",
        "heavy": True,
        "manual_reason": "OpenNeuro requires choosing a concrete dataset id before running the download command.",
    },
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def fetch_text(url: str, out: Path) -> tuple[str, str | None]:
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        out.write_bytes(r.content)
        return "fetched", None
    except Exception as e:
        return "fetch_failed", str(e)


def fetch_csv(url: str, out: Path) -> tuple[str, str | None]:
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)
        # sanity check
        with out.open("r", encoding="utf-8", errors="replace") as fh:
            sample = fh.read(2048)
        if "," not in sample and "\t" not in sample:
            return "fetch_failed", "downloaded file is not a recognizable table"
        return "fetched", None
    except Exception as e:
        return "fetch_failed", str(e)


def source_destination(root: Path, name: str) -> Path:
    return root / "raw" / name


def write_manifest(root: Path, source_dir: Path, rec: dict[str, Any]) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "manifest.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")


def materialize_source(root: Path, name: str, cfg: dict[str, Any], mode: str) -> tuple[dict[str, Any], bool]:
    run_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    rec: dict[str, Any] = {"source": name, **cfg, "run_utc": run_utc}
    d = source_destination(root, name)
    d.mkdir(parents=True, exist_ok=True)
    failed = False

    if mode == "metadata_only":
        rec["status"] = "metadata_only"
    elif cfg["heavy"]:
        rec["status"] = "manual_materialization_required"
        rec["reason"] = cfg.get("manual_reason", "Source requires manual selection or a large download workflow before materialization.")
    else:
        out = d / "payload.bin"
        st, err = fetch_text(cfg["url"], out)
        rec["status"] = st
        if st == "fetched":
            rec["files"] = [{"path": str(out.relative_to(root)), "sha256": sha256_file(out)}]
        else:
            rec["error"] = err
            failed = True

    write_manifest(root, d, rec)
    return rec, failed


def build_parser() -> argparse.ArgumentParser:
    groups = sorted({cfg["group"] for cfg in SOURCES.values()} | {"all"})
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-group", default="all", choices=groups)
    ap.add_argument("--source", choices=sorted(SOURCES), help="Materialize or mark one specific source_id from the source catalog.")
    ap.add_argument("--mode", default="full", choices=["metadata_only", "fetch", "compute", "plots", "full"])
    ap.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    for k in SOURCES:
        ap.add_argument(f"--fetch-{k.replace('_', '-')}", action="store_true")
        ap.add_argument(f"--no-fetch-{k.replace('_', '-')}", dest=f"fetch_{k}", action="store_false")
        ap.set_defaults(**{f"fetch_{k}": True if k in ["igrf14", "wmm2025", "omni", "desi", "pantheon"] else False})
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.source and a.output_dir == DEFAULT_OUTPUT_DIR:
        a.output_dir = LATENTES_OUTPUT_DIR

    root = Path(a.output_dir)
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    selected_groups = [a.dataset_group] if a.dataset_group != "all" else sorted({cfg["group"] for cfg in SOURCES.values()})
    results = []
    failed = []

    for name, cfg in SOURCES.items():
        if a.source and name != a.source:
            continue
        if not a.source:
            if cfg["group"] not in selected_groups:
                continue
            if not getattr(a, f"fetch_{name}"):
                continue
        rec, did_fail = materialize_source(root, name, cfg, a.mode)
        results.append(rec)
        if did_fail:
            failed.append(name)

    # Cosmology lightweight curated pulls for direct pipeline use. Skip this when a
    # single --source was requested so the command maps exactly to one catalog target.
    curated = []
    if not a.source and "cosmology" in selected_groups and a.mode in ("fetch", "full", "compute"):
        curated_dir = raw / "cosmology_curated"
        curated_dir.mkdir(parents=True, exist_ok=True)
        curated_urls = {
            "pantheon_readme.md": "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/README.md",
            "desi_dr2_results_i_arxiv.html": "https://arxiv.org/abs/2503.14738",
        }
        for fname, url in curated_urls.items():
            target = curated_dir / fname
            status, err = fetch_text(url, target)
            item = {"name": fname, "url": url, "status": status}
            if status == "fetched":
                item["sha256"] = sha256_file(target)
            else:
                item["error"] = err
            curated.append(item)

        # mirror current repo-ready real data into artifact to unify YAML outputs
        for fname, src in CURATED_LOCAL_REAL.items():
            if src.exists():
                dst = curated_dir / fname
                dst.write_bytes(src.read_bytes())
                curated.append({"name": fname, "source": str(src), "status": "copied_from_repo", "sha256": sha256_file(dst)})
            else:
                curated.append({"name": fname, "source": str(src), "status": "missing_in_repo"})

        with (curated_dir / "CURATED_SOURCES.json").open("w", encoding="utf-8") as fh:
            json.dump(curated, fh, indent=2, ensure_ascii=False)

        with (curated_dir / "CURATED_SOURCES.md").open("w", encoding="utf-8") as fh:
            fh.write("# CURATED_SOURCES\n\n")
            fh.write("|name|status|origin|\n|---|---|---|\n")
            for item in curated:
                origin = item.get("url") or item.get("source", "-")
                fh.write(f"|{item['name']}|{item['status']}|{origin}|\n")

    (raw / "SOURCES.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    ds = ["# DATA_SOURCES", "", "|source|group|version|status|url|", "|---|---|---|---|---|"]
    fr = ["# FETCH_REPORT", "", f"mode: `{a.mode}`"]
    for r in results:
        ds.append(f"|{r['source']}|{r['group']}|{r['version']}|{r['status']}|{r['url']}|")
        fr.append(f"- {r['source']}: {r['status']}")
        if "reason" in r:
            fr.append(f"  - reason: {r['reason']}")
    (root / "DATA_SOURCES.md").write_text("\n".join(ds), encoding="utf-8")
    (root / "FETCH_REPORT.md").write_text("\n".join(fr), encoding="utf-8")
    if a.mode == "compute" and any(x in failed for x in ["omni", "pantheon"]):
        raise SystemExit("Essential data missing for compute mode: omni/pantheon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
