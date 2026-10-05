#!/usr/bin/env python3
"""RLL authorial science ingress: stdlib-only source custody/materialization.

Factory/tooling boundary only. This module is not part of the freestanding runtime.
It never promotes downloaded bytes to scientific evidence or a claim by itself.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

TOKEN_VAZIO = "TOKEN_VAZIO"
SCHEMA = "rll.science_ingress_manifest.v1"
ALLOWED_KINDS = {"image", "pdf", "data", "text", "webpage", "archive"}
ALLOWED_CREDENTIALS = {
    "none",
    "pat_actions",
    "pat_agents",
    "pat_env",
    "pat_environments",
}
GITHUB_API_HOST = "api.github.com"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class _RejectCredentialedRedirect(urllib.request.HTTPRedirectHandler):
    """Fail closed before an Authorization-bearing request can follow a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise ValueError("credentialed redirects are forbidden")


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("top-level JSON must be an object")
    return obj


def validate_manifest(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if doc.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false for source-ingress manifests")
    sources = doc.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        return errors
    seen: set[str] = set()
    for idx, source in enumerate(sources):
        prefix = f"sources[{idx}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix}: must be object")
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append(f"{prefix}.id: required string")
        elif sid in seen:
            errors.append(f"{prefix}.id: duplicate {sid}")
        else:
            seen.add(sid)
        kind = source.get("kind")
        if kind not in ALLOWED_KINDS:
            errors.append(f"{prefix}.kind: invalid {kind!r}")
        url = source.get("url")
        if not isinstance(url, str):
            errors.append(f"{prefix}.url: required string")
        else:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{prefix}.url: only absolute https URLs are allowed")
        filename = source.get("filename")
        if not isinstance(filename, str) or not SAFE_NAME_RE.fullmatch(filename):
            errors.append(f"{prefix}.filename: unsafe or missing")
        expected = source.get("expected_sha256")
        if expected != TOKEN_VAZIO and not (
            isinstance(expected, str) and SHA256_RE.fullmatch(expected)
        ):
            errors.append(
                f"{prefix}.expected_sha256: must be lowercase sha256 or TOKEN_VAZIO"
            )
        max_bytes = source.get("max_bytes")
        if (
            not isinstance(max_bytes, int)
            or isinstance(max_bytes, bool)
            or not (1 <= max_bytes <= 2_147_483_648)
        ):
            errors.append(f"{prefix}.max_bytes: integer 1..2147483648 required")
        credential = source.get("credential_profile", "none")
        if credential not in ALLOWED_CREDENTIALS:
            errors.append(f"{prefix}.credential_profile: invalid {credential!r}")
        if credential != "none":
            parsed = urllib.parse.urlparse(str(url))
            if parsed.hostname != GITHUB_API_HOST:
                errors.append(f"{prefix}: PAT profiles are restricted to api.github.com")
            if "/contents/" not in parsed.path:
                errors.append(
                    f"{prefix}: PAT profiles require GitHub contents API URL"
                )
        authority = source.get("authority")
        if not isinstance(authority, str) or not authority:
            errors.append(f"{prefix}.authority: required")
        license_state = source.get("license")
        if not isinstance(license_state, str) or not license_state:
            errors.append(f"{prefix}.license: required; TOKEN_VAZIO is valid")
    return errors


def _read_bounded(response: Any, max_bytes: int) -> bytes:
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"source exceeds max_bytes={max_bytes}")
    return data


def _decode_github_contents(payload: bytes) -> bytes:
    doc = json.loads(payload.decode("utf-8"))
    if (
        not isinstance(doc, dict)
        or doc.get("encoding") != "base64"
        or not isinstance(doc.get("content"), str)
    ):
        raise ValueError("GitHub contents response must contain base64 content")
    return base64.b64decode(doc["content"], validate=False)


def _kind_check(kind: str, data: bytes) -> bool:
    if kind == "pdf":
        return data.startswith(b"%PDF-")
    if kind == "image":
        return (
            data.startswith(b"\x89PNG\r\n\x1a\n")
            or data.startswith(b"\xff\xd8\xff")
            or data.startswith((b"GIF87a", b"GIF89a"))
        )
    if kind == "data":
        if not data:
            return False
        try:
            json.loads(data.decode("utf-8"))
            return True
        except Exception:  # noqa: BLE001
            return b"," in data or b"\t" in data or b"\n" in data
    if kind in {"text", "webpage"}:
        try:
            data.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    if kind == "archive":
        return data.startswith((b"PK\x03\x04", b"\x1f\x8b"))
    return False


def acquire_source(
    source: dict[str, Any],
    out_dir: Path,
    token: str | None,
    allow_unpinned: bool,
) -> dict[str, Any]:
    expected = source["expected_sha256"]
    if expected == TOKEN_VAZIO and not allow_unpinned:
        raise ValueError(
            f"{source['id']}: expected_sha256 is TOKEN_VAZIO; "
            "pass --allow-unpinned only for discovery"
        )
    credential = source.get("credential_profile", "none")
    url = source["url"]
    headers = {"User-Agent": "RLL-authorial-science-ingress/1"}
    if credential != "none":
        if not token:
            raise ValueError(f"{source['id']}: selected credential profile is absent")
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname != GITHUB_API_HOST or "/contents/" not in parsed.path:
            raise ValueError(
                f"{source['id']}: credentialed URL is outside bounded GitHub contents API"
            )
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"

    request = urllib.request.Request(url, headers=headers, method="GET")
    if credential != "none":
        opener = urllib.request.build_opener(_RejectCredentialedRedirect())
        response_context = opener.open(request, timeout=30)
    else:
        response_context = urllib.request.urlopen(request, timeout=30)

    with response_context as response:
        final_url = response.geturl()
        parsed_final = urllib.parse.urlparse(final_url)
        if parsed_final.scheme != "https":
            raise ValueError(f"{source['id']}: redirect left https")
        if credential != "none" and parsed_final.hostname != GITHUB_API_HOST:
            raise ValueError(f"{source['id']}: credentialed response left api.github.com")
        payload = _read_bounded(response, int(source["max_bytes"]))
    data = _decode_github_contents(payload) if credential != "none" else payload

    if len(data) > int(source["max_bytes"]):
        raise ValueError(f"{source['id']}: decoded source exceeds max_bytes")
    if not _kind_check(source["kind"], data):
        raise ValueError(
            f"{source['id']}: kind signature check failed for {source['kind']}"
        )
    digest = hashlib.sha256(data).hexdigest()
    pinned = expected != TOKEN_VAZIO
    if pinned and digest != expected:
        raise ValueError(f"{source['id']}: sha256 mismatch")

    target = out_dir / source["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {
        "id": source["id"],
        "filename": source["filename"],
        "bytes": len(data),
        "sha256": digest,
        "expected_sha256": expected,
        "hash_state": "VERIFIED_PINNED" if pinned else "OBSERVED_UNPINNED",
        "credential_profile": credential,
        "credential_present_boolean": bool(token) if credential != "none" else False,
        "source_url": url,
        "authority": source["authority"],
        "license": source["license"],
    }


def audit_payload(
    manifest_path: Path, doc: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    return {
        "schema": "rll.science_ingress.audit.v1",
        "manifest": manifest_path.as_posix(),
        "decision": "PASS_STATIC" if not errors else "FAIL",
        "claim_allowed": False,
        "source_artifact_execution_evidence_claim_separated": True,
        "errors": errors,
        "source_count": (
            len(doc.get("sources", [])) if isinstance(doc.get("sources"), list) else 0
        ),
    }


def cmd_audit(args: argparse.Namespace) -> int:
    doc = load_json(args.manifest)
    errors = validate_manifest(doc)
    payload = audit_payload(args.manifest, doc, errors)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def cmd_materialize(args: argparse.Namespace) -> int:
    doc = load_json(args.manifest)
    errors = validate_manifest(doc)
    receipt: dict[str, Any] = {
        "schema": "rll.science_ingress.receipt.v1",
        "manifest": args.manifest.as_posix(),
        "claim_allowed": False,
        "scientific_confirmation": False,
        "network_execution": True,
        "results": [],
        "errors": list(errors),
    }
    if errors:
        receipt["decision"] = "FAIL_STATIC"
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return 2

    profile = args.credential_profile
    token = os.environ.get("RLL_INGRESS_TOKEN") if profile != "none" else None
    try:
        for source in doc["sources"]:
            source_profile = source.get("credential_profile", "none")
            if source_profile != profile and source_profile != "none":
                raise ValueError(
                    f"{source['id']}: manifest credential_profile={source_profile} "
                    f"does not match selected profile={profile}"
                )
            source_token = token if source_profile != "none" else None
            receipt["results"].append(
                acquire_source(source, args.out, source_token, args.allow_unpinned)
            )
    except Exception as exc:  # noqa: BLE001
        receipt["errors"].append(str(exc))
        receipt["decision"] = "FAIL"
    else:
        states = {item["hash_state"] for item in receipt["results"]}
        receipt["decision"] = (
            "PASS_PINNED" if states == {"VERIFIED_PINNED"} else "OBSERVED_UNPINNED"
        )
    receipt["credential_profile_selected"] = profile
    receipt["credential_value_observed"] = False
    receipt["credential_value_hashed"] = False
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"decision": receipt["decision"], "receipt": args.receipt.as_posix()},
            ensure_ascii=False,
        )
    )
    return 0 if receipt["decision"] in {"PASS_PINNED", "OBSERVED_UNPINNED"} else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("manifest", type=Path)
    audit.set_defaults(func=cmd_audit)
    materialize = sub.add_parser("materialize")
    materialize.add_argument("manifest", type=Path)
    materialize.add_argument("--out", type=Path, required=True)
    materialize.add_argument("--receipt", type=Path, required=True)
    materialize.add_argument(
        "--credential-profile",
        choices=sorted(ALLOWED_CREDENTIALS),
        default="none",
    )
    materialize.add_argument("--allow-unpinned", action="store_true")
    materialize.set_defaults(func=cmd_materialize)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
