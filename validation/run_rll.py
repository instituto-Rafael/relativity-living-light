import json
import math
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.load_data import load_real_data


def rll(z_values):
    return [
        70.0 * math.sqrt(0.3 * (1.0 + float(z)) ** 3 + 0.7)
        + 0.1 * math.log(1.0 + float(z))
        for z in z_values
    ]


if __name__ == "__main__":
    os.makedirs("validation_outputs", exist_ok=True)

    z, y, yerr = load_real_data()
    pred = rll(z)

    with open("validation_outputs/rll.json", "w", encoding="utf-8") as f:
        json.dump({"model": "RLL", "values": pred}, f)

    print("RLL done")
