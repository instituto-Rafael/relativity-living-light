"""RLL structural integration primitives.

This module keeps observational data immutable and integrates hypotheses through
explicit mathematical operators, source registries, and claim gates.
It does not establish new physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


class EpistemicStatus(str, Enum):
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    HYPOTHESIS = "hypothesis"
    REFERENCE_ONLY = "reference_only"
    TOKEN_VAZIO = "TOKEN_VAZIO"


class ExecutionDecision(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class TransitionParameters:
    omega_s0: float
    z_t: float
    w_t: float

    def validate(self) -> None:
        if self.omega_s0 < 0:
            raise ValueError("omega_s0 must be non-negative")
        if self.z_t < 0:
            raise ValueError("z_t must be non-negative")
        if self.w_t <= 0:
            raise ValueError("w_t must be positive")


def _safe_logistic(x: float) -> float:
    if x >= 0:
        e = math.exp(-x)
        return e / (1.0 + e)
    e = math.exp(x)
    return 1.0 / (1.0 + e)


def logistic_transition_z(z: float, z_t: float, w_t: float) -> float:
    """Return f(z)=1/[1+exp((z-z_t)/w_t)] with overflow-safe evaluation."""
    if z < 0:
        raise ValueError("z must be non-negative")
    if z_t < 0:
        raise ValueError("z_t must be non-negative")
    if w_t <= 0:
        raise ValueError("w_t must be positive")
    return _safe_logistic((z - z_t) / w_t)


def transition_density_factor_z(z: float, z_t: float, w_t: float) -> float:
    """Dimensionless RLL transition factor g(z)."""
    f = logistic_transition_z(z, z_t, w_t)
    return f + (1.0 - f) * (1.0 + z) ** 3


def transition_density_fraction_z(z: float, params: TransitionParameters) -> float:
    params.validate()
    return params.omega_s0 * transition_density_factor_z(z, params.z_t, params.w_t)


def transition_w_eff_z(z: float, z_t: float, w_t: float) -> float:
    """Effective EoS from continuity: w=-1+(1+z)/3 d ln(g)/dz."""
    f = logistic_transition_z(z, z_t, w_t)
    df_dz = -f * (1.0 - f) / w_t
    matter_factor = (1.0 + z) ** 3
    dm_dz = 3.0 * (1.0 + z) ** 2
    g = f + (1.0 - f) * matter_factor
    dg_dz = df_dz * (1.0 - matter_factor) + (1.0 - f) * dm_dz
    return -1.0 + ((1.0 + z) / 3.0) * (dg_dz / g)


def bulk_viscous_pressure(pressure: float, hubble_rate: float, xi: float) -> float:
    """p_eff = p - 3 H xi. Units must be supplied consistently by the caller."""
    if hubble_rate < 0 or xi < 0:
        raise ValueError("hubble_rate and xi must be non-negative")
    return pressure - 3.0 * hubble_rate * xi


def interaction_source(beta: float, expansion_rate: float, density: float) -> float:
    """Generic Q=beta*H*rho interaction source; interpretation remains hypothesis-bound."""
    if expansion_rate < 0 or density < 0:
        raise ValueError("expansion_rate and density must be non-negative")
    return beta * expansion_rate * density


def distance_duality_eta(d_l: float, d_a: float, z: float) -> float:
    """η(z)=d_L/[(1+z)^2 d_A]; η=1 under standard distance duality."""
    if d_l <= 0 or d_a <= 0 or z < 0:
        raise ValueError("distances must be positive and z non-negative")
    return d_l / (((1.0 + z) ** 2) * d_a)


def alcock_paczynski_ratio(d_m: float, d_h: float) -> float:
    """F_AP=D_M/D_H, independent of the sound-horizon normalization."""
    if d_m <= 0 or d_h <= 0:
        raise ValueError("d_m and d_h must be positive")
    return d_m / d_h


def frb_delay_residual(
    observed_delay: float,
    dispersion_measure: float,
    frequency: float,
    plasma_coefficient: float,
) -> float:
    """Residual after the standard ν^-2 plasma delay.

    The caller owns the unit convention. No RLL frequency exponent is assumed.
    """
    if dispersion_measure < 0 or frequency <= 0 or plasma_coefficient < 0:
        raise ValueError("invalid FRB inputs")
    standard_delay = plasma_coefficient * dispersion_measure * frequency ** -2
    return observed_delay - standard_delay


def stable_payload_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_registry(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("registry root must be an object")
    return payload


def validate_source_registry(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        return errors
    seen: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"sources[{index}].source_id is required")
        elif source_id in seen:
            errors.append(f"duplicate source_id: {source_id}")
        else:
            seen.add(source_id)
        if source.get("verification_status") not in {"primary_verified", "metadata_verified", "pending_fulltext"}:
            errors.append(f"sources[{index}].verification_status invalid")
        if not source.get("locator"):
            errors.append(f"sources[{index}].locator is required")
        if not source.get("safe_use"):
            errors.append(f"sources[{index}].safe_use is required")
    return errors


def evaluate_branch_readiness(
    branch: Mapping[str, Any],
    available_artifacts: Iterable[str],
) -> tuple[ExecutionDecision, list[str]]:
    available = set(available_artifacts)
    requirements = branch.get("required_artifacts", [])
    if not isinstance(requirements, list):
        return ExecutionDecision.BLOCKED, ["required_artifacts must be a list"]
    missing = [item for item in requirements if item not in available]
    status = branch.get("status")
    if status == EpistemicStatus.TOKEN_VAZIO.value:
        return ExecutionDecision.TOKEN_VAZIO, missing or ["branch explicitly TOKEN_VAZIO"]
    if missing:
        return ExecutionDecision.BLOCKED, missing
    if status in {
        EpistemicStatus.IMPLEMENTED.value,
        EpistemicStatus.PARTIAL.value,
        EpistemicStatus.HYPOTHESIS.value,
        EpistemicStatus.REFERENCE_ONLY.value,
    }:
        return ExecutionDecision.READY, []
    return ExecutionDecision.BLOCKED, ["unknown epistemic status"]


def validate_integration_registry(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("raw_data_policy") != "immutable":
        errors.append("raw_data_policy must be immutable")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    branches = payload.get("branches")
    if not isinstance(branches, list) or not branches:
        errors.append("branches must be a non-empty list")
        return errors
    ids: set[str] = set()
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict):
            errors.append(f"branches[{index}] must be an object")
            continue
        branch_id = branch.get("branch_id")
        if not isinstance(branch_id, str) or not branch_id:
            errors.append(f"branches[{index}].branch_id is required")
        elif branch_id in ids:
            errors.append(f"duplicate branch_id: {branch_id}")
        else:
            ids.add(branch_id)
        if branch.get("status") not in {status.value for status in EpistemicStatus}:
            errors.append(f"branches[{index}].status invalid")
        if not isinstance(branch.get("equations"), list):
            errors.append(f"branches[{index}].equations must be a list")
        if not isinstance(branch.get("observables"), list):
            errors.append(f"branches[{index}].observables must be a list")
        if not isinstance(branch.get("required_artifacts"), list):
            errors.append(f"branches[{index}].required_artifacts must be a list")
        if not branch.get("claim_boundary"):
            errors.append(f"branches[{index}].claim_boundary is required")
    return errors
