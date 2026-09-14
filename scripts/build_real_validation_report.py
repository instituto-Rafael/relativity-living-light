from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EVIDENCE_SCAN_JSON = Path("results/audit/rll_model_evidence_scan.json")


def _load_model_comparison(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Model comparison JSON not found at {path}. Run real pipeline first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_evidence_scan(path: Path | None) -> dict | None:
    """Load optional evidence scan JSON.  Returns None when not available."""
    if path is None:
        path = DEFAULT_EVIDENCE_SCAN_JSON
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _extract_evidence_scan_summary(scan: dict | None) -> dict:
    """Extract the evidence-scan fields that reports must surface (issue #422)."""
    if scan is None:
        return {
            "claim_status": "TOKEN_VAZIO",
            "claim_summary": "Evidence scan not available.",
            "best_by_AICc": None,
            "best_by_BIC": None,
            "H0_all_equal": None,
            "blocking_reasons": [],
            "warnings": [],
        }
    rll_scan = next(
        (row for row in scan.get("model_scans", []) if row.get("model") == "RLL"),
        {},
    )
    return {
        "claim_status": scan.get("claim_status", "TOKEN_VAZIO"),
        "claim_summary": scan.get("claim_summary"),
        "best_by_AICc": scan.get("best_by_AICc"),
        "best_by_BIC": scan.get("best_by_BIC"),
        "H0_all_equal": scan.get("H0_all_equal"),
        "delta_AICc_rll_minus_cpl": rll_scan.get("delta_AICc_CPL"),
        "delta_BIC_rll_minus_cpl": rll_scan.get("delta_BIC_CPL"),
        "blocking_reasons": scan.get("blocking_reasons", []),
        "warnings": scan.get("warnings", []),
    }


def _render_evidence_scan_section(summary: dict) -> str:
    def _safe(value: object) -> str:
        if value is None:
            return "TOKEN_VAZIO"
        # Strip characters that could alter Markdown rendering.
        return str(value).replace("|", "&#124;").replace("\n", " ").replace("\r", "")

    lines = ["", "## Evidence Scan", ""]
    lines.append(f"- claim_status: **{_safe(summary['claim_status'])}**")
    lines.append(f"- claim_summary: {_safe(summary.get('claim_summary'))}")
    lines.append(f"- best_by_AICc: {_safe(summary.get('best_by_AICc'))}")
    lines.append(f"- best_by_BIC: {_safe(summary.get('best_by_BIC'))}")
    lines.append(f"- H0_all_equal: {_safe(summary.get('H0_all_equal'))}")
    aicc_delta = summary.get("delta_AICc_rll_minus_cpl")
    bic_delta = summary.get("delta_BIC_rll_minus_cpl")
    lines.append(f"- Delta AICc RLL-CPL: {_safe(aicc_delta)}")
    lines.append(f"- Delta BIC RLL-CPL: {_safe(bic_delta)}")
    blocking = summary.get("blocking_reasons", [])
    lines.append(f"- blocking_reasons: {', '.join(_safe(r) for r in blocking) if blocking else 'none'}")
    warnings = summary.get("warnings", [])
    lines.append(f"- warnings: {', '.join(_safe(w) for w in warnings) if warnings else 'none'}")
    return "\n".join(lines) + "\n"


def _extract_model_metrics(model: dict, model_key: str) -> dict:
    nested_models = model.get("models", {}) if isinstance(model.get("models"), dict) else {}
    nested_block = nested_models.get(model_key, {}) if isinstance(nested_models.get(model_key), dict) else {}

    legacy_block = model.get(model_key, {}) if isinstance(model.get(model_key), dict) else {}

    chi2 = model.get(f"chi2_{model_key}")
    if chi2 is None:
        chi2 = nested_block.get("chi2", legacy_block.get("chi2"))

    aic = model.get(f"AIC_{model_key}")
    if aic is None:
        aic = nested_block.get("aic", nested_block.get("AIC", legacy_block.get("AIC", legacy_block.get("aic"))))

    bic = model.get(f"BIC_{model_key}")
    if bic is None:
        bic = nested_block.get("bic", nested_block.get("BIC", legacy_block.get("BIC", legacy_block.get("bic"))))

    return {
        "chi2": chi2,
        "AIC": aic,
        "BIC": bic,
    }


def _render_table(report: dict) -> str:
    rows = [
        ("RLL", report["rll"]),
        ("LCDM", report["lcdm"]),
    ]
    lines = [
        "# Model Comparison (Real Validation)",
        "",
        "| Model | chi2 | AIC | BIC | n_params | dataset | rerun_tolerance |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for name, payload in rows:
        lines.append(
            f"| {name} | {payload['chi2']:.6f} | {payload['AIC']:.6f} | {payload['BIC']:.6f} | "
            f"{payload['n_params']} | {report['dataset']} | {report['rerun_tolerance']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build real validation report artifacts")
    parser.add_argument(
        "--input-json",
        type=Path,
        default=Path("data/results/model_comparison.json"),
        help="Input model comparison JSON generated by the real pipeline",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("results/real_validation_report.json"),
    )
    parser.add_argument(
        "--out-table",
        type=Path,
        default=Path("results/model_comparison_table.md"),
    )
    parser.add_argument(
        "--dataset",
        default="Pantheon+SH0ES",
    )
    parser.add_argument(
        "--rerun-tolerance",
        default="|ΔAIC|<=1e-6, |ΔBIC|<=1e-6, |Δχ²|<=1e-6",
    )
    parser.add_argument(
        "--evidence-scan-json",
        type=Path,
        default=None,
        help=(
            "Optional path to evidence scan JSON (rll_model_evidence_scan.json). "
            f"Defaults to {DEFAULT_EVIDENCE_SCAN_JSON} when not provided."
        ),
    )
    args = parser.parse_args()

    model = _load_model_comparison(args.input_json)

    rll_metrics = _extract_model_metrics(model, "rll")
    lcdm_metrics = _extract_model_metrics(model, "lcdm")

    evidence_scan = _load_evidence_scan(args.evidence_scan_json)
    evidence_summary = _extract_evidence_scan_summary(evidence_scan)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(args.input_json),
        "dataset": args.dataset,
        "rerun_tolerance": args.rerun_tolerance,
        "n_obs": model["n_obs"],
        "k_rll": model.get("k_rll", 5),
        "k_lcdm": model.get("k_lcdm", 2),
        "delta_chi2_rll_minus_lcdm": model.get("delta_chi2_rll_minus_lcdm"),
        "delta_aic_rll_minus_lcdm": model.get("delta_aic_rll_minus_lcdm"),
        "delta_bic_rll_minus_lcdm": model.get("delta_bic_rll_minus_lcdm"),
        "interpretation_label": model.get("interpretation_label"),
        "claim_boundary": model.get(
            "claim_boundary",
            "No superiority claim unless real-data metrics pass predefined thresholds.",
        ),
        "rll": {
            "chi2": rll_metrics["chi2"],
            "AIC": rll_metrics["AIC"],
            "BIC": rll_metrics["BIC"],
            "n_params": model.get("k_rll", 5),
        },
        "lcdm": {
            "chi2": lcdm_metrics["chi2"],
            "AIC": lcdm_metrics["AIC"],
            "BIC": lcdm_metrics["BIC"],
            "n_params": model.get("k_lcdm", 2),
        },
        "evidence_scan": evidence_summary,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_table.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    table_content = _render_table(report) + _render_evidence_scan_section(evidence_summary)
    args.out_table.write_text(table_content, encoding="utf-8")


if __name__ == "__main__":
    main()
