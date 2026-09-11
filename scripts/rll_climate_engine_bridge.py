#!/usr/bin/env python3
"""Zero-trust Climate Engine bridge for RLL.

The bridge treats Climate Engine as an EXTERNAL_COMPUTE_AND_VISUALIZATION
provider. It does not treat the provider as the primary sensor/source authority,
and it never promotes visualization, correlation, residual or provider agreement
into a causal claim.

SOURCE != COMPUTE_PROVIDER != EVIDENCE != CLAIM
VISUALIZATION != EVIDENCE
RESIDUAL != CAUSE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

REGISTRY_PATH = Path("data/climate/rll_external_compute_registry.v1.json")
CONTRACT_PATH = Path("data/contracts/rll_climate_engine_bridge.v1.json")
MAX_BYTES_DEFAULT = 8 * 1024 * 1024
TIMEOUT_DEFAULT = 30
REDACT_KEYS = {"authorization", "api_key", "apikey", "token", "tile_fetcher"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def provider_spec(registry: dict[str, Any], provider_id: str = "climate_engine") -> dict[str, Any]:
    for provider in registry.get("providers", []):
        if provider.get("id") == provider_id:
            return provider
    raise ValueError(f"provider not declared: {provider_id}")


def validate_allowed_url(url: str, allowed_host: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("external compute URL must use HTTPS")
    if parsed.hostname != allowed_host:
        raise ValueError(f"external compute host not allowed: {parsed.hostname}")


def compact_coordinates(value: str) -> str:
    parsed = json.loads(value)
    if not isinstance(parsed, list) or not parsed:
        raise ValueError("coordinates must be a non-empty JSON list")
    return json.dumps(parsed, separators=(",", ":"))


def build_request(operation: str, args: argparse.Namespace, provider: dict[str, Any]) -> str:
    operations = provider["operations"]
    if operation not in operations:
        raise ValueError(f"unsupported operation: {operation}")

    params: dict[str, str] = {}
    if operation in {"metadata_dates", "metadata_variables"}:
        if not args.dataset:
            raise ValueError("--dataset is required")
        params["dataset"] = args.dataset

    elif operation == "timeseries_coordinates":
        required = {
            "dataset": args.dataset,
            "variable": args.variable,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "coordinates": args.coordinates,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing required parameters: {missing}")
        params.update({
            "dataset": args.dataset,
            "variable": args.variable,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "coordinates": compact_coordinates(args.coordinates),
            "area_reducer": args.area_reducer,
        })

    elif operation == "map_values":
        required = {
            "dataset": args.dataset,
            "variable": args.variable,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "temporal_statistic": args.temporal_statistic,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"missing required parameters: {missing}")
        params.update({
            "dataset": args.dataset,
            "variable": args.variable,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "temporal_statistic": args.temporal_statistic,
            "colormap_opacity": str(args.colormap_opacity),
            "colormap_type": args.colormap_type,
        })

    base = provider["base_url"].rstrip("/")
    url = f"{base}{operations[operation]}?{urlencode(params)}"
    validate_allowed_url(url, provider["allowed_host"])
    return url


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in REDACT_KEYS:
                if key.lower() == "tile_fetcher":
                    clean[key] = "TOKEN_VAZIO_EPHEMERAL_TILE_HANDLE"
                else:
                    clean[key] = "REDACTED_SECRET_OR_EPHEMERAL"
            else:
                clean[key] = sanitize_json(item)
        return clean
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    return value


def read_capped(response, max_bytes: int) -> bytes:
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("response exceeds configured byte cap")
    return data


def build_receipt(
    *,
    operation: str,
    request_url: str,
    execute: bool,
    credential_state: str,
    gate_status: str,
    response_sha256: str | None = None,
    response_bytes: int | None = None,
    http_status: int | None = None,
    response_content_type: str | None = None,
    sanitized_response_path: str | None = None,
    response_contains_tile_handle: bool = False,
) -> dict[str, Any]:
    return {
        "schema": "rll.climate_engine_bridge.receipt.v1",
        "provider": "climate_engine",
        "provider_role": "EXTERNAL_COMPUTE_AND_VISUALIZATION",
        "operation": operation,
        "request_url": request_url,
        "network_execution_requested": execute,
        "credential_state": credential_state,
        "gate_status": gate_status,
        "response_sha256": response_sha256,
        "response_bytes": response_bytes,
        "http_status": http_status,
        "response_content_type": response_content_type,
        "sanitized_response_path": sanitized_response_path,
        "response_contains_tile_handle": response_contains_tile_handle,
        "source_primary_authority": "PRESERVE_UPSTREAM_DATASET_AUTHORITY",
        "provider_output_state": "EXTERNAL_COMPUTE_PRODUCT",
        "visualization_state": "DERIVED_VIEW",
        "observed_cross_domain": False,
        "statistical_independence_established": False,
        "cause": "TOKEN_VAZIO_CAUSA",
        "claim_allowed": False,
        "F_ok": "request contract resolved" if not execute else "bounded external compute request executed",
        "F_gap": (
            "provider result is not independent causal evidence; primary-source authority, "
            "cross-provider independence and ΔOBS promotion remain separate gates"
        ),
        "F_next": (
            "compare the hashed derived product with an independently sourced RLL path "
            "before any numerical ΔOBS promotion"
        ),
    }


def execute_operation(
    operation: str,
    request_url: str,
    provider: dict[str, Any],
    output_dir: Path,
    api_key: str | None,
    timeout: int,
    max_bytes: int,
) -> tuple[dict[str, Any], int]:
    if not api_key:
        return build_receipt(
            operation=operation,
            request_url=request_url,
            execute=True,
            credential_state="TOKEN_VAZIO_CLIMATE_ENGINE_API_KEY",
            gate_status="BLOCKED_CREDENTIAL",
        ), 3

    request = Request(
        request_url,
        headers={
            "Authorization": api_key,
            "User-Agent": "RLL-ClimateEngine-Bridge/1",
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        validate_allowed_url(final_url, provider["allowed_host"])
        body = read_capped(response, max_bytes)
        status = getattr(response, "status", None)
        content_type = response.headers.get("Content-Type", "")
    digest = hashlib.sha256(body).hexdigest()

    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"response is not UTF-8 JSON: {exc}") from exc

    contains_tile = isinstance(parsed, dict) and "tile_fetcher" in parsed
    sanitized = sanitize_json(parsed)
    output_dir.mkdir(parents=True, exist_ok=True)
    sanitized_path = output_dir / f"{operation}.sanitized.json"
    sanitized_path.write_text(
        json.dumps(sanitized, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    receipt = build_receipt(
        operation=operation,
        request_url=request_url,
        execute=True,
        credential_state="PRESENT_NOT_LOGGED",
        gate_status="EXTERNAL_COMPUTE_RESPONSE_OBSERVED",
        response_sha256=digest,
        response_bytes=len(body),
        http_status=status,
        response_content_type=content_type,
        sanitized_response_path=str(sanitized_path),
        response_contains_tile_handle=contains_tile,
    )
    return receipt, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--operation",
        required=True,
        choices=["metadata_dates", "metadata_variables", "timeseries_coordinates", "map_values"],
    )
    parser.add_argument("--dataset")
    parser.add_argument("--variable")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--coordinates")
    parser.add_argument("--area-reducer", default="mean", choices=["mean", "median", "min", "max"])
    parser.add_argument("--temporal-statistic", default="mean", choices=["mean", "median", "max", "min", "total"])
    parser.add_argument("--colormap-opacity", type=float, default=0.7)
    parser.add_argument("--colormap-type", default="continuous", choices=["continuous", "discrete"])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output-dir", default="artifacts/rll-climate-engine")
    parser.add_argument("--receipt", default="-")
    args = parser.parse_args()

    try:
        registry = load_json(REGISTRY_PATH)
        contract = load_json(CONTRACT_PATH)
        provider = provider_spec(registry, contract["provider_id"])
        request_url = build_request(args.operation, args, provider)

        if not args.execute:
            receipt = build_receipt(
                operation=args.operation,
                request_url=request_url,
                execute=False,
                credential_state="TOKEN_VAZIO_NOT_ACCESSED_IN_DRY_RUN",
                gate_status="DRY_RUN",
            )
            rc = 0
        else:
            receipt, rc = execute_operation(
                args.operation,
                request_url,
                provider,
                Path(args.output_dir),
                os.environ.get("CLIMATE_ENGINE_API_KEY"),
                int(contract["network_policy"].get("timeout_seconds", TIMEOUT_DEFAULT)),
                int(contract["network_policy"].get("max_response_bytes", MAX_BYTES_DEFAULT)),
            )
    except Exception as exc:
        receipt = {
            "schema": "rll.climate_engine_bridge.receipt.v1",
            "gate_status": "FAIL_CLOSED",
            "error": str(exc),
            "cause": "TOKEN_VAZIO_CAUSA",
            "claim_allowed": False,
        }
        rc = 2

    text = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if args.receipt == "-":
        print(text, end="")
    else:
        out = Path(args.receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
