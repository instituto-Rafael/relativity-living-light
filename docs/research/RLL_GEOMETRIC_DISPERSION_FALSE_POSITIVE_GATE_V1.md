# RLL — Geometric Dispersion / False-Positive Gate V1

Status: `PREREGISTERED_DIAGNOSTIC / claim_allowed=false`  
Date: 2026-10-04  
Base authority: `rll/lab@d8ba8fb3d8fa10bab3fcc190fcc749dec91ba3b6`

## 0. Boundary

This note composes already-authored mathematics with statistical diagnostics without promoting geometry, numerology, Venturi metaphors, modular encodings or symbolic constants into a cosmological mechanism.

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
DIAGNOSTIC_FIT != PHYSICAL_MODEL
CORRELATION != MECHANISM
```

Canonical source routes:

- `rafaelmeloreisnovo/Matem-tica-/docs/formal/PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSWALK_V1.md`
- `rafaelmeloreisnovo/Matem-tica-/docs/formal/GLOBAL_CONTEXT_SEMANTIC_DYNAMICS_CLOSURE_V4.md`
- `rafaelmeloreisnovo/papers/papers/RAFAELIA_GEODESIC_TOROIDAL_14D_VISUAL_SYNTHESIS_2026-09-12.md`
- `rafaelmeloreisnovo/papers/research_notes/2026-09-19_EIGHT_CONNECTED_GEOMETRY_PREDECESSOR_CROSSWALK_V1.md`
- RLL observational authority remains the existing likelihood/covariance stack.

## 1. One-interaction statistical layer

For one complete population of N parcels:

```text
sigma^2 = sum_i (x_i-mu)^2 / N
```

For an observed sample of n parcels:

```text
s^2 = sum_i (x_i-xbar)^2 / (n-1)
Var(xbar) ~= s^2/n
SE(xbar) = s/sqrt(n)
```

For two independent sample means:

```text
Var(xbar_A-xbar_B) ~= s_A^2/n_A + s_B^2/n_B
```

If observations are correlated, the independent formula is not authoritative. For a contrast vector `a` and covariance `C`:

```text
Var(a^T y) = a^T C a
```

The existing RLL covariance path therefore has precedence over a scalar `n-1` shortcut whenever full covariance is available.

## 2. Regression layer

The simple diagnostic line is:

```text
y_hat = beta0 + beta1*x
```

For actual correlated RLL residuals, the intended confirmatory form is generalized least squares:

```text
r = y - mu_baseline(theta)
beta_hat = (X^T C^-1 X)^-1 X^T C^-1 r
```

A geometric feature block may enter `X`; it must not silently replace the physical RLL equations.

## 3. Safety-stock analogy -> uncertainty reserve

`stock of safety` is retained only as an uncertainty-buffer analogy.

For a mean under an independent normal approximation:

```text
B_mean(k) = k*s/sqrt(n)
```

For one future independent observation:

```text
B_pred(k) = k*s*sqrt(1+1/n)
```

For correlated cosmological data the reserve must be derived from the predictive covariance, not from the inventory formula. The value of `k` is a preregistered coverage choice, not a fitted constant chosen after seeing the result.

## 4. Formal geometry block

### 4.1 Pythagoras / difference

With `delta=|a-b|`:

```text
c^2 = a^2+b^2 = 2ab + delta^2
```

For the law of cosines:

```text
c^2 = a^2+b^2-2ab*cos(theta)
D_theta = -2ab*cos(theta)
```

The negative cross term is algebraic structure, not negative geometric area.

### 4.2 Bhaskara / negative completed-square term

```text
A*x^2+B*x+C = 0
Delta_B = B^2-4AC
x_pm = (-B +- sqrt(Delta_B))/(2A)
A*x^2+B*x+C = A*(x+B/(2A))^2 - Delta_B/(4A)
```

The project label `D_Q=-Delta_B/(4A)` is allowed as terminology; the algebra is classical.

### 4.3 PBIP cut gate

```text
q^2 = r^2-d_perp^2
Delta_B = 4*(r^2-d_perp^2) = 4*q^2
```

Hence `Delta_B>0` means two real intersections, `=0` tangency and `<0` no real intersection.

### 4.4 Isosceles/equilateral 30-degree gate

For equal sides `L` and half-apex angle `alpha`:

```text
b = 2L*sin(alpha)
h = L*cos(alpha)
```

At `alpha=30 deg`:

```text
b/L = 1
h/L = sqrt(3)/2
```

Two quantities must stay distinct:

```text
h_radial/r   = sqrt(3)/2 ~= 0.8660254037844386
h_inscribed/r = 3/2 = 1.5
```

If a family of right-triangle legs is being compared, use `delta_i=|a_i-b_i|`; then `delta_min`, `delta_max`, mean and sample variance are ensemble statistics. A single right triangle has only one `|a-b|` leg difference.

## 5. Toroidal / geodesic / Venturi namespaces

Toroidal meridian:

```text
(rho-R)^2+z^2=r^2
```

A line `z=m*rho+b` generates a quadratic and Bhaskara classifies the intersection.

Venturi namespaces remain separate:

```text
VENTURI.PHYSICAL != VENTURI.METAPHOR != VENTURI.COMPUTATIONAL
```

Physical ideal-flow equations:

```text
A1*v1=A2*v2
P + (1/2)*rho*v^2 + rho*g*h = constant
```

They are not cosmological equations. Physical Venturi stays `TOKEN_VAZIO_PHYSICAL` without fluid geometry, boundary conditions, fluid properties and measurements.

## 6. Spiral correction and adversarial control

The canonical historical spiral found in the authored source is:

```text
z_n = r0*(sqrt(3)/2)^n * exp(i*n*pi*phi)
```

Therefore:

```text
q = sqrt(3)/2 ~= 0.8660254037844386  # contraction
phase_n = n*pi*phi
```

Do not collapse these three different numbers:

```text
sqrt(3)/2  ~= 0.8660254037844386
sqrt(3/2)  ~= 1.224744871391589
3/2        = 1.5
```

`(3/2)^n` is implemented only as an adversarial non-canonical expansion control. If a claimed signal appears only after this substitution, it fails the source-faithfulness gate.

`pi*phi ~= 5.0832036923152595` is the one-step phase multiplier in the cited spiral; it is not automatically a radial scale or physical constant.

## 7. log(log(999))

No canonical `log(log(999))` operator with a frozen base was found in the selected formal sources. Existing source material explicitly leaves the log domain/base unresolved for the historical `rho=phi*log(x) mod 2pi` family.

Therefore:

```text
LOG_BASE = TOKEN_VAZIO
physical_role = TOKEN_VAZIO
```

Numerical branches are diagnostic only:

```text
ln(ln(999))             ~= 1.932499886168131
log10(log10(999))       ~= 0.4770583481420184
```

The difference is itself evidence that the base cannot be omitted.

## 8. Modular carrier requested in this interaction

Use the declared exact-ratio phase operator:

```text
theta_m(n) = 2*pi*(n mod m)/m
```

for

```text
M = {3,7,14,10,30,5,50,70}
```

The combined residue signature repeats after

```text
lcm(3,7,14,10,30,5,50,70) = 1050
```

This creates a bounded arithmetic carrier `Z_1050`; it does not create a 1050-unit physical period.

A confirmatory analysis must account for the fact that many moduli are algebraically dependent. Treating every residue as an independent hypothesis would inflate false positives.

## 9. 77/33 and 777/333 — representation-invariance gate

Exactly:

```text
gcd(77,33) = 11
gcd(777,333) = 111
77/33 = 7/3
777/333 = 7/3
```

There is no missing numerical `11` in the ratio. The `11` is the common reduction factor of the first representation; the second representation removes `111`.

This becomes a useful falsifier:

```text
F(77,33) = F(777,333) = F(7,3)
```

must hold for any operator claiming to depend only on the ratio. If the result changes, the signal is representation/digit dependent and is classified as a possible base artifact rather than a robust invariant.

## 10. Square, zero and non-existence

For a declared square with side `L`:

```text
A = L^2
```

But the state contract is:

```text
L=0, object declared -> A=0
object absent / unknown -> A=TOKEN_VAZIO
```

`TOKEN_VAZIO` must never be zero-filled to make a regression matrix numerically convenient. Missingness needs an explicit mask, exclusion rule or probabilistic missing-data model.

## 11. Fourteen-axis carrier

The authored 14D synthesis is an operational descriptor, not a physical 14-dimensional spacetime:

```text
G14=(metric, angular, triangular, polynomial, sign/orientation,
     curvilinear, rotational, fluid, spiral/recurrence, focal,
     geodesic, toroidal, matrix, transformational)
```

Each axis enters a design matrix only after a numeric observable, unit/domain and source are declared. An axis name alone is not a parameter value.

## 12. RLL parameter boundary

Current RLL cosmology parameters remain in their own namespace, e.g.:

```text
(H0, Om, OL, Os0, zt, wt, Ob_h2, sigma8)
```

The geometry block may be tested first as residual covariates:

```text
y = mu_RLL(theta) + X_geo*beta + epsilon
```

It may not be substituted directly into `H0`, density parameters or other dimensional quantities because of a matching number or symbol.

## 13. False-positive academic gate

A geometric/modular block is only allowed to advance from `SCREENING` to `CONFIRMATORY_CANDIDATE` if all applicable gates pass:

1. source formula and namespace frozen before the result;
2. units/domain declared;
3. covariance used when observations are correlated;
4. one omnibus block test or multiplicity correction is preregistered;
5. holdout/leave-one-source-out behavior is recorded;
6. phase permutation negative control fails to reproduce the signal;
7. non-canonical `(3/2)^n` adversarial spiral does not outperform by arbitrary choice;
8. `77/33`, `777/333`, `7/3` give the same output for ratio-only operators;
9. `TOKEN_VAZIO` is not encoded as numeric zero;
10. effect size and uncertainty are reported, not only a threshold/p-value;
11. baseline models remain present;
12. the result survives the existing RLL scientific evidence gates.

Failure of any required confirmatory gate keeps:

```text
claim_allowed=false
```

## 14. Executable verifier

```bash
python tools/rll_geometric_dispersion_false_positive_gate.py
python -m unittest tests.test_rll_geometric_dispersion_false_positive_gate -v
```

The executable layer validates only the bounded mathematical/statistical identities in this note. It does not execute cosmological fitting.

## 15. Current state

```text
FORMAL:
  sample/population variance distinction
  variance-of-mean formulas under stated independence
  Pythagoras/difference identity
  Bhaskara/PBIP classification
  isosceles 30-degree gate
  canonical spiral transcription
  exact fraction reduction
  modular LCM=1050
  void != zero state boundary

DIAGNOSTIC_ONLY:
  OLS line
  safety-stock uncertainty analogy
  modular/geometric feature block
  log(log(999)) numeric branches

TOKEN_VAZIO:
  physical celestial-body mapping
  canonical log base/operator
  causal cosmological role for pi*phi
  physical Venturi mapping
  mapping G14 -> RLL physical parameters
```

## R3

```text
F_ok   = requested formulas are composed in one falsifiable diagnostic contract; source-faithfulness and representation invariance are explicit
F_gap  = real observation vector/covariance binding, physical units and G14->RLL mapping remain TOKEN_VAZIO
F_next = run focused unit tests/CI; only after PASS bind the feature block to a preregistered held-out RLL dataset without changing canonical physics
```
