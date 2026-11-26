"""Nominal RLL age comparison. Run from the repository root with python -m tools.rll_age_gate."""
import hashlib
import json
import math
import platform
from pathlib import Path

from src.rll.cosmology_radiation import omega_r_from_h0

H0 = 67.4
MATTER = 0.315
HUBBLE_GYR = 3.0856775814913673e19 / H0 / (31557600 * 1e9)
COHORT = Path("data/chronology/oldest_gc_v1.json")


def interval_gyr(z_low, z_high, sector, radiation, panels=2048):
    """Integrate cosmic time using x=sqrt(a), including the infinite-redshift endpoint."""
    if not (0 <= z_low < z_high and 0 <= radiation and 0 <= sector
            and MATTER + radiation + sector <= 1 and panels >= 2 and panels % 2 == 0):
        raise ValueError("invalid redshifts, densities or Simpson panel count")
    start = 1 / math.sqrt(1 + z_high)
    step = (1 / math.sqrt(1 + z_low) - start) / panels
    total = 0.0
    for i in range(panels + 1):
        x = start + i * step
        if x == 0:
            continue
        a = x * x
        exponent = (1 / a - 2) / 0.3
        decay = math.exp(-abs(exponent))
        f = (decay if exponent >= 0 else 1) / (1 + decay)
        density = radiation + (MATTER + sector * (1 - f)) * a
        density += (1 - MATTER - sector - radiation + sector * f) * a**4
        weight = 1 if i in (0, panels) else 4 if i % 2 else 2
        total += weight * 2 * x * a / math.sqrt(density)
    return HUBBLE_GYR * total * step / 3


def report():
    cohort = json.loads(COHORT.read_text())
    radiation = omega_r_from_h0(H0)
    rows = []
    for sector in (0.0, 0.02):
        age = interval_gyr(0, math.inf, sector, radiation)
        rows.append({"omega_s0": sector, "age_gyr": age,
                     "formation_margin_gyr": age - cohort["age_gyr"]})
    paths = [COHORT, Path(__file__), Path("src/rll/cosmology_radiation.py"),
             Path("tests/test_rll_age_gate.py"), Path(".github/workflows/rll-age-gate.yml")]
    return {"schema": "rll.age-screen.v1", "claim_allowed": False,
            "python": platform.python_version(), "source": cohort, "omega_r": radiation,
            "results": rows, "input_sha256": {
                str(p.relative_to(Path.cwd()) if p.is_absolute() else p):
                hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
