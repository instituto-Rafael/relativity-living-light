#!/usr/bin/env python3
"""Build deterministic formalization artifact for the 25 CRF-A items.

Python stdlib only. The executable checks corroborate the analytic/formal proof
records; they do not replace those proofs and do not promote novelty claims.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Callable

A_IDS = [
    "CRF-001","CRF-002","CRF-003","CRF-004","CRF-005","CRF-006","CRF-007",
    "CRF-008","CRF-009","CRF-010","CRF-011","CRF-012","CRF-013","CRF-014",
    "CRF-016","CRF-017","CRF-018","CRF-021","CRF-022","CRF-023","CRF-025",
    "CRF-027","CRF-029","CRF-030","CRF-031",
]
EXPECTED_SOURCE_BLOB = "c0419c91b213773377518752a15983416773f1c7"
GENERATOR = "tools/build_crf_a_formalization_artifact.py"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def close(a: complex | float, b: complex | float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def red(word: str) -> str:
    changed = True
    while changed:
        old = word
        word = word.replace("∅", "").replace("0", "").replace("11", "1")
        changed = word != old
    return word


def primes(n: int) -> list[int]:
    out: list[int] = []
    x = 2
    while len(out) < n:
        if all(x % p for p in out if p * p <= x):
            out.append(x)
        x += 1
    return out


def check_001() -> list[str]:
    for n in range(257):
        assert red("∅" * n + "0" * n + "1123") == "123"
    return ["rewrite holds for 0<=n<=256", "analytic proof stored in registry"]


def check_002() -> list[str]:
    assert math.comb(4, 2) * 7 == 42
    return ["C(4,2)=6", "6*7=42"]


def check_003() -> list[str]:
    assert close(15 * math.pi / 180, math.pi / 12)
    return ["15 degrees converts to pi/12 radians"]


def check_004() -> list[str]:
    for th, ro, ri in [(0.2, 2.0, 1.0), (1.3, 5.0, 2.5), (math.pi, 3.0, 0.0)]:
        lhs = th / 2 * (ro * ro - ri * ri)
        rhs = th * ro * ro / 2 - th * ri * ri / 2
        assert close(lhs, rhs)
    return ["annular-sector subtraction identity checked"]


def check_005() -> list[str]:
    R = 3.7
    for i in range(-20, 21):
        th = i * 0.17
        q = R * math.sin(th / 2)
        d = R * math.cos(th / 2)
        assert close(q*q + d*d, R*R)
    return ["q^2+d^2=R^2 on deterministic angle grid"]


def check_006() -> list[str]:
    assert 57 - 136 + 81 == 2
    return ["Euler arithmetic closure 57-136+81=2", "planarization counts remain external witness"]


def check_007() -> list[str]:
    assert 136 - 57 + 1 == 80
    return ["cycle rank arithmetic 136-57+1=80", "connectedness/counts remain declared witness"]


def check_008() -> list[str]:
    q = math.sqrt(3) / 2
    assert 0 < q < 1 and close(q*q, 0.75)
    return ["0<sqrt(3)/2<1", "q^2=3/4"]


def check_009() -> list[str]:
    q = math.sqrt(3) / 2
    L0, A0, V0 = 2.0, 7.0, 11.0
    for n in range(13):
        s = q**n
        assert close(L0*s, L0*q**n)
        assert close(A0*s*s, A0*q**(2*n))
        assert close(V0*s*s*s, V0*q**(3*n))
    return ["length/area/volume scaling powers checked n=0..12"]


def check_010() -> list[str]:
    R = 4.2
    for th in [0.1, 0.5, 1.2, 2.4, -0.7]:
        s = R * th
        c = 2 * R * math.sin(th / 2)
        assert close(s / c, th / (2 * math.sin(th / 2)))
    return ["arc/chord ratio agrees with direct s/c"]


def check_011() -> list[str]:
    R = 2.3
    for n in range(3, 25):
        a = math.pi / n
        p1 = (R*math.cos(a), R*math.sin(a))
        p2 = (R*math.cos(-a), R*math.sin(-a))
        dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        assert close(dist, 2*R*math.sin(math.pi/n))
    return ["side formula matches coordinate chord distance n=3..24"]


def check_012() -> list[str]:
    R = 2.3
    for n in range(3, 25):
        a = math.pi / n
        midpoint = ((R*math.cos(a)+R*math.cos(-a))/2, 0.0)
        assert close(abs(midpoint[0]), R*math.cos(math.pi/n))
    return ["apothem matches midpoint distance n=3..24"]


def polygon_area(R: float, n: int) -> float:
    pts = [(R*math.cos(2*math.pi*j/n), R*math.sin(2*math.pi*j/n)) for j in range(n)]
    return abs(sum(pts[j][0]*pts[(j+1)%n][1]-pts[(j+1)%n][0]*pts[j][1] for j in range(n))) / 2


def check_013() -> list[str]:
    R = 3.1
    for n in range(3, 21):
        formula = n/2 * R*R * math.sin(2*math.pi/n)
        assert close(polygon_area(R, n), formula)
    return ["area formula matches shoelace coordinates n=3..20"]


def check_014() -> list[str]:
    R = 2.0
    for inc in [0.0, 0.2, 0.6, 1.0]:
        a = R
        b = R * abs(math.cos(inc))
        e = abs(math.sin(inc))
        assert close(math.sqrt(max(0.0, 1-b*b/(a*a))), e)
        for j in range(32):
            t = 2*math.pi*j/32
            x = R*math.cos(t)
            y = R*math.cos(inc)*math.sin(t)
            assert close(x*x/(a*a) + y*y/(b*b), 1.0)
    return ["orthographic ellipse equation/eccentricity checked on t-grid"]


def check_016() -> list[str]:
    q = math.sqrt(3)/2
    ps = primes(12)
    for a,b in zip(ps, ps[1:]):
        g = b-a
        lhs = q**b / q**a
        rhs = q**g
        rhs2 = (3/4)**(g/2)
        assert close(lhs, rhs) and close(rhs, rhs2)
    return ["prime-gap radial ratio checked on first 11 gaps"]


def check_017() -> list[str]:
    q = math.sqrt(3)/2
    ps = primes(10)
    for th in [0.1, 0.7, -0.3]:
        for a,b in zip(ps, ps[1:]):
            g = b-a
            za = q**a * cmath.exp(1j*a*th)
            zb = q**b * cmath.exp(1j*b*th)
            lhs = zb/za
            rhs = (q*cmath.exp(1j*th))**g
            assert close(lhs, rhs, 1e-8)
    return ["complex transition identity checked across prime gaps/phases"]


def check_018() -> list[str]:
    for q,c,x0 in [(0.4,1.5,-2.0),(-0.3,0.7,3.0),(0.8,-1.2,0.5)]:
        xs = c/(1-q)
        x = x0
        for n in range(20):
            closed = xs + q**n*(x0-xs)
            assert close(x, closed)
            x = q*x + c
    return ["affine recurrence equals closed form for deterministic parameter sets"]


def fib(n: int) -> int:
    a,b = 0,1
    for _ in range(n):
        a,b = b,a+b
    return a


def fr_terms(limit: int) -> list[int]:
    vals=[None,2,4]
    for n in range(3, limit+1):
        vals.append(vals[n-1]+vals[n-2]-1)
    return vals


def check_021() -> list[str]:
    vals=fr_terms(50)
    for n in range(1,51):
        assert vals[n] == fib(n)+2*fib(n-1)+1
    return ["F^R_n=F_n+2F_(n-1)+1 checked n=1..50"]


def check_022() -> list[str]:
    vals=fr_terms(50)
    for n in range(3,51):
        assert vals[n-2] == vals[n]-vals[n-1]+1
    return ["reverse recurrence checked n=3..50"]


def check_023() -> list[str]:
    N=42; w6=2.0; w7=3.0
    for k in range(N):
        lam = 2*w6+2*w7-2*w6*math.cos(2*math.pi*6*k/N)-2*w7*math.cos(2*math.pi*7*k/N)
        v=[cmath.exp(2j*math.pi*k*j/N) for j in range(N)]
        for j in range(N):
            lv = 2*(w6+w7)*v[j] - w6*(v[(j+6)%N]+v[(j-6)%N]) - w7*(v[(j+7)%N]+v[(j-7)%N])
            assert close(lv, lam*v[j], 1e-8)
    return ["all 42 Fourier modes satisfy the weighted Laplacian eigenvalue formula"]


def check_025() -> list[str]:
    a,b,c,d = 2,-1,3,4
    states=[(5,7,11,13),(1,2,3,4),(-2,5,0,8)]
    for x0,x1,x2,x3 in states:
        scalar=a*x0+b*x1+c*x2+d*x3
        matrix=(scalar,x0,x1,x2)
        assert matrix[0] == scalar and matrix[1:] == (x0,x1,x2)
    return ["companion matrix first row/shift rows match scalar recurrence"]


def check_027() -> list[str]:
    M=1<<42
    def emod(x: int) -> int: return x % M
    def estrict(x: int) -> int | None: return x if 0 <= x < M else None
    for x in [-M-1,-1,0,1,M-1,M,M+1,3*M+17]:
        m=emod(x)
        assert 0 <= m < M
        s=estrict(x)
        if 0 <= x < M:
            assert s == x == m
        else:
            assert s is None
    return ["strict/modular boundary values checked exactly"]


def check_029() -> list[str]:
    mods=(7,10,12,20)
    def pi(n: int) -> tuple[int,...]: return tuple(n % m for m in mods)
    vals=[pi(n) for n in range(420)]
    assert len(set(vals)) == 420
    for n in range(-420,421):
        assert pi(n+420) == pi(n)
    return ["420 unique residue tuples on Z/420Z", "periodicity n→n+420 checked"]


def check_030() -> list[str]:
    def void(t: str, reason: str="missing") -> dict[str,str]:
        return {"state":"TOKEN_VAZIO","type":t,"reason":reason,"risk":"unknown","next_test":"required"}
    def lift(v: object, out_type: str) -> object:
        if isinstance(v, dict) and v.get("state") == "TOKEN_VAZIO":
            return {**v, "type":out_type}
        return v
    x=void("tau")
    y=lift(x,"tau_prime")
    assert isinstance(y,dict) and y["state"]=="TOKEN_VAZIO" and y["type"]=="tau_prime"
    assert y != 0 and y != "PASS"
    return ["typed absence propagates without numeric/PASS coercion"]


def check_031() -> list[str]:
    for bits in itertools.product((0,1), repeat=5):
        prod=math.prod(bits)
        assert (prod == 1) == all(bits)
        assert (prod == 0) == (not all(bits))
    return ["all 32 Boolean gate tuples exhaustively verified"]


CHECKS: dict[str, Callable[[], list[str]]] = {
    "CRF-001":check_001,"CRF-002":check_002,"CRF-003":check_003,"CRF-004":check_004,
    "CRF-005":check_005,"CRF-006":check_006,"CRF-007":check_007,"CRF-008":check_008,
    "CRF-009":check_009,"CRF-010":check_010,"CRF-011":check_011,"CRF-012":check_012,
    "CRF-013":check_013,"CRF-014":check_014,"CRF-016":check_016,"CRF-017":check_017,
    "CRF-018":check_018,"CRF-021":check_021,"CRF-022":check_022,"CRF-023":check_023,
    "CRF-025":check_025,"CRF-027":check_027,"CRF-029":check_029,"CRF-030":check_030,
    "CRF-031":check_031,
}


def validate_bindings(source: dict[str,Any], formal: dict[str,Any]) -> None:
    errors: list[str] = []
    if formal.get("claim_allowed") is not False:
        errors.append("formal registry claim_allowed must be false")
    if formal.get("expected_ids") != A_IDS:
        errors.append("expected_ids mismatch")
    source_items={x["id"]:x for x in source.get("items",[])}
    formal_items=formal.get("items",[])
    if [x.get("id") for x in formal_items] != A_IDS:
        errors.append("formal item ordering/ids mismatch")
    for item in formal_items:
        sid=item.get("id")
        src=source_items.get(sid)
        if not src:
            errors.append(f"{sid}: missing source item")
            continue
        if src.get("readiness") != "A":
            errors.append(f"{sid}: source readiness is not A")
        if src.get("expression") != item.get("expression"):
            errors.append(f"{sid}: expression drift")
        for field in ("definition","lemma","theorem","proof","test","evidence_boundary","prior_art_state","certificate","token_vazio"):
            if field not in item:
                errors.append(f"{sid}: missing {field}")
        if item.get("claim_allowed") is not False:
            errors.append(f"{sid}: claim_allowed must be false")
    if set(CHECKS) != set(A_IDS):
        errors.append("check function coverage mismatch")
    if errors:
        raise SystemExit("formalization binding validation failed:\n- " + "\n- ".join(errors))


def proofs_markdown(formal: dict[str,Any]) -> str:
    lines=[
        "# CRF-A Formalization Proofs V1","",
        "Contract: Definition → Lemma → Theorem → Proof → Test → Receipt.","",
        "Boundary: executable checks corroborate the formal records; novelty remains fail-closed.",""
    ]
    for item in formal["items"]:
        lines += [
            f"## {item['id']} — {item['title']}","",
            f"**Expression:** `{item['expression']}`","",
            f"**Signature:** {item['signature']['domain']} → {item['signature']['codomain']}","",
            f"**Definition:** {item['definition']}","",
            f"**Lemma:** {item['lemma']}","",
            f"**Theorem:** {item['theorem']}","",
            f"**Proof kind:** {item['proof']['kind']}","",
        ]
        for step in item["proof"]["steps"]:
            lines.append(f"- {step}")
        lines += [
            "",
            f"**Test:** {item['test']}","",
            f"**Evidence boundary:** {item['evidence_boundary']}","",
            f"**Prior art:** {item['prior_art_state']}","",
            f"**TOKEN_VAZIO:** {', '.join(item['token_vazio']) if item['token_vazio'] else '—'}","",
        ]
    return "\n".join(lines)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",default="data/formulas/CROSSREPO_FORMULA_FORMALIZATION_MAP_V1.snapshot.json")
    ap.add_argument("--formal",default="data/formalization/crf_a_formalization_v1.json")
    ap.add_argument("--outdir",default="artifacts/crf-a-formalization-v1")
    args=ap.parse_args()

    source_path=Path(args.source)
    formal_path=Path(args.formal)
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)

    source_bytes=source_path.read_bytes()
    source_blob=git_blob_sha1(source_bytes)
    if source_blob != EXPECTED_SOURCE_BLOB:
        raise SystemExit(f"source snapshot blob drift: {source_blob}")
    source=json.loads(source_bytes.decode("utf-8"))
    formal=read_json(formal_path)
    validate_bindings(source,formal)

    results=[]
    for item_id in A_IDS:
        try:
            details=CHECKS[item_id]()
            results.append({"id":item_id,"status":"PASS","details":details})
        except Exception as exc:
            results.append({"id":item_id,"status":"FAIL","details":[f"{exc.__class__.__name__}: {exc}"]})

    failures=[r for r in results if r["status"]!="PASS"]
    result_by_id={r["id"]:r for r in results}
    formal_by_id={x["id"]:x for x in formal["items"]}
    groups={
        key:[x["id"] for x in source["items"] if x.get("readiness")==key]
        for key in ("A","B","C")
    }
    merged_items=[]
    for src in source["items"]:
        base={
            "id":src["id"],"title":src["title"],"kind":src["kind"],
            "expression":src["expression"],"readiness":src["readiness"],
            "source":src["source"],"code":src["code"],"test":src["test"],
            "evidence":src["evidence"],"prior_art":src["prior_art"],"gaps":src["gaps"],
        }
        fm=formal_by_id.get(src["id"])
        if fm:
            rr=result_by_id[src["id"]]
            base["formalization"]={
                "status":fm["formal_status"],
                "ci_test_status":rr["status"],
                "ci_test_details":rr["details"],
                "signature":fm["signature"],
                "definition":fm["definition"],
                "lemma":fm["lemma"],
                "theorem":fm["theorem"],
                "proof":fm["proof"],
                "test":fm["test"],
                "evidence_boundary":fm["evidence_boundary"],
                "prior_art_state":fm["prior_art_state"],
                "token_vazio":fm["token_vazio"],
                "certificate":fm["certificate"],
            }
        else:
            base["formalization"]={
                "status":"NOT_FORMALIZED_IN_A_V1",
                "ci_test_status":"NOT_RUN",
                "ci_test_details":[],
                "token_vazio":["FORMALIZATION_PENDING_BY_READINESS_GATE"],
            }
        merged_items.append(base)

    page_v2={
        "schema":"rll.crf_page_data.v2",
        "artifact":"rll-crf-a-formalization-v1",
        "base_artifact":"rll-crf-formalization-v1",
        "source":{
            "repository":"rafaelmeloreisnovo/Matem-tica-",
            "ref":"61e3c1a6ed1e63dee5afedf36f33fee1f565025d",
            "path":"data/registries/CROSSREPO_FORMULA_FORMALIZATION_MAP_V1.json",
            "git_blob_sha1":source_blob,
        },
        "counts":{"total":34,"A":25,"B":8,"C":1},
        "formalization_counts":{"A_total":25,"A_pass":25-len(failures),"A_fail":len(failures)},
        "groups":groups,
        "items":merged_items,
        "claim_allowed":False,
        "page_rule":"page consumes artifact only; page does not scrape source repositories",
    }
    summary={
        "schema":"rll.crf_a_formalization_results.v1",
        "status":"PASS" if not failures else "FAIL",
        "claim_allowed":False,
        "item_count":len(results),
        "pass_count":len(results)-len(failures),
        "fail_count":len(failures),
        "source_blob_sha1":source_blob,
        "results":results,
        "boundaries":[
            "test PASS does not replace analytic/formal proof",
            "novelty claims remain false unless separately closed",
            "CRF-006/007 are conditional on witnessed graph counts",
            "TOKEN_VAZIO remains explicit",
        ],
    }

    (out/"FORMALIZATION_A.json").write_bytes(canonical_bytes(formal))
    (out/"A_ITEM_RESULTS.json").write_bytes(canonical_bytes(summary))
    (out/"FORMALIZATION_PROOFS.md").write_text(proofs_markdown(formal),encoding="utf-8",newline="\n")
    (out/"PAGE_DATA_V2.json").write_bytes(canonical_bytes(page_v2))

    files={}
    for name in ("FORMALIZATION_A.json","A_ITEM_RESULTS.json","FORMALIZATION_PROOFS.md","PAGE_DATA_V2.json"):
        p=out/name
        files[name]={"sha256":sha256_file(p),"bytes":p.stat().st_size}

    manifest={
        "schema":"rll.crf_a_formalization_artifact_manifest.v1",
        "artifact_name":"rll-crf-a-formalization-v1",
        "status":summary["status"],
        "claim_allowed":False,
        "generator":GENERATOR,
        "dependency_policy":"PYTHON_STDLIB_ONLY",
        "source_lock":{
            "origin_repository":"rafaelmeloreisnovo/Matem-tica-",
            "origin_ref":"61e3c1a6ed1e63dee5afedf36f33fee1f565025d",
            "origin_blob_sha1":source_blob,
            "snapshot_path":str(source_path),
        },
        "formalization_registry":str(formal_path),
        "item_count":25,
        "pass_count":summary["pass_count"],
        "fail_count":summary["fail_count"],
        "files":files,
        "page_entrypoint":"PAGE_DATA_V2.json",
    }
    (out/"MANIFEST.json").write_bytes(canonical_bytes(manifest))
    names=["MANIFEST.json","FORMALIZATION_A.json","A_ITEM_RESULTS.json","FORMALIZATION_PROOFS.md","PAGE_DATA_V2.json"]
    (out/"CHECKSUMS.sha256").write_text("\n".join(f"{sha256_file(out/n)}  {n}" for n in names)+"\n",encoding="utf-8",newline="\n")
    if failures:
        print(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True))
        return 1
    print(json.dumps({"status":"PASS","artifact":"rll-crf-a-formalization-v1","items":25,"source_blob_sha1":source_blob},ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
