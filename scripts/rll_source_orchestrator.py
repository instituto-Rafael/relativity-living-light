#!/usr/bin/env python3
"""RLL public literature metadata intake: Nature journals (Crossref) + Zenodo.

Standard library only. Metadata is NOT a scientific result. No PDF, dataset,
credential, article text, build, or database write. Live fetch is opt-in.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

NATURE_ISSN = {
    "nature": "0028-0836",
    "nature-communications": "2041-1723",
    "nature-astronomy": "2397-3366",
}
MAX_BYTES = 2_000_000
SCHEMA = "rll.science_sources.v1"
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
QUERY_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{3,80}$")


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha256(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def doi_key(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    v = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)", "", value.strip(), flags=re.I)
    v = v.lower()
    return v if DOI_PATTERN.fullmatch(v) else None


def display(value: object, maximum: int = 220) -> str:
    if isinstance(value, list):
        value = next((v for v in value if isinstance(v, str)), "")
    return " ".join(value.split())[:maximum] if isinstance(value, str) else ""


def date_parts(value: object) -> str | None:
    if isinstance(value, dict):
        parts = value.get("date-parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], list):
            nums = parts[0][:3]
            if nums and isinstance(nums[0], int):
                return "-".join(str(v).zfill(2) if i else str(v) for i, v in enumerate(nums))
    return None


def crossref_records(payload: dict, journal: str) -> list[dict]:
    message = payload.get("message")
    items = message.get("items") if isinstance(message, dict) else None
    if not isinstance(items, list):
        raise ValueError("Crossref missing message.items")
    records = []
    for item in items:
        if not isinstance(item, dict):
            continue
        doi = doi_key(item.get("DOI"))
        if not doi:
            continue
        license_info = item.get("license") or []
        licenses = sorted({display(l.get("URL"), 300) for l in license_info
                          if isinstance(l, dict) and l.get("URL")}) if isinstance(license_info, list) else []
        authors = item.get("author") or []
        people = [display(" ".join(str(a.get(k, "")) for k in ("given", "family")).strip(), 100)
                  for a in authors[:12] if isinstance(a, dict)] if isinstance(authors, list) else []
        records.append({
            "provider": "crossref", "collection": journal,
            "provider_record_id": doi, "doi": doi,
            "title": display(item.get("title")) or "TOKEN_VAZIO",
            "authors": [p for p in people if p], "published": date_parts(item.get("published")),
            "container": display(item.get("container-title")),
            "record_url": "https://doi.org/" + doi,
            "license_refs": licenses, "metadata_sha256": sha256(item),
            "content_downloaded": False,
        })
    return records


def zenodo_records(payload: dict) -> list[dict]:
    envelope = payload.get("hits")
    hits = envelope.get("hits") if isinstance(envelope, dict) else None
    if not isinstance(hits, list):
        raise ValueError("Zenodo missing hits.hits")
    result = []
    for item in hits:
        if not isinstance(item, dict):
            continue
        meta = item.get("metadata") or {}
        if not isinstance(meta, dict):
            continue
        ident = str(item.get("id", ""))
        if not re.fullmatch(r"[0-9]{1,24}", ident):
            continue
        doi = doi_key(item.get("doi") or meta.get("doi"))
        lic = meta.get("license")
        lic_id = display(lic.get("id") if isinstance(lic, dict) else lic, 100)
        creators = meta.get("creators") or []
        people = [display(a.get("name") or (a.get("person_or_org") or {}).get("name"), 100)
                  for a in creators[:12] if isinstance(a, dict)] if isinstance(creators, list) else []
        result.append({
            "provider": "zenodo", "collection": "public-records",
            "provider_record_id": ident, "doi": doi,
            "title": display(meta.get("title")) or "TOKEN_VAZIO",
            "authors": [p for p in people if p],
            "published": display(meta.get("publication_date"), 24) or None,
            "container": "Zenodo",
            "record_url": "https://zenodo.org/records/" + ident,
            "license_refs": [lic_id] if lic_id else [],
            "metadata_sha256": sha256(item),
            "content_downloaded": False,
        })
    return result


def merge(records: list[dict]) -> list[dict]:
    by_key = {}
    for record in records:
        # Missing DOI gets a namespaced provider identity, never title matching.
        key = "doi:" + record["doi"] if record["doi"] else (
            record["provider"] + ":" + record["provider_record_id"])
        by_key.setdefault(key, []).append(record)
    merged = []
    for key, observations in sorted(by_key.items()):
        observations.sort(key=lambda r: (r["provider"], r["collection"], r["provider_record_id"]))
        titles = {r["title"].casefold() for r in observations if r["title"] != "TOKEN_VAZIO"}
        merged.append({
            "key": key, "doi": observations[0]["doi"],
            "observations": observations,
            "metadata_title_disagreement": len(titles) > 1,
            "cross_source_identity": len({r["provider"] for r in observations}) > 1,
            "claim_allowed": False,
        })
    return merged


class _SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).netloc != urlsplit(req.full_url).netloc or (
                urlsplit(newurl).scheme != "https"):
            raise ValueError("Cross-host redirect disallowed")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_json(url: str) -> dict:
    host = urlsplit(url)
    if host.scheme != "https" or host.hostname not in {"api.crossref.org", "zenodo.org"}:
        raise ValueError("Provider host not allowlisted")
    req = Request(url, headers={"Accept": "application/json",
                               "User-Agent": "RLL-Science-Source-Intake/1.0 (GitHub institute-Rafael; read-only)"})
    with build_opener(_SameHostRedirect()).open(req, timeout=18) as response:
        if response.status != 200:
            raise ValueError("HTTP response not OK")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Provider response exceeds 2MB bound")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Provider response root must be JSON object")
    return value


def endpoints(query: str, limit: int, journals: list[str]) -> list[tuple[str, str]]:
    if not QUERY_PATTERN.fullmatch(query):
        raise ValueError("Query must be 3-80 characters: letters, numbers, spaces, _ or -")
    if not (1 <= limit <= 20):
        raise ValueError("limit must be 1..20")
    urls = []
    for journal in sorted(set(journals)):
        if journal not in NATURE_ISSN:
            raise ValueError("Unrecognized journal")
        url = "https://api.crossref.org/journals/" + NATURE_ISSN[journal] + "/works?" + urlencode({
            "query.bibliographic": query,
            "rows": limit,
            "select": "DOI,title,author,published,container-title,license",
        })
        urls.append(("crossref:" + journal, url))
    urls.append(("zenodo", "https://zenodo.org/api/records/?" + urlencode({
        "q": query, "size": min(limit, 20), "page": 1, "sort": "bestmatch",
    })))
    return urls


def collect(query: str, limit: int, journals: list[str], fetch, observed_at: str) -> dict:
    rows = []
    provider_status = {}
    for name, url in endpoints(query, limit, journals):
        try:
            data = fetch(url)
            values = zenodo_records(data) if name == "zenodo" else crossref_records(
                data, name.split(":", 1)[1])
            rows.extend(values[:limit])
            provider_status[name] = {"status": "OBSERVED", "records": len(values[:limit]),
                                     "request_url": url}
        except (ValueError, KeyError, TypeError, HTTPError, URLError,
                OSError, TimeoutError, json.JSONDecodeError) as exc:
            provider_status[name] = {"status": "TOKEN_VAZIO",
                                     "error_type": type(exc).__name__, "request_url": url}
    return {
        "schema": SCHEMA, "observed_at": observed_at, "query": query,
        "limit_per_source": limit, "provider_status": provider_status,
        "records": merge(rows), "total_unique": len(merge(rows)),
        "all_sources_observed": all(v["status"] == "OBSERVED" for v in provider_status.values()),
        "kind": "BIBLIOGRAPHIC_METADATA_ONLY",
        "scientific_validation": False, "claim_allowed": False,
        "raw_text_downloaded": False, "download_performed": False,
        "requires_review": True,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=["offline", "live"], default="offline")
    p.add_argument("--query", default="cosmology")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--journal", action="append", choices=sorted(NATURE_ISSN))
    p.add_argument("--output", type=Path, default=Path("artifacts/rll-science-sources/catalog.json"))
    args = p.parse_args(argv)
    journals = args.journal or ["nature", "nature-communications"]
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if args.mode == "offline":
        # A deterministic non-network contract probe; never presented as harvested papers.
        def offline(url: str) -> dict:
            return {"hits": {"hits": []}} if "zenodo.org" in url else {"message": {"items": []}}
        result = collect(args.query, args.limit, journals, offline, stamp)
        result["mode"] = "OFFLINE_CONTRACT_TEST"
        result["all_sources_observed"] = False
        for provider in result["provider_status"].values():
            provider["status"] = "NOT_RUN"
        # Tests assert syntax and bounded parser outputs, not real retrieval.
    else:
        result = collect(args.query, args.limit, journals, get_json, stamp)
        result["mode"] = "LIVE_METADATA_FETCH"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    data = canonical(result) + b"\n"
    args.output.write_bytes(data)
    receipt = {"schema": "rll.science_sources.receipt.v1",
               "catalog_sha256": hashlib.sha256(data).hexdigest(),
               "catalog_path": str(args.output), "mode": result["mode"],
               "all_sources_observed": result["all_sources_observed"],
               "claim_allowed": False, "observed_at": stamp}
    (args.output.parent / "receipt.json").write_bytes(canonical(receipt) + b"\n")
    print(json.dumps({"mode": result["mode"], "catalog": str(args.output),
                      "unique": result["total_unique"],
                      "provider_status": {k: v["status"] for k, v in result["provider_status"].items()},
                      "claim_allowed": False}, sort_keys=True))
    return 0 if args.mode == "offline" or result["all_sources_observed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
