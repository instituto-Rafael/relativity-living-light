#!/usr/bin/env python3
"""Rx deterministic self-test.

No third-party packages. No training. No AI runtime.
"""

from __future__ import annotations

import ast
import importlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.contracts import active_contract
from rx.cosmology import ORAD, e2
from rx.kernel import invert_matrix, quad_form, read_csv, simpson
failures = []
contract_id, contract = active_contract()

def check(condition, label):
    if condition:
        print("PASS", label)
    else:
        print("FAIL", label)
        failures.append(label)

check(abs(simpson(lambda x: x * x, 0.0, 1.0, 128) - (1.0 / 3.0)) < 1.0e-10, "simpson_x2")

m = [[4.0, 1.0], [1.0, 3.0]]
mi = invert_matrix(m)
check(abs(mi[0][0] - 3.0 / 11.0) < 1.0e-12, "matrix_inverse_00")
check(abs(mi[0][1] + 1.0 / 11.0) < 1.0e-12, "matrix_inverse_01")
check(abs(quad_form([1.0, 2.0], [[2.0, 0.0], [0.0, 3.0]]) - 14.0) < 1.0e-12, "quadratic_form")

lcdm = [67.4, 0.315, 0.02236, 0.811]
wcdm = [67.4, 0.315, -1.0, 0.02236, 0.811]
cpl = [67.4, 0.315, -1.0, 0.0, 0.02236, 0.811]
rll = [67.4, 0.315, 0.0, 1.0, 0.3, 0.02236, 0.811]
for z in (0.0, 0.5, 1.0, 2.4, 10.0):
    base = e2("LCDM", z, lcdm)
    check(abs(e2("wCDM", z, wcdm) - base) < 1.0e-12, "nested_wCDM_z_%s" % z)
    check(abs(e2("CPL", z, cpl) - base) < 1.0e-12, "nested_CPL_z_%s" % z)
    check(abs(e2("RLL", z, rll) - base) < 1.0e-12, "nested_RLL_z_%s" % z)

hz = read_csv(ROOT / "data" / "real" / "cosmology" / "Hz_cosmic_chronometers_independent.csv")
bao = read_csv(ROOT / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv")
growth = read_csv(ROOT / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv")
check(len(hz) == 28, "current_Hz_count_28")
check(len(bao) == 13, "current_BAO_count_13")
check(len(growth) == 16, "current_growth_count_16")
check(len(hz) + len(bao) + len(growth) + 3 == 60, "current_multiprobe_N_60")
check(contract_id == "RX-STRUCTURE-D-PARITY-V1", "active_contract_id")
check(abs(float(contract["omega_r"]) - ORAD) < 1.0e-15, "contract_omega_r_matches_runtime")
check(contract["growth_mode"] == "structure_d_proxy", "contract_growth_mode")
check(contract["cmb_acoustic_mode"] == "structure_d_rd", "contract_cmb_mode")
check(contract["claim_allowed"] is False, "contract_claim_closed")
try:
    importlib.import_module("data.pipelines.structure_d")
    structure_namespace_ok = True
except Exception:
    structure_namespace_ok = False
check(structure_namespace_ok, "structure_d_namespace_import_without_legacy_dependencies")

stdlib = set(getattr(sys, "stdlib_module_names", ()))
stdlib.update({"__future__"})
for path in sorted((ROOT / "rx").glob("*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    external = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in stdlib and root != "rx":
                    external.add(root)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            root = node.module.split(".")[0]
            if root not in stdlib and root != "rx":
                external.add(root)
    check(not external, "stdlib_only_%s" % path.name)

result = {
    "schema": "rll.rx.selftest.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "pass": not failures,
    "failures": failures,
    "training": False,
    "ai_runtime": False,
    "third_party_python_dependencies": [],
    "current_multiprobe_N": len(hz) + len(bao) + len(growth) + 3,
    "physics_contract_id": contract_id,
}
out = ROOT / "results" / "rx_selftest.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if failures:
    print("RX_SELFTEST=FAIL", failures)
    raise SystemExit(1)

print("RX_SELFTEST=PASS")
print("training=False ai_runtime=False third_party_python_dependencies=0")
print("wrote", out.relative_to(ROOT))
