from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from rx.http import RxHttpError, get_bytes


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "real_sources" / "real_data_registry.json"
MANIFEST = ROOT / "data" / "real_sources" / "real_data_manifest.json"

ALLOWED_HOSTS = {"raw.githubusercontent.com"}
ALLOWED_PATH_PREFIXES = {
    "raw.githubusercontent.com": "/PantheonPlusSH0ES/DataRelease/",
}
MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def iter_candidate_files(registry: dict, dataset_id: str | None):
    for dataset in registry.get("datasets", []):
        if dataset_id and dataset.get("id") != dataset_id:
            continue
        for entry in dataset.get("candidate_remote_files", []):
            yield dataset, entry


def validate_candidate_url(url: str) -> dict:
    parsed = urlsplit(str(url))
    if parsed.scheme != "https":
        raise ValueError("https_required")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("host_not_allowlisted")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("userinfo_forbidden")
    if parsed.query:
        raise ValueError("query_forbidden")
    if parsed.fragment:
        raise ValueError("fragment_forbidden")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid_port") from exc
    if port is not None:
        raise ValueError("custom_port_forbidden")
    prefix = ALLOWED_PATH_PREFIXES.get(parsed.hostname, "")
    if not prefix or not parsed.path.startswith(prefix):
        raise ValueError("path_not_allowlisted")
    return {
        "host": parsed.hostname,
        "path_prefix": prefix,
        "https": True,
    }


def _atomic_write_bytes(dst: Path, payload: bytes) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    try:
        tmp.write_bytes(payload)
        os.replace(tmp, dst)
    finally:
        if tmp.exists():
            tmp.unlink()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def download_first_available(urls: list[str], dst: Path, timeout: int = 30) -> dict:
    errors: list[str] = []
    for url in urls:
        try:
            policy = validate_candidate_url(url)
            data = get_bytes(
                url,
                allowed_hosts=ALLOWED_HOSTS,
                timeout=min(int(timeout), 30),
                max_bytes=MAX_DOWNLOAD_BYTES,
                user_agent="RLL-Real-Data-Materializer/2.0",
            )
            _atomic_write_bytes(dst, data)
            return {
                "ok": True,
                "url": url,
                "network_policy": policy,
                "local_path": _display_path(dst),
                "bytes": len(data),
                "sha256": sha256_file(dst),
                "max_download_bytes": MAX_DOWNLOAD_BYTES,
                "errors": errors,
            }
        except (RxHttpError, ValueError, OSError) as exc:
            errors.append(f"{url}: {exc.__class__.__name__}:{exc}")
    return {
        "ok": False,
        "url": None,
        "local_path": _display_path(dst),
        "bytes": None,
        "sha256": None,
        "max_download_bytes": MAX_DOWNLOAD_BYTES,
        "errors": errors,
    }


def materialize(
    dataset_id: str | None,
    dry_run: bool,
    authorize_network_materialization: bool = False,
) -> dict:
    if not dry_run and not authorize_network_materialization:
        raise PermissionError(
            "network materialization requires explicit "
            "--authorize-network-materialization"
        )

    registry = load_registry()
    results = []
    for dataset, entry in iter_candidate_files(registry, dataset_id):
        dst = ROOT / entry["local_path"]
        candidate_urls = list(entry.get("urls", []))
        policy_checks = []
        for url in candidate_urls:
            try:
                policy_checks.append({"url": url, "allowed": True, **validate_candidate_url(url)})
            except ValueError as exc:
                policy_checks.append({"url": url, "allowed": False, "reason": str(exc)})

        item = {
            "dataset_id": dataset.get("id"),
            "local_path": entry["local_path"],
            "candidate_urls": candidate_urls,
            "url_policy_checks": policy_checks,
            "note": entry.get("note"),
            "already_exists": dst.exists(),
        }
        if dst.exists():
            item.update({
                "ok": True,
                "materialized": False,
                "bytes": dst.stat().st_size,
                "sha256": sha256_file(dst),
            })
        elif dry_run:
            item.update({
                "ok": None,
                "materialized": False,
                "bytes": None,
                "sha256": None,
            })
        else:
            dl = download_first_available(candidate_urls, dst)
            item.update(dl)
            item["materialized"] = bool(dl.get("ok"))
        results.append(item)

    manifest = {
        "schema": "rll.real_data_materialization_manifest.v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "registry": str(REGISTRY.relative_to(ROOT)),
        "dataset_filter": dataset_id,
        "dry_run": dry_run,
        "network_materialization_authorized": bool(authorize_network_materialization),
        "network_policy": {
            "https_only": True,
            "allowed_hosts": sorted(ALLOWED_HOSTS),
            "allowed_path_prefixes": ALLOWED_PATH_PREFIXES,
            "query_fragment_custom_port": "FORBIDDEN",
            "max_download_bytes": MAX_DOWNLOAD_BYTES,
            "network_write": False,
        },
        "results": results,
        "claim_boundary": registry.get("claim_boundary"),
        "claim_allowed": False,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize declared real-data files with bounded read-only network policy."
    )
    parser.add_argument("--dataset", default=None, help="Optional dataset id, e.g. pantheon_plus_shoes")
    parser.add_argument("--dry-run", action="store_true", help="Do not download; show planned materialization and URL policy.")
    parser.add_argument(
        "--authorize-network-materialization",
        action="store_true",
        help="Explicit human opt-in required before any remote download.",
    )
    args = parser.parse_args()

    if args.dry_run and args.authorize_network_materialization:
        raise SystemExit("--dry-run and --authorize-network-materialization are mutually exclusive")

    try:
        manifest = materialize(
            dataset_id=args.dataset,
            dry_run=args.dry_run,
            authorize_network_materialization=args.authorize_network_materialization,
        )
    except PermissionError as exc:
        print(str(exc))
        raise SystemExit(3)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))

    failed = [r for r in manifest["results"] if r.get("ok") is False]
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
