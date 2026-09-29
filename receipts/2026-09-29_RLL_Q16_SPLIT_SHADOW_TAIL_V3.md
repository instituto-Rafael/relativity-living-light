# Receipt — RLL Q16 Split / Shadow / Tail Policy V3

Date: 2026-09-29
PR: #1012
Provider run: 36506082422
Provider job: 109207732794
claim_allowed: false

## Canonical kernel audit
SHADOW_GATE=PASS
SIBLING_CALL_OPTIMIZATION=DISABLED
SOURCE_SHA256=286a5c87aadfea377773d5622cbf7f59526c18f1009e347c6e03352d6f0f242f
ELF_SHA256=acb156be6408885316a3ae7aedf9b1fddd9224ac92c4bb42cf68197b41b56a61
RLLNONNULLQ16V2 state=PASS exact=1311,65536,19661 stress=1311,65536,21299 stress_delta=0,0,1638 stress_gate=DIAGNOSTIC null_os=0 grid_evals=1782 claim_allowed=0

## Split executable boundary
generator -> 132-byte matrix -> recovery
GENERATOR_SHA256=705fb1485622aa085d3959a4c363a82253522277677e90bd9bfdde38c123728d
MATRIX_SHA256=406d13ea9a5ad10af3629a01d2df9af4ca8bd667ac0f2192c00324262658ab94
RECOVERY_SHA256=b2f9565379e9b3efd5b98da407674582f124eb87b2e891c0737d99395c706919
RLLRECQ16 state=PASS best=1311,65536,19661 grid_evals=1782 claim_allowed=0
SPLIT_EXECUTABLES=PASS
INDEPENDENT_REIMPLEMENTATION=TOKEN_VAZIO

## ARMv7 audit
ARMV7_SHADOW_GATE=PASS
ARMV7_SIBLING_CALL_OPTIMIZATION=DISABLED
ARMV7_OBJECT_SHA256=d679d8e1c4363eceaa89f73e2c52fca0abd24cf94a697c889a861f7f7ed35dcb
ARMV7_PHYSICAL_EXECUTION=TOKEN_VAZIO

## Interpretation
-Wshadow -Werror proves the compiled source passes the selected compiler shadow diagnostic; it is not a universal proof that every possible semantic shadow concept is absent.
-fno-optimize-sibling-calls disables the compiler sibling/tail-call optimization used for this build; this receipt does not claim a universal ZERO_TAIL theorem.
Separate generator/recovery ELFs prove executable/state separation, not an independent algorithmic reimplementation.
Physical ARMv7 execution remains TOKEN_VAZIO until a device-generated receipt exists.

## R3
F_ok = V2 merged + shadow-hard build + sibling-call optimization disabled + frozen source/ELF hashes + split generator/recovery PASS + 132-byte matrix boundary + ARMv7 object audit PASS.
F_gap = physical ARMv7 execution + independent reimplementation + held-out observational discrimination.
F_next = execute scripts/run_rll_nonnull_q16_physical_armv7_v3.sh on the canonical ARMv7 device and commit only the resulting receipt; then implement the recovery algorithm independently from a clean specification.
