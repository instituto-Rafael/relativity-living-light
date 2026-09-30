import json
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.load_data import load_real_data


def compare(y, yerr, lcdm_vals, rll_vals):
    if not (len(y) == len(yerr) == len(lcdm_vals) == len(rll_vals)):
        raise ValueError("comparison vectors must have equal length")
    chi_lcdm = sum(
        ((float(pred) - float(obs)) / (float(sig) + 1e-8)) ** 2
        for pred, obs, sig in zip(lcdm_vals, y, yerr)
    )
    chi_rll = sum(
        ((float(pred) - float(obs)) / (float(sig) + 1e-8)) ** 2
        for pred, obs, sig in zip(rll_vals, y, yerr)
    )
    return {
        "chi2_lcdm": float(chi_lcdm),
        "chi2_rll": float(chi_rll),
        "delta": float(chi_lcdm - chi_rll),
        "claim_boundary": (
            "comparison metric only; no superiority claim without predefined "
            "real-data thresholds"
        ),
    }


if __name__ == "__main__":
    os.makedirs("validation_outputs", exist_ok=True)

    z, y, yerr = load_real_data()

    with open("validation_outputs/lcdm.json", encoding="utf-8") as handle:
        lcdm = json.load(handle)
    with open("validation_outputs/rll.json", encoding="utf-8") as handle:
        rll = json.load(handle)

    result = compare(y, yerr, lcdm["values"], rll["values"])

    with open("validation_outputs/comparison.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("RESULT:", result)
