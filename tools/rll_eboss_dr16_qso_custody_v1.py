#!/usr/bin/env python3
"""Offline custody and BAO marginal diagnostic for eBOSS DR16 QSO.

Source: SDSS DR16 cosmology release v1_0_1 (Alam et al., arXiv:2007.08991),
Cobaya bao.sdss_dr16_baoplus_qso, exact data blobs pinned below. This is
one tracer, not the complete SDSS likelihood. No joint ingestion or claim.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = "https://github.com/CobayaSampler/bao_data"
RELEASE = "https://svn.sdss.org/public/data/eboss/DR16cosmo/tags/v1_0_1/"
NAMES = ("sdss_DR16_BAOplus_QSO_FSBAO_DMDHfs8.dat",
         "sdss_DR16_BAOplus_QSO_FSBAO_DMDHfs8_covtot.txt")
BLOBS = ("f12c30f6aa673c7c3ba66a619e9f60c4ff3522c7",
         "293352d31f4f7a0932443e6754fc5458320e4eda")
ORDER = ("DM_over_rs", "DH_over_rs", "f_sigma8")


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def read_pinned(path, expected):
    raw = path.read_bytes()
    if git_blob(raw) != expected:
        raise ValueError("SOURCE_BLOB_MISMATCH: " + path.name)
    return raw, dict(path=path.name, git_blob=expected, size_bytes=len(raw),
                     sha256=hashlib.sha256(raw).hexdigest())


def cholesky(c):
    n = len(c)
    if n not in (2, 3) or any(len(row) != n for row in c):
        raise ValueError("COVARIANCE_SHAPE")
    if any(not math.isfinite(c[i][j]) or c[i][j] != c[j][i]
           for i in range(n) for j in range(n)):
        raise ValueError("COVARIANCE_FINITE_SYMMETRIC")
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            v = c[i][j] - math.fsum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if not math.isfinite(v) or v <= 0:
                    raise ValueError("COVARIANCE_NOT_SPD")
                lower[i][j] = math.sqrt(v)
            else:
                lower[i][j] = v / lower[j][j]
    return lower


def parse(vector, matrix):
    rows = [line.split() for line in vector.decode("ascii").splitlines() if line.strip()]
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise ValueError("VECTOR_SHAPE")
    if tuple(row[2] for row in rows) != ORDER:
        raise ValueError("VECTOR_ORDER")
    z = [float(row[0]) for row in rows]
    obs = [float(row[1]) for row in rows]
    if z != [1.48] * 3 or any(not math.isfinite(x) or x <= 0 for x in obs):
        raise ValueError("VECTOR_VALUES")
    c = [[float(v) for v in line.split()] for line in matrix.decode("ascii").splitlines() if line.strip()]
    if len(c) != 3:
        raise ValueError("COVARIANCE_SHAPE")
    cholesky(c)
    # Marginalize unmodeled f_sigma8: select covariance, never precision submatrix.
    marginal = [row[:2] for row in c[:2]]
    cholesky(marginal)
    return obs, c, marginal


def chi2_bao(obs, pred, cov):
    if len(obs) != 2 or len(pred) != 2 or any(not math.isfinite(x) or x <= 0 for x in (*obs, *pred)):
        raise ValueError("INVALID_BAO_VECTOR")
    lower = cholesky(cov)
    if len(lower) != 2:
        raise ValueError("BAO_COVARIANCE_SHAPE")
    x0 = (obs[0] - pred[0]) / lower[0][0]
    x1 = (obs[1] - pred[1] - lower[1][0] * x0) / lower[1][1]
    result = x0*x0 + x1*x1
    if not math.isfinite(result):
        raise ValueError("NONFINITE_CHI2")
    return result


def build(root, prediction=None):
    data, a = read_pinned(root / NAMES[0], BLOBS[0])
    matrix, b = read_pinned(root / NAMES[1], BLOBS[1])
    obs, c, marginal = parse(data, matrix)
    return dict(schema="rll.eboss_dr16_qso_custody.v1", state="PASS_QSO_CUSTODY_SCOPED",
                source=SOURCE, release=RELEASE, likelihood="bao.sdss_dr16_baoplus_qso",
                source_files=[a, b], z_eff=1.48, order=list(ORDER), observed=obs,
                full_covariance=c, bao_marginal_covariance=marginal,
                chi2_bao=None if prediction is None else chi2_bao(obs[:2], prediction, marginal),
                prediction=None if prediction is None else list(prediction),
                prediction_provenance="NOT_SUPPLIED" if prediction is None else "CALLER_SUPPLIED_UNVERIFIED",
                model_selection="NOT_RUN", growth="BLOCKED_PERTURBATION_CLOSURE",
                joint_ingestion="BLOCKED_CROSS_SURVEY_OVERLAP_AND_COVARIANCE",
                rights="TOKEN_VAZIO_REDISTRIBUTION_AUTHORITY",
                claim_allowed=False, promotion_allowed=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir", type=Path, required=True)
    p.add_argument("--bao-prediction", nargs=2, type=float, metavar=("DM_RD", "DH_RD"))
    a = p.parse_args()
    print(json.dumps(build(a.source_dir, a.bao_prediction), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
