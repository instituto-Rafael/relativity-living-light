#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import struct
from itertools import combinations

N = 8
D = 7
EPS = 1e-10


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', x))[0]


def build_matrix() -> list[list[float]]:
    a = [[f32((i << 1) + j) for j in range(N)] for i in range(N)]
    b = [[f32(i + 3 * j) for j in range(N)] for i in range(N)]
    c = [[f32(0.0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for k in range(N):
            aik = a[i][k]
            for j in range(N):
                c[i][j] = f32(c[i][j] + f32(aik * b[k][j]))
    return c


def norm2(v: list[float]) -> float:
    return sum(x * x for x in v)


def lift_column(c: list[list[float]], j: int, scale: float) -> dict[str, object]:
    raw_t = float(c[0][j])
    raw_v = [float(c[d + 1][j]) for d in range(D)]
    raw_delta = raw_t * raw_t - norm2(raw_v)
    q = [x / scale for x in raw_v]
    x0 = math.sqrt(1.0 + norm2(q))
    p = [x / (x0 + 1.0) for x in q]
    r2 = norm2(p)
    return {
        'column': j,
        'raw_delta': raw_delta,
        'q': q,
        'x0': x0,
        'p': p,
        'radius': math.sqrt(r2),
        'hyperboloid_residual': abs(x0 * x0 - norm2(q) - 1.0),
        'radius_identity_residual': abs(r2 - (x0 - 1.0) / (x0 + 1.0)),
    }


def ball_to_hyperboloid(p: list[float]) -> tuple[float, list[float]]:
    r2 = norm2(p)
    denom = 1.0 - r2
    return (1.0 + r2) / denom, [2.0 * x / denom for x in p]


def poincare_distance(p: list[float], q: list[float]) -> float:
    rp = norm2(p)
    rq = norm2(q)
    diff = norm2([a - b for a, b in zip(p, q)])
    arg = 1.0 + 2.0 * diff / ((1.0 - rp) * (1.0 - rq))
    return math.acosh(max(1.0, arg))


def project_timelike(t: float, v: list[float]) -> list[float]:
    delta = t * t - norm2(v)
    if not (t > 0.0 and delta > 0.0):
        raise ValueError('fixture is not future timelike')
    s = math.sqrt(delta)
    x0 = t / s
    xs = [x / s for x in v]
    return [x / (x0 + 1.0) for x in xs]


def lorentz_boost(t: float, v: list[float], xi: float) -> tuple[float, list[float]]:
    ch, sh = math.cosh(xi), math.sinh(xi)
    out = list(v)
    out_t = ch * t + sh * v[0]
    out[0] = sh * t + ch * v[0]
    return out_t, out


def masked_softmax(logits: list[float], valid: list[bool]) -> list[float]:
    active = [x for x, ok in zip(logits, valid) if ok]
    if not active:
        return [0.0] * len(logits)
    m = max(active)
    exps = [math.exp(x - m) if ok else 0.0 for x, ok in zip(logits, valid)]
    z = sum(exps)
    return [x / z for x in exps]


def validate() -> dict[str, object]:
    c = build_matrix()
    scale = max(abs(x) for row in c for x in row)
    points = [lift_column(c, j, scale) for j in range(N)]
    ps = [p['p'] for p in points]

    roundtrip_residuals = []
    radial_residuals = []
    for item in points:
        x0r, xsr = ball_to_hyperboloid(item['p'])
        roundtrip_residuals.append(max(abs(x0r - item['x0']), max(abs(a - b) for a, b in zip(xsr, item['q']))))
        radial_residuals.append(abs(poincare_distance([0.0] * D, item['p']) - 2.0 * math.atanh(item['radius'])))

    dist = [[poincare_distance(ps[i], ps[j]) for j in range(N)] for i in range(N)]
    symmetry = max(abs(dist[i][j] - dist[j][i]) for i in range(N) for j in range(N))
    diagonal = max(abs(dist[i][i]) for i in range(N))
    triangle_violation = 0.0
    for i, j, k in combinations(range(N), 3):
        triangle_violation = max(
            triangle_violation,
            dist[i][k] - dist[i][j] - dist[j][k],
            dist[i][j] - dist[i][k] - dist[k][j],
            dist[j][k] - dist[j][i] - dist[i][k],
        )

    eta = 0.75
    t = math.cosh(eta)
    v = [math.sinh(eta)] + [0.0] * (D - 1)
    p_t = project_timelike(t, v)
    x0_t, xs_t = ball_to_hyperboloid(p_t)

    xi = 0.37
    bt, bv = lorentz_boost(t, v, xi)
    boost_before = t * t - norm2(v)
    boost_after = bt * bt - norm2(bv)
    p_b = project_timelike(bt, bv)

    probs = masked_softmax([0.0, 0.0, 0.0], [True, False, True])
    zero_valid_probs = masked_softmax([0.0, 0.0], [True, True])

    checks = {
        'matrix_shape_8x8': len(c) == 8 and all(len(row) == 8 for row in c),
        'matrix_anchors': c[0][0] == 140.0 and c[7][7] == 3472.0,
        'raw_columns_all_spacelike': all(p['raw_delta'] < 0.0 for p in points),
        'canonical_lift_hyperboloid_identity': max(p['hyperboloid_residual'] for p in points) < 1e-12,
        'canonical_lift_radius_identity': max(p['radius_identity_residual'] for p in points) < 1e-12,
        'all_points_inside_ball': all(0.0 <= p['radius'] < 1.0 for p in points),
        'ball_hyperboloid_roundtrip': max(roundtrip_residuals) < 1e-12,
        'radial_distance_identity': max(radial_residuals) < 1e-12,
        'pairwise_distances_finite_nonnegative': all(math.isfinite(x) and x >= 0.0 for row in dist for x in row),
        'distance_symmetry': symmetry < 1e-12,
        'distance_diagonal_zero': diagonal < 1e-12,
        'triangle_inequality': triangle_violation <= 1e-12,
        'strict_timelike_fixture_activates_projection': norm2(p_t) < 1.0 and abs(x0_t * x0_t - norm2(xs_t) - 1.0) < 1e-12,
        'strict_timelike_roundtrip': abs(x0_t - t) < 1e-12 and max(abs(a - b) for a, b in zip(xs_t, v)) < 1e-12,
        'lorentz_boost_preserves_minkowski_norm': abs(boost_before - boost_after) < 1e-12,
        'boosted_point_remains_inside_ball': norm2(p_b) < 1.0,
        'token_vazio_mask_is_explicit': probs[1] == 0.0 and abs(sum(probs) - 1.0) < 1e-15,
        'zero_vector_remains_valid_when_unmasked': all(x > 0.0 for x in zero_valid_probs) and abs(sum(zero_valid_probs) - 1.0) < 1e-15,
        'no_nan_or_inf': all(math.isfinite(p['radius']) and all(math.isfinite(x) for x in p['p']) for p in points),
    }

    passed = sum(checks.values())
    return {
        'schema': 'rll.poincare_ball_7d.emergent_validation.v1',
        'status': 'PASS' if passed == len(checks) else 'FAIL',
        'checks_total': len(checks),
        'checks_passed': passed,
        'checks_failed': len(checks) - passed,
        'checks': checks,
        'metrics': {
            'scale': scale,
            'radius_min': min(p['radius'] for p in points),
            'radius_max': max(p['radius'] for p in points),
            'max_hyperboloid_residual': max(p['hyperboloid_residual'] for p in points),
            'max_radius_identity_residual': max(p['radius_identity_residual'] for p in points),
            'max_roundtrip_residual': max(roundtrip_residuals),
            'max_radial_distance_residual': max(radial_residuals),
            'max_distance_symmetry_residual': symmetry,
            'max_distance_diagonal_residual': diagonal,
            'max_triangle_violation': triangle_violation,
            'boost_norm_residual': abs(boost_before - boost_after),
            'timelike_fixture_radius': math.sqrt(norm2(p_t)),
            'boosted_fixture_radius': math.sqrt(norm2(p_b)),
        },
        'states': {
            'raw_hyperboloid_membership': 'FAIL_PRECONDITION_SPACELIKE',
            'canonical_lift': 'PASS_COMPUTATIONAL_EMBEDDING',
            'hyperbolic_metric': 'PASS_DETERMINISTIC_VALIDATION',
            'explicit_token_vazio_mask': 'PASS_SEMANTIC_CONTRACT',
            'lorentz_fixture': 'PASS_SYNTHETIC_FIXTURE',
            'native_aarch64_runtime': 'TOKEN_VAZIO',
            'hardware_cache_dmb': 'TOKEN_VAZIO_ENVIRONMENT',
            'physical_stability': 'TOKEN_VAZIO',
            'cosmology': 'PROHIBITED_BY_SCOPE',
            'claim_allowed': False,
        },
        'lateral_emergents': [
            'zero vector is a valid geometric point and cannot encode TOKEN_VAZIO by itself',
            'strict negative result and canonical lift must remain separate evidence states',
            'H7-to-B7 roundtrip is a stronger validator than radius-only membership',
            'pairwise geodesic distance is the valid bridge from embedding to geometric attention',
            'Lorentz invariance can be tested with synthetic timelike fixtures without claiming physical measurement',
            'hardware ordering, physical stability and cosmology require independent receipts and cannot be inferred from geometry',
        ],
    }


if __name__ == '__main__':
    report = validate()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
