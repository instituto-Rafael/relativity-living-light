#!/usr/bin/env python3
"""Scan RLL likelihood outputs for evidence, stability and claim boundaries.

This scanner answers a narrow question: from an already generated results CSV,
what can be calculated with high confidence without inventing new physics?

It computes:
- AIC/AICc/BIC rankings and deltas;
- RLL deltas relative to CPL/w0waCDM when present;
- consistency of N, k and dof;
- suspicious shared/boundary-like H0 behavior;
- RLL authorial-parameter collapse diagnostics;
- claim_status based only on observable metadata in the result table.

It does not claim that RLL is physically true. It only reports whether the
current data/result table favors, disfavors, or blocks claims under the declared
operational policy.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "structure_d" / "joint_real_likelihood.csv"
DEFAULT_REGISTRY = ROOT / "data" / "inputs" / "cosmology_joint" / "parameter_origin_registry.json"
DEFAULT_JSON_OUT = ROOT / "results" / "audit" / "rll_model_evidence_scan.json"
DEFAULT_MD_OUT = ROOT / "results" / "audit" / "rll_model_evidence_scan.md"

REQUIRED_MODELS = {
    "LCDM": "LCDM",
    "wCDM": "wCDM",
    "CPL": "CPL",
    "RLL": "RLL",
}

INFORMATION_COLUMNS = ("chi2", "AIC", "AICc", "BIC")
COMPONENT_PREFIX = "chi2_"
EPS = 1e-10


@dataclass
class ModelScan:
    model: str
    row_name: str
    chi2: float | None
    AIC: float | None
    AICc: float | None
    BIC: float | None
    N: int | None
    k: int | None
    dof: int | None
    dof_consistent: bool | None
    delta_AICc_best: float | None
    delta_BIC_best: float | None
    delta_AICc_CPL: float | None
    delta_BIC_CPL: float | None
    H0: float | None
    Os0: float | None
    zt: float | None
    wt: float | None
    component_chi2: dict[str, float]
    local_flags: list[str]


@dataclass
class EvidenceScan:
    input_csv: str
    registry: str
    registry_schema: str | None
    commit_sha: str | None
    row_count: int
    models_present: list[str]
    missing_required_model_classes: list[str]
    best_by_AICc: str | None
    best_by_BIC: str | None
    H0_all_equal: bool | None
    H0_values: list[float]
    claim_status: str
    claim_summary: str
    blocking_reasons: list[str]
    warnings: list[str]
    model_scans: list[ModelScan]


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    try:
        val = float(text)
    except ValueError:
        return None
    if math.isnan(val) or math.isinf(val):
        return None
    return val


def parse_int(value: Any) -> int | None:
    val = parse_float(value)
    if val is None:
        return None
    if abs(val - round(val)) > 1e-9:
        return None
    return int(round(val))


def model_class(name: str) -> str:
    upper = name.upper()
    if "CPL" in upper or "W0WA" in upper:
        return "CPL"
    if "WCDM" in upper:
        return "wCDM"
    if "RLL" in upper:
        return "RLL"
    if "LCDM" in upper or "ΛCDM" in name:
        return "LCDM"
    return name


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"FAIL: input CSV not found: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_registry_schema(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data.get("schema") if isinstance(data, dict) else None


def git_sha() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def min_model(rows: list[dict[str, str]], column: str) -> dict[str, str] | None:
    scored = [(parse_float(row.get(column)), row) for row in rows]
    scored = [(score, row) for score, row in scored if score is not None]
    if not scored:
        return None
    return min(scored, key=lambda item: item[0])[1]


def find_cpl_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    cpl_rows = [row for row in rows if model_class(row.get("model", "")) == "CPL"]
    if not cpl_rows:
        return None
    return min(cpl_rows, key=lambda row: parse_float(row.get("AICc")) or float("inf"))


def finite_values(rows: Iterable[dict[str, str]], column: str) -> list[float]:
    out: list[float] = []
    for row in rows:
        val = parse_float(row.get(column))
        if val is not None:
            out.append(val)
    return out


def collect_components(row: dict[str, str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in row.items():
        if key.startswith(COMPONENT_PREFIX):
            parsed = parse_float(value)
            if parsed is not None:
                out[key] = parsed
    return out


def scan(input_csv: Path, registry: Path) -> EvidenceScan:
    rows = read_csv(input_csv)
    registry_schema = read_registry_schema(registry)
    commit = git_sha()

    present_classes = sorted({model_class(row.get("model", "")) for row in rows})
    missing = sorted(set(REQUIRED_MODELS) - set(present_classes))

    best_aicc_row = min_model(rows, "AICc")
    best_bic_row = min_model(rows, "BIC")
    cpl_row = find_cpl_row(rows)
    best_aicc = parse_float(best_aicc_row.get("AICc")) if best_aicc_row else None
    best_bic = parse_float(best_bic_row.get("BIC")) if best_bic_row else None
    cpl_aicc = parse_float(cpl_row.get("AICc")) if cpl_row else None
    cpl_bic = parse_float(cpl_row.get("BIC")) if cpl_row else None

    h0_values = finite_values(rows, "H0")
    h0_all_equal = None
    if h0_values:
        h0_all_equal = max(h0_values) - min(h0_values) <= EPS

    warnings: list[str] = []
    blocking: list[str] = []

    if missing:
        blocking.append(f"missing required baseline model classes: {', '.join(missing)}")
    if registry_schema is None:
        blocking.append("parameter registry schema unavailable or invalid")
    if cpl_row is None:
        blocking.append("CPL/w0waCDM baseline absent; RLL cannot be interpreted against the DESI-era standard dynamic-DE baseline")
    if h0_all_equal is True:
        warnings.append(
            "H0_all_equal=True: H0 is identical across all model rows — "
            "check for fixed prior, hard clamp or optimizer boundary. "
            "This is an operational warning that prevents strong claims until H0/r_d ablation "
            "is executed (see data/inputs/cosmology_joint/h0_rd_ablation_matrix.json)."
        )

    model_scans: list[ModelScan] = []
    rll_scan: ModelScan | None = None

    for row in rows:
        row_name = row.get("model", "")
        klass = model_class(row_name)
        n_val = parse_int(row.get("N"))
        k_val = parse_int(row.get("k"))
        dof_val = parse_int(row.get("dof"))
        dof_ok = None
        if n_val is not None and k_val is not None and dof_val is not None:
            dof_ok = (n_val - k_val == dof_val)

        aicc = parse_float(row.get("AICc"))
        bic = parse_float(row.get("BIC"))
        local_flags: list[str] = []
        if dof_ok is False:
            local_flags.append("N-k-dof mismatch")
        if klass == "RLL":
            os0 = parse_float(row.get("Os0"))
            if os0 is not None and abs(os0) <= EPS:
                local_flags.append("RLL authorial amplitude Os0 collapsed to zero")
            if aicc is not None and cpl_aicc is not None and aicc > cpl_aicc:
                local_flags.append("RLL AICc worse than CPL")
            if bic is not None and cpl_bic is not None and bic > cpl_bic:
                local_flags.append("RLL BIC worse than CPL")

        scan_row = ModelScan(
            model=klass,
            row_name=row_name,
            chi2=parse_float(row.get("chi2")),
            AIC=parse_float(row.get("AIC")),
            AICc=aicc,
            BIC=bic,
            N=n_val,
            k=k_val,
            dof=dof_val,
            dof_consistent=dof_ok,
            delta_AICc_best=(aicc - best_aicc) if aicc is not None and best_aicc is not None else None,
            delta_BIC_best=(bic - best_bic) if bic is not None and best_bic is not None else None,
            delta_AICc_CPL=(aicc - cpl_aicc) if aicc is not None and cpl_aicc is not None else None,
            delta_BIC_CPL=(bic - cpl_bic) if bic is not None and cpl_bic is not None else None,
            H0=parse_float(row.get("H0")),
            Os0=parse_float(row.get("Os0")),
            zt=parse_float(row.get("zt")),
            wt=parse_float(row.get("wt")),
            component_chi2=collect_components(row),
            local_flags=local_flags,
        )
        model_scans.append(scan_row)
        if klass == "RLL":
            rll_scan = scan_row

    if any(ms.dof_consistent is False for ms in model_scans):
        blocking.append("at least one model row has inconsistent N-k-dof")

    claim_status = "CLAIM_BLOCKED"
    summary = "Blocking metadata/gate failure prevents a positive RLL claim."

    if rll_scan is None:
        blocking.append("RLL row absent")
    elif rll_scan.delta_AICc_CPL is not None and rll_scan.delta_BIC_CPL is not None:
        if rll_scan.delta_AICc_CPL <= 0 and rll_scan.delta_BIC_CPL <= 0:
            claim_status = "PASS_LIMITED"
            summary = "RLL is not worse than CPL by AICc/BIC in this result table; still require covariance, priors and reproducibility gates."
        elif rll_scan.Os0 is not None and abs(rll_scan.Os0) <= EPS:
            claim_status = "CLAIM_BLOCKED"
            summary = "RLL is disfavored relative to CPL and its authorial amplitude collapses to zero in this result table."
            blocking.append("RLL Os0 collapsed to zero")
        else:
            claim_status = "CLAIM_BLOCKED"
            summary = "RLL is worse than CPL by AICc/BIC in this result table."
            blocking.append("RLL worse than CPL by information criteria")
    else:
        claim_status = "CLAIM_BLOCKED"
        summary = "Cannot compute RLL deltas relative to CPL."

    if blocking and claim_status != "CLAIM_BLOCKED":
        claim_status = "CLAIM_BLOCKED"
        summary = "Blocking metadata/gate failure prevents a positive RLL claim."

    return EvidenceScan(
        input_csv=str(input_csv.relative_to(ROOT) if input_csv.is_relative_to(ROOT) else input_csv),
        registry=str(registry.relative_to(ROOT) if registry.is_relative_to(ROOT) else registry),
        registry_schema=registry_schema,
        commit_sha=commit,
        row_count=len(rows),
        models_present=present_classes,
        missing_required_model_classes=missing,
        best_by_AICc=best_aicc_row.get("model") if best_aicc_row else None,
        best_by_BIC=best_bic_row.get("model") if best_bic_row else None,
        H0_all_equal=h0_all_equal,
        H0_values=h0_values,
        claim_status=claim_status,
        claim_summary=summary,
        blocking_reasons=blocking,
        warnings=warnings,
        model_scans=model_scans,
    )


def fmt(value: Any) -> str:
    if value is None:
        return "TOKEN_VAZIO"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def write_json(result: EvidenceScan, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(result)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(result: EvidenceScan, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# RLL Model Evidence Scan")
    lines.append("")
    lines.append("> Auto-generated by `tools/scan_rll_model_evidence.py`. This report measures current result-table evidence only; it does not establish physical truth.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- input_csv: `{result.input_csv}`")
    lines.append(f"- registry: `{result.registry}`")
    lines.append(f"- registry_schema: `{fmt(result.registry_schema)}`")
    lines.append(f"- commit_sha: `{fmt(result.commit_sha)}`")
    lines.append(f"- claim_status: **{result.claim_status}**")
    lines.append(f"- claim_summary: {result.claim_summary}")
    lines.append(f"- best_by_AICc: `{fmt(result.best_by_AICc)}`")
    lines.append(f"- best_by_BIC: `{fmt(result.best_by_BIC)}`")
    lines.append(f"- H0_all_equal: `{fmt(result.H0_all_equal)}`")
    lines.append("")

    if result.blocking_reasons:
        lines.append("## Blocking reasons")
        lines.append("")
        for reason in result.blocking_reasons:
            lines.append(f"- {reason}")
        lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in result.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.append("## Model table")
    lines.append("")
    lines.append("| model | row | chi2 | AICc | BIC | N | k | dof | dAICc_CPL | dBIC_CPL | flags |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for ms in result.model_scans:
        flags = "; ".join(ms.local_flags) if ms.local_flags else ""
        lines.append(
            f"| {ms.model} | `{ms.row_name}` | {fmt(ms.chi2)} | {fmt(ms.AICc)} | {fmt(ms.BIC)} | "
            f"{fmt(ms.N)} | {fmt(ms.k)} | {fmt(ms.dof)} | {fmt(ms.delta_AICc_CPL)} | {fmt(ms.delta_BIC_CPL)} | {flags} |"
        )
    lines.append("")

    lines.append("## RLL authorial diagnostics")
    lines.append("")
    rll = next((ms for ms in result.model_scans if ms.model == "RLL"), None)
    if rll is None:
        lines.append("TOKEN_VAZIO: RLL row absent.")
    else:
        lines.append(f"- Os0: `{fmt(rll.Os0)}`")
        lines.append(f"- zt: `{fmt(rll.zt)}`")
        lines.append(f"- wt: `{fmt(rll.wt)}`")
        lines.append(f"- Delta AICc vs CPL: `{fmt(rll.delta_AICc_CPL)}`")
        lines.append(f"- Delta BIC vs CPL: `{fmt(rll.delta_BIC_CPL)}`")
        if rll.local_flags:
            lines.append("- flags:")
            for flag in rll.local_flags:
                lines.append(f"  - {flag}")
    lines.append("")

    lines.append("## Certainty boundary")
    lines.append("")
    lines.append("Calculable with high confidence from this CSV: ranks, deltas, N-k-dof consistency, H0 equality, RLL Os0 collapse, and component chi2 presence.")
    lines.append("Not calculable from this CSV alone: physical truth of RLL, posterior robustness, covariance correctness, external reproducibility, and CLASS/CAMB growth validity.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan RLL model-evidence CSV for claim-safe diagnostics.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input results CSV")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Parameter registry JSON")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT, help="Output JSON report")
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT, help="Output Markdown report")
    parser.add_argument("--no-write", action="store_true", help="Only print summary; do not write outputs")
    args = parser.parse_args()

    result = scan(args.input, args.registry)
    if not args.no_write:
        write_json(result, args.json_out)
        write_markdown(result, args.md_out)

    print(f"claim_status={result.claim_status}")
    print(f"best_by_AICc={result.best_by_AICc}")
    print(f"best_by_BIC={result.best_by_BIC}")
    print(f"H0_all_equal={result.H0_all_equal}")
    if result.blocking_reasons:
        print("blocking_reasons:")
        for reason in result.blocking_reasons:
            print(f"- {reason}")
    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
