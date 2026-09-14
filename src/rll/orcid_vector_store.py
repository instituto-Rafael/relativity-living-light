from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping, Sequence

from rll.orcid_vector_model import (
    SCHEMA_VERSION, TOKEN_VAZIO, VECTOR_DIMENSIONS, VECTOR_MODEL,
    ValidationResult, canonical_json, canonicalize_orcid, classify_disciplines,
    cosine, hash_embedding, iter_orcid_works, now, normalize, normalize_doi,
    parse_crossref, parse_datacite, parse_openalex, parse_orcid_summary, sha,
    validate_metadata,
)


class VectorStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.migrate()

    def __enter__(self) -> "VectorStore":
        return self

    def __exit__(self, *_: Any) -> None:
        self.connection.close()

    def migrate(self) -> None:
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY,provider TEXT,source_record_id TEXT,fetched_at TEXT,payload_sha256 TEXT,payload_json TEXT,UNIQUE(provider,source_record_id,payload_sha256));
        CREATE TABLE IF NOT EXISTS artifacts(id INTEGER PRIMARY KEY,logical_id TEXT,revision INTEGER,parent_artifact_id INTEGER,owner_orcid TEXT,title TEXT,abstract TEXT,doi TEXT,publication_year INTEGER,work_type TEXT,journal TEXT,url TEXT,disciplines_json TEXT,discipline_confidence_json TEXT,classification_method TEXT,metadata_state TEXT,claim_allowed INTEGER DEFAULT 0 CHECK(claim_allowed=0),content_sha256 TEXT,created_at TEXT,UNIQUE(logical_id,revision),UNIQUE(logical_id,content_sha256));
        CREATE TABLE IF NOT EXISTS artifact_sources(artifact_id INTEGER,source_id INTEGER,role TEXT,validation_state TEXT,validation_score REAL,details_json TEXT,PRIMARY KEY(artifact_id,source_id,role));
        CREATE TABLE IF NOT EXISTS vectors(artifact_id INTEGER,model TEXT,dimensions INTEGER,vector_json TEXT,text_sha256 TEXT,created_at TEXT,PRIMARY KEY(artifact_id,model));
        CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT,entity_id TEXT,payload_json TEXT,previous_hash TEXT,event_hash TEXT UNIQUE,created_at TEXT);
        """)
        self.connection.commit()

    def append_event(self, kind: str, entity: str, payload: Mapping[str, Any]) -> str:
        row = self.connection.execute("SELECT event_hash FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
        previous = row[0] if row else "0" * 64
        body = canonical_json({"event_type": kind, "entity_id": entity, "payload": payload, "previous_hash": previous})
        event_hash = sha(body)
        self.connection.execute("INSERT INTO events(event_type,entity_id,payload_json,previous_hash,event_hash,created_at) VALUES(?,?,?,?,?,?)", (kind, entity, canonical_json(payload), previous, event_hash, now()))
        return event_hash

    def store_source(self, provider: str, record_id: str, payload: Mapping[str, Any]) -> int:
        payload_json, digest = canonical_json(payload), sha(canonical_json(payload))
        self.connection.execute("INSERT OR IGNORE INTO sources(provider,source_record_id,fetched_at,payload_sha256,payload_json) VALUES(?,?,?,?,?)", (provider, record_id, now(), digest, payload_json))
        return int(self.connection.execute("SELECT id FROM sources WHERE provider=? AND source_record_id=? AND payload_sha256=?", (provider, record_id, digest)).fetchone()[0])

    def latest_artifact(self, logical_id: str) -> sqlite3.Row | None:
        return self.connection.execute("SELECT * FROM artifacts WHERE logical_id=? ORDER BY revision DESC LIMIT 1", (logical_id,)).fetchone()

    def _store(self, artifact: Mapping[str, Any], source_id: int, role: str, validation: ValidationResult | None = None) -> tuple[int, bool]:
        labels, confidence = classify_disciplines(" ".join(str(artifact.get(k) or "") for k in ("title", "abstract", "journal")))
        body = {k: artifact.get(k) for k in ("logical_id", "owner_orcid", "title", "abstract", "doi", "publication_year", "work_type", "journal", "url", "metadata_state")}
        body.update({"disciplines": labels, "claim_allowed": False})
        digest = sha(canonical_json(body))
        existing = self.connection.execute("SELECT id FROM artifacts WHERE logical_id=? AND content_sha256=?", (artifact["logical_id"], digest)).fetchone()
        if existing:
            artifact_id = int(existing[0])
            self.connection.execute("INSERT OR IGNORE INTO artifact_sources VALUES(?,?,?,?,?,?)", (artifact_id, source_id, role, validation.state if validation else artifact.get("metadata_state", TOKEN_VAZIO), validation.score if validation else 0.0, canonical_json(validation.details if validation else {})))
            self.connection.commit()
            return artifact_id, False
        latest = self.latest_artifact(str(artifact["logical_id"]))
        revision = int(latest["revision"]) + 1 if latest else 1
        parent = int(latest["id"]) if latest else None
        cur = self.connection.execute("""INSERT INTO artifacts(logical_id,revision,parent_artifact_id,owner_orcid,title,abstract,doi,publication_year,work_type,journal,url,disciplines_json,discipline_confidence_json,classification_method,metadata_state,claim_allowed,content_sha256,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,?,?)""", (artifact["logical_id"], revision, parent, artifact["owner_orcid"], artifact.get("title") or TOKEN_VAZIO, artifact.get("abstract"), normalize_doi(artifact.get("doi")), artifact.get("publication_year"), artifact.get("work_type"), artifact.get("journal"), artifact.get("url"), canonical_json(labels), canonical_json(confidence), "rll-keyword-v1", artifact.get("metadata_state") or TOKEN_VAZIO, digest, now()))
        artifact_id = int(cur.lastrowid)
        text = " ".join(str(artifact.get(k) or "") for k in ("title", "abstract", "journal"))
        self.connection.execute("INSERT INTO vectors VALUES(?,?,?,?,?,?)", (artifact_id, VECTOR_MODEL, VECTOR_DIMENSIONS, canonical_json(hash_embedding(text)), sha(normalize(text)), now()))
        self.connection.execute("INSERT INTO artifact_sources VALUES(?,?,?,?,?,?)", (artifact_id, source_id, role, validation.state if validation else artifact.get("metadata_state", TOKEN_VAZIO), validation.score if validation else 0.0, canonical_json(validation.details if validation else {})))
        self.append_event("ARTIFACT_REVISION_CREATED", str(artifact["logical_id"]), {"artifact_id": artifact_id, "revision": revision, "content_sha256": digest, "claim_allowed": False})
        self.connection.commit()
        return artifact_id, True

    def ingest_orcid_record(self, record: Mapping[str, Any], owner_orcid: str) -> dict[str, int]:
        owner = canonicalize_orcid(owner_orcid)
        source_id = self.store_source("orcid", owner, record)
        summaries = list(iter_orcid_works(record))
        created = unchanged = empty = 0
        for item in summaries:
            artifact = parse_orcid_summary(item, owner)
            _, was_created = self._store(artifact, source_id, "AUTHOR_REGISTRY")
            created += int(was_created)
            unchanged += int(not was_created)
            empty += int(artifact["title"] == TOKEN_VAZIO)
        self.append_event("ORCID_RECORD_INGESTED", owner, {"works_seen": len(summaries), "created": created, "claim_allowed": False})
        self.connection.commit()
        return {"works_seen": len(summaries), "created": created, "unchanged": unchanged, "token_vazio": empty}

    def enrich_artifact(self, logical_id: str, payload: Mapping[str, Any], *, provider: str) -> tuple[int, bool, ValidationResult]:
        latest = self.latest_artifact(logical_id)
        if latest is None:
            raise KeyError(f"Artefato não encontrado: {logical_id}")
        parsed = parse_crossref(payload) if provider == "crossref" else parse_datacite(payload) if provider == "datacite" else parse_openalex(payload) if provider == "openalex" else (_ for _ in ()).throw(ValueError(f"Provider não suportado: {provider}"))
        source_id = self.store_source(provider, str(parsed["provider_record_id"]), payload)
        validation = validate_metadata(dict(latest), parsed, str(latest["owner_orcid"]))
        merged = {k: latest[k] for k in ("logical_id", "owner_orcid", "title", "abstract", "doi", "publication_year", "work_type", "journal", "url")}
        for key in ("title", "abstract", "doi", "publication_year", "work_type", "journal", "url"):
            if merged.get(key) in (None, "", TOKEN_VAZIO) and parsed.get(key) not in (None, ""):
                merged[key] = parsed[key]
        merged["metadata_state"] = validation.state
        artifact_id, created = self._store(merged, source_id, "METADATA_VALIDATION", validation)
        return artifact_id, created, validation

    def search(self, query: str, *, disciplines: Sequence[str] = (), limit: int = 10, owner_orcid: str | None = None) -> list[dict[str, Any]]:
        query_vector = hash_embedding(query)
        rows = self.connection.execute("""SELECT a.*,v.vector_json FROM artifacts a JOIN vectors v ON v.artifact_id=a.id WHERE a.revision=(SELECT MAX(x.revision) FROM artifacts x WHERE x.logical_id=a.logical_id)""").fetchall()
        output = []
        required = set(disciplines)
        owner = canonicalize_orcid(owner_orcid) if owner_orcid else None
        for row in rows:
            labels = set(json.loads(row["disciplines_json"]))
            if owner and row["owner_orcid"] != owner:
                continue
            if required and not required.issubset(labels):
                continue
            output.append({"logical_id": row["logical_id"], "revision": row["revision"], "title": row["title"], "doi": row["doi"], "publication_year": row["publication_year"], "disciplines": sorted(labels), "metadata_state": row["metadata_state"], "claim_allowed": False, "score": round(cosine(query_vector, json.loads(row["vector_json"])), 8)})
        return sorted(output, key=lambda item: (-item["score"], item["logical_id"]))[:limit]

    def verify_event_chain(self) -> tuple[bool, str]:
        previous = "0" * 64
        for row in self.connection.execute("SELECT * FROM events ORDER BY sequence"):
            body = canonical_json({"event_type": row["event_type"], "entity_id": row["entity_id"], "payload": json.loads(row["payload_json"]), "previous_hash": previous})
            expected = sha(body)
            if row["previous_hash"] != previous or row["event_hash"] != expected:
                return False, previous
            previous = expected
        return True, previous

    def status(self) -> dict[str, Any]:
        ok, tip = self.verify_event_chain()
        scalar = lambda sql: int(self.connection.execute(sql).fetchone()[0])
        return {"schema": SCHEMA_VERSION, "database": str(self.path), "logical_artifacts": scalar("SELECT COUNT(DISTINCT logical_id) FROM artifacts"), "artifact_revisions": scalar("SELECT COUNT(*) FROM artifacts"), "sources": scalar("SELECT COUNT(*) FROM sources"), "events": scalar("SELECT COUNT(*) FROM events"), "token_vazio_revisions": scalar("SELECT COUNT(*) FROM artifacts WHERE metadata_state='TOKEN_VAZIO'"), "vector_model": VECTOR_MODEL, "vector_dimensions": VECTOR_DIMENSIONS, "claim_allowed": False, "event_chain_ok": ok, "event_chain_tip": tip}

    def export_candidates(self, owner_orcid: str | None = None) -> dict[str, Any]:
        owner = canonicalize_orcid(owner_orcid) if owner_orcid else None
        rows = self.connection.execute("SELECT * FROM artifacts a WHERE revision=(SELECT MAX(x.revision) FROM artifacts x WHERE x.logical_id=a.logical_id) ORDER BY publication_year,title").fetchall()
        works = []
        for row in rows:
            if owner and row["owner_orcid"] != owner:
                continue
            works.append({"logical_id": row["logical_id"], "title": row["title"], "doi": row["doi"], "publication_year": row["publication_year"], "metadata_state": row["metadata_state"], "orcid_write_state": "TOKEN_VAZIO_MEMBER_API_OR_MANUAL_REVIEW", "claim_allowed": False})
        return {"schema": "rll.orcid_export.v1", "owner_orcid": owner or TOKEN_VAZIO, "claim_allowed": False, "works": works}

    def markdown_report(self, owner_orcid: str | None = None) -> str:
        status = self.status()
        candidates = self.export_candidates(owner_orcid)
        lines = ["# ORCID ↔ RLL — relatório vetorial", "", f"- Artefatos lógicos: **{status['logical_artifacts']}**", f"- Revisões: **{status['artifact_revisions']}**", f"- Cadeia de eventos: **{'OK' if status['event_chain_ok'] else 'FAIL'}**", "- Claim global: `false`", "", "## Trabalhos"]
        for item in candidates["works"]:
            lines.append(f"- **{item['title']}** — `{item['metadata_state']}` — `{item['logical_id']}`")
        return "\n".join(lines) + "\n"
