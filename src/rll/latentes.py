"""Deterministic RLL-LATENTES utilities.

The module intentionally keeps the first implementation small and auditable:
validation, dry-run orchestration, scoring, negative-control status, provenance
and report generation are pure or file-local operations. Network collection is
represented by manifests until a source-specific fetcher is explicitly added.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import validate

DEFAULT_CATALOG = Path("data/rll_latentes/observations.yml")
DEFAULT_SCHEMA = Path("schemas/rll_latentes_observations.schema.json")
LATENT_SCORE_FIELDS = ("C", "I", "P", "E", "Rc", "Ru", "Am", "Vb")
FNV64_OFFSET = 0xCBF29CE484222325
FNV64_PRIME = 0x100000001B3
SEMANTIC_DIRECTIONS = (
    "d1_lexical_structure",
    "d2_entity_domain",
    "d3_relational_isogonic",
    "d4_antagonic_constraints",
    "d5_causal_temporal",
    "d6_epistemic_gap",
    "d7_operational_governance",
)
SEMANTIC_UNIT_ID_PATTERN = r"STU-[A-Z0-9_]{2,24}-[0-9]{4,12}"
PROMPT_TOKEN_PATTERN = r"[^\W_]+(?:['’-][^\W_]+)*"
# Stable machine-readable labels; presentation layers may use title case.
REQUIRED_EVIDENCE_CATEGORIES = ("domain evidence", "operational authorization", "independent proof")
NUMERIC_ID_DIGITS = 12
NUMERIC_ID_MODULO = 10**NUMERIC_ID_DIGITS


@dataclass(frozen=True)
class LatentScore:
    """Validated RLL-LATENTES score package."""

    C: float
    I: float
    P: float
    E: float
    Rc: float
    Ru: float
    Am: float
    Vb: float
    S_L: float
    status: str


@dataclass(frozen=True)
class PipelinePlan:
    """Dry-run plan entry for one source."""

    source_id: str
    domain: str
    ingest_target: str
    normalize_target: str
    null_model_target: str
    score_target: str
    report_target: str
    suggested_command: str
    rollback: str


def ucase_prompt(prompt: str) -> str:
    """Normalize a prompt without discarding its Unicode characters."""

    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string")
    normalized = " ".join(prompt.split())
    if not normalized:
        raise ValueError("prompt must not be empty")
    return normalized.upper()


def _prompt_tokens(prompt: str) -> list[dict[str, Any]]:
    # [^\W_] means a Unicode word character excluding underscore.
    return [
        {"surface": match.group(0), "normalized": match.group(0), "index": index}
        for index, match in enumerate(re.finditer(PROMPT_TOKEN_PATTERN, prompt, re.UNICODE))
    ]


def build_semantic_token_unit(prompt: str, *, unit_id: str | None = None, language: str = "pt-BR") -> dict[str, Any]:
    """Create a conservative, schema-shaped seven-direction prompt analysis.

    The function records what can be established from the prompt alone. It does
    not infer domain facts, causal claims, authorization, or evidence that the
    input does not provide.
    """

    normalized = ucase_prompt(prompt)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    # Truncate the digest to a decimal-safe, fixed-width identifier.
    numeric_id = int(digest[:NUMERIC_ID_DIGITS], 16) % NUMERIC_ID_MODULO
    token_unit_id = unit_id or f"STU-PROMPT-{numeric_id:0{NUMERIC_ID_DIGITS}d}"
    if not re.fullmatch(SEMANTIC_UNIT_ID_PATTERN, token_unit_id):
        raise ValueError(f"unit_id must match {SEMANTIC_UNIT_ID_PATTERN}")
    if not isinstance(language, str) or len(language) < 2:
        raise ValueError("language must contain at least two characters")

    lexical_tokens = _prompt_tokens(normalized)
    payload = {
        "unit_id": token_unit_id,
        "raw_span": normalized,
        "language": language,
        "lexical_tokens": lexical_tokens,
        "views_7d": {
            "d1_lexical_structure": {
                "normalized_form": normalized,
                "syntactic_roles": [],
                "ambiguities": ["semantic roles require explicit interpretation"],
            },
            "d2_entity_domain": {
                "domains": ["unclassified"],
                "entities": [item["normalized"] for item in lexical_tokens],
                "domain_variables": [],
                "units": [],
            },
            "d3_relational_isogonic": {
                "isogonic_links": [],
                "dependencies": [],
                "analogical_links": [],
                "invariants": [],
            },
            "d4_antagonic_constraints": {
                "antagonic_links": [],
                "constraints": [],
                "contradictions": [],
                "failure_modes": [],
            },
            "d5_causal_temporal": {
                "causes": [],
                "effects": [],
                "forward_paths": [],
                "backward_paths": [],
                "derivative_paths": [],
                "antiderivative_paths": [],
                "temporal_scope": "unspecified",
            },
            "d6_epistemic_gap": {
                "evidence_state": "unobserved",
                # Copy the immutable defaults so callers can add observed gaps.
                "missing_variables": list(REQUIRED_EVIDENCE_CATEGORIES),
                "token_vazio": True,
                "uncertainties": ["prompt-only analysis has no attached evidence"],
                "falsifiers": ["attach verifiable source and reproduce the procedure"],
            },
            "d7_operational_governance": {
                "intended_action": "classify and route for review",
                "execution_gate": "human_review",
                "audit_required": True,
                "next_action": "supply evidence, authorization, and acceptance criteria",
                "runtime_target": "governed prompt analysis",
            },
        },
        "evidence_refs": [],
        "uncertainty": 1.0,
        "epistemic_status": "gap",
        "use_policy": {
            "privacy": "unknown",
            "training_eligibility": "unknown",
            "retention": "session",
            "purpose": "inference",
            "owner": "user",
        },
        "created_at": utc_now_iso(),
    }
    validate_semantic_token_unit(payload)
    return payload


def validate_semantic_token_unit(payload: dict[str, Any]) -> None:
    """Enforce the safety invariants that prevent a gap becoming an assertion."""

    if tuple(payload.get("views_7d", {})) != SEMANTIC_DIRECTIONS:
        raise ValueError("semantic token unit must contain the ordered seven directions")
    gap = payload["views_7d"]["d6_epistemic_gap"]
    governance = payload["views_7d"]["d7_operational_governance"]
    if gap["token_vazio"] and not gap["missing_variables"]:
        raise ValueError("TOKEN_VAZIO flag requires non-empty missing_variables list")
    if gap["token_vazio"] and payload["epistemic_status"] != "gap":
        raise ValueError("TOKEN_VAZIO requires epistemic_status=gap")
    if gap["token_vazio"] and governance["execution_gate"] == "allow":
        raise ValueError("TOKEN_VAZIO cannot execute directly")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return payload


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def validate_catalog(catalog_path: Path, schema_path: Path) -> dict[str, Any]:
    """Validate YAML catalog against JSON Schema and semantic invariants."""

    payload = load_yaml(catalog_path)
    schema = load_json(schema_path)
    validate(payload, schema)

    steps = [item["step"] for item in payload["future_steps"]]
    if steps != list(range(1, 8)):
        raise ValueError(f"future_steps must be exactly [1..7], got {steps}")

    source_ids = [item["source_id"] for item in payload["sources"]]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source_id values must be unique")

    for source in payload["sources"]:
        tests = source.get("falsifiable_latent_tests", [])
        if not tests:
            raise ValueError(f"source has no falsifiable tests: {source['source_id']}")
        target = str(source["local_target"])
        if not target.startswith(("artifacts/rll_latentes/", "results/rll_latentes/")):
            raise ValueError(f"unsafe local_target for {source['source_id']}: {target}")

    return payload


def score_latent(C: float, I: float, P: float, E: float, Rc: float, Ru: float, Am: float, Vb: float) -> LatentScore:
    """Compute S_L with strict domain validation."""

    values = {"C": C, "I": I, "P": P, "E": E, "Rc": Rc, "Ru": Ru, "Am": Am, "Vb": Vb}
    for name, value in values.items():
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} must be finite")
    for name in ("C", "I", "P", "E", "Rc", "Am", "Vb"):
        value = float(values[name])
        if value < 0.0 or value > 1.0:
            raise ValueError(f"{name} must be in [0, 1]")
    if float(Ru) < 0.0:
        raise ValueError("Ru must be >= 0")

    numerator = float(C) * float(I) * float(P) * float(E) * float(Rc)
    denominator = 1.0 + float(Ru) + float(Am) + float(Vb)
    score = numerator / denominator
    if score < 0.2:
        status = "rejected_noise"
    elif score < 0.4:
        status = "weak_candidate"
    elif score < 0.7:
        status = "fertile_candidate"
    else:
        status = "requires_independent_replication"
    return LatentScore(float(C), float(I), float(P), float(E), float(Rc), float(Ru), float(Am), float(Vb), score, status)


def smooth_state(current: float, incoming: float, alpha: float = 0.25) -> float:
    """Apply C_{t+1}=(1-alpha)C_t+alpha*C_in with bounded alpha."""

    if not all(math.isfinite(float(value)) for value in (current, incoming, alpha)):
        raise ValueError("smooth_state inputs must be finite")
    if alpha < 0.0 or alpha > 1.0:
        raise ValueError("alpha must be in [0, 1]")
    return (1.0 - alpha) * float(current) + alpha * float(incoming)


def entropy_milli(data: bytes) -> int:
    """Return the documented milliscale entropy proxy for byte streams."""

    if not data:
        return 0
    unique = len(set(data))
    transitions = sum(1 for left, right in zip(data, data[1:]) if left != right)
    transition_term = 0 if len(data) == 1 else (transitions * 2000) // (len(data) - 1)
    return (unique * 6000) // 256 + transition_term


def fnv1a64(data: bytes) -> int:
    """Stable FNV-1a 64-bit digest for compact provenance fingerprints."""

    value = FNV64_OFFSET
    for byte in data:
        value ^= byte
        value = (value * FNV64_PRIME) & 0xFFFFFFFFFFFFFFFF
    return value


def toroidal_map(data: bytes, entropy: int, digest: str, state: str) -> tuple[float, float, float, float, float, float, float]:
    """Map (dados, entropia, hash, estado) to seven normalized toroidal phases."""

    seed = data + str(entropy).encode("utf-8") + digest.encode("utf-8") + state.encode("utf-8")
    raw = hashlib.sha256(seed).digest()
    return tuple(int.from_bytes(raw[index * 4 : index * 4 + 4], "big") / 2**32 for index in range(7))


def classify_control(score: LatentScore, controls_present: bool, null_rejected: bool) -> str:
    """Apply negative-control status discipline to a score."""

    if not controls_present:
        return "provisional"
    if not null_rejected:
        return "rejected_noise"
    return score.status


def build_plan(catalog: dict[str, Any]) -> list[PipelinePlan]:
    orchestration = catalog["orchestration"]
    stages = {stage["id"]: stage for stage in orchestration["stages"]}
    plans: list[PipelinePlan] = []
    for source in catalog["sources"]:
        source_id = source["source_id"]
        plans.append(
            PipelinePlan(
                source_id=source_id,
                domain=source["domain"],
                ingest_target=stages["ingest"]["output"].format(source_id=source_id),
                normalize_target=stages["normalize"]["output"].format(source_id=source_id),
                null_model_target=stages["null_model"]["output"].format(source_id=source_id),
                score_target=stages["score"]["output"].format(source_id=source_id),
                report_target=stages["report"]["output"].format(source_id=source_id),
                suggested_command=source["suggested_command"],
                rollback=stages["ingest"]["rollback"],
            )
        )
    return plans


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def print_json(payload: Any, *, sort_keys: bool = False) -> None:
    """Emit consistent human-readable JSON for CLI responses."""

    print(json.dumps(payload, indent=2, sort_keys=sort_keys, ensure_ascii=False))


def write_dry_run_manifests(catalog: dict[str, Any], root: Path) -> list[Path]:
    """Materialize source manifests without network access or destructive writes."""

    written: list[Path] = []
    for plan in build_plan(catalog):
        path = root / plan.ingest_target / "manifest.json"
        payload = {
            "mode": "dry_run",
            "created_at_utc": utc_now_iso(),
            "source_id": plan.source_id,
            "domain": plan.domain,
            "suggested_command": plan.suggested_command,
            "target": plan.ingest_target,
            "status": "planned_no_download",
            "rollback": plan.rollback,
        }
        write_json(path, payload)
        written.append(path)
    return written


def write_null_model(catalog: dict[str, Any], root: Path, source_id: str) -> Path:
    source = next(item for item in catalog["sources"] if item["source_id"] == source_id)
    plan = next(item for item in build_plan(catalog) if item.source_id == source_id)
    path = root / plan.null_model_target
    payload = {
        "source_id": source_id,
        "domain": source["domain"],
        "status": "planned_negative_control",
        "controls": source["falsifiable_latent_tests"],
        "claim_policy": catalog["meta"]["claim_policy"],
    }
    write_json(path, payload)
    return path


def write_score_csv(root: Path, source_id: str, score: LatentScore, status: str) -> Path:
    path = root / "results" / "rll_latentes" / "scores" / f"{source_id}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*LATENT_SCORE_FIELDS, "S_L", "status", "control_status"])
        writer.writeheader()
        row = asdict(score)
        row["control_status"] = status
        writer.writerow(row)
    return path


def merkle_root(paths: Iterable[Path]) -> str:
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)]
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    layer = hashes
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [hashlib.sha256((layer[index] + layer[index + 1]).encode("utf-8")).hexdigest() for index in range(0, len(layer), 2)]
    return layer[0]


def write_provenance(root: Path, paths: Iterable[Path]) -> Path:
    material = [path for path in paths if path.exists()]
    path = root / "results" / "rll_latentes" / "provenance" / "merkle_manifest.json"
    payload = {
        "created_at_utc": utc_now_iso(),
        "artifact_count": len(material),
        "merkle_root": merkle_root(material),
        "artifacts": [{"path": str(item), "sha256": hashlib.sha256(item.read_bytes()).hexdigest()} for item in sorted(material)],
    }
    write_json(path, payload)
    return path


def write_report(root: Path, source_id: str, score: LatentScore, control_status: str, provenance_path: Path) -> Path:
    path = root / "results" / "rll_latentes" / "reports" / f"{source_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# RLL-LATENTES validation report — {source_id}

- `S_L`: {score.S_L:.6f}
- score status: `{score.status}`
- control status: `{control_status}`
- provenance: `{provenance_path}`

## Scientific boundary

This report is a pipeline artifact, not a discovery claim. A candidate remains provisional until null models, negative controls, uncertainty analysis and independent replication are complete.
"""
    path.write_text(text, encoding="utf-8")
    return path


def run_dry_pipeline(catalog_path: Path, schema_path: Path, root: Path, source_id: str | None = None) -> dict[str, Any]:
    catalog = validate_catalog(catalog_path, schema_path)
    manifests = write_dry_run_manifests(catalog, root)
    selected = source_id or catalog["sources"][0]["source_id"]
    null_path = write_null_model(catalog, root, selected)
    score = score_latent(C=0.9, I=0.99, P=1.0, E=0.88, Rc=0.95, Ru=0.3, Am=0.2, Vb=0.1)
    control_status = classify_control(score, controls_present=True, null_rejected=False)
    score_path = write_score_csv(root, selected, score, control_status)
    provenance_path = write_provenance(root, [*manifests, null_path, score_path])
    report_path = write_report(root, selected, score, control_status, provenance_path)
    return {
        "catalog_sources": len(catalog["sources"]),
        "future_steps": len(catalog["future_steps"]),
        "selected_source": selected,
        "manifests": [str(path) for path in manifests],
        "null_model": str(null_path),
        "score": str(score_path),
        "provenance": str(provenance_path),
        "report": str(report_path),
        "control_status": control_status,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rll-latentes", description="RLL-LATENTES deterministic pipeline")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--root", type=Path, default=Path("."))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate catalog and schema invariants")
    plan_parser = subparsers.add_parser("plan", help="Emit dry-run orchestration plan")
    plan_parser.add_argument("--json", action="store_true")
    fetch_parser = subparsers.add_parser("fetch", help="Materialize dry-run fetch manifests")
    fetch_parser.add_argument("--dry-run", action="store_true", required=True)
    score_parser = subparsers.add_parser("score", help="Compute one deterministic reference score")
    score_parser.add_argument("--source-id", default=None)
    report_parser = subparsers.add_parser("report", help="Run all seven steps in dry-run mode")
    report_parser.add_argument("--source-id", default=None)
    tokenize_parser = subparsers.add_parser("tokenize", help="Build a governed seven-direction prompt unit")
    prompt_group = tokenize_parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file", type=Path)
    tokenize_parser.add_argument("--unit-id", default=None)
    subparsers.add_parser("verify", help="Validate catalog and emit provenance-ready status")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    catalog = validate_catalog(args.catalog, args.schema)

    if args.command == "validate":
        print_json({"status": "ok", "sources": len(catalog["sources"]), "future_steps": len(catalog["future_steps"])}, sort_keys=True)
        return 0
    if args.command == "plan":
        plan = [asdict(item) for item in build_plan(catalog)]
        if args.json:
            print_json(plan, sort_keys=True)
        else:
            for item in plan:
                print(f"{item['source_id']} -> {item['ingest_target']}")
        return 0
    if args.command == "fetch":
        paths = write_dry_run_manifests(catalog, args.root)
        print_json({"status": "dry_run", "written": [str(path) for path in paths]}, sort_keys=True)
        return 0
    if args.command == "score":
        selected = args.source_id or catalog["sources"][0]["source_id"]
        score = score_latent(C=0.9, I=0.99, P=1.0, E=0.88, Rc=0.95, Ru=0.3, Am=0.2, Vb=0.1)
        status = classify_control(score, controls_present=False, null_rejected=False)
        path = write_score_csv(args.root, selected, score, status)
        print_json({"status": status, "score_path": str(path), "S_L": score.S_L}, sort_keys=True)
        return 0
    if args.command == "report":
        print_json(run_dry_pipeline(args.catalog, args.schema, args.root, args.source_id), sort_keys=True)
        return 0
    if args.command == "tokenize":
        prompt = args.prompt
        if args.prompt_file is not None:
            prompt = args.prompt_file.read_text(encoding="utf-8")
        print_json(build_semantic_token_unit(prompt, unit_id=args.unit_id))
        return 0
    if args.command == "verify":
        print_json({"status": "verified", "schema": str(args.schema), "catalog": str(args.catalog)}, sort_keys=True)
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
