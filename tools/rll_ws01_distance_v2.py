"""Post-failure WS01 successor; numeric consistency, never model validation."""
import hashlib
import json
import math
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))

from rx import cosmology
CONTRACT = ROOT / "data/contracts/rll_ws01_distance_integration_tolerance.v2.json"
PANEL_COUNTS = dict(log_coarse=1024, log_fine=4096, log_trapezoid=16384,
                    direct_coarse=16384, direct_fine=32768)


def accepts(a, b, rtol=1e-6, atol=0.001):
    return all(math.isfinite(x) and x > 0 for x in (a, b)) and abs(a - b) <= atol + rtol * abs(b)


def load():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (c.get("schema") != "rll.ws01_distance_integration_tolerance.v2"
            or c.get("status") != "SUCCESSOR_PROTOCOL_FROZEN_BEFORE_V2_EXECUTION_POSTHOC_TO_V1_FAILURE"
            or c.get("claim_allowed") is not False
            or c.get("tolerance") != {"rtol": 1e-6, "atol_mpc": 0.001}
            or c.get("steps") != PANEL_COUNTS
            or c.get("predecessor", {}).get("result") != "FAIL_PREREGISTERED_DISTANCE_TOLERANCE"
            or c.get("predecessor", {}).get("preserve") is not True
            or set(c.get("models", {})) != {"LCDM", "RLL_NULL", "RLL_PROBE"}
            or c.get("omega_r") != 0.0000918
            or c.get("replay_redshifts") != [.01,.1,.3,.5,1,1.5,2,3,5,10,1100]
            or c.get("additional_redshifts") != [.02,.7,4.658,100,1089.92,1500]):
        raise ValueError("WS01_V2_PROTOCOL_DRIFT")
    return c


def trapezoid(model, z, v, panels):
    xmax = math.log1p(z)
    h = xmax / panels
    def integrand(x):
        zp1 = math.exp(x)
        e2 = cosmology.e2(model, zp1 - 1, v)
        if not math.isfinite(e2) or e2 <= 0:
            raise ValueError("NONPOSITIVE_E2")
        return zp1 / math.sqrt(e2)
    total = math.fsum(integrand(i*h) for i in range(1, panels))
    return cosmology.C_KMS / v[0] * h * (total + .5*(integrand(0)+integrand(xmax)))


def build():
    c = load()
    previous_radiation = cosmology.ORAD
    rows = []
    reference = {}
    replay = set(c["replay_redshifts"])
    zs = sorted(replay | set(c["additional_redshifts"]))
    try:
        cosmology.ORAD = c["omega_r"]
        for label in ("LCDM", "RLL_NULL", "RLL_PROBE"):
            model = "LCDM" if label == "LCDM" else "RLL"
            v = c["models"][label]
            last = 0.0
            for z in zs:
                def dc(n, mode):
                    return cosmology.comoving_distance_mpc(model, z, v, steps=n, integration_mode=mode)
                coarse = dc(PANEL_COUNTS["log_coarse"], "log1p")
                fine = dc(PANEL_COUNTS["log_fine"], "log1p")
                tr = trapezoid(model, z, v, PANEL_COUNTS["log_trapezoid"])
                direct0 = dc(PANEL_COUNTS["direct_coarse"], "direct_z")
                direct1 = dc(PANEL_COUNTS["direct_fine"], "direct_z")
                if label == "LCDM":
                    reference[z] = fine
                checks = {
                    "log_fine_vs_trapezoid": accepts(fine, tr),
                    "log_fine_vs_direct_fine": accepts(fine, direct1),
                    "log_coarse_vs_log_fine": accepts(coarse, fine),
                    "direct_coarse_vs_direct_fine": accepts(direct0, direct1),
                    "positive_finite": all(math.isfinite(x) and x > 0 for x in (coarse,fine,tr,direct0,direct1)),
                    "strict_monotonic_distance": fine > last,
                    "LCDM_RLL_NULL_equivalence": label != "RLL_NULL" or accepts(fine, reference[z]),
                }
                rows.append(dict(model=label, z=z, cohort="REPLAY" if z in replay else "ADDITIONAL_NUMERIC",
                                 fine=fine, trap=tr, direct_coarse=direct0, direct_fine=direct1,
                                 checks=checks))
                last = fine
    finally:
        cosmology.ORAD = previous_radiation
    failures = [dict(model=r["model"], z=r["z"], failed=[k for k,v in r["checks"].items() if not v])
                for r in rows if not all(r["checks"].values())]
    return dict(schema="rll.ws01_distance_v2.receipt", state="FAIL_V2_NUMERIC" if failures else "PASS_V2_NUMERIC_SCOPED",
                predecessor_state=c["predecessor"]["result"], claim_allowed=False,
                promotion_allowed=False, row_count=len(rows), replay_rows=sum(r["cohort"]=="REPLAY" for r in rows),
                additional_rows=sum(r["cohort"]=="ADDITIONAL_NUMERIC" for r in rows),
                contract_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                failures=failures, rows=rows)


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2, allow_nan=False))
    raise SystemExit(2 if result["failures"] else 0)
