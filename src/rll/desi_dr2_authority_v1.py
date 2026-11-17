"""Source-bound DESI DR2 covariance order gate; no data or physical-model mutation.

Source authority (reviewed 2026-11-17):
CobayaSampler/bao_data master:
  desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt
    Git blob 8aff444fdb42c0946342aa0011ab287eda097c4c
  desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt
    Git blob fd8e5697ab61379b07b52efb781ea6713417a4d9
RLL covariance raw SHA-256 is bound to the observed source file. The upstream
mean orders Ly-alpha as DH then DM, while the RLL observation table orders DM,
then DH. This module reindexes a COPY of the covariance, never its source.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

SOURCE_SHA256 = "4c95c45bf14f8eb49bf03fa512984448428920f7a2ba0a846dae30ed1da08658"
SOURCE_MEAN_BLOB = "8aff444fdb42c0946342aa0011ab287eda097c4c"
SOURCE_COV_BLOB = "fd8e5697ab61379b07b52efb781ea6713417a4d9"
# (tracer, observable, redshift, upstream measurement), in ORIGINAL upstream order.
UPSTREAM = (
    ("BGS", "DV_over_rd", 0.295, 7.94167639),
    ("LRG1", "DM_over_rd", 0.510, 13.58758434),
    ("LRG1", "DH_over_rd", 0.510, 21.86294686),
    ("LRG2", "DM_over_rd", 0.706, 17.35069094),
    ("LRG2", "DH_over_rd", 0.706, 19.45534918),
    ("LRG3_PLUS_ELG1", "DM_over_rd", 0.934, 21.57563956),
    ("LRG3_PLUS_ELG1", "DH_over_rd", 0.934, 17.64149464),
    ("ELG2", "DM_over_rd", 1.321, 27.60085612),
    ("ELG2", "DH_over_rd", 1.321, 14.17602155),
    ("QSO", "DM_over_rd", 1.484, 30.51190063),
    ("QSO", "DH_over_rd", 1.484, 12.81699964),
    ("Lya", "DH_over_rd", 2.330, 8.631545674846294),
    ("Lya", "DM_over_rd", 2.330, 38.988973961958784),
)


def align_verified_desi_covariance(points, raw_cov, source_path):
    """Fail closed on wrong source/order; reorder covariance to observation rows.

    Returns aligned covariance and source evidence metadata. Never auto-detect
    an alternative covariance from sigma/variance resemblance alone.
    """
    if hashlib.sha256(Path(source_path).read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("BLOCKED_DESI_COVARIANCE_SOURCE_SHA256")
    a = np.asarray(raw_cov, dtype=float)
    if a.shape != (13, 13) or not np.isfinite(a).all():
        raise ValueError("BLOCKED_DESI_COVARIANCE_SHAPE_OR_FINITE")
    if not np.allclose(a, a.T, rtol=0.0, atol=1e-14):
        raise ValueError("BLOCKED_DESI_COVARIANCE_ASYMMETRIC")
    if np.min(np.linalg.eigvalsh(a)) <= 0.0:
        raise ValueError("BLOCKED_DESI_COVARIANCE_NOT_SPD")
    if len(points) != len(UPSTREAM):
        raise ValueError("BLOCKED_DESI_MEAN_DIMENSION")
    source_index = {(tr, obs, z): i for i, (tr, obs, z, _) in enumerate(UPSTREAM)}
    if len(source_index) != len(UPSTREAM):
        raise ValueError("BLOCKED_DESI_SOURCE_IDENTITIES_NOT_UNIQUE")
    perm = []
    sigma = []
    for _, row in points.iterrows():
        key = (str(row["tracer"]), str(row["observable"]), round(float(row["z_eff"]), 3))
        if key not in source_index or source_index[key] in perm:
            raise ValueError("BLOCKED_DESI_OBSERVABLE_IDENTITY_OR_DUPLICATE")
        source_i = source_index[key]
        if not np.isfinite(float(row["value"])) or abs(float(row["value"]) - UPSTREAM[source_i][3]) > 0.01:
            raise ValueError("BLOCKED_DESI_MEAN_SOURCE_VALUE_MISMATCH")
        sig = float(row["sigma"])
        if not np.isfinite(sig) or sig <= 0:
            raise ValueError("BLOCKED_DESI_SIGMA_NONPOSITIVE")
        sigma.append(sig)
        perm.append(source_i)
    if sorted(perm) != list(range(13)):
        raise ValueError("BLOCKED_DESI_INCOMPLETE_PERMUTATION")
    aligned = a[np.ix_(perm, perm)].copy()
    # Rounded paper marginals need not exactly match the Cobaya covariance;
    # protect against gross ordering mistakes without claiming equal marginal errors.
    variance_ratios = np.diag(aligned) / np.square(np.asarray(sigma))
    if np.max(np.abs(variance_ratios - 1.0)) > 0.15:
        raise ValueError("BLOCKED_DESI_COVARIANCE_MEAN_SIGMA_ALIGNMENT")
    return aligned, {
        "state": "SOURCE_BOUND_SCOPED",
        "source_covariance_sha256": SOURCE_SHA256,
        "cobaya_upstream_mean_git_blob": SOURCE_MEAN_BLOB,
        "cobaya_upstream_cov_git_blob": SOURCE_COV_BLOB,
        "source_order_to_observation_order": perm,
        "lyalpha_reordered": perm[-2:] == [12, 11],
        "max_variance_to_rounded_sigma_relative_delta": float(np.max(np.abs(variance_ratios - 1.0))),
        "claim_allowed": False,
    }


def observation_vector_n(inputs):
    """Dimension of the *current* vector, not effective independent sky modes.

    The source pipeline evaluates 3 CMB distance priors when its 3x3 covariance
    is present; old +2 silently undercounts. A malformed covariance must not
    be silently substituted for the 2-prior fallback.
    """
    n = len(inputs["hz"]) + len(inputs["desi"]) + len(inputs["fs8"])
    cmb = inputs["cmb"]
    if "covariance" not in cmb:
        return n + 2  # Explicit historical 2-observable diagonal fallback.
    if cmb.get("parameter_order") != ["R", "la", "ob_h2"]:
        raise ValueError("BLOCKED_CMB_PARAMETER_ORDER")
    cov = np.asarray(cmb["covariance"], dtype=float)
    if cov.shape != (3, 3) or not np.isfinite(cov).all():
        raise ValueError("BLOCKED_CMB_COVARIANCE_SHAPE")
    if not np.allclose(cov, cov.T, rtol=0.0, atol=1e-12):
        raise ValueError("BLOCKED_CMB_COVARIANCE_ASYMMETRIC")
    if np.min(np.linalg.eigvalsh(cov)) <= 0.0:
        raise ValueError("BLOCKED_CMB_COVARIANCE_NOT_SPD")
    return n + 3
