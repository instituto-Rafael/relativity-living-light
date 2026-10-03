#!/usr/bin/env python3
"""Fetch one public arXiv Atom record and emit a pending, source-hashed candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse, request
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "results/relational_validation/packages/ACADEMIC_CORR_001/relation_graph.json"
ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_NS = "http://arxiv.org/schemas/atom"
IDENTIFIER_RE = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?$")
VERSION_RE = re.compile(r"v\d+$")
MAX_RESPONSE_BYTES = 2_000_000


def normalize_arxiv_identifier(value: str) -> tuple[str, str | None]:
    raw = value.strip()
    if raw.startswith(("https://", "http://")):
        parsed = parse.urlparse(raw)
        if parsed.hostname not in {"arxiv.org", "www.arxiv.org"}:
            raise ValueError("URL must use arxiv.org")
        parts = parsed.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] not in {"abs", "pdf"}:
            raise ValueError("URL must be an arXiv abstract or PDF URL")
        raw = parts[1]
        if raw.endswith(".pdf"):
            raw = raw[:-4]
    raw = raw.strip("/")
    if not IDENTIFIER_RE.fullmatch(raw):
        raise ValueError("expected an arXiv identifier such as 2503.14738 or an arxiv.org/abs URL")
    version_match = VERSION_RE.search(raw)
    version = version_match.group(0) if version_match else None
    base = VERSION_RE.sub("", raw)
    return base, version


def _text(entry: ET.Element, tag: str, namespace: str = ATOM_NS) -> str:
    element = entry.find(f"{{{namespace}}}{tag}")
    if element is None or element.text is None:
        return ""
    return " ".join(element.text.split())


def parse_arxiv_atom(raw_xml: bytes, requested_id: str) -> dict[str, Any]:
    root = ET.fromstring(raw_xml)
    entries = root.findall(f"{{{ATOM_NS}}}entry")
    if len(entries) != 1:
        raise ValueError(f"arXiv API returned {len(entries)} entries; expected exactly one")
    entry = entries[0]
    entry_id = _text(entry, "id")
    if not entry_id:
        raise ValueError("arXiv Atom entry is missing its canonical id")
    record_id = parse.urlparse(entry_id).path.rstrip("/").split("/")[-1]
    if not record_id:
        raise ValueError("arXiv Atom entry id is not a paper URL")
    authors = []
    for author in entry.findall(f"{{{ATOM_NS}}}author"):
        name = _text(author, "name")
        if name:
            authors.append(name)
    categories = sorted(
        category.attrib["term"]
        for category in entry.findall(f"{{{ATOM_NS}}}category")
        if category.attrib.get("term")
    )
    return {
        "requested_arxiv_id": requested_id,
        "returned_arxiv_id": record_id,
        "work_id": f"arxiv:{record_id}",
        "title": _text(entry, "title"),
        "authors": authors,
        "published": _text(entry, "published"),
        "updated": _text(entry, "updated"),
        "abstract": _text(entry, "summary"),
        "categories": categories,
        "doi": _text(entry, "doi", ARXIV_NS),
        "journal_reference": _text(entry, "journal_ref", ARXIV_NS),
        "source_locator": f"https://arxiv.org/abs/{record_id}",
    }


def make_candidate(
    raw_xml: bytes,
    requested_id: str,
    relation_targets: list[str],
    relation_note: str,
    graph: dict[str, Any],
    retrieved_at: str,
    run_id: str = "local-run",
    actor: str = "local-user",
) -> dict[str, Any]:
    record = parse_arxiv_atom(raw_xml, requested_id)
    returned_base_id, _ = normalize_arxiv_identifier(record["returned_arxiv_id"])
    requested_base_id, _ = normalize_arxiv_identifier(requested_id)
    if returned_base_id != requested_base_id:
        raise ValueError(
            "requested ID {} differs from API result {}; no substitution was made".format(
                requested_base_id, record["returned_arxiv_id"]
            )
        )
    note = relation_note.strip()
    target_ids = [item.strip() for item in relation_targets if item.strip()]
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("relation target list contains duplicates")
    if len(target_ids) > 20:
        raise ValueError("at most 20 relation targets may be submitted in one intake")
    graph_nodes = {node.get("id") for node in graph.get("nodes", []) if isinstance(node, dict)}
    unknown = sorted(set(target_ids) - graph_nodes)
    if unknown:
        raise ValueError(f"unknown relation target node(s): {', '.join(unknown)}")
    if target_ids and not note:
        raise ValueError("relation_note is required when relation targets are supplied")
    if len(note) > 500:
        raise ValueError("relation_note must be 500 characters or fewer")

    digest = hashlib.sha256(raw_xml).hexdigest()
    candidate_relations = [
        {
            "from": record["work_id"],
            "to": target_id,
            "edge_type": "human_declared_relation_candidate",
            "relation_note": note,
            "source_locator": record["source_locator"],
            "source_sha256": digest,
            "review_state": "RELATIONAL_PENDING",
            "claim_allowed": False,
        }
        for target_id in target_ids
    ]
    return {
        "schema": "rll.research_source_candidate.v1",
        **record,
        "retrieved_at": retrieved_at,
        "source_api": "https://export.arxiv.org/api/query",
        "source_sha256": digest,
        "metadata_evidence_state": "VERIFIED_PUBLIC_METADATA_RESPONSE_HASHED",
        "candidate_relations": candidate_relations,
        "claim_allowed": False,
        "claim_boundary": "Public bibliographic metadata is traceability, not evidence for a scientific claim.",
        "run_id": run_id,
        "actor": actor,
    }


def fetch_arxiv_xml(arxiv_id: str) -> bytes:
    base_id, _ = normalize_arxiv_identifier(arxiv_id)
    query = parse.urlencode({"id_list": base_id, "max_results": 1})
    url = f"https://export.arxiv.org/api/query?{query}"
    req = request.Request(
        url,
        headers={"User-Agent": "RLLResearchFragments/1.0 (public metadata intake)"},
    )
    with request.urlopen(req, timeout=30) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("arXiv API response exceeded the 2 MB safety limit")
    return raw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arxiv-id", required=True)
    parser.add_argument("--relation-targets", default="")
    parser.add_argument("--relation-note", default="")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        base_id, requested_version = normalize_arxiv_identifier(args.arxiv_id)
        raw_xml = fetch_arxiv_xml(base_id)
        graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        targets = [item for item in args.relation_targets.split(",") if item.strip()]
        retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        candidate = make_candidate(
            raw_xml=raw_xml,
            requested_id=base_id,
            relation_targets=targets,
            relation_note=args.relation_note,
            graph=graph,
            retrieved_at=retrieved_at,
            run_id=os.environ.get("GITHUB_RUN_ID", "local-run"),
            actor=os.environ.get("GITHUB_ACTOR", "local-user"),
        )
        if requested_version and not candidate["returned_arxiv_id"].endswith(requested_version):
            raise ValueError(
                f"requested version {requested_version} differs from API result "
                f"{candidate['returned_arxiv_id']}; no version substitution was made"
            )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "source.atom.xml").write_bytes(raw_xml)
        (args.output_dir / "candidate.json").write_text(
            json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (ValueError, ET.ParseError, OSError, request.URLError, json.JSONDecodeError) as exc:
        print(f"arXiv intake failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"pending arXiv candidate {candidate['work_id']} "
        f"sha256={candidate['source_sha256']} relations={len(candidate['candidate_relations'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
