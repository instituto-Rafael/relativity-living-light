#!/usr/bin/env python3
"""Validate zero-third-party imports in the legacy validacao_real core bundle."""
from __future__ import annotations
import ast,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=[
 ROOT/"validacao_real/fetch_real_data.py",
 ROOT/"validacao_real/compute_validation.py",
 ROOT/"validacao_real/make_figures.py",
 ROOT/"validacao_real/render_report.py",
]
stdlib=set(getattr(sys,"stdlib_module_names",()))
local={"rx","internal","validacao_real"}
rows=[]; violations=[]; parse_errors=[]
for path in FILES:
    rel=str(path.relative_to(ROOT))
    try:
        tree=ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        parse_errors.append({"path":rel,"error":str(exc)})
        continue
    imports=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    external=sorted(name for name in imports if name not in stdlib and name not in local and name!="__future__")
    rows.append({"path":rel,"imports":sorted(imports),"external":external})
    for name in external:
        violations.append({"path":rel,"module":name})

payload={
 "schema":"rll.validacao_real.zero_dependency_core.v1",
 "pass":not violations and not parse_errors,
 "files":rows,
 "violations":violations,
 "parse_errors":parse_errors,
 "third_party_python_dependencies":sorted({x["module"] for x in violations}),
 "claim_allowed":False,
 "boundary":"This gate checks imports/syntax only; it does not prove numerical parity, scientific validity, or runtime isolation."
}
out=ROOT/"results/validacao_real_zero_dependency_core.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(0 if payload["pass"] else 5)
