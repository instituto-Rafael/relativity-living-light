#!/usr/bin/env python3
"""H-CRIT: bounded scalar diagnostics, NOT equations of state or RLL fitting.

Standard-library only; no networking, no external data reads or side effects.
Every input name carries its SI unit. Synthetic values are not observations.
"""
import argparse
import json
import math
from pathlib import Path

C = 299792458.0
G = 6.67430e-11
EPS0 = 8.8541878128e-12
MU0 = 1.25663706212e-6
KB = 1.380649e-23
HBAR = 1.054571817e-34
QE = 1.602176634e-19
ME = 9.1093837139e-31
NA = 6.02214076e23

class Blocked(ValueError):
    """Missing, nonfinite, dimensionally ambiguous, or unphysical input."""

def number(data, name, minimum=None, positive=False):
    if name not in data:
        raise Blocked("TOKEN_VAZIO:" + name)
    x = data[name]
    if isinstance(x, bool) or not isinstance(x, (float, int)):
        raise Blocked("INVALID_TYPE:" + name)
    x = float(x)
    if not math.isfinite(x):
        raise Blocked("NONFINITE:" + name)
    if positive and x <= 0:
        raise Blocked("NONPOSITIVE:" + name)
    if minimum is not None and x < minimum:
        raise Blocked("OUT_OF_DOMAIN:" + name)
    return x

def _thermal(a):
    return {"value": KB * (number(a, "n_e_m3", minimum=0) * number(a, "T_e_K", minimum=0)
                         + number(a, "n_i_m3", minimum=0) * number(a, "T_i_K", minimum=0)), "unit": "Pa"}

def _adiabatic(a):
    gamma = number(a, "gamma", positive=True)
    if gamma <= 1: raise Blocked("GAMMA_MUST_EXCEED_ONE")
    t0 = number(a, "T0_K", positive=True)
    d0 = number(a, "rho0_kg_m3", positive=True)
    d1 = number(a, "rho1_kg_m3", positive=True)
    return {"value": t0 * (d1 / d0) ** (gamma - 1), "unit": "K"}

def _plasma(a):
    n = number(a, "n_e_m3", minimum=0)
    return {"value": math.sqrt(n * QE * QE / (EPS0 * ME)), "unit": "rad/s"}

def _cyclotron(a):
    return {"value": QE * number(a, "B_T") / ME, "unit": "rad/s"}

def _debye(a):
    n = number(a, "n_e_m3", positive=True)
    t = number(a, "T_e_K", minimum=0)
    return {"value": math.sqrt(EPS0 * KB * t / (n * QE * QE)), "unit": "m"}

def _magnetic(a):
    b = number(a, "B_T")
    return {"value": b * b / (2 * MU0), "unit": "Pa"}

def _electric(a):
    e = number(a, "E_V_m")
    return {"value": EPS0 * e * e / 2, "unit": "Pa"}

def _beta(a):
    b = number(a, "B_T")
    if b == 0: raise Blocked("ZERO_MAGNETIC_FIELD")
    return {"value": 2 * MU0 * number(a, "thermal_P_Pa", minimum=0) / (b * b), "unit": "1"}

def _shock(a):
    gam = number(a, "gamma", positive=True)
    mach = number(a, "M", positive=True)
    if gam <= 1 or mach <= 1: raise Blocked("CLASSICAL_SHOCK_DOMAIN")
    return {"value": ((gam + 1) * mach * mach) /
            ((gam - 1) * mach * mach + 2), "unit": "1"}

def _fermi(a):
    n = number(a, "n_e_m3", minimum=0)
    p = HBAR * (3 * math.pi * math.pi * n) ** (1 / 3)
    pc = p * C
    mc2 = ME * C * C
    kinetic = (pc * pc) / (math.hypot(pc, mc2) + mc2)
    return {"value": kinetic / (QE * 1e6), "unit": "MeV"}

def _area(a):
    return {"value": 4 / number(a, "ligament_d_m", positive=True), "unit": "m^-1"}

def _relative_modulus(a):
    before = number(a, "E_before_Pa", positive=True)
    after = number(a, "E_after_Pa", positive=True)
    return {"value": (after - before) / before, "unit": "1"}

def _schwarzschild(a):
    return {"value": 2 * G * number(a, "M_kg", positive=True) / (C * C), "unit": "m"}

def _compactness(a):
    return {"value": G * number(a, "M_kg", positive=True) /
            (number(a, "R_m", positive=True) * C * C), "unit": "1"}

def _tide(a):
    mass = number(a, "M_kg", positive=True)
    r = number(a, "r_m", positive=True)
    ell = number(a, "ell_m", minimum=0)
    if ell >= r: raise Blocked("LINEAR_TIDE_DOMAIN")
    return {"value": 2 * G * mass * ell / r**3, "unit": "m/s^2"}

def _photon(a):
    wavelength = number(a, "lambda_m", positive=True)
    return {"value": 6.62607015e-34 * C / wavelength, "unit": "J"}

def _molar_ev(a):
    return {"value": number(a, "E_eV", minimum=0) * QE * NA, "unit": "J/mol"}

def _optical_depth(a):
    return {"value": number(a, "alpha_m_inv", minimum=0) *
            number(a, "path_m", minimum=0), "unit": "1"}

def _power(a):
    return {"value": number(a, "energy_J", minimum=0) /
            number(a, "duration_s", positive=True), "unit": "W"}

def _capillary(a):
    return {"value": 2 * number(a, "surface_tension_N_m", minimum=0) /
            number(a, "radius_m", positive=True), "unit": "Pa"}

def _radiation(a):
    return {"value": number(a, "flux_W_m2", minimum=0) / C, "unit": "Pa"}

def _coulomb(a):
    r = number(a, "separation_m", positive=True)
    q1 = number(a, "q1_C")
    q2 = number(a, "q2_C")
    return {"value": q1 * q2 / (4 * math.pi * EPS0 * r * r), "unit": "N"}

def _redshift(a):
    rs = 2 * G * number(a, "M_kg", positive=True) / (C * C)
    r = number(a, "r_m", positive=True)
    if r <= rs: raise Blocked("STATIC_OBSERVER_OUTSIDE_HORIZON_ONLY")
    return {"value": math.sqrt(1 - rs / r), "unit": "1"}

def _density_mol(a):
    return {"value": number(a, "amount_mol", minimum=0) /
            number(a, "area_m2", positive=True), "unit": "mol/m2"}

def _mu_capture_margin(a):
    # Purely algebraic margin of supplied chemical potentials; no reaction-rate prediction.
    mp = number(a, "mu_p_MeV")
    me = number(a, "mu_e_MeV")
    mn = number(a, "mu_n_MeV")
    mnu = number(a, "mu_nu_MeV")
    return {"value": mp + me - mn - mnu, "unit": "MeV"}

def _chi2(a):
    d = a.get("residual")
    cov = a.get("covariance")
    if not isinstance(d, list) or not 1 <= len(d) <= 32:
        raise Blocked("INVALID_RESIDUAL_VECTOR")
    n = len(d)
    if not isinstance(cov, list) or len(cov) != n:
        raise Blocked("INVALID_COVARIANCE_SHAPE")
    v = [number({"x": x}, "x") for x in d]
    mat = []
    for row in cov:
        if not isinstance(row, list) or len(row) != n:
            raise Blocked("INVALID_COVARIANCE_SHAPE")
        mat.append([number({"x": x}, "x") for x in row])
    for i in range(n):
        for j in range(n):
            if not math.isclose(mat[i][j], mat[j][i], rel_tol=1e-10, abs_tol=1e-12):
                raise Blocked("ASYMMETRIC_COVARIANCE")
    # Cholesky: reject non-SPD and never silently invert a singular covariance.
    lower = [[0.] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                rem = mat[i][i] - s
                if rem <= 0: raise Blocked("COVARIANCE_NOT_SPD")
                lower[i][j] = math.sqrt(rem)
            else:
                lower[i][j] = (mat[i][j] - s) / lower[j][j]
    y = [0.] * n
    for i in range(n):
        y[i] = (v[i] - sum(lower[i][j] * y[j] for j in range(i))) / lower[i][i]
    return {"value": sum(x * x for x in y), "unit": "1"}


def _fermi_momentum(a):
    n = number(a, "n_e_m3", minimum=0)
    return {"value": HBAR * (3 * math.pi**2 * n) ** (1/3), "unit": "kg*m/s"}

def _theta(a):
    ef = number(a, "E_F_MeV", positive=True)
    return {"value": KB * number(a, "T_K", minimum=0) / (ef * 1e6 * QE), "unit": "1"}

def _electron_pressure_nr(a):
    n = number(a, "n_e_m3", minimum=0)
    pf = HBAR * (3 * math.pi**2 * n) ** (1/3)
    if pf / (ME * C) > 0.1: raise Blocked("NONREL_DEGENERACY_DOMAIN")
    return {"value": HBAR**2 * (3 * math.pi**2)**(2/3) * n**(5/3) / (5 * ME), "unit": "Pa"}

def _coupling(a):
    ni = number(a, "n_i_m3", positive=True)
    z = number(a, "Z", positive=True)
    t = number(a, "T_K", positive=True)
    spacing = (3 / (4 * math.pi * ni)) ** (1/3)
    return {"value": z * z * QE * QE / (4 * math.pi * EPS0 * spacing * KB * t), "unit": "1"}

def _mass_defect(a):
    return {"value": number(a, "delta_mass_kg") * C**2, "unit": "J"}

def _reaction_power(a):
    rate = number(a, "rate_m3_s", minimum=0)
    q = number(a, "Q_J", minimum=0)
    volume = number(a, "volume_m3", minimum=0)
    return {"value": rate * q * volume, "unit": "W"}

def _jeans(a):
    cs = number(a, "sound_speed_m_s", positive=True)
    density = number(a, "rho_kg_m3", positive=True)
    if cs >= .1 * C: raise Blocked("NEWTONIAN_JEANS_DOMAIN")
    return {"value": math.pi**2.5 * cs**3 / (6 * G**1.5 * math.sqrt(density)), "unit": "kg"}

def _accretion(a):
    eta = number(a, "eta", minimum=0)
    if eta > 1: raise Blocked("EFFICIENCY_GT_ONE")
    return {"value": eta * number(a, "mdot_kg_s", minimum=0) * C**2, "unit": "W"}

def _frequency(a):
    return {"value": number(a, "g", positive=True) * number(a, "nu_emit_Hz", minimum=0), "unit": "Hz"}

def _radiation_balance(a):
    return {"value": number(a, "emit_W", minimum=0) - number(a, "atmos_W", minimum=0)
            - number(a, "solar_W", minimum=0) - number(a, "nonrad_W", minimum=0), "unit": "W"}

def _hubble(a):
    return {"value": C / number(a, "H_s_inv", positive=True), "unit": "m"}

def _aicc(a):
    chi2 = number(a, "chi2", minimum=0)
    k = number(a, "k", minimum=0)
    n = number(a, "N", positive=True)
    if k != int(k) or n != int(n) or n <= k + 1: raise Blocked("AICC_DOMAIN")
    return {"value": chi2 + 2*k + 2*k*(k+1)/(n-k-1), "unit": "1"}

def _electrowetting(a):
    theta0 = number(a, "theta0_rad", minimum=0)
    if theta0 > math.pi: raise Blocked("THETA_DOMAIN")
    ca = number(a, "C_area_F_m2", minimum=0)
    voltage = number(a, "V_V")
    gamma = number(a, "gamma_N_m", positive=True)
    ct = math.cos(theta0) + ca * voltage**2 / (2 * gamma)
    if not -1 <= ct <= 1: raise Blocked("YOUNG_LIPPMANN_SATURATION")
    return {"value": math.acos(ct), "unit": "rad"}

def _electrostriction(a):
    return {"value": number(a, "Q_m2_V2") * number(a, "E_V_m")**2, "unit": "1"}

def _piezoelectric(a):
    return {"value": number(a, "d_m_V") * number(a, "E_V_m"), "unit": "1"}

def _heat_flux(a):
    return {"value": -number(a, "conductivity_W_m_K", minimum=0)
            * number(a, "grad_T_K_m"), "unit": "W/m2"}

def _hall_petch(a):
    return {"value": number(a, "sigma0_Pa", minimum=0)
            + number(a, "k_Pa_sqrt_m", minimum=0) / math.sqrt(number(a, "grain_m", positive=True)), "unit": "Pa"}

def _clapeyron(a):
    dv = number(a, "delta_v_m3_mol")
    if dv == 0: raise Blocked("ZERO_PHASE_VOLUME_DIFFERENCE")
    return {"value": number(a, "delta_s_J_mol_K") / dv, "unit": "Pa/K"}

def _damkohler(a):
    return {"value": number(a, "flow_s", positive=True) /
            number(a, "reaction_s", positive=True), "unit": "1"}

KERNELS = {
 "thermal_pressure": _thermal, "adiabatic_T": _adiabatic,
 "plasma_omega": _plasma, "cyclotron_omega": _cyclotron,
 "debye_length": _debye, "magnetic_pressure": _magnetic,
 "electric_pressure": _electric, "plasma_beta": _beta,
 "shock_ratio": _shock, "fermi_kinetic": _fermi,
 "ligament_A_over_V": _area, "measured_modulus_delta": _relative_modulus,
 "schwarzschild_r": _schwarzschild, "compactness": _compactness,
 "tidal_acceleration": _tide, "photon_energy": _photon,
 "ev_per_mol": _molar_ev, "optical_depth": _optical_depth,
 "energy_per_time": _power, "capillary_pressure": _capillary,
 "radiation_pressure": _radiation, "coulomb_force": _coulomb,
 "schwarzschild_g": _redshift, "molar_area": _density_mol,
 "chemical_margin": _mu_capture_margin, "chi2_spd": _chi2,
 "fermi_momentum": _fermi_momentum, "degeneracy_theta": _theta,
 "degenerate_pressure_nr": _electron_pressure_nr, "coulomb_gamma": _coupling,
 "mass_defect_energy": _mass_defect, "reaction_power": _reaction_power,
 "jeans_mass": _jeans, "accretion_power": _accretion,
 "frequency_shift": _frequency, "radiation_balance": _radiation_balance,
 "hubble_distance": _hubble, "aicc": _aicc,
 "electrowetting": _electrowetting, "electrostriction": _electrostriction,
 "piezoelectric": _piezoelectric, "thermal_flux": _heat_flux,
 "hall_petch": _hall_petch, "clapeyron_slope": _clapeyron,
 "damkohler": _damkohler
}

def evaluate(kernel, inputs):
    if kernel not in KERNELS: raise Blocked("KERNEL_NOT_IMPLEMENTED:" + kernel)
    if not isinstance(inputs, dict): raise Blocked("INPUT_OBJECT_REQUIRED")
    result = KERNELS[kernel](inputs)
    if not math.isfinite(result["value"]): raise Blocked("NONFINITE_RESULT")
    return result

def audit(registry):
    if registry.get("schema") != "RLL_HCRIT_H01_H72_SCOPED_V1": raise Blocked("SCHEMA")
    rows = registry.get("entries")
    if not isinstance(rows, list) or len(rows) != 72: raise Blocked("REQUIRED_72_IDS")
    ids = [r.get("id") for r in rows]
    if ids != ["H%02d" % i for i in range(1, 73)]: raise Blocked("ID_ORDER_DUPLICATE_OR_GAP")
    for row in rows:
        for key in ("id", "domain", "name", "expression", "observable", "falsifier", "classification"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise Blocked("MISSING_FIELD:" + row.get("id", "?") + ":" + key)
        if row.get("claim_allowed") is not False or row.get("data") != "TOKEN_VAZIO":
            raise Blocked("CLAIM_OR_DATA_PROMOTION:" + row["id"])
        kernel = row.get("kernel")
        if kernel is not None and kernel not in KERNELS:
            raise Blocked("UNRECOGNIZED_KERNEL:" + row["id"])
        if row.get("execution") != ("SCALAR_KERNEL_AVAILABLE" if kernel else "MODEL_REQUIRED"):
            raise Blocked("FALSE_EXECUTION_STATUS:" + row["id"])
    return {"entries": len(rows), "scalar_kernels": len(KERNELS),
            "bound_rows": sum(x.get("kernel") is not None for x in rows),
            "full_physical_models": 0, "observational_fits": 0,
            "claim_allowed": False, "status": "STRUCTURAL_AUDIT_ONLY"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path)
    p.add_argument("--audit", action="store_true")
    p.add_argument("--kernel", choices=sorted(KERNELS))
    p.add_argument("--input-json")
    a = p.parse_args()
    if a.audit:
        if not a.registry: p.error("--registry is required for --audit")
        print(json.dumps(audit(json.loads(a.registry.read_text(encoding="utf-8"))), sort_keys=True))
    elif a.kernel:
        if a.input_json is None: p.error("--input-json required for --kernel")
        print(json.dumps(evaluate(a.kernel, json.loads(a.input_json)), sort_keys=True))
    else: p.error("select --audit or --kernel")
if __name__ == "__main__":
    main()
