#!/usr/bin/env python3
"""H-CRIT S3: typed provenance/physics boundaries, not EOS/GRMHD/experimental proof.

Zero external libraries, network, implicit unit conversions, claims or side effects.
Inputs are explicit SI scalars and descriptive provenance references.
"""
import math
import re

MU0 = 1.25663706212e-6
_SHA = re.compile(r"^[0-9a-f]{64}$")

class Blocked(ValueError):
    pass

def fail(code):
    raise Blocked(code)

def scalar(x, name, positive=False, nonnegative=False):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        fail('INVALID_FINITE_NUMBER:' + name)
    if positive and x <= 0 or nonnegative and x < 0:
        fail('OUT_OF_DOMAIN:' + name)
    return float(x)

def field(d, name):
    if not isinstance(d, dict) or name not in d or d[name] is None:
        fail('TOKEN_VAZIO:' + name)
    return d[name]

def ref(d, name):
    value = field(d, name)
    if not isinstance(value, str) or not value.strip():
        fail('INVALID_REF:' + name)
    return value

def digest(d, name):
    value = ref(d, name)
    if not _SHA.fullmatch(value):
        fail('INVALID_SHA256:' + name)
    return value

def labels(rows, origin):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 32:
        fail('INVALID_LABELS:' + origin)
    found = []
    for row in rows:
        key = ref(row, 'id')
        # Compound identity, never an unlabeled integer matrix index.
        if len(key.split('|')) < 4 or any(not part.strip() for part in key.split('|')):
            fail('UNBOUND_OBSERVATION:' + key)
        unit = ref(row, 'unit')
        found.append((key, unit))
    if len(set(found)) != len(found) or len({k for k, u in found}) != len(found):
        fail('DUPLICATE_OBSERVATION:' + origin)
    return found

def covariance_bound_chi2(packet):
    """Reorder covariance on BOTH axes against uniquely identified vector rows."""
    vector = field(packet, 'vector')
    covariance = field(packet, 'covariance')
    digest(vector, 'sha256')
    digest(covariance, 'sha256')
    ref(vector, 'source_ref')
    ref(covariance, 'source_ref')
    v_rows = field(vector, 'rows')
    c_rows = field(covariance, 'axis')
    vid = labels(v_rows, 'vector')
    cid = labels(c_rows, 'covariance')
    if len(vid) != len(cid) or set(vid) != set(cid):
        fail('ORDER_OR_UNIT_IDENTITY_MISMATCH')
    vals = [scalar(field(r, 'residual'), 'residual') for r in v_rows]
    raw = field(covariance, 'matrix')
    n = len(vid)
    if not isinstance(raw, list) or len(raw) != n:
        fail('COVARIANCE_SHAPE')
    mat = []
    for row in raw:
        if not isinstance(row, list) or len(row) != n:
            fail('COVARIANCE_SHAPE')
        mat.append([scalar(x, 'covariance') for x in row])
    idx = {identity: i for i, identity in enumerate(cid)}
    p = [idx[identity] for identity in vid]
    ordered = [[mat[i][j] for j in p] for i in p]
    for i in range(n):
        for j in range(n):
            if not math.isclose(ordered[i][j], ordered[j][i], rel_tol=1e-10, abs_tol=1e-12):
                fail('COVARIANCE_NOT_SYMMETRIC')
    # Pure Python SPD Cholesky, no silent pseudoinverse.
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            correction = sum(lower[i][k]*lower[j][k] for k in range(j))
            if i == j:
                rem = ordered[i][i] - correction
                if rem <= 0:
                    fail('COVARIANCE_NOT_SPD')
                lower[i][j] = math.sqrt(rem)
            else:
                lower[i][j] = (ordered[i][j] - correction)/lower[j][j]
    y = []
    for i in range(n):
        y.append((vals[i]-sum(lower[i][j]*y[j] for j in range(i)))/lower[i][i])
    return {'chi2': sum(x*x for x in y), 'unit':'1',
            'reordered': p != list(range(n)), 'row_count': n,
            'external_primary_order_verified': False, 'claim_allowed': False}

def capture_margin(packet):
    """Only for p+e^- <-> n+nu_e, with rest mass in all chemical potentials."""
    if field(packet, 'reaction') != 'p+e->n+nu_e':
        fail('WRONG_REACTION_FOR_CAPTURE_GATE')
    if field(packet, 'mu_convention') != 'FULL_INCLUDES_REST_ENERGY':
        fail('CHEMICAL_POTENTIAL_CONVENTION')
    m = {key: scalar(field(packet, key), key) for key in
         ('mu_p_MeV', 'mu_e_MeV', 'mu_n_MeV', 'mu_nu_e_MeV')}
    return {'affinity_MeV': m['mu_p_MeV']+m['mu_e_MeV']-m['mu_n_MeV']-m['mu_nu_e_MeV'],
            'rate': 'TOKEN_VAZIO', 'equilibrium': 'NOT_DETERMINED',
            'claim_allowed': False}

def chemical_affinity(packet):
    """Generic sum(nu*mu), with explicitly declared baryon/charge conservation."""
    if field(packet, 'mu_convention') != 'SAME_ZERO_AND_REST_ENERGY':
        fail('INCONSISTENT_CHEMICAL_ZERO')
    terms = field(packet, 'terms')
    if not isinstance(terms, list) or len(terms) < 2:
        fail('REACTION_TERMS_REQUIRED')
    names = set()
    balance_q = balance_b = delta = 0.0
    for term in terms:
        name = ref(term, 'species')
        if name in names:
            fail('DUPLICATED_REACTION_SPECIES')
        names.add(name)
        nu = scalar(field(term, 'nu'), 'nu')
        if not nu or not nu.is_integer():
            fail('STOICHIOMETRY_REQUIRED')
        charge = scalar(field(term, 'charge_e'), 'charge_e')
        baryon = scalar(field(term, 'baryon_number'), 'baryon_number')
        mu = scalar(field(term, 'mu_MeV'), 'mu_MeV')
        balance_q += nu * charge
        balance_b += nu * baryon
        delta += nu * mu
    if abs(balance_q) > 1e-12 or abs(balance_b) > 1e-12:
        fail('REACTION_CHARGE_OR_BARYON_NONCONSERVATION')
    return {'sum_products_minus_reactants_MeV': delta, 'affinity_MeV': -delta,
            'rate': 'TOKEN_VAZIO', 'claim_allowed': False}

def optical_depth(packet):
    """Integrated optical depth; does NOT perform transfer or spectral transport."""
    kind = field(packet, 'carrier')
    if kind == 'neutrino':
        species = ref(packet, 'neutrino_species')
        if species not in ('nu_e', 'anti_nu_e', 'nu_mu', 'anti_nu_mu', 'nu_tau', 'anti_nu_tau'):
            fail('UNKNOWN_NEUTRINO_SPECIES')
        scalar(field(packet, 'energy_MeV'), 'energy_MeV', positive=True)
        ref(packet, 'opacity_model_ref')
        ref(packet, 'composition_ref')
        ref(packet, 'eos_ref')
    elif kind == 'photon':
        scalar(field(packet, 'wavelength_m'), 'wavelength_m', positive=True)
        ref(packet, 'opacity_model_ref')
    else:
        fail('UNKNOWN_RADIATION_CARRIER')
    segments = field(packet, 'segments')
    if not isinstance(segments, list) or not segments:
        fail('PATH_SEGMENTS_REQUIRED')
    tau = 0.0
    for segment in segments:
        length = scalar(field(segment, 'length_m'), 'length_m', positive=True)
        coeff = scalar(field(segment, 'attenuation_per_m'), 'attenuation_per_m', nonnegative=True)
        tau += length * coeff
    if not math.isfinite(tau):
        fail('NUMERICAL_OVERFLOW')
    return {'tau': tau, 'unit': '1', 'carrier': kind,
            'transport_solved': False, 'claim_allowed': False}

def nanoporous_modulus(packet):
    if field(packet, 'material') != 'AuAg_dealloyed_Au':
        fail('NANOPOROUS_GOLD_MATERIAL_UNVERIFIED')
    ref(packet, 'sample_ref')
    d = scalar(field(packet, 'ligament_d_m'), 'ligament_d_m', positive=True)
    before = field(packet, 'before')
    after = field(packet, 'after')
    def state(x):
        e = scalar(field(x, 'modulus_Pa'), 'modulus_Pa', positive=True)
        v = scalar(field(x, 'potential_V'), 'potential_V')
        q = scalar(field(x, 'surface_charge_C_m2'), 'surface_charge_C_m2')
        t = scalar(field(x, 'temperature_K'), 'temperature_K', positive=True)
        c = scalar(field(x, 'adsorbate_fraction'), 'adsorbate_fraction', nonnegative=True)
        if c > 1: fail('ADSORBATE_COVERAGE_DOMAIN')
        return e, v, q, t, c
    a, b = state(before), state(after)
    return {'relative_modulus_change': (b[0]-a[0])/a[0],
            'potential_change_V': b[1]-a[1],
            'charge_change_C_m2': b[2]-a[2],
            'temperature_change_K': b[3]-a[3],
            'adsorbate_change': b[4]-a[4],
            'ideal_cylindrical_area_over_volume_m_inv': 4/d,
            'charge_vs_adsorbate_causality_established': False,
            'geometry_measured_3d': False,
            'claim_allowed': False}

def magnetic_maxwell_stress(packet):
    b = field(packet, 'B_T')
    if not isinstance(b, list) or len(b) != 3:
        fail('MAGNETIC_VECTOR_3D_REQUIRED')
    b = [scalar(v, 'B_T') for v in b]
    norm2 = sum(v*v for v in b)
    if not math.isfinite(norm2): fail('NUMERICAL_OVERFLOW')
    stress = [[(b[i]*b[j]-(norm2/2 if i==j else 0))/MU0
               for j in range(3)] for i in range(3)]
    return {'tensor_Pa': stress, 'scalar_magnetic_pressure_Pa': norm2/(2*MU0),
            'force_density': 'TOKEN_VAZIO', 'claim_allowed': False}

def audit_h01_h72_registry(registry):
    """Fail-closed bridge for the legacy registry; no scientific status promotion."""
    if not isinstance(registry, dict) or registry.get('schema') != 'RLL_HCRIT_H01_H72_SCOPED_V1':
        fail('REGISTRY_SCHEMA_MISMATCH')
    rows = registry.get('entries')
    if not isinstance(rows, list) or len(rows) != 72:
        fail('REGISTRY_EXPECTED_72')
    ids = ['H%02d' % i for i in range(1, 73)]
    if [r.get('id') for r in rows if isinstance(r, dict)] != ids:
        fail('REGISTRY_DUPLICATE_OR_ID_GAP')
    for row in rows:
        if row.get('claim_allowed') is not False or row.get('data') != 'TOKEN_VAZIO':
            fail('REGISTRY_FALSE_CLAIM_OR_DATA')
        if row.get('execution') != ('SCALAR_KERNEL_AVAILABLE' if row.get('kernel') else 'MODEL_REQUIRED'):
            fail('REGISTRY_FALSE_EXECUTION')
    expected = ['H18','H34','H40','H45','H46','H47','H48','H63','H70']
    if set(GATES) != set(expected):
        fail('SEMANTIC_BRIDGE_GAP')
    return {'ids': len(ids), 'semantic_overload_pairs':
            [['H18','H63'],['H34','H70']],
            's3_typed_gates': len(GATES),
            'legacy_registry_untouched': True,
            'scientific_validation': 'NOT_RUN', 'claim_allowed': False}

def select_falsifiers(controls, target_risks):
    """Deterministic greedy risk coverage; heuristic, not proof of optimality.

    Costs are USER-SUPPLIED ordinal units, never measured workload or probability.
    Selection is invariant under list order and never upgrades evidence.
    """
    if not isinstance(target_risks, list) or not target_risks or any(not isinstance(x,str) or not x for x in target_risks):
        fail('TARGET_RISKS_REQUIRED')
    if not isinstance(controls,list) or not controls:
        fail('FALSIFIER_CATALOG_REQUIRED')
    ids=set()
    for item in controls:
        ident=ref(item,'id')
        if ident in ids:fail('DUPLICATE_FALSIFIER')
        ids.add(ident)
        scalar(field(item,'relative_cost'), 'relative_cost',positive=True)
        cover=field(item,'covers')
        if not isinstance(cover,list) or len(set(cover)) != len(cover) or any(not isinstance(x,str) or not x for x in cover):
            fail('FALSIFIER_COVERAGE_INVALID')
    todo=set(target_risks)
    chosen=[]
    while todo:
        choices=[]
        for item in controls:
            marginal=set(item['covers']) & todo
            if marginal:
                choices.append((len(marginal)/float(item['relative_cost']),len(marginal),-float(item['relative_cost']),item['id'],marginal))
        if not choices:break
        # Explicit stable ID tie-break rather than first/last occurrence.
        best=sorted(choices,key=lambda v:(-v[0],-v[1],-v[2],v[3]))[0]
        chosen.append({'id':best[3],'new_risks':sorted(best[4])})
        todo-=best[4]
    return {'selected':chosen,'uncovered':sorted(todo),
            'method':'GREEDY_COVERAGE_HEURISTIC_NOT_OPTIMALITY_PROOF',
            'claim_allowed':False}

GATES = {'H40': covariance_bound_chi2, 'H18': capture_margin,
         'H63': chemical_affinity, 'H34': optical_depth, 'H70': optical_depth,
         'H45': nanoporous_modulus, 'H46': nanoporous_modulus,
         'H47': nanoporous_modulus, 'H48': magnetic_maxwell_stress}

def run(gate_id, packet):
    if gate_id not in GATES: fail('GATE_NOT_IMPLEMENTED:' + str(gate_id))
    if not isinstance(packet, dict): fail('OBJECT_REQUIRED')
    return GATES[gate_id](packet)
