#!/usr/bin/env python3
from __future__ import annotations

"""Freeze the official ACT DR6.02 LCDM posterior configuration for local replay.

This consumes the official LAMBDA chain archive after extraction and records the
exact MCMC input/updated configuration, MCMC controls, parameter priors,
covariance files and a best observed chain point. The archive also contains a
separate ``*.minimize.*`` configuration; it is preserved as auxiliary custody
but is never silently selected as the posterior-chain authority.

This tool does not execute a local posterior and therefore cannot resolve the
posterior reproduction token.
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

SCHEMA = "rll.act_dr6_posterior_reproduction_contract.v1"
TOKEN = "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: YAML mapping required")
    return value


def primary_mcmc_file(root: Path, suffix: str) -> Path:
    """Select exactly one non-minimize config for posterior-chain authority."""
    all_matches = sorted(root.rglob(f"*{suffix}"))
    primary = [path for path in all_matches if ".minimize." not in path.name]
    if len(primary) != 1:
        raise ValueError(
            f"expected exactly one non-minimize *{suffix}, found {len(primary)} "
            f"(all matches={len(all_matches)})"
        )
    return primary[0]


def chain_header_and_best(chain_files: list[Path]) -> tuple[list[str], dict[str, float], int]:
    header: list[str] | None = None
    best_row: list[float] | None = None
    best_minuslogpost = math.inf
    total_rows = 0
    for path in chain_files:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for raw in stream:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    if header is None:
                        candidate = line.lstrip("#").strip().split()
                        lowered = [c.lower() for c in candidate]
                        if len(candidate) >= 3 and candidate[0].lower() in {"weight", "weights"} and "minuslogpost" in lowered:
                            header = candidate
                    continue
                values = [float(x) for x in line.split()]
                total_rows += 1
                if header is not None and len(values) != len(header):
                    raise ValueError(f"{path}: chain/header column mismatch {len(values)} != {len(header)}")
                if len(values) < 2:
                    raise ValueError(f"{path}: chain row has fewer than two columns")
                minuslogpost = values[1]
                if minuslogpost < best_minuslogpost:
                    best_minuslogpost = minuslogpost
                    best_row = values
    if header is None:
        raise ValueError("no Cobaya chain header found")
    if best_row is None:
        raise ValueError("no chain samples found")
    return header, {name: value for name, value in zip(header, best_row)}, total_rows


def normalize_parameter(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    allowed = {"prior", "ref", "proposal", "value", "drop", "derived", "latex", "renames"}
    return {key: value[key] for key in sorted(value) if key in allowed}


def file_receipt(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def build(extracted: Path, source_url: str) -> dict[str, Any]:
    if not extracted.is_dir():
        raise ValueError("extracted reference directory missing")

    input_yaml = primary_mcmc_file(extracted, ".input.yaml")
    updated_yaml = primary_mcmc_file(extracted, ".updated.yaml")
    input_cfg = load_yaml(input_yaml)
    updated_cfg = load_yaml(updated_yaml)

    chain_files = sorted(
        path
        for path in extracted.rglob("*.txt")
        if len(path.name.rsplit(".", 2)) == 3 and path.name.rsplit(".", 2)[-2].isdigit()
    )
    if not chain_files:
        raise ValueError("no official chain files found")
    header, best, total_rows = chain_header_and_best(chain_files)

    covmats = sorted(extracted.rglob("*.covmat"))
    minimums = sorted(extracted.rglob("*.minimum"))
    progress = sorted(extracted.rglob("*.progress"))
    minimize_configs = sorted(
        path
        for path in extracted.rglob("*.yaml")
        if ".minimize." in path.name
    )

    params = input_cfg.get("params") if isinstance(input_cfg.get("params"), dict) else {}
    sampler = input_cfg.get("sampler") if isinstance(input_cfg.get("sampler"), dict) else {}
    updated_sampler = updated_cfg.get("sampler") if isinstance(updated_cfg.get("sampler"), dict) else {}
    likelihood = input_cfg.get("likelihood") if isinstance(input_cfg.get("likelihood"), dict) else {}
    theory = input_cfg.get("theory") if isinstance(input_cfg.get("theory"), dict) else {}

    sampled_params = [
        name
        for name, spec in params.items()
        if isinstance(spec, dict) and isinstance(spec.get("prior"), dict)
    ]
    if not sampled_params:
        raise ValueError("official MCMC config exposes no sampled parameters with explicit prior mappings")
    missing_best = sorted(name for name in sampled_params if name not in best)
    if missing_best:
        raise ValueError("official chain header missing sampled params: " + ", ".join(missing_best))

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
        key: (mcmc_updated[key] if key in mcmc_updated else mcmc_input[key])
        for key in sorted(mcmc_keys)
        if key in mcmc_updated or key in mcmc_input
    }
    if not mcmc_contract:
        raise ValueError("official MCMC stopping/proposal contract is empty")

    return {
        "schema": SCHEMA,
        "state": "OFFICIAL_ACT_DR6_LCDM_POSTERIOR_CONTRACT_FROZEN",
        "claim_allowed": False,
        "publication_ready": False,
        "token": TOKEN,
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
            "specifications": {str(name): normalize_parameter(spec) for name, spec in params.items()},
        },
        "mcmc_contract": mcmc_contract,
        "covariance": [file_receipt(path, extracted) for path in covmats],
        "minimum_files": [file_receipt(path, extracted) for path in minimums],
        "progress_files": [file_receipt(path, extracted) for path in progress],
        "reference_chains": {
            "chain_file_count": len(chain_files),
            "total_noncomment_rows": total_rows,
            "header": header,
            "best_observed_minuslogpost": float(best["minuslogpost"]),
            "best_observed_sampled_parameters": {name: float(best[name]) for name in sampled_params},
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
        },
        "resolved_token": None,
        "reduces_token": TOKEN,
        "next_required_action": "Execute the frozen local Cobaya/CAMB ACT+Planck-lowE LCDM posterior, preserve raw chains and convergence diagnostics, then compare marginals against this official reference contract.",
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
    print(
        json.dumps(
            {
                "state": payload["state"],
                "sampled_parameters": payload["parameters"]["count_sampled"],
                "chain_rows": payload["reference_chains"]["total_noncomment_rows"],
                "best_minuslogpost": payload["reference_chains"]["best_observed_minuslogpost"],
                "aux_minimize_configs": len(payload["authority"]["auxiliary_minimize_configs"]),
                "claim_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
