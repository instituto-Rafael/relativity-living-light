from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from rll.orcid_vector_model import *  # re-export public API
from rll.orcid_vector_store import VectorStore


class Http:
    def get(self, url: str, headers: Mapping[str, str] | None = None) -> dict[str, Any]:
        request = urllib.request.Request(url, headers={"User-Agent": "RLL-ORCID/1.0", "Accept": "application/json", **dict(headers or {})})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise ValueError("Resposta remota não é objeto JSON")
        return payload


def sync_remote(store: VectorStore, owner: str, token: str, enrich: bool, mailto: str | None, openalex_key: str | None) -> dict[str, Any]:
    http = Http()
    headers = {"Authorization": f"Bearer {token}"}
    record = http.get(f"{ORCID_API}/{urllib.parse.quote(owner)}/record", headers)
    result = store.ingest_orcid_record(record, owner)
    counters = {"datacite_ok": 0, "crossref_ok": 0, "openalex_ok": 0, "errors": 0}
    if enrich:
        rows = store.connection.execute("SELECT logical_id,doi FROM artifacts a WHERE revision=(SELECT MAX(x.revision) FROM artifacts x WHERE x.logical_id=a.logical_id) AND owner_orcid=?", (owner,)).fetchall()
        for row in rows:
            if not row["doi"]:
                continue
            doi = urllib.parse.quote(row["doi"], safe="")
            try:
                store.enrich_artifact(row["logical_id"], http.get(f"{DATACITE_API}/{doi}"), provider="datacite")
                counters["datacite_ok"] += 1
            except Exception as exc:
                counters["errors"] += 1
                store.append_event("EXTERNAL_SOURCE_ERROR", row["logical_id"], {"provider": "datacite", "error": str(exc), "claim_allowed": False})
            try:
                params = f"?mailto={urllib.parse.quote(mailto)}" if mailto else ""
                store.enrich_artifact(row["logical_id"], http.get(f"{CROSSREF_API}/{doi}{params}"), provider="crossref")
                counters["crossref_ok"] += 1
            except Exception as exc:
                counters["errors"] += 1
                store.append_event("EXTERNAL_SOURCE_ERROR", row["logical_id"], {"provider": "crossref", "error": str(exc), "claim_allowed": False})
            try:
                identifier = urllib.parse.quote(f"https://doi.org/{row['doi']}", safe="")
                params = {}
                if openalex_key:
                    params["api_key"] = openalex_key
                if mailto:
                    params["mailto"] = mailto
                suffix = "?" + urllib.parse.urlencode(params) if params else ""
                store.enrich_artifact(row["logical_id"], http.get(f"{OPENALEX_API}/{identifier}{suffix}"), provider="openalex")
                counters["openalex_ok"] += 1
            except Exception as exc:
                counters["errors"] += 1
                store.append_event("EXTERNAL_SOURCE_ERROR", row["logical_id"], {"provider": "openalex", "error": str(exc), "claim_allowed": False})
        store.connection.commit()
    return {"ingest": result, "enrichment": counters if enrich else None}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON raiz deve ser objeto")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rll-orcid", description="ORCID ↔ RLL: metadados, validação e vetores append-only")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    ingest = sub.add_parser("ingest-file"); ingest.add_argument("input", type=Path); ingest.add_argument("--orcid", required=True)
    sync = sub.add_parser("sync"); sync.add_argument("--orcid", required=True); sync.add_argument("--token-env", default="ORCID_ACCESS_TOKEN"); sync.add_argument("--enrich", action="store_true"); sync.add_argument("--mailto"); sync.add_argument("--openalex-key-env", default="OPENALEX_API_KEY")
    enrich = sub.add_parser("enrich-file"); enrich.add_argument("input", type=Path); enrich.add_argument("--provider", choices=["crossref", "datacite", "openalex"], required=True); enrich.add_argument("--logical-id", required=True)
    search = sub.add_parser("search"); search.add_argument("query"); search.add_argument("--discipline", action="append", default=[]); search.add_argument("--limit", type=int, default=10); search.add_argument("--orcid")
    sub.add_parser("status"); sub.add_parser("verify-chain")
    report = sub.add_parser("report"); report.add_argument("--output", type=Path, default=Path("artifacts/orcid_rll/ORCID_RLL_VECTOR_REPORT.md")); report.add_argument("--orcid")
    export = sub.add_parser("export-orcid"); export.add_argument("--output", type=Path, default=Path("artifacts/orcid_rll/orcid_work_candidates.json")); export.add_argument("--orcid")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with VectorStore(args.db) as store:
            if args.command == "init" or args.command == "status":
                output: Any = store.status()
            elif args.command == "ingest-file":
                output = {"ingest": store.ingest_orcid_record(load_json(args.input), args.orcid), "status": store.status()}
            elif args.command == "sync":
                owner = canonicalize_orcid(args.orcid); token = os.environ.get(args.token_env, "").strip()
                if not token:
                    raise ValueError(f"{args.token_env} ausente; use token ORCID /read-public apenas em runtime")
                output = {**sync_remote(store, owner, token, args.enrich, args.mailto, os.environ.get(args.openalex_key_env)), "status": store.status()}
            elif args.command == "enrich-file":
                aid, created, validation = store.enrich_artifact(args.logical_id, load_json(args.input), provider=args.provider)
                output = {"artifact_id": aid, "created_revision": created, "validation": {"state": validation.state, "score": validation.score, "details": validation.details}, "status": store.status()}
            elif args.command == "search":
                output = store.search(args.query, disciplines=args.discipline, limit=args.limit, owner_orcid=args.orcid)
            elif args.command == "verify-chain":
                ok, tip = store.verify_event_chain(); output = {"ok": ok, "tip": tip}
                print(json.dumps(output, indent=2)); return 0 if ok else 2
            elif args.command == "report":
                args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(store.markdown_report(args.orcid), encoding="utf-8"); print(args.output); return 0
            else:
                output = store.export_candidates(args.orcid); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); print(args.output); return 0
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)); return 0
    except (ValueError, KeyError, sqlite3.Error, OSError) as exc:
        print(f"rll-orcid: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
