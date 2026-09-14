#!/usr/bin/env python3
from __future__ import annotations

"""Freeze the ACT DR6.02 LCDM posterior authority needed for a local replay.

The official LAMBDA archive contains both MCMC and minimizer configurations and
may expose Cobaya aliases/drop/derived columns whose chain names are not a
1:1 copy of the input parameter keys. The replay authority is therefore frozen
from priors, likelihood set, theory family, MCMC controls, covariance and raw
reference chains. Chain-name alignment is diagnostic, never silently repaired.
"""

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

import yaml

SCHEMA = "rll.act_dr6_posterior_reproduction_contract.v2"
TOKEN = "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_receipt(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: YAML mapping required")
    return value


def primary_mcmc_file(root: Path, suffix: str) -> Path:
    matches = sorted(root.rglob(f"*{suffix}"))
    primary = [path for path in matches if ".minimize." not in path.name]
    if len(primary) != 1:
        raise ValueError(
            f"expected exactly one non-minimize *{suffix}, found {len(primary)} "
            f"(all matches={len(matches)})"
        )
    return primary[0]


def is_chain_file(path: Path) -> bool:
    parts = path.name.rsplit(".", 2)
    return len(parts) == 3 and parts[-2].isdigit() and parts[-1] == "txt"


def scan_chains(chain_files: list[Path]) -> dict[str, Any]:
    if not chain_files:
        raise ValueError("no official chain files found")

    explicit_header: list[str] | None = None
    header_source: str | None = None
    first_data_columns: int | None = None
    best_values: list[float] | None = None
    best_minuslogpost = math.inf
    total_rows = 0

    for path in chain_files:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for raw in stream:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    candidate = line.lstrip("#").strip().split()
                    lowered = [item.lower() for item in candidate]
                    if explicit_header is None and "minuslogpost" in lowered and len(candidate) >= 3:
                        explicit_header = candidate
                        header_source = str(path.name)
                    continue
                values = [float(item) for item in line.split()]
                if len(values) < 2:
                    raise ValueError(f"{path}: chain row has fewer than weight/minuslogpost columns")
                if first_data_columns is None:
                    first_data_columns = len(values)
                elif len(values) != first_data_columns:
                    raise ValueError(
                        f"{path}: inconsistent chain column count {len(values)} != {first_data_columns}"
                    )
                total_rows += 1
                minuslogpost = values[1]
                if not math.isfinite(minuslogpost):
                    continue
                if minuslogpost < best_minuslogpost:
                    best_minuslogpost = minuslogpost
                    best_values = values

    if total_rows <= 0 or best_values is None or first_data_columns is None:
        raise ValueError("official reference chains contain no finite samples")

    header_usable = explicit_header is not None and len(explicit_header) == first_data_columns
    if header_usable:
        best_mapping = {name: value for name, value in zip(explicit_header or [], best_values)}
        header = explicit_header
    else:
        best_mapping = {}
        header = explicit_header or []

    return {
        "total_noncomment_rows": total_rows,
        "column_count": first_data_columns,
        "header": header,
        "header_source": header_source,
        "header_usable_for_parameter_mapping": header_usable,
        "best_observed_minuslogpost": float(best_minuslogpost),
        "best_mapping": best_mapping,
    }


def normalize_json_config(value: Any) -> Any:
    """Preserve YAML non-finite sentinels without emitting invalid JSON numbers.

    Cobaya configuration may legitimately use YAML ``.inf``/``-.inf`` as
    unbounded control values. JSON has no interoperable infinity literal and
    this module intentionally serializes with ``allow_nan=False``. Encode only
    configuration sentinels as explicit strings; observed chain values are
    validated separately and must remain finite where promoted into the
    contract.
    """
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    if isinstance(value, dict):
        return {str(key): normalize_json_config(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_json_config(item) for item in value]
    return value


def normalize_parameter(value: Any) -> Any:
    if not isinstance(value, dict):
        return normalize_json_config(value)
    allowed = {"prior", "ref", "proposal", "value", "drop", "derived", "latex", "renames"}
    return normalize_json_config({key: value[key] for key in sorted(value) if key in allowed})


def build(extracted: Path, source_url: str) -> dict[str, Any]:
    if not extracted.is_dir():
        raise ValueError("extracted reference directory missing")

    input_yaml = primary_mcmc_file(extracted, ".input.yaml")
    updated_yaml = primary_mcmc_file(extracted, ".updated.yaml")
    input_cfg = load_yaml(input_yaml)
    updated_cfg = load_yaml(updated_yaml)

    params = input_cfg.get("params") if isinstance(input_cfg.get("params"), dict) else {}
    sampler = input_cfg.get("sampler") if isinstance(input_cfg.get("sampler"), dict) else {}
    updated_sampler = updated_cfg.get("sampler") if isinstance(updated_cfg.get("sampler"), dict) else {}
    likelihood = input_cfg.get("likelihood") if isinstance(input_cfg.get("likelihood"), dict) else {}
    theory = input_cfg.get("theory") if isinstance(input_cfg.get("theory"), dict) else {}

    sampled_params = [
        str(name)
        for name, spec in params.items()
        if isinstance(spec, dict) and spec.get("prior") is not None
    ]
    if not sampled_params:
        raise ValueError("official MCMC config exposes no parameters with explicit non-null priors")
    if not likelihood:
        raise ValueError("official MCMC config exposes no likelihood components")
    if not theory:
        raise ValueError("official MCMC config exposes no theory component")

    mcmc_input = sampler.get("mcmc") if isinstance(sampler.get("mcmc"), dict) else {}
    mcmc_updated = updated_sampler.get("mcmc") if isinstance(updated_sampler.get("mcmc"), dict) else {}
    mcmc_keys = {
        "Rminus1_stop",
        "Rminus1_cl_stop",
        "burn_in",
        "covmat",
        "covmat_params",
        "learn_proposal",
        "learn_proposal_Rminus1_max",
        "learn_proposal_Rminus1_max_early",
        "max_samples",
        "max_tries",
        "output_every",
        "oversample_power",
        "proposal_scale",
    }
    mcmc_contract = {
        key: normalize_json_config(mcmc_updated[key] if key in mcmc_updated else mcmc_input[key])
        for key in sorted(mcmc_keys)
        if key in mcmc_updated or key in mcmc_input
    }
    if not mcmc_contract:
        raise ValueError("official MCMC stopping/proposal contract is empty")

    covmats = sorted(extracted.rglob("*.covmat"))
    if not covmats:
        raise ValueError("official archive exposes no covariance matrix for replay custody")

    chain_files = sorted(path for path in extracted.rglob("*.txt") if is_chain_file(path))
    chain_scan = scan_chains(chain_files)
    best_mapping = chain_scan.pop("best_mapping")
    mapped_sampled = [name for name in sampled_params if name in best_mapping]
    unmapped_sampled = [name for name in sampled_params if name not in best_mapping]
    best_sampled: dict[str, float] = {}
    for name in mapped_sampled:
        value = float(best_mapping[name])
        if not math.isfinite(value):
            raise ValueError(f"official best reference sample has non-finite sampled parameter: {name}")
        best_sampled[name] = value

    minimize_configs = sorted(
        path for path in extracted.rglob("*.yaml") if ".minimize." in path.name
    )
    minimums = sorted(extracted.rglob("*.minimum"))
    progress = sorted(extracted.rglob("*.progress"))

    return {
        "schema": SCHEMA,
        "state": "OFFICIAL_ACT_DR6_LCDM_POSTERIOR_CONTRACT_FROZEN",
        "claim_allowed": False,
        "publication_ready": False,
        "token": TOKEN,
        "serialization_contract": {
            "configuration_positive_infinity": "Infinity",
            "configuration_negative_infinity": "-Infinity",
            "configuration_nan": "NaN",
            "observed_chain_values_must_be_finite_when_promoted": True,
        },
        "authority": {
            "provider": "NASA/GSFC LAMBDA",
            "product": "ACT DR6.02 actlite LCDM CAMB chain",
            "source_url": source_url,
            "input_yaml": file_receipt(input_yaml, extracted),
            "updated_yaml": file_receipt(updated_yaml, extracted),
            "selection_rule": "posterior authority is the unique non-minimize input/updated YAML pair",
            "auxiliary_minimize_configs": [file_receipt(path, extracted) for path in minimize_configs],
        },
        "components": {
            "likelihood_names": sorted(map(str, likelihood.keys())),
            "theory_names": sorted(map(str, theory.keys())),
            "sampler_names": sorted(map(str, sampler.keys())),
        },
        "parameters": {
            "sampled": sampled_params,
            "count_sampled": len(sampled_params),
            "mapped_to_reference_chain": mapped_sampled,
            "unmapped_to_reference_chain": unmapped_sampled,
            "mapping_is_required_for_replay": False,
            "specifications": {str(name): normalize_parameter(spec) for name, spec in params.items()},
        },
        "mcmc_contract": mcmc_contract,
        "covariance": [file_receipt(path, extracted) for path in covmats],
        "minimum_files": [file_receipt(path, extracted) for path in minimums],
        "progress_files": [file_receipt(path, extracted) for path in progress],
        "reference_chains": {
            "chain_file_count": len(chain_files),
            **chain_scan,
            "best_observed_sampled_parameters_when_name_aligned": best_sampled,
            "files": [file_receipt(path, extracted) for path in chain_files],
        },
        "local_reproduction_contract": {
            "must_preserve_sampled_parameter_priors": True,
            "must_preserve_likelihood_set": True,
            "must_preserve_theory_family": True,
            "must_preserve_mcmc_stopping_policy": True,
            "must_start_from_versioned_covmat_or_demonstrate_equivalent_adaptation": True,
            "must_store_raw_local_chains": True,
            "must_report_local_Rminus1": True,
            "must_compare_local_marginals_to_official_reference": True,
            "reference_chain_name_alignment_is_diagnostic_not_replay_authority": True,
        },
        "resolved_token": None,
        "reduces_token": TOKEN,
        "next_required_action": "Execute the frozen local Cobaya/CAMB ACT+Planck-lowE LCDM posterior, preserve raw chains and convergence diagnostics, then compare marginals against the official reference chains using explicit alias/rename mapping where needed.",
        "scientific_boundary": "Freezing the official posterior contract eliminates configuration ambiguity but is not a local posterior reproduction and has no RLL CMB validation effect.",
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extracted", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build(args.extracted, args.source_url)
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        "sampled_parameters": payload["parameters"]["count_sampled"],
        "unmapped_sampled_parameters": payload["parameters"]["unmapped_to_reference_chain"],
        "chain_rows": payload["reference_chains"]["total_noncomment_rows"],
        "best_minuslogpost": payload["reference_chains"]["best_observed_minuslogpost"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
