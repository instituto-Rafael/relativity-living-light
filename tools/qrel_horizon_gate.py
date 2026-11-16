"""Bounded exact-algebra falsifier for a *surrogate* of Dorau--Much (2026).

This is NOT a QFT modular-theory implementation or a gravity prediction.
Fraction arithmetic checks the finite-support, 1+1-dimensional null-flux
moment and the conditional Bekenstein--Hawking coefficient. No dependencies.
See docs/science/QREL_DORAU_MUCH_GATE_V1.md for scope and provenance.
"""
from fractions import Fraction

DOI = "10.1103/lmq8-nsty"
MAX_DEGREE = 16


def _fraction(value):
    if isinstance(value, float):
        raise TypeError("float forbidden: use integer or Fraction for exact algebra")
    return Fraction(value)


def _polynomial_value(coefficients, u):
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value * u + coefficient
    return value


def _derivative(coefficients):
    return tuple(Fraction(i) * value for i, value in enumerate(coefficients) if i)


def null_flux_moment(coefficients, length=1):
    """Exactly integrate -u [d(phi)/du]^2 du on [-length, 0].

    Input is phi(u)=sum(coefficients[i]*u**i), with phi and phi' zero
    at both endpoints. Only a finite patch with transverse area=1 is tested;
    polynomial compact extension is C1 rather than necessarily C-infinity.
    """
    length = _fraction(length)
    coefficients = tuple(_fraction(v) for v in coefficients)
    if not 0 < length or not 2 <= len(coefficients) <= MAX_DEGREE + 1:
        raise ValueError("positive length and degree 1..16 required")
    derivative = _derivative(coefficients)
    if any(_polynomial_value(p, u) for p in (coefficients, derivative)
           for u in (Fraction(0), -length)):
        raise ValueError("phi and phi' must vanish at interval endpoints")
    # Antiderivative of -u times the squared polynomial derivative.
    # i,j index u**i and u**j of phi', so the moment equals
    # sum_{ij} d_i*d_j*(-L)**(i+j+2)/(i+j+2).
    return sum((a * b * (-length) ** (i+j+2) / (i+j+2)
                for i, a in enumerate(derivative)
                for j, b in enumerate(derivative)), Fraction(0))


def symbolic_area_bridge(flux, *, assume_bh_area_law=False, coherent_state=False):
    """Return quantities in multiples of pi; never infer the area law.

    S_rel/pi = 2*flux; (delta A)/pi = 4*S_rel/pi *only if*
    a separate area-law assumption is enabled, in G=hbar=c=kB=1.
    No physical entropy is inferred for arbitrary input profiles/states.
    """
    flux = _fraction(flux)
    if flux < 0:
        raise ValueError("negative null flux violates this gate's premise")
    if not coherent_state:
        raise ValueError("coherent-state restriction is required")
    s_rel_over_pi = 2 * flux
    area_over_pi = (4 * s_rel_over_pi) if assume_bh_area_law else None
    alpha_over_pi = (area_over_pi / flux) if (flux and area_over_pi is not None) else None
    return {"flux": flux, "s_rel_over_pi": s_rel_over_pi,
            "area_over_pi": area_over_pi, "alpha_over_pi": alpha_over_pi,
            "area_law_assumed": bool(assume_bh_area_law),
            "physical_claim_allowed": False}


def null_contractions_vanish_1p1(a_tt, a_tx, a_xx):
    """For symmetric A_ab in diag(-1,1), test null k=(1,+/-1).

    This limited 1+1 identity tests only A_ab proportional to g_ab;
    it does NOT establish the four-dimensional geometric theorem.
    """
    a_tt, a_tx, a_xx = map(_fraction, (a_tt, a_tx, a_xx))
    return a_tt + 2 * a_tx + a_xx == 0 and a_tt - 2 * a_tx + a_xx == 0


def gate_witness():
    # phi=u^2(u+1)^2 on [-1,0], C1 under zero extension.
    flux = null_flux_moment((0, 0, 1, 2, 1))
    values = symbolic_area_bridge(flux, assume_bh_area_law=True, coherent_state=True)
    return {"doi": DOI, "state": "FORMAL_CONSISTENCY_SURROGATE_ONLY",
            "flux_exact": str(flux), "s_rel_over_pi_exact": str(values["s_rel_over_pi"]),
            "area_over_pi_exact": str(values["area_over_pi"]),
            "alpha_over_pi_exact": str(values["alpha_over_pi"]),
            "area_law_assumed": True, "modular_theory_proven": False,
            "four_dimensional_gravity_derived": False,
            "rll_deviation_observed": "TOKEN_VAZIO", "claim_allowed": False}
