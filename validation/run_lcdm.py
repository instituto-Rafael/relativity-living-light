import json
import math
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.load_data import load_real_data


def lcdm(z_values):
    return [
        70.0 * math.sqrt(0.3 * (1.0 + float(z)) ** 3 + 0.7)
        for z in z_values
    ]


if __name__ == "__main__":
    os.makedirs("validation_outputs", exist_ok=True)

    z, y, yerr = load_real_data()
    pred = lcdm(z)

    with open("validation_outputs/lcdm.json", "w", encoding="utf-8") as f:
        json.dump({"model": "LCDM", "values": pred}, f)

    print("LCDM done")
