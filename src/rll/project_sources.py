from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VECTOR_MODEL = "rll-hash32-v1"
VECTOR_DIMENSIONS = 32
TOKEN_VAZIO = "TOKEN_VAZIO"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text)
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def embedding(text: str) -> list[float]:
    vector = [0.0] * VECTOR_DIMENSIONS
    for token in re.findall(r"[a-z0-9]+", normalize(text)):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_DIMENSIONS
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[index] += sign * (1.0 + math.log1p(len(token)))
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "rll.project_sources_manifest.v1":
        raise ValueError("schema de manifesto inválido")
    if data.get("claim_allowed") is not False or data.get("raw_bodies_committed") is not False:
        raise ValueError("manifesto viola fronteira de claim/privacidade")
    sources = data.get("sources")
    if not isinstance(sources, list) or data.get("source_count") != len(sources):
        raise ValueError("source_count inconsistente")
    source_ids = [item.get("source_id") for item in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source_id duplicado")
    return data


def chunks(text: str, limit: int = 1800) -> Iterable[tuple[str, str]]:
    title = "ROOT"
    buffer: list[str] = []
    size = 0

    def flush() -> tuple[str, str] | None:
        nonlocal buffer, size
        body = "\n".join(buffer).strip()
        buffer, size = [], 0
        return (title, body) if body else None

    for line in text.splitlines():
        if re.match(r"^#{1,4}\s+", line.strip()):
            item = flush()
            if item:
                yield item
            title = re.sub(r"^#{1,4}\s+", "", line.strip())
            continue
        if size + len(line) + 1 > limit:
            item = flush()
            if item:
                yield item
        buffer.append(line)
        size += len(line) + 1
    item = flush()
    if item:
        yield item


class ProjectCorpus:
    def __init__(self, db: Path | str):
        self.path = Path(db)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(self.path)
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE IF NOT EXISTS project_documents(
              source_id TEXT PRIMARY KEY,
              display_name TEXT,
              content_sha256 TEXT,
              size_bytes INTEGER,
              line_count INTEGER,
              temporal_state TEXT,
              rll_relation TEXT,
              visibility TEXT,
              ingestion_policy TEXT,
              summary TEXT,
              claim_allowed INTEGER DEFAULT 0 CHECK(claim_allowed=0),
              verification_state TEXT,
              body_stored INTEGER DEFAULT 0 CHECK(body_stored IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS project_chunks(
              source_id TEXT,
              chunk_index INTEGER,
              heading TEXT,
              body TEXT,
              body_sha256 TEXT,
              vector_json TEXT,
              claim_allowed INTEGER DEFAULT 0 CHECK(claim_allowed=0),
              PRIMARY KEY(source_id,chunk_index)
            );
            CREATE TABLE IF NOT EXISTS project_events(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,
              event_type TEXT,
              source_id TEXT,
              payload_json TEXT,
              previous_hash TEXT,
              event_hash TEXT UNIQUE
            );
            """
        )
        self.con.commit()

    def __enter__(self) -> "ProjectCorpus":
        return self

    def __exit__(self, *_: Any) -> None:
        self.con.close()

    def event(self, kind: str, source_id: str, payload: Mapping[str, Any]) -> str:
        row = self.con.execute(
            "SELECT event_hash FROM project_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous = row[0] if row else "0" * 64
        event_hash = hashlib.sha256(
            canonical_json(
                {
                    "event_type": kind,
                    "source_id": source_id,
                    "payload": payload,
                    "previous_hash": previous,
                }
            ).encode()
        ).hexdigest()
        self.con.execute(
            "INSERT INTO project_events(event_type,source_id,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?)",
            (kind, source_id, canonical_json(payload), previous, event_hash),
        )
        return event_hash

    def ingest(self, manifest: Mapping[str, Any], root: Path) -> dict[str, int]:
        counts = {"verified": 0, "pointer_only": 0, "chunks": 0, "missing": 0, "mismatch": 0}
        for item in manifest["sources"]:
            source_id = item["source_id"]
            policy = item["ingestion_policy"]
            state = "POINTER_ONLY"
            body_stored = 0
            parts: list[tuple[str, str]] = []
            filename = item.get("local_filename")
            if policy == "ingest":
                path = root / filename if filename else None
                if not path or not path.is_file():
                    state = "TOKEN_VAZIO_MISSING_LOCAL_FILE"
                    counts["missing"] += 1
                else:
                    raw = path.read_bytes()
                    actual = digest_bytes(raw)
                    if actual != item["content_sha256"]:
                        state = "HASH_MISMATCH"
                        counts["mismatch"] += 1
                    else:
                        state = "VERIFIED_LOCAL_HASH"
                        counts["verified"] += 1
                        body_stored = 1
                        parts = list(chunks(raw.decode("utf-8-sig", errors="replace")))
            else:
                counts["pointer_only"] += 1

            self.con.execute(
                """
                INSERT INTO project_documents VALUES(?,?,?,?,?,?,?,?,?,?,0,?,?)
                ON CONFLICT(source_id) DO UPDATE SET
                  display_name=excluded.display_name,
                  content_sha256=excluded.content_sha256,
                  size_bytes=excluded.size_bytes,
                  line_count=excluded.line_count,
                  temporal_state=excluded.temporal_state,
                  rll_relation=excluded.rll_relation,
                  visibility=excluded.visibility,
                  ingestion_policy=excluded.ingestion_policy,
                  summary=excluded.summary,
                  verification_state=excluded.verification_state,
                  body_stored=excluded.body_stored
                """,
                (
                    source_id,
                    item["display_name"],
                    item["content_sha256"],
                    item["size_bytes"],
                    item["line_count"],
                    item["temporal_state"],
                    item["rll_relation"],
                    item["visibility"],
                    policy,
                    item["summary"],
                    state,
                    body_stored,
                ),
            )
            if body_stored:
                self.con.execute("DELETE FROM project_chunks WHERE source_id=?", (source_id,))
                for index, (heading, body) in enumerate(parts):
                    self.con.execute(
                        "INSERT INTO project_chunks VALUES(?,?,?,?,?,?,0)",
                        (
                            source_id,
                            index,
                            heading,
                            body,
                            digest_bytes(body.encode()),
                            canonical_json(embedding(heading + "\n" + body)),
                        ),
                    )
                counts["chunks"] += len(parts)
            self.event(
                "PROJECT_SOURCE_INGESTED",
                source_id,
                {"verification_state": state, "chunks": len(parts), "claim_allowed": False},
            )
        self.con.commit()
        return counts

    def search(self, query: str, limit: int = 10, relation: str | None = None) -> list[dict[str, Any]]:
        query_vector = embedding(query)
        rows = self.con.execute(
            """
            SELECT d.source_id,d.display_name,d.rll_relation,d.visibility,d.verification_state,
                   c.chunk_index,c.heading,c.body,c.vector_json
              FROM project_chunks c JOIN project_documents d USING(source_id)
            """
        ).fetchall()
        output: list[dict[str, Any]] = []
        for row in rows:
            if relation and row["rll_relation"] != relation:
                continue
            output.append(
                {
                    "source_id": row["source_id"],
                    "display_name": row["display_name"],
                    "rll_relation": row["rll_relation"],
                    "visibility": row["visibility"],
                    "verification_state": row["verification_state"],
                    "chunk_index": row["chunk_index"],
                    "heading": row["heading"],
                    "snippet": row["body"][:240].replace("\n", " "),
                    "score": round(cosine(query_vector, json.loads(row["vector_json"])), 8),
                    "claim_allowed": False,
                }
            )
        return sorted(
            output,
            key=lambda item: (-item["score"], item["source_id"], item["chunk_index"]),
        )[:limit]

    def status(self) -> dict[str, Any]:
        scalar = lambda query: int(self.con.execute(query).fetchone()[0])
        return {
            "documents": scalar("SELECT COUNT(*) FROM project_documents"),
            "chunks": scalar("SELECT COUNT(*) FROM project_chunks"),
            "verified": scalar("SELECT COUNT(*) FROM project_documents WHERE verification_state='VERIFIED_LOCAL_HASH'"),
            "pointer_only": scalar("SELECT COUNT(*) FROM project_documents WHERE verification_state='POINTER_ONLY'"),
            "claim_allowed": False,
            "vector_model": VECTOR_MODEL,
        }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="rll-project-sources")
    root.add_argument("--db", type=Path, default=Path("artifacts/orcid_rll/orcid_rll.sqlite3"))
    commands = root.add_subparsers(dest="cmd", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("--manifest", type=Path, default=Path("configs/project_sources_manifest.v1.json"))
    ingest.add_argument("--source-root", type=Path, required=True)
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--relation")
    search.add_argument("--limit", type=int, default=10)
    commands.add_parser("status")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        with ProjectCorpus(args.db) as corpus:
            if args.cmd == "ingest":
                output: Any = {
                    "ingest": corpus.ingest(load_manifest(args.manifest), args.source_root),
                    "status": corpus.status(),
                }
            elif args.cmd == "search":
                output = corpus.search(args.query, args.limit, args.relation)
            else:
                output = corpus.status()
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError, sqlite3.Error) as error:
        print(f"rll-project-sources: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
