#!/usr/bin/env python3
"""Receipt-producing public-source fetcher for the RLL climate registry.

Network access is opt-in. The default action lists or dry-runs sources. The tool
uses Python's standard library rather than wget so status, content type, byte cap
and SHA-256 are captured consistently. It accepts JSON, XML, text and binary data
without interpreting scientific meaning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_filename(source_id: str, content_type: str) -> str:
    suffix = ".bin"
    if "json" in content_type:
        suffix = ".json"
    elif "xml" in content_type:
        suffix = ".xml"
    elif "text" in content_type or "html" in content_type:
        suffix = ".txt"
    return source_id + suffix


def fetch(source: dict[str, Any], output_dir: Path, timeout: float, max_bytes: int) -> dict[str, Any]:
    url = source["sample_url"]
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("only HTTPS is allowed")
    if parsed.hostname != source["domain"]:
        raise ValueError("URL hostname does not match declared source domain")
    request = urllib.request.Request(url, headers={"User-Agent": "RLL-Climate-Custody/1.0"})
    context = ssl.create_default_context()
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        while True:
            chunk = response.read(min(65536, max_bytes - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(f"response exceeds byte cap {max_bytes}")
            digest.update(chunk)
            chunks.append(chunk)
        status = getattr(response, "status", 200)
        final_url = response.geturl()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / safe_filename(source["id"], content_type)
    target.write_bytes(b"".join(chunks))
    return {
        "source_id": source["id"],
        "requested_url": url,
        "final_url": final_url,
        "status": status,
        "content_type": content_type,
        "bytes": total,
        "sha256": digest.hexdigest(),
        "saved_path": str(target),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "scientific_interpretation_performed": False,
        "claim_allowed": False
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="data/climate/rll_climate_source_registry.v1.json")
    parser.add_argument("--source")
    parser.add_argument("--output-dir", default="artifacts/climate_sources")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-bytes", type=int, default=5_000_000)
    parser.add_argument("--execute", action="store_true", help="perform the network GET; otherwise dry-run")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    try:
        registry = load_registry(Path(args.registry))
        sources = {item["id"]: item for item in registry["sources"]}
        if args.list or not args.source:
            print(json.dumps({"sources": sorted(sources), "default_mode": "DRY_RUN", "claim_allowed": False}, indent=2))
            return 0
        if args.source not in sources:
            raise ValueError(f"unknown source {args.source}")
        source = sources[args.source]
        if not args.execute:
            print(json.dumps({
                "mode": "DRY_RUN",
                "source_id": source["id"],
                "url": source["sample_url"],
                "domain": source["domain"],
                "format": source["format"],
                "claim_allowed": False
            }, indent=2))
            return 0
        receipt = fetch(source, Path(args.output_dir), args.timeout, args.max_bytes)
        receipt_path = Path(args.output_dir) / f"{source['id']}.receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    except Exception as exc:  # explicit CLI boundary: return a receipt, not a traceback
        print(json.dumps({"status": "FAIL", "error": str(exc), "claim_allowed": False}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
