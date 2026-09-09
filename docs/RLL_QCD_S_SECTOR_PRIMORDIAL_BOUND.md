# RLL QCD Primordial Bound — s-sector only

**Epistemic state:** `DERIVED_BOUND / PASS_LIMITED_S_SECTOR / claim_allowed=false / publication_effect=NONE`

This note closes one narrow question without promoting a full-RLL cosmological claim:

> Given the historical scoped 95% upper limit on `Omega_s0`, how large can the canonical RLL `s`-sector contribution to the expansion rate be in the QCD temperature interval 130–400 MeV?

It does **not** set `Omega_B0` or `Omega_P0` to zero by inference. Therefore the full-RLL primordial verdict remains `TOKEN_VAZIO`.

## 1. Canonical RLL inequality

The canonical background uses

```text
g(z) = f(z) + [1-f(z)] (1+z)^3
```

with logistic `0 <= f(z) <= 1`. For `z >= 0`, let `A=(1+z)^3 >= 1`. Then

```text
g(z) = f + (1-f)A <= A = (1+z)^3.
```

For the `s` sector alone,

```text
rho_s/rho_rad
= Omega_s0 g(z) / [Omega_rad (1+z)^4]
<= Omega_s0 / [Omega_rad (1+z)].
```

The bound is independent of `z_t` and `w_t`.

## 2. Conservative thermal envelope

Entropy conservation gives

```text
1+z = (T/T0) [g_s(T)/g_s0]^(1/3).
```

V1 deliberately does not import a lattice-QCD numeric table. Instead it uses the conservative floor `g_s(T)/g_s0 >= 1`, which minimizes `z` and therefore maximizes the possible `s`-sector fraction.

Likewise, `Omega_rad >= Omega_gamma`. We use a rounded-down photon-density floor

```text
Omega_gamma h^2 >= 2.46e-5
```

and the widest canonical H0 bound `H0 <= 90 km/s/Mpc`. This again maximizes the allowed ratio.

Historical scoped input:

```text
Omega_s0(95% UL) = 0.0017772301590821408
```

It is used only as an upper-envelope input. It is not promoted to a current Bayes/model-preference receipt because later G6 convergence/RNG work remains part of the active evidence chain.

## 3. Result

The worst endpoint is the lowest temperature, `T=130 MeV`:

```text
1+z_floor                 = 5.536100388262539e11
Omega_gamma_floor         = 3.037037037037037e-5
rho_s/rho_r upper         = 1.057035637262421e-10
Delta H/H upper           = 5.285178186172438e-11
```

At `400 MeV`:

```text
Delta H/H upper           = 1.717682910536682e-11
```

Thus, under the declared `Omega_s0` upper envelope,

```text
max_{130..400 MeV} DeltaH_s/H < 5.29e-11.
```

Adding neutrinos to `Omega_rad` and using the actual QCD-era `g_s(T)>g_s0` both tighten this result further.

## 4. BBN comparison — proxy only

Using the PDG BBN review input `N_nu=2.898 +/- 0.141` (68% CL) and standard `N_nu=3.044`, a comparison built here with `central + 1.96 sigma` gives

```text
DeltaH/H_BBN_proxy = 0.010480317457112864.
```

This is **not** declared to be a universal QCD-era bound. It is only an order-of-magnitude comparison to a published primordial expansion probe.

The conservative RLL `s`-sector envelope is

```text
1.9829638827565774e8 times smaller
= 8.297314804 log10 orders smaller
```

than that proxy.

## 5. Verdicts

```text
RLL_S_SECTOR_QCD_BOUND = PASS_LIMITED_DERIVED_BOUND
RLL_FULL_QCD_GATE      = TOKEN_VAZIO
claim_allowed          = false
RLL_beats_LCDM         = NOT_INFERRED
Bayes_factor_updated   = false
```

`PASS_LIMITED` means only that the currently bounded `s` component is too small to create a measurable primordial expansion deviation in this conservative envelope. It is not evidence in favor of RLL.

The full model remains unresolved because `Omega_B0` and `Omega_P0` scale radiation-like in the canonical equation and need independent primordial bounds/receipts. The post-RNG-fix MCMC reference receipt also remains required before any current posterior/model-preference statement.

## 6. Reproduction

```bash
python3 tools/rll_qcd_s_sector_bound.py > rll_qcd_s_sector_bound.receipt.json
pytest -q tests/test_rll_qcd_s_sector_bound.py
```

The CLI emits a deterministic machine-readable receipt. The tests include monotonicity, the exact `g(z)` upper-bound proof cases, conservative entropy behavior, the canonical numerical envelope, BBN-proxy scale, and the invariant that full RLL remains `TOKEN_VAZIO`.

## 7. Reference roles

- Borsanyi et al. (2016), *Lattice QCD for Cosmology*, arXiv:1606.07494: thermal/entropy history and `g_rho`, `g_s` framework.
- Bazavov et al. / HotQCD, *Phys. Rev. D* **90**, 094503 (2014), DOI `10.1103/PhysRevD.90.094503`: QCD equation of state across the crossover; numeric table is **not** silently imported here.
- Particle Data Group (2024), Big-Bang Nucleosynthesis review: BBN `N_nu` input and the explicit boundary that no directly identified relic currently reconstructs the quark–hadron transition in detail.
- ALICE/CMS light-ion results (2026): `REFERENCE_ONLY` for QCD collectivity; they are not a cosmological RLL likelihood.

## R3

- **F_ok:** analytic s-sector upper bound is reproducible and independent of `z_t,w_t`.
- **F_gap:** `Omega_B0`, `Omega_P0`, lattice numeric tightening, post-RNG MCMC reference receipt.
- **F_next:** close radiation-like RLL terms first; only then evaluate a full-RLL QCD-era expansion gate.
