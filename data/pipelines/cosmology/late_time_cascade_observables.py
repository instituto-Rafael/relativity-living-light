#!/usr/bin/env python3
"""Late-time cascade observable projection V1.

This module is a deliberately phenomenological SHADOW adapter.  It projects a
user-supplied, dimensionless late-time cascade template onto observables that
can later be compared with large-scale-structure / BAO and peculiar-velocity
pipelines.  It does NOT derive the template from gravitational-wave strain,
stellar collisions, a stress-energy tensor, or the Einstein equations.

Scientific boundary:
    source event -> trigger energy      = TOKEN_VAZIO
    strain -> trigger energy            = TOKEN_VAZIO
    event population -> template A_c    = TOKEN_VAZIO
    CMB lensing / ISW bridge            = TOKEN_VAZIO
    claim_allowed                       = False

The exact null A_c=0 returns the supplied baseline power point-by-point.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Iterable, Mapping

C_M_S = 299_792_458.0
SCHEMA = "rll.late_time_cascade_observables.v1"
CLAIM_ALLOWED = False


@dataclass(frozen=True)
class CascadeTemplate:
    """Phenomenological late-time transfer template.

    amplitude is dimensionless. damping_k must have the same inverse-length
    unit as k. beta controls a dimensionless redshift envelope.
    """

    amplitude: float
    damping_k: float
    beta: float = 0.0
    z_ref: float = 0.0

    def validate(self) -> None:
        vals = (self.amplitude, self.damping_k, self.beta, self.z_ref)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("template parameters must be finite")
        if self.damping_k <= 0.0:
            raise ValueError("damping_k must be > 0")
        if self.z_ref <= -1.0:
            raise ValueError("z_ref must be > -1")



def cascade_transfer(k: float, z: float, template: CascadeTemplate) -> float:
    """Return dimensionless phenomenological transfer T_c(k,z).

    T_c = A_c exp[-(k/k_d)^2] [(1+z)/(1+z_ref)]^beta

    This is a falsifiable nuisance/template coordinate, not a derived law.
    """

    template.validate()
    if not math.isfinite(k) or k < 0.0:
        raise ValueError("k must be finite and >= 0")
    if not math.isfinite(z) or z <= -1.0:
        raise ValueError("z must be finite and > -1")
    envelope = ((1.0 + z) / (1.0 + template.z_ref)) ** template.beta
    return template.amplitude * math.exp(-((k / template.damping_k) ** 2)) * envelope



def project_power_point(
    k: float,
    z: float,
    baseline_power: float,
    template: CascadeTemplate,
) -> dict[str, float]:
    """Project a baseline power point through the shadow cascade template."""

    if not math.isfinite(baseline_power) or baseline_power < 0.0:
        raise ValueError("baseline_power must be finite and >= 0")
    transfer = cascade_transfer(k, z, template)
    multiplier = 1.0 + transfer
    if multiplier < 0.0:
        raise ValueError("template would create negative projected power")
    projected = baseline_power * multiplier
    return {
        "k": float(k),
        "z": float(z),
        "baseline_power": float(baseline_power),
        "cascade_transfer": float(transfer),
        "projected_power": float(projected),
        "delta_power": float(projected - baseline_power),
    }



def damp_bao_wiggle(k: float, wiggle: float, sigma_c: float) -> float:
    """Apply an extra Gaussian damping coordinate to an existing BAO wiggle.

    O_bao,obs = O_bao,base exp[-(k sigma_c)^2 / 2]

    sigma_c is a nuisance/template scale.  This operation can suppress/broaden
    an existing oscillatory component; it cannot generate the primordial BAO
    standard ruler and must not be interpreted as its origin.
    """

    if not math.isfinite(k) or k < 0.0:
        raise ValueError("k must be finite and >= 0")
    if not math.isfinite(wiggle):
        raise ValueError("wiggle must be finite")
    if not math.isfinite(sigma_c) or sigma_c < 0.0:
        raise ValueError("sigma_c must be finite and >= 0")
    return wiggle * math.exp(-0.5 * (k * sigma_c) ** 2)



def observed_redshift_from_peculiar_velocity(
    z_cosmological: float,
    v_parallel_m_s: float,
) -> float:
    """First-order line-of-sight peculiar-velocity redshift mapping.

    z_obs ~= z_cos + (1 + z_cos) v_parallel/c for |v| << c.

    This function only supplies the kinematic first-order coordinate. It does
    not claim a Pantheon magnitude correction or covariance likelihood.
    """

    if not math.isfinite(z_cosmological) or z_cosmological <= -1.0:
        raise ValueError("z_cosmological must be finite and > -1")
    if not math.isfinite(v_parallel_m_s) or abs(v_parallel_m_s) >= C_M_S:
        raise ValueError("peculiar velocity must be finite with |v| < c")
    return z_cosmological + (1.0 + z_cosmological) * v_parallel_m_s / C_M_S



def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()



def run_projection(config: Mapping[str, Any]) -> dict[str, Any]:
    """Run a deterministic shadow projection and return an auditable receipt."""

    template_raw = config.get("template")
    if not isinstance(template_raw, Mapping):
        raise ValueError("config.template must be an object")
    template = CascadeTemplate(
        amplitude=float(template_raw["amplitude"]),
        damping_k=float(template_raw["damping_k"]),
        beta=float(template_raw.get("beta", 0.0)),
        z_ref=float(template_raw.get("z_ref", 0.0)),
    )
    template.validate()

    power_points_raw = config.get("power_points", [])
    if not isinstance(power_points_raw, Iterable) or isinstance(
        power_points_raw, (str, bytes, Mapping)
    ):
        raise ValueError("power_points must be an array")
    power_points = [
        project_power_point(
            float(point["k"]),
            float(point["z"]),
            float(point["baseline_power"]),
            template,
        )
        for point in power_points_raw
    ]

    bao_raw = config.get("bao_wiggles", [])
    if not isinstance(bao_raw, Iterable) or isinstance(bao_raw, (str, bytes, Mapping)):
        raise ValueError("bao_wiggles must be an array")
    bao_wiggles = []
    for point in bao_raw:
        k = float(point["k"])
        wiggle = float(point["wiggle"])
        sigma_c = float(point["sigma_c"])
        damped = damp_bao_wiggle(k, wiggle, sigma_c)
        bao_wiggles.append(
            {
                "k": k,
                "wiggle": wiggle,
                "sigma_c": sigma_c,
                "damped_wiggle": damped,
            }
        )

    sn_raw = config.get("peculiar_velocity_points", [])
    if not isinstance(sn_raw, Iterable) or isinstance(sn_raw, (str, bytes, Mapping)):
        raise ValueError("peculiar_velocity_points must be an array")
    velocity_points = []
    for point in sn_raw:
        z_cos = float(point["z_cosmological"])
        velocity = float(point["v_parallel_m_s"])
        z_obs = observed_redshift_from_peculiar_velocity(z_cos, velocity)
        velocity_points.append(
            {
                "z_cosmological": z_cos,
                "v_parallel_m_s": velocity,
                "z_observed_first_order": z_obs,
                "delta_z": z_obs - z_cos,
            }
        )

    receipt_core: dict[str, Any] = {
        "schema": SCHEMA,
        "scientific_state": "SHADOW_HYPOTHESIS_OBSERVABLE_PROJECTION",
        "claim_allowed": CLAIM_ALLOWED,
        "background_modified": False,
        "bao_origin_claimed": False,
        "template": {
            "amplitude": template.amplitude,
            "damping_k": template.damping_k,
            "beta": template.beta,
            "z_ref": template.z_ref,
        },
        "power_points": power_points,
        "bao_wiggles": bao_wiggles,
        "peculiar_velocity_points": velocity_points,
        "controls": {
            "exact_null": "template.amplitude = 0 -> projected_power = baseline_power",
            "baseline_authority": "externally supplied LCDM/wCDM/CPL/RLL baseline",
            "no_double_counting": "no new homogeneous density term is added",
        },
        "token_vazio": [
            "strain_to_trigger_energy",
            "stellar_collision_population_to_template_amplitude",
            "cascade_template_to_pantheon_covariance_likelihood",
            "cascade_template_to_cmb_lensing_isw",
            "independent_observational_replication",
        ],
    }
    receipt = dict(receipt_core)
    receipt["receipt_sha256"] = _canonical_sha256(receipt_core)
    return receipt
