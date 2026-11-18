"""RLL G0/G1 spatial geometry diagnostics; no physical/inference claims.

Euclidean vectors in a declared local orthonormal frame, angles in radians.
No library other than Python stdlib. 3D distances require source distance,
which is not reconstructed from sky position alone.
"""
import math


def _v3(values, name):
    try:
        out = tuple(float(x) for x in values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + ' must be a finite 3-vector') from exc
    if len(out) != 3 or not all(math.isfinite(x) for x in out):
        raise ValueError(name + ' must be a finite 3-vector')
    return out


def _angles(ra_rad, dec_rad):
    ra, dec = float(ra_rad), float(dec_rad)
    if not (math.isfinite(ra) and math.isfinite(dec) and -math.pi/2 <= dec <= math.pi/2):
        raise ValueError('finite RA and declination in [-pi/2, pi/2] required')
    return ra, dec


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def sky_direction(ra_rad, dec_rad, distance=None):
    """Return ICRS-style direction; distance is never inferred from angles.

    With distance=None only a *unit direction* is known. If a finite, positive
    source distance is explicitly supplied, return observer-relative XYZ.
    Frame origin/epoch are caller responsibilities, not assumed here.
    """
    ra, dec = _angles(ra_rad, dec_rad)
    cd = math.cos(dec)
    u = (cd*math.cos(ra), cd*math.sin(ra), math.sin(dec))
    result = {'direction': u, 'position': None, 'distance_status':
              'TOKEN_VAZIO_LINE_OF_SIGHT_DISTANCE', 'claim_allowed': False}
    if distance is not None:
        d = float(distance)
        if not (math.isfinite(d) and d > 0.0):
            raise ValueError('source distance must be finite and positive')
        p = tuple(d*x for x in u)
        if not all(math.isfinite(x) for x in p):
            raise ValueError('cartesian position exceeds finite range')
        result['position'] = p
        result['distance_status'] = 'DISTANCE_SUPPLIED_NOT_INFERRED'
    return result


def tangent_frame_components(displacement, ra_rad, dec_rad):
    """Resolve XYZ displacement into local east/north/line-of-sight axes.

    Direction (ra,dec) defines observer-relative orthonormal frame. This is
    a *linear projection*, not a claim about orbit, distance or gravitational
    potential. All three components use the input vector's declared units.
    """
    d = _v3(displacement, 'displacement')
    ra, dec = _angles(ra_rad, dec_rad)
    east = (-math.sin(ra), math.cos(ra), 0.0)
    north = (-math.sin(dec)*math.cos(ra), -math.sin(dec)*math.sin(ra), math.cos(dec))
    los = sky_direction(ra, dec)['direction']
    e, n, z = _dot(d, east), _dot(d, north), _dot(d, los)
    transverse = math.hypot(e, n)
    spatial = math.hypot(*d)
    if not all(math.isfinite(x) for x in (e, n, z, transverse, spatial)):
        raise ValueError('input magnitude exceeds finite range')
    return {
        'east': e, 'north': n, 'line_of_sight': z,
        'diagonal_2d': transverse, 'diagonal_3d': spatial,
        'inclination_to_sky_rad': math.atan2(z, transverse) if spatial else None,
        'distance_status': 'INPUT_3D_REQUIRED', 'claim_allowed': False,
    }


def spatial_diagonal(p0, p1, ra_rad, dec_rad):
    """3D chord and its sky-plane/LOS decomposition; no motion from one chord."""
    a, b = _v3(p0, 'p0'), _v3(p1, 'p1')
    d = tuple(y-x for x,y in zip(a,b))
    if not all(math.isfinite(x) for x in d):
        raise ValueError('displacement exceeds finite range')
    return {'difference': d, **tangent_frame_components(d, ra_rad, dec_rad)}


def hex_oblique_diagonal(a, b):
    """Length of a*e1+b*e2 where unit basis vectors meet at 60 degrees."""
    a, b = float(a), float(b)
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError('finite coefficients required')
    v = math.hypot(a+0.5*b, 0.5*math.sqrt(3.0)*b)
    if not math.isfinite(v):
        raise ValueError('length not finite')
    return v


def nonplanarity_four_points(points):
    """Signed, dimensionless triple-product index for FOUR 3D positions.

    Each of three chord vectors is independently normalized; |index| <= 1.
    Exactly zero means coplanarity only in exact arithmetic; observational
    significance requires covariance/error propagation and a tolerance model.
    Three points alone cannot reject coplanarity.
    """
    try:
        p = tuple(_v3(x, 'point') for x in points)
    except (TypeError, ValueError) as exc:
        raise ValueError('four finite 3D positions required') from exc
    if len(p) != 4:
        raise ValueError('exactly four spatial positions are required')
    base = p[0]
    v = [tuple(q[i]-base[i] for i in range(3)) for q in p[1:]]
    if any(not all(math.isfinite(c) for c in x) for x in v):
        raise ValueError('spatial differences exceed finite range')
    lengths = [math.hypot(*x) for x in v]
    if any(not math.isfinite(x) or x == 0.0 for x in lengths):
        return {'state': 'TOKEN_VAZIO_DEGENERATE_CHORD', 'index': None,
                'claim_allowed': False}
    a,b,c = [tuple(x/l for x in v0) for v0,l in zip(v,lengths)]
    signed = _dot(a, _cross(b,c))
    signed = max(-1.0,min(1.0,signed))
    return {'state': 'DEFINED_GEOMETRY_ONLY', 'index': signed,
            'absolute_index': abs(signed), 'claim_allowed': False}


def tilted_ellipse_point(center, axis_u, axis_v, semimajor, semiminor, theta_rad):
    """Point/tangent on a 3D ellipse in an explicitly declared plane.

    A 3D ellipse remains planar at any one epoch; different epochs may have
    different planes. No material-point time correspondence is inferred.
    """
    center, u, v = _v3(center,'center'), _v3(axis_u,'axis_u'), _v3(axis_v,'axis_v')
    a, b, t = float(semimajor), float(semiminor), float(theta_rad)
    if not all(math.isfinite(x) for x in (a,b,t)) or not (a >= b > 0):
        raise ValueError('finite semiaxes a >= b > 0 and finite angle required')
    if not (abs(math.hypot(*u)-1.0)<1e-10 and
            abs(math.hypot(*v)-1.0)<1e-10 and abs(_dot(u,v))<1e-10):
        raise ValueError('ellipse axes must be orthonormal')
    cs, sn = math.cos(t), math.sin(t)
    point = tuple(center[i]+a*cs*u[i]+b*sn*v[i] for i in range(3))
    tangent = tuple(-a*sn*u[i]+b*cs*v[i] for i in range(3))
    if not all(math.isfinite(x) for x in (*point,*tangent)):
        raise ValueError('projected ellipse exceeds finite range')
    return {'position': point, 'tangent': tangent, 'plane_normal': _cross(u,v),
            'claim_allowed': False}
