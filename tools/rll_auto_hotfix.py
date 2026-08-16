#!/usr/bin/env python3
"""Observe RLL operational inconsistencies and propose only bounded safe repairs.

The engine is deliberately conservative:
- observation is broader than mutation;
- safe mutation is limited to deterministic repository-local contracts;
- scientific claims, data, external settings, secrets and branch protection are
  never auto-mutated;
- unresolved observations remain explicit TOKEN_VAZIO/INCERTEZA entries.

Products are machine-readable and human-readable so every run can be audited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SCHEMA = "rll.operational_auto_hotfix.v1"
CONTRACT = Path(".github/workflow-contract.yml")
WORKFLOWS = Path(".github/workflows")
DEFAULT_OUTPUT = Path("artifacts/operational-auto-hotfix")
ACTIVE_RE = re.compile(r"^(?P<indent>\s*)active_workflows:\s*(?P<count>\d+)\s*$", re.MULTILINE)
FLOATING_ACTION_RE = re.compile(r"^\s*uses:\s*(actions/[A-Za-z0-9_.-]+)@(v\d+(?:\.\d+)*)\s*$", re.MULTILINE)
PATH_LITERAL_RE = re.compile(r"['\"]((?:scripts|tools|tests|docs|data)/[^'\"]+)['\"]")
TOKEN_PATTERNS = {
    "TOKEN_VAZIO": re.compile(r"\bTOKEN_VAZIO[A-Z0-9_:-]*\b"),
    "INCERTEZA": re.compile(r"\bINCERTEZA[A-Z0-9_:-]*\b", re.IGNORECASE),
    "TODO_FIXME": re.compile(r"\b(?:TODO|FIXME)\b"),
}


@dataclass(frozen=True)
class Observation:
    id: str
    kind: str
    urgency: str
    state: str
    source: str
    evidence: str
    auto_fixable: bool
    proposed_action: str
    falsifier: str
    provenance: str


@dataclass(frozen=True)
class StateVector:
    schema: str
    commit_sha: str
    observations: int
    p0: int
    p1: int
    p2: int
    token_vazio: int
    uncertainty: int
    auto_fixable: int
    blocked_from_automation: int
    f_ok: list[str]
    f_gap: list[str]
    f_next: list[str]
    claim_allowed: bool
    publication_effect: str


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_expected(text: str) -> int:
    matches = list(ACTIVE_RE.finditer(text))
    if len(matches) != 1:
        raise ValueError("contract must contain exactly one active_workflows scalar")
    if matches[0].group("indent") != "  ":
        raise ValueError("active_workflows must use two-space indentation")
    return int(matches[0].group("count"))


def executable_workflows(root: Path) -> list[Path]:
    base = root / WORKFLOWS
    if not base.is_dir():
        raise ValueError(f"workflow directory missing: {base}")
    return sorted({*base.glob("*.yml"), *base.glob("*.yaml")})


def _obs_id(kind: str, source: str, evidence: str) -> str:
    digest = hashlib.sha256(f"{kind}\0{source}\0{evidence}".encode()).hexdigest()[:12]
    return f"OBS-{digest.upper()}"


def make_observation(
    *, kind: str, urgency: str, state: str, source: str, evidence: str,
    auto_fixable: bool, proposed_action: str, falsifier: str, provenance: str,
) -> Observation:
    return Observation(
        id=_obs_id(kind, source, evidence), kind=kind, urgency=urgency,
        state=state, source=source, evidence=evidence, auto_fixable=auto_fixable,
        proposed_action=proposed_action, falsifier=falsifier, provenance=provenance,
    )


def scan(root: Path) -> tuple[list[Observation], dict[str, object]]:
    contract_path = root / CONTRACT
    if not contract_path.is_file():
        raise ValueError(f"contract missing: {contract_path}")
    contract_text = contract_path.read_text(encoding="utf-8")
    expected = read_expected(contract_text)
    workflows = executable_workflows(root)
    actual = len(workflows)
    observations: list[Observation] = []

    if expected != actual:
        observations.append(make_observation(
            kind="WORKFLOW_INVENTORY_DRIFT", urgency="P0", state="OPEN",
            source=CONTRACT.as_posix(),
            evidence=f"expected={expected};actual={actual}", auto_fixable=True,
            proposed_action="synchronize only inventory.active_workflows to executable count",
            falsifier="workflow_contract_sync reports expected==actual",
            provenance="filesystem census + executable contract",
        ))

    for workflow in workflows:
        rel = workflow.relative_to(root).as_posix()
        text = workflow.read_text(encoding="utf-8")
        for match in FLOATING_ACTION_RE.finditer(text):
            observations.append(make_observation(
                kind="FLOATING_ACTION_REF", urgency="P1", state="OPEN",
                source=rel, evidence=f"{match.group(1)}@{match.group(2)}",
                auto_fixable=False,
                proposed_action="replace floating tag only with repository-vetted immutable SHA",
                falsifier="no actions/*@vN floating reference remains in the workflow",
                provenance="static workflow source scan",
            ))
        for path_match in PATH_LITERAL_RE.finditer(text):
            candidate = path_match.group(1)
            if "*" in candidate or "${{" in candidate:
                continue
            if not (root / candidate).exists():
                observations.append(make_observation(
                    kind="MISSING_LOCAL_WORKFLOW_DEPENDENCY", urgency="P1", state="OPEN",
                    source=rel, evidence=candidate, auto_fixable=False,
                    proposed_action="restore dependency or correct path after provenance review",
                    falsifier=f"repository path exists: {candidate}",
                    provenance="static workflow path scan",
                ))

    # Scan governance authorities for explicit epistemic debt. This does not
    # auto-resolve those tokens; it makes them navigable.
    scan_files: list[Path] = [contract_path]
    for directory in (root / "data" / "governance", root / "docs" / "governance"):
        if directory.is_dir():
            scan_files.extend(sorted(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".jsonl", ".yml", ".yaml", ".md", ".txt"}))
    for path in scan_files:
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in TOKEN_PATTERNS.items():
            for match in pattern.finditer(text):
                token = match.group(0)
                kind = "EPISTEMIC_TOKEN" if label == "TOKEN_VAZIO" else ("UNCERTAINTY_TOKEN" if label == "INCERTEZA" else "MAINTENANCE_MARKER")
                urgency = "P2" if label == "TOKEN_VAZIO" else "P1"
                observations.append(make_observation(
                    kind=kind, urgency=urgency, state=token,
                    source=rel, evidence=token, auto_fixable=False,
                    proposed_action="bind source/evidence/falsifier/next gate; never invent closure",
                    falsifier="token is replaced by an evidenced terminal state with receipt",
                    provenance="literal governance-authority scan",
                ))

    # Deduplicate stable observations.
    unique = {obs.id: obs for obs in observations}
    ordered = sorted(unique.values(), key=lambda item: (item.urgency, item.kind, item.source, item.id))
    metadata = {
        "expected_workflows": expected,
        "actual_workflows": actual,
        "workflow_paths": [p.relative_to(root).as_posix() for p in workflows],
        "contract_sha256": sha256_bytes(contract_path.read_bytes()),
    }
    return ordered, metadata


def apply_safe(root: Path, observations: list[Observation], metadata: dict[str, object]) -> bool:
    drift = [item for item in observations if item.kind == "WORKFLOW_INVENTORY_DRIFT" and item.auto_fixable]
    if not drift:
        return False
    contract_path = root / CONTRACT
    before = contract_path.read_text(encoding="utf-8")
    read_expected(before)
    actual = int(metadata["actual_workflows"])
    after = ACTIVE_RE.sub(f"  active_workflows: {actual}", before, count=1)
    contract_path.write_text(after, encoding="utf-8")
    return after != before


def build_vector(observations: list[Observation], changed: bool) -> StateVector:
    p0 = sum(item.urgency == "P0" for item in observations)
    p1 = sum(item.urgency == "P1" for item in observations)
    p2 = sum(item.urgency == "P2" for item in observations)
    token_vazio = sum(item.kind == "EPISTEMIC_TOKEN" for item in observations)
    uncertainty = sum(item.kind == "UNCERTAINTY_TOKEN" for item in observations)
    fixable = sum(item.auto_fixable for item in observations)
    blocked = len(observations) - fixable
    f_ok = ["observer is deterministic and repository-local", "scientific auto-mutation forbidden", "receipts are hash-bound"]
    if changed:
        f_ok.append("bounded safe repair applied in workspace")
    f_gap = [item.id for item in observations if not item.auto_fixable][:64]
    f_next = [item.proposed_action for item in observations if item.urgency in {"P0", "P1"}][:32]
    return StateVector(
        schema="rll.operational_state_vector.v1",
        commit_sha=os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_COMMIT"),
        observations=len(observations), p0=p0, p1=p1, p2=p2,
        token_vazio=token_vazio, uncertainty=uncertainty,
        auto_fixable=fixable, blocked_from_automation=blocked,
        f_ok=f_ok, f_gap=f_gap, f_next=f_next,
        claim_allowed=False, publication_effect="NONE",
    )


def write_products(root: Path, output: Path, observations: list[Observation], metadata: dict[str, object], changed: bool) -> None:
    out = output if output.is_absolute() else root / output
    out.mkdir(parents=True, exist_ok=True)
    vector = build_vector(observations, changed)
    obs_lines = "".join(json.dumps(asdict(item), ensure_ascii=False, sort_keys=True) + "\n" for item in observations)
    (out / "observations.jsonl").write_text(obs_lines, encoding="utf-8")
    (out / "state_vector.json").write_text(json.dumps(asdict(vector), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": SCHEMA,
        "commit_sha": vector.commit_sha,
        "metadata": metadata,
        "changed": changed,
        "observation_count": len(observations),
        "observation_sha256": sha256_bytes(obs_lines.encode("utf-8")),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "direct_main_commit": "FORBIDDEN",
        "auto_merge": False,
        "safe_auto_fix_classes": ["WORKFLOW_INVENTORY_DRIFT"],
        "blocked_auto_fix_domains": ["scientific_claim", "scientific_data", "external_settings", "secrets", "branch_protection", "physical_interpretation"],
    }
    (out / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# RLL Operational Auto-Hotfix Observation", "",
        f"- expected workflows: `{metadata['expected_workflows']}`",
        f"- actual workflows: `{metadata['actual_workflows']}`",
        f"- observations: `{len(observations)}`",
        f"- P0/P1/P2: `{vector.p0}/{vector.p1}/{vector.p2}`",
        f"- TOKEN_VAZIO: `{vector.token_vazio}`",
        f"- INCERTEZA: `{vector.uncertainty}`",
        f"- safe workspace mutation applied: `{str(changed).lower()}`",
        "- claim_allowed: `false`", "- publication_effect: `NONE`", "",
        "## Priority observations", "",
    ]
    priority = [o for o in observations if o.urgency in {"P0", "P1"}]
    lines.extend(f"- `{o.id}` `{o.urgency}` `{o.kind}` — {o.source}: {o.evidence} → {o.proposed_action}" for o in priority[:100])
    if not priority:
        lines.append("- `NONE`")
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-products", action="store_true")
    parser.add_argument("--apply-safe", action="store_true")
    parser.add_argument("--strict", action="store_true", help="fail if P0/P1 observations remain after optional safe repair")
    args = parser.parse_args(list(argv) if argv is not None else None)
    root = args.repo_root.resolve()
    try:
        observations, metadata = scan(root)
        changed = apply_safe(root, observations, metadata) if args.apply_safe else False
        if changed:
            observations, metadata = scan(root)
        if args.write_products:
            write_products(root, args.output_dir, observations, metadata, changed)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR RLL_AUTO_HOTFIX: {exc}")
        return 2
    p0p1 = [o for o in observations if o.urgency in {"P0", "P1"}]
    print(f"operational auto-hotfix: observations={len(observations)} p0p1={len(p0p1)} expected={metadata['expected_workflows']} actual={metadata['actual_workflows']} changed={changed}")
    if args.strict and p0p1:
        for item in p0p1[:50]:
            print(f"{item.urgency} {item.kind} {item.source}: {item.evidence}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
