#!/usr/bin/env python3
"""Private local SQLite reconstruction adapter; standard library only.

Observed fields are indexed, never promoted to executed/scientific evidence.
The original bytes and duplicate object keys remain recoverable.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import tempfile

KINDS = {1: "object", 2: "array", 3: "string", 4: "number", 5: "bool", 6: "null"}
FIELDS = {
    "repo_id": "repository_reference", "base_commit_sha": "base_commit_reference",
    "previous_turn_id": "previous_turn_reference", "branch": "branch_reference",
    "branch_name": "branch_reference", "external_pull_request_id": "pr_reference",
    "output_diff": "diff_record", "follow_up_diff": "follow_up_record",
    "pull_request_info": "pr_record", "terminal_chunk_citation": "terminal_citation",
    "file_id": "external_file_reference", "missing_reason": "gap_observation",
    "status": "reported_status", "citations": "citation_container",
}
SCHEMA = """
CREATE TABLE IF NOT EXISTS sources(sha256 TEXT PRIMARY KEY, name TEXT, bytes BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS tokens(source TEXT, id INTEGER, kind TEXT, start INTEGER,
 end INTEGER, parent INTEGER, key TEXT, pointer TEXT, value_json TEXT,
 PRIMARY KEY(source,id), FOREIGN KEY(source) REFERENCES sources(sha256));
CREATE TABLE IF NOT EXISTS observations(source TEXT, token INTEGER, category TEXT,
 state TEXT NOT NULL DEFAULT 'OBSERVED_UNPROMOTED', PRIMARY KEY(source,token,category));
CREATE TABLE IF NOT EXISTS references_observed(source TEXT, token INTEGER, relation TEXT,
 target_literal TEXT, resolution TEXT NOT NULL DEFAULT 'PENDING', PRIMARY KEY(source,token,relation));
CREATE TABLE IF NOT EXISTS snapshots(source TEXT, object_token INTEGER, path TEXT,
 content_token INTEGER, sha256 TEXT, scope TEXT, PRIMARY KEY(source,object_token));
CREATE TABLE IF NOT EXISTS candidates(source TEXT, token INTEGER, category TEXT,
 character_start INTEGER, character_end INTEGER, text TEXT, state TEXT,
 PRIMARY KEY(source,token,category,character_start));
CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY, timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
 source TEXT, kind TEXT, summary TEXT, parent INTEGER);
"""

def decode(raw, start, end):
    return json.loads(raw[start:end])

def escape(value):
    return value.replace("~", "~0").replace("/", "~1")

def ingest(db, scanner, path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if db.execute("SELECT 1 FROM sources WHERE sha256=?", (digest,)).fetchone():
        return digest, "ALREADY_PRESENT"
    # Scan the exact bytes hashed, even if the original changes concurrently.
    with tempfile.TemporaryDirectory(prefix="rv3-source-") as temp:
        frozen = Path(temp) / "source.json"
        frozen.write_bytes(raw)
        scanned = subprocess.run([str(scanner.resolve()), str(frozen)],
                                 capture_output=True, check=True, text=True)
    rows = [tuple(map(int, line.split("\t"))) for line in scanned.stdout.splitlines()]
    pointers, indices, members, scalars = {}, {}, {}, {}
    with db:
        db.execute("INSERT INTO sources VALUES(?,?,?)", (digest, path.name, raw))
        for tid, kind, start, end, parent, ks, ke in rows:
            key = decode(raw, ks, ke) if ks >= 0 else None
            if parent < 0:
                pointer = ""
            elif key is not None:
                pointer = pointers[parent] + "/" + escape(key)
            else:
                ordinal = indices.get(parent, 0)
                indices[parent] = ordinal + 1
                pointer = pointers[parent] + "/" + str(ordinal)
            pointers[tid] = pointer
            # Pointer alone is not identity: duplicate keys may share pointers.
            value = decode(raw, start, end) if kind >= 3 else None
            value_json = raw[start:end].decode("utf-8") if kind >= 3 else None
            db.execute("INSERT INTO tokens VALUES(?,?,?,?,?,?,?,?,?)",
                       (digest, tid, KINDS[kind], start, end, parent, key, pointer, value_json))
            members.setdefault(parent, {}).setdefault(key, []).append(tid)
            scalars[tid] = value
            if key in FIELDS:
                category = FIELDS[key]
                db.execute("INSERT INTO observations(source,token,category) VALUES(?,?,?)",
                           (digest, tid, category))
                if category.endswith("reference") and isinstance(value, (str, int)) and not isinstance(value, bool):
                    db.execute("INSERT INTO references_observed(source,token,relation,target_literal) VALUES(?,?,?,?)",
                               (digest, tid, category, json.dumps(value, ensure_ascii=False)))
            if isinstance(value, str):
                # Candidate formulas only. No semantic equivalence/author claim.
                for match in re.finditer(r"\$\$(.+?)\$\$|\\\[(.+?)\\\]", value, re.S):
                    text = match.group(1) or match.group(2)
                    db.execute("INSERT INTO candidates VALUES(?,?,?,?,?,?,?)",
                               (digest, tid, "formula_candidate", match.start(), match.end(), text, "AUDIT"))
        for object_token, fields in members.items():
            path_ids = fields.get("path", []) + fields.get("file_path", [])
            content_ids = fields.get("content", [])
            if len(path_ids) == len(content_ids) == 1:
                observed_path, content = scalars[path_ids[0]], scalars[content_ids[0]]
                if isinstance(observed_path, str) and isinstance(content, str):
                    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    db.execute("INSERT INTO snapshots VALUES(?,?,?,?,?,?)",
                               (digest, object_token, observed_path, content_ids[0], content_hash,
                                "OBSERVED_CONTENT_COMPLETENESS_UNKNOWN"))
        db.execute("INSERT INTO ledger(source,kind,summary) VALUES(?,?,?)",
                   (digest, "INGEST", json.dumps({"tokens": len(rows), "claim_allowed": False})))
    return digest, "INGESTED"

def export_snapshots(db, root):
    """Only explicit path+content candidates; unsafe paths retained in DB only."""
    root = root.resolve()
    for source, obj, path, token in db.execute("SELECT source,object_token,path,content_token FROM snapshots"):
        p = PurePosixPath(path)
        if p.is_absolute() or ".." in p.parts or "\\" in path or "\x00" in path or not p.parts:
            continue
        # Namespace each observation: never pretend this is a Git checkout.
        target = root / source / str(obj) / Path(*p.parts)
        if not target.resolve().is_relative_to(root):
            raise ValueError("snapshot path escapes export root")
        value_json, = db.execute("SELECT value_json FROM tokens WHERE source=? AND id=?",
                                 (source, token)).fetchone()
        content = json.loads(value_json).encode("utf-8")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != content:
                raise ValueError("existing observation differs; refusing overwrite")
        else:
            with target.open("xb") as out:
                out.write(content)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scanner", type=Path, required=True)
    ap.add_argument("--database", type=Path, required=True)
    ap.add_argument("--export-snapshots", type=Path)
    ap.add_argument("sources", nargs="+", type=Path)
    args = ap.parse_args()
    db = sqlite3.connect(args.database)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)
    try:
        for source in args.sources:
            digest, state = ingest(db, args.scanner, source)
            print(json.dumps({"source_sha256": digest, "state": state, "claim_allowed": False}))
        if args.export_snapshots:
            export_snapshots(db, args.export_snapshots)
    finally:
        db.close()

if __name__ == "__main__":
    main()
