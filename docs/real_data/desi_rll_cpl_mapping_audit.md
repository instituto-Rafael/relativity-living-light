# DESI DR2 / RLL CPL-mapping audit

Status: `QUANTITATIVE_LOCAL_MISMATCH / GLOBAL_TEST_REQUIRED / claim_allowed=false`

## 1. Audit finding

DESI DR2 motivates testing dynamical-dark-energy likelihoods and the collaboration's key `w0-wa` result favors a region with

```text
w0 > -1
wa < 0
```

for the CPL convention

```text
w(a) = w0 + wa (1-a).
```

The current RLL logistic-density background uses

```text
f(z) = 1/(1+exp((z-z_t)/w_t)),  w_t > 0
R(a) = f + (1-f)a^-3
rho_s = Omega_s0 rho_c0 R(a)
```

The historical/documented pressure ratio is

```text
p_doc/(Omega_s0 rho_c0) = -f
w_doc = -f/R.
```

A separate 2026-08-08 continuity audit shows that `(rho_s,p_doc)` is not separately conserved during a genuine transition. If `rho_s(a)` is preserved and separate conservation is imposed, the pressure becomes

```text
p_cons/(Omega_s0 rho_c0)
  = -f + [f'/3](a^-3-1),

f' = df/dln(a).
```

## 2. Exact local CPL map at a=1

For CPL,

```text
wa = - dw/dln(a) |_(a=1).
```

At `a=1`, `R=1`. Let

```text
f0  = f(z=0)
f0' = df/dln(a)|_(a=1) = f0(1-f0)/w_t.
```

### 2.1 Documented pressure ratio

Differentiating `w_doc=-f/R` gives

```text
w0_doc = -f0
wa_doc = f0' + 3 f0(1-f0).
```

Because `w_t>0` and `0<f0<1`, every term in `wa_doc` is positive:

```text
wa_doc > 0.
```

### 2.2 Separately conserved reconstruction

For the continuity-reconstructed pressure,

```text
w0_cons = -f0
wa_cons = 2 f0' + 3 f0(1-f0).
```

Therefore, again for `w_t>0` and a nontrivial transition,

```text
wa_cons > wa_doc > 0.
```

The continuity correction does **not** rotate this RLL family into the DESI-favored `wa<0` quadrant. It increases the positive local CPL slope.

## 3. Central-parameter receipt

Using the repository central values

```text
z_t = 1.164
w_t = 0.405
```

the executable formulas give

```text
f0       = 0.9465498439751858
f0'      = 0.12492157245861035
w0_doc   = -0.9465498439751858
wa_doc   = +0.2767012829958220
w0_cons  = -0.9465498439751858
wa_cons  = +0.4016228554544323
```

These values are now pinned by regression tests in `tests/test_rll_background_continuity.py` and emitted by `scripts/check_rll_background.py` under `local_cpl_today`.

## 4. Important formula-family divergence

The diagnostic Pantheon path `scripts/pantheon/models_pantheon.py` contains another object also named RLL:

```text
w(z) = w0 + wa g(z)
```

with a logistic transition `g(z)`, followed by integration of the dark-energy continuity relation to obtain `rho_de(z)`.

That is not algebraically identical to the canonical logistic-density family above:

```text
RLL_density_family:
  rho_s prescribed directly as f+(1-f)a^-3

RLL_EoS_family:
  w(z) prescribed directly and rho_de obtained by integration
```

The two families may be compared as alternatives, but likelihood evidence from one must not be silently assigned to the other.

Required bridge:

```text
explicit_parameter_map + same H(z) test + same likelihood + provenance receipt
```

Until that exists:

```text
RLL_density_family_equals_RLL_EoS_family = TOKEN_VAZIO
cross_family_evidence_transfer = BLOCKED
```

## 5. Literature boundary

The DESI DR2 key paper reports that allowing `w0-wa` evolution improves the combined fit and identifies a favored `w0>-1, wa<0` region. Extended DESI analyses also find a preference for histories featuring phantom-divide crossing, while quintessence-only histories remain disfavored but not excluded.

Recent interacting-dark-sector studies are especially relevant because a background expansion can be degenerate with an evolving-EoS model while producing different matter growth. This is exactly why RLL cannot be judged by `H(z)`/distance fitting alone after the continuity ambiguity is exposed.

Operationally:

```text
background_match != physical_model_match
same_Hz != same_growth
same_distance_likelihood != same_perturbations
```

## 6. Claim boundary

- DESI DR2 does not confirm RLL.
- The canonical RLL logistic-density family has a local CPL slope with the opposite `wa` sign to the key DESI-favored quadrant for `w_t>0`.
- Imposing separate conservation preserves that sign mismatch and makes `wa` more positive for the central parameters.
- A single minimally coupled canonical scalar cannot realize genuine smooth phantom crossing.
- The Pantheon logistic-EoS diagnostic is a distinct mathematical family unless an explicit equivalence map is demonstrated.
- Interacting-sector closure remains `TOKEN_VAZIO` until `Q` and the receiving sector are implemented at background and perturbation levels.

Preferred boundary statement:

> Current real-data evidence supports further model discrimination, not scientific validation. The canonical logistic-density RLL family is locally on the opposite `wa` side of the DESI DR2 key favored CPL quadrant for positive transition width; its conserved reconstruction does not remove that mismatch. An interacting closure remains a viable hypothesis class to test, not an established explanation.
