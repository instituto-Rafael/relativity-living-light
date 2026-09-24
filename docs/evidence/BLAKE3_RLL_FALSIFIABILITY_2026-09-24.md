# BLAKE3 ↔ RLL — falsifiability gate — 2026-09-24

## Scope

This gate tests whether several numeric/branching patterns found around BLAKE3 can
be promoted into an RLL relation without conflating distinct structures.

Invariant:

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
```

The separate hypothesis that OpenAI-export/log dates were altered is **not used
as a premise** here. Its state in this gate is
`TOKEN_VAZIO_OUT_OF_SCOPE_NO_EVIDENCE_IN_THIS_GATE`.

## Sources fixed for this audit

### BLAKE3 fork

Repository: `rafaelmeloreisnovo/BLAKE3`

- `c/blake3_impl.h` blob `facd5997435736a9f15491f490805ceff6c0453f`
- `c/blake3_portable.c` blob `062dd1b47fb6424f4d3db4c6edd2f90efcb92973`
- `c/blake3.c` blob `00f91f444922df7c8e7b5ff69343852cbbf4c613`
- `src/lib.rs` blob `6f652071de0ad06626c427e40354e7ee4872be76`

Canonical external cross-check:
`BLAKE3-team/BLAKE3-specs/blake3.tex`.

### RLL

Repository: `instituto-Rafael/relativity-living-light`

- `tools/iml/iml_pipeline.py` blob
  `9b71f4deacb431c25a8ca0b88a7ef5c0da208f93`
- `MathRaf.md` blob `6faeae4f24eb80b98b974cdf9c7e908440e35192`
- `docs/MASTER_UNIFIED_DOCUMENTATION_2026.md` blob
  `269b44417d9bb289388b0e766f9447835b99a59b`

## Structural findings

| Candidate number | Canonical binding found | State |
|---:|---|---|
| 3 | three user-facing BLAKE3 modes: hash, keyed hash, derive key | `PASS_CANONICAL` |
| 4 | four G operations per parallel column phase and four per diagonal phase | `PASS_CANONICAL` |
| 5 | no semantically selected canonical binding in this gate | `TOKEN_VAZIO` |
| 6 | no semantically selected canonical binding in this gate | `TOKEN_VAZIO` |
| 7 | seven compression rounds; seven internal flag bits | `PASS_CANONICAL` |
| 8 | eight G calls per round; eight chaining-value words | `PASS_CANONICAL` |

These counts are **not the same object**. Equality or proximity of integers is
not evidence of a shared mechanism.

### Actual tree branching

BLAKE3's hash tree is binary. A parent combines exactly two child chaining
values. Therefore:

```text
literal child arity = 2
```

The hypothesis "BLAKE3 literally branches 3..8 ways per parent" is falsified by
the canonical tree construction.

However, tree **depth** can equal 3..8. For complete power-of-two chunk counts:

| chunks | input bytes | complete-tree depth |
|---:|---:|---:|
| 8 | 8,192 | 3 |
| 16 | 16,384 | 4 |
| 32 | 32,768 | 5 |
| 64 | 65,536 | 6 |
| 128 | 131,072 | 7 |
| 256 | 262,144 | 8 |

This is an input-dependent depth relation, not a 3..8 child branching factor.

## 42 falsifier

The BLAKE3 core inspected here gives:

- rotations: `16, 12, 8, 7`; arithmetic sum = `43`;
- `7` rounds × `8` G calls/round = `56`;
- binary parent arity = `2`;
- no `BitOmega` definition was found in the examined BLAKE3 core sources.

Therefore this gate does **not** promote an intrinsic BLAKE3 `42` invariant.
A canonical formula/derivation binding 42 to BLAKE3 remains
`TOKEN_VAZIO_NO_CANONICAL_BINDING`.

## RLL period-42 falsification

The current RLL IML code computes, for 84 iterations,

```text
x[n+1] = (sqrt(3)/2) * x[n] - pi*sin(279 degrees)
x0 = 0.314159
comparison = round(x mod 1, 12)
```

The exact gate result is:

```text
seq[0:42] == seq[42:84]  -> False
step 42 mod 1            -> 0.106130777368
step 43 mod 1            -> 0.113410671216
```

So the **real/float recurrence used by the current IML pipeline does not have
period 42 under this test**. This agrees with `MathRaf.md`, which derives that
the real affine recurrence with multiplier `sqrt(3)/2` converges to a fixed
point rather than satisfying a nontrivial exact period.

A separate finite-state/Q16.16 implementation may have cycles, but its exact
period must be measured from its actual transition function and arithmetic.
That result cannot be imported from the float recurrence.

## Provenance conflict: BitOmega ↔ BLAKE3/RMR ↔ 42

`docs/MASTER_UNIFIED_DOCUMENTATION_2026.md` states:

```text
period(BitOmega) = 42 | BLAKE3/RMR | Confirmed; do NOT break
```

But in the evidence examined for this gate:

1. the BLAKE3 core sources above do not define `BitOmega`;
2. focused indexed search of `rafaelmeloreisnovo/BLAKE3` produced no
   `BitOmega` core match;
3. focused indexed search in `rafaelmeloreisnovo/ChipQuantum` found BitOmega
   as a separate state/scheduler/toroidal concept, including a 10-state design
   and 42-attractor hypotheses, but did not surface the claimed raw
   `bitomega.log` generator/evidence.

State:

```text
TOKEN_VAZIO_PROVENANCE_CONFLICT
claim_allowed=false
```

Promotion requires the raw generating program or log, exact commit, input
seed/state, arithmetic domain, transition function, and period detector.

## Executable gate

```bash
python tests/test_blake3_rll_falsifiability.py
python tools/blake3_rll_falsifiability.py
```

The CI job additionally asserts that the global claim gate remains closed.

## R3

`F_ok`: BLAKE3 tree arity, modes, rounds, flags, G structure and RLL float
42-cycle test are separated and executable.

`F_gap`: canonical bindings for counts 5 and 6; intrinsic BLAKE3-42 relation;
raw BitOmega period-42 generator/log; any date-integrity claim about external
chat exports.

`F_next`: recover the exact BitOmega generator/log and run the same period
detector over the owning implementation; separately test the Q16.16 transition
function if it exists.

`claim_allowed=false`.
