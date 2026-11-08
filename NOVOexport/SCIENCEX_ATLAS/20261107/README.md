# Science X → RAFAELIA Ω | Atlas V3 | 364 news records

**Status:** DRAFT/HOLD · `claim_allowed=false` · `physical_model_executed=NOT_RUN` · **Main unchanged**.

## Reproducible evidence / origin

- User's source: Science X network saved MHTML for Phys.org page, `2026-11-08 00:37:16 UTC`, SHA-256 `34fc8357a32e773011d5a7e7e5ada4ef73c3804de989b78e4242a29a59538cb0`.
- Exactly **276 card occurrences** → **268 unique Phys.org URLs** (8 repeated card occurrences preserved by the separate private capture).
- User's pasted network sections: **87 additional unique titles** from Phys.org / Medical Xpress / Tech Xplore / Science X.
- Historical **20** articles from Atlas V2 retained, of which **9** are absent from the new two inputs; **total unique 364**, no double count.
- Public file [news_titles_routes_v3.json](news_titles_routes_v3.json) contains **titles/URL locators/date labels/candidate classification only**. It deliberately excludes publisher excerpts and private Drive locators.
- Some labels such as "3 hours ago" are kept **as printed**, anchored to the MHTML capture timestamp, never converted into unproved publication times.
- Missing URLs for pasted headlines use `null` and the **typed gap** `TOKEN_VAZIO_UNRESOLVED`, never a guessed link.
- Source classification is **triage metadata**, not a statement of factual validity. Health news is not medical guidance.

## Cross-disciplinary routes (conditional; no source-code adoption)

| Theme | Evidence & conservative falsifier | Producer bridge |
| --- | --- | --- |
| QGP heavy-quark transport | [Du Plessis & Scheihing-Hitschfeld](https://arxiv.org/abs/2604.21895), PRL DOI `10.1103/7fd5-1kq5`: leading-order weak-coupling momentum-transfer kernel with Gaussian core, non-Gaussian asymmetric exponential tails; test finite higher cumulants, generalized equilibration, heavy-flavor data; H0 Gaussian | RLL/Papers/QCD observational route only, no direct cosmological inference |
| Aharonov–Bohm trapped-ion Z₂ | [Saner et al.](https://arxiv.org/abs/2507.19588), Nature Physics `10.1038/s41567-026-03400-6`: `[H,G_m]=0` constraint and loop `φ=0` versus `φ=π` state-dependent tunneling; control noise and finite size | Matematica/Teoremas/Cosmos — simulation/test scaffold, not quantum hardware proof |
| AI backdoor defense | arXiv `2610.00685`, `2610.00663`, `2603.13461`: benchmark adaptive triggers, clean-performance losses, out-of-distribution attacks and poisoning provenance | RafGitTools/HyperMemoria/Termux, test candidates only; no deployment from press source |
| Astronomy + optical computing | Galaxy, CMB, clocks, LOFAR, PTA, space quantum/cold atoms; choose independent observable/perturbation data before physical claims | RLL/Vectra/Scientific research, route on demand |
| Medicine and biology | Specify clinical vs animal vs in-vitro vs modeling, participants, controls, outcomes, effect size and harms | Ethica[8] review only; no patient decisions from headlines |
| Ecology, history, socioeconomics and engineering | Sampling methods, exposure, uncertainty and unintended effects | Cross-cutting methods; not evidence of a cosmological model |

**Critical distinction:** CCC+TL, RLL, ΛCDM and laboratory gauge simulations are different hypotheses/regimes. Their headlines do not establish cross-model support. Prior [falsifier gates](../CCC_TL_RLL/20261107/README.md) stay unchanged, including adverse chronometer/CMB comparisons.

## Gates

- `python -m unittest tests/test_sciencex_atlas_v3.py`: integrity of 364 public metadata rows, 268/87/9 reconciliation, unique title/URL, academic loci, no excerpts, no claims.
- **What this test means:** structural catalog validation only. No astrophysical likelihood, QGP first-principles computation, ion-trap experiment, biomedical trial or cyber-defense benchmark was executed here.
- **Promotion:** no auto-merge; exact HEAD CI and independent scientific/data gates `NOT_RUN`. Do not conflate `IMPLEMENTED_UNTESTED` with `PASS`.
- **Rollback:** close DRAFT PR or revert additive index change; `main` and model code untouched. Preserve prior20 and MHTML source hashes.
- **R3:** F_ok=364 sources linked and typed; F_gap=missing source URLs/primary papers/physical+medical+security tests; F_next=rank conditional falsifiers (QGP moments, AB loop, backdoor adversarial triggers, astrophysical observational holdout).
