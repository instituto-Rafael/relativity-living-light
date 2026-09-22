# RLL Source State Lookback

Status: draft_track_v0.1
Data: 2026-06-16
Tema: sinal observado agora, fonte no passado e estado atual incerto.

## Nucleo

O sinal observado e registro de um evento passado, nao garantia do estado presente da fonte.

No RLL:

Observed_Signal(t0) = Source_State(te) + Propagation(te_to_t0) + Instrument_Model(t0)

Onde:
- te = tempo de emissao
- t0 = tempo de observacao
- Source_State(te) = estado da fonte quando emitiu
- Source_State(t0) = estado atual estimado ou desconhecido
- Propagation = expansao, redshift, absorcao, lenteamento e selecao

## Estados possiveis

SOURCE_STABLE
SOURCE_DIMMED
SOURCE_BRIGHTENED
SOURCE_OBSCURED
SOURCE_QUENCHED
SOURCE_MERGED
SOURCE_COMPACT_REMNANT
SOURCE_ACCRETING
SOURCE_OFF_CENTER_OR_WANDERING
SOURCE_UNKNOWN

## Claim boundary

Nao afirmar que a fonte ainda existe igual apenas porque seu sinal chegou.
Nao afirmar estado atual sem modelo ou novas observacoes.
Preservar TOKEN_VAZIO quando o estado atual nao puder ser inferido.

## Ponte RLL

compressao energia -> emissao transiente -> propagacao cosmologica -> observacao -> inferencia -> lacuna auditavel


## Retarded spacetime / dynamic foreground bridge — V1

The source-state track now has an executable contract:

- `data/contracts/rll_retarded_spacetime_state.v1.yml`
- `docs/science/RLL_RETARDED_SPACETIME_STATE_V1.md`
- `tools/validate_rll_retarded_spacetime_state.py`

The observation is represented as an emission event on the past light cone plus
an evolving propagation path. The later matter state remains a separate
timelike inference.

Key boundaries:

```text
OBSERVATION_EVENT != PRESENT_SOURCE_STATE
NULL_SIGNAL_PATH != TIMELIKE_MATTER_WORLDLINE
GLOBAL_COSMOLOGICAL_PARAMETER != POST_HOC_PER_POINT_PARAMETER
```

The contract also separates cosmological epoch/lookback, source proper time,
peculiar velocity, dynamic gravitational foreground, lensing/time delay, plasma
dispersion/rotation/scattering and instrument/selection uncertainty.

"Age of a position" is not used as a physical primitive. The stored quantities
are cosmological age of the event, lookback time, source-age/proper-time
estimates, and independently defined formation-age proxies.

Strong-gravity plasma remains under the separate GRMHD/GRPIC authority.
No new plasma-gravity force is claimed and physical syntropy remains
`TOKEN_VAZIO_PHYSICAL_DEFINITION`.

State: `FORMAL_MODEL_SHADOW`; `claim_allowed=false`.


### Ordered region-context extension

The canonical parent remains `data/contracts/rll_retarded_spacetime_state.v1.yml`.
The new `data/contracts/rll_retarded_spacetime_region_context.v1.yaml` is a typed extension for the ordered intervening-region stack.

It adds explicit fields for:
- cosmic time/lookback/scale factor at photon crossing;
- photon crossing time and moving-region state;
- peculiar/bulk velocity fields;
- GR redshift/lensing/Shapiro/time-delay terms;
- plasma/MHD propagation terms with a strict no-new-force boundary;
- matter environment / neighboring mass distribution;
- covariance/provenance at segment level;
- causal rule that post-crossing changes cannot alter a photon that has already left the region.

Shared source-state, proper-time, geometry, uncertainty and claim semantics remain governed by the parent contract. `claim_allowed=false`.
