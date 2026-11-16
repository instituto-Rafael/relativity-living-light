"""Claim-safe diagnostic gate for the simple deterministic validation route.

A chi2 ordering at one fixed implementation point is evidence about that run,
not a standalone falsification or model-selection claim.
"""
from __future__ import annotations

import json
from pathlib import Path

OUTPUT_DIR = Path("validation_outputs")


def evaluate(comparison: dict) -> dict:
    chi_lcdm = float(comparison["chi2_lcdm"])
    chi_rll = float(comparison["chi2_rll"])
    delta = chi_rll - chi_lcdm

    if delta > 0.0:
        diagnostic = "RLL_HIGHER_CHI2_IN_THIS_RUN"
    elif delta < 0.0:
        diagnostic = "RLL_LOWER_CHI2_IN_THIS_RUN"
    else:
        diagnostic = "CHI2_EQUAL_IN_THIS_RUN"

    return {
        "diagnostic_state": diagnostic,
        "chi2_lcdm": chi_lcdm,
        "chi2_rll": chi_rll,
        "delta_chi2_rll_minus_lcdm": delta,
        "claim_allowed": False,
        "model_selection_claim_allowed": False,
        "falsification_claim_allowed": False,
        "required_for_promotion": [
            "predeclared comparable parameter freedom",
            "validated likelihood/covariance policy",
            "robust optimization or posterior convergence",
            "baseline/adversary comparison",
            "reproducible evidence receipt",
        ],
        "boundary": (
            "This gate reports the chi2 ordering of the current deterministic run. "
            "It does not declare a winner, confirm a model, or falsify a physical theory."
        ),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    comparison_path = OUTPUT_DIR / "comparison.json"
    if not comparison_path.exists():
        raise FileNotFoundError(f"missing comparison artifact: {comparison_path}")

    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    result = evaluate(comparison)
    output = OUTPUT_DIR / "falsification_gate.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("FINAL DIAGNOSTIC:", result)
    print("claim_allowed=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
