# RLL — Genoma de Formas, Duplo Watchdog e Mandala Auditável V1

Date: 2026-09-19
State: METHOD_CONTRACT / BOUNDED_FORM_GENOME
claim_allowed: false

## Purpose

Extend the recurrent session sweep with two mechanisms:

1. cross-supervised watchdog topology for uncertainty/risk/process monitoring;
2. form genome that decomposes geometry into small auditable fragments and recombines them under bounded random permutations.

The biological analogy is preserved as analogy, not biological equivalence.

## Biological analogy boundary

Canonical gene expression is not:

mRNA -> builds the complementary DNA strand

The safe method analogy is:

DNA-like store        ~ immutable form library
messenger-like plan   ~ selected ordered expression plan
translation-like step ~ render/compose a form phenotype

Actual DNA replication copies DNA templates. Ordinary mRNA is transcribed from DNA and translated into protein. RNA-to-DNA copying is a special reverse-transcription route, not the ordinary mRNA mechanism.

FORM_GENOME_ANALOGY = SOFTWARE/METHOD_METAPHOR
BIOLOGICAL_EQUIVALENCE = false

## Export-derived symbolic basis

From the longitudinal export:

YIN = 0
YANG = 1
three binary lines -> 2^3 = 8 states
two 3-line blocks -> 2^6 = 64 states

The export also preserves:
- Tao/Yin-Yang as correlated poles with seeds of the opposite pole, center, rotation and scale;
- authorial vector [4,8,3,5,2,4,8,6] as OPERATOR_AUTHORIAL_UNVALIDATED;
- a visual mandala with eight sectors and 42 Chaves;
- a separate operational RLL family 42=6x7.

These are not silently merged.

BAGUA_8 != MANDALA_VISUAL_8 != HYPERFORMAS_42

Mapping between the 8-sector mandala and the 6x7 operational state space:
TOKEN_VAZIO_MAPPING

## Geometric state families

Polarity:
B2 = {0,1}

Trigram computational state:
B8 = {0,1}^3
|B8| = 8

Six-line computational state:
H64 = {0,1}^6 = B8 x B8
|H64| = 64

Raw bits are canonical computational identity. Historical/cultural names are optional metadata.

Hamming mutation distance:
d_H(a,b) = number of bit positions where a_i != b_i

Regular-octagon symmetry:
D8 = 8 rotations + 8 reflections
|D8| = 16

This is a mathematical transformation family only.

Hyperformas-42 preserves the existing RLL decomposition:
42 = 6 * 7
V approximately Z6 x Z7

For state s in [0,41]:
sector = s // 7
level  = s % 7
s      = 7*sector + level

Source graph and measured weights remain independently gated by RLL Canon 28.

## Form gene

FormGene =
<
family,
bits_or_index,
orientation,
scale,
operator,
layer,
epistemic_state,
source_ref,
provenance_hash
>

The typed tuple plus provenance is the state; no single field is the whole form.

## Messenger-like expression plan

M = [G_0,G_1,...,G_k]

LIBRARY = append-only
EXPRESSION_PLAN = ephemeral/testable
PHENOTYPE = derived artifact

A failed composition never deletes genes/fragments; it emits a receipt.

## Bounded composition space

Candidate:
C =
<
six_line_6bit,
octagon_action,
hyperforma_42,
projection_sector_8,
operator_bundle
>

A finite naive cross product already contains:
64 * 16 * 42 = 43008

before scale, layer, evidence and other operators.

Default:
RULER -> SAMPLE -> SCORE -> TEST -> PRUNE -> RECEIPT -> RESAMPLE

No total enumeration is required.

## Mandala projection

For visual sector q in [0,7]:
theta_q = 45 deg * q

The mandala is a view/addressing projection, not a proof layer.

It does not prove equivalence among:
octagon sectors,
trigram identities,
hyperformas 42,
biological states.

## Dual cross-watchdog topology

Objects:
P  = monitored process
WA = watchdog A
WB = watchdog B
WM = meta-watchdog / disagreement supervisor

WA and WB observe:
- process epoch progression;
- process receipt/hash;
- own monotonic sequence;
- peer monotonic sequence;
- timeout/miss counters.

Anti-mutual-petting invariant:
PEER_HEARTBEAT_WITHOUT_PROCESS_PROGRESS != HEALTH

A watchdog cannot declare health solely because the peer is alive.

This blocks:
P dead
WA <-> WB continue petting
=> false HEALTHY

Meta-watchdog decision classes:
WA OK + WB OK + process agrees -> HEALTHY
one watchdog fails but process independently advances -> DEGRADED_FAILOVER
WA/WB disagree on epoch/hash -> QUARANTINE
process stale to both -> FAILSAFE_BLOCK
both watchdogs stale -> FAILSAFE_BLOCK
stable recovered receipts -> FAILBACK_CANDIDATE

Each epoch emits a chained receipt:
Receipt_t =
<
process_epoch,
process_hash,
WA_seq,
WB_seq,
WA_view,
WB_view,
decision,
residual_risk
>

## Watchdog-of-watchdog residual risk

Two logical watchdogs may share a common-mode failure:
same clock,
same memory,
same power/runtime,
same parser,
same corrupted source.

DUAL_WATCHDOG != INDEPENDENT_REDUNDANCY_AUTOMATICALLY

Independence fields:
independent_clock
independent_state_source
independent_failure_domain
independent_implementation

Residual risk remains explicit.

## Form risks

Each generated combination is classified for:
provenance completeness,
layer collision,
symbol collision,
unsupported cross-family mapping,
duplicate orbit/state,
untyped operator,
epistemic promotion risk,
watchdog state,
deterministic replay.

Possible states:
PASS_STRUCTURE
CANDIDATE
DEGRADED
QUARANTINED
BLOCKED
TOKEN_VAZIO_MAPPING
TOKEN_VAZIO_SOURCE
TOKEN_VAZIO_OPERATOR
NOT_RUN

## Tao/Yin-Yang relation

The export stores the authorial state:
D_theta =
<Yin_theta,Yang_theta,seed_Yang_in_Yin,seed_Yin_in_Yang,center,rotation,scale>

and possible invariant:
A_plus(theta) * A_minus(theta) = kappa

This remains an authorial mathematical representation unless a measured system supplies units and a falsifier.

For the engine, Yin/Yang supplies binary polarity and complement unless another layer is explicitly enabled.

## From octagon to mandala without explosion

Use group actions rather than arbitrary reorderings.

Instead of treating all 8! = 40320 vertex reorderings as equally meaningful:
start with D8 symmetry orbit (16 actions)
then test only declared non-symmetry permutations.

This separates redrawing from structural change.

## Watchdog-driven recurrent sweep

FORWARD
-> WATCHDOG_CROSSCHECK
-> GAP_DISCOVERY
-> REVERSE
-> WATCHDOG_CROSSCHECK
-> RELATION_OF_RELATIONS
-> FORM_RECOMBINATION
-> WATCHDOG_CROSSCHECK
-> COMPRESS
-> NEW_REPRESENTATION
-> RESWEEP

Every stage may halt independently.

## R3

F_ok: export-derived binary/trigram/six-line structure, octagon symmetry, 42=6x7 family, form-genome contract and cross-watchdog topology are separated and composable.
F_gap: mapping between eight mandala sectors and 42 operational hyperformas remains TOKEN_VAZIO; full transcript/export binding remains incomplete; watchdog failure-domain independence has not been measured.
F_next: run deterministic bounded samples, emit chained receipts, compare symmetry-orbit duplicates and inject watchdog failures to verify failover/quarantine/failsafe behavior.
