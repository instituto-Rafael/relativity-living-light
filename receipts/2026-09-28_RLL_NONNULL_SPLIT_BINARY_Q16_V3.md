# Receipt — RLL Non-null Split Binary Q16 V3

Date: 2026-09-28
claim_allowed: false
provider_run: 36505526162
provider_job: 109205987964
tested_head: 887c7b91b2c0309d75852955ebb97caa233dac9e

## Separation

Generator: core/lowlevel_runtime/c/rll_nonnull_fixture_generator_q16.c
Recovery: core/lowlevel_runtime/c/rll_nonnull_recovery_q16.c

The generator contains the injection and emits only an RLF1 little-endian fixture.
The recovery does not contain a generator mode or expected-result comparison; it consumes the fixture through stdin, scans the frozen Q16 manifold, and emits recovered coordinates.

State: PASS_BINARY_SEPARATION
Independent reimplementation: TOKEN_VAZIO

## Provider execution

exact:
RLLREC1 state=PASS best=1311,65536,19661 score_q16=0 grid_evals=1782 claim_allowed=0

stress:
RLLREC1 state=PASS best=1311,65536,21299 score_q16=4129 grid_evals=1782 claim_allowed=0

null:
RLLREC1 state=PASS best=0,39322,13107 score_q16=0 grid_evals=1782 claim_allowed=0

PASS_SPLIT_STATIC_ELF
PASS_IDENTIFIER_SHADOW_WERROR
PASS_SPLIT_BINARY_RECOVERY
PASS_ARMV7_OBJECT_NO_UNDEFINED
PASS_ARMV7_NAMED_TAIL_BRANCH_AUDIT
ARMV7_PHYSICAL_EXECUTION=TOKEN_VAZIO

## Frozen source hashes

generator_source_sha256=94c0846f1b35860e7ca4b7a6b629850cbdd3ae7e9924155e2011c48f8c88e7b7
recovery_source_sha256=83d01759bef5ac1e896850f9e882eaeeb41a820ec6b2e1bb4d50ff0713f3cc56

## Provider x86_64 binary hashes

generator_exact_elf_sha256=ce6c9db996eb8b2fdcb0323a5d6e2662f1820db2052fab5c54b1cedc413e6d84
generator_stress_elf_sha256=8d4a3285d1220f234fab1c21f58dc8b7892e06ac168a6a339c64fab2f9b8d94a
generator_null_elf_sha256=e0d2ec536e38ac29cac07857e114a0d6675747bd1f606d3950cf40092971460c
recovery_elf_sha256=9bc390ea4e32a962d1462274d682186d8342169e9bb6e010ec83027d681cf5f2

## Fixture hashes

exact_fixture_sha256=46b95e042f2332c3541f49faefa326394c6cb5c582bcf4233ac07765b2cfd1ea
stress_fixture_sha256=96845a8dbb1f1b22cb5111aec23ef23aba4c61e13ee262110e4a04c1ec1df71e
null_fixture_sha256=255ff7ede6fc1b183a8cadffcf99fc730f46178d9fd125e43591d0c4c251a843

## Output hashes

exact_output_sha256=e55e24dce81f70402bf426886fe8a39373a6d0f0080e18959f8cfb3960ea52e8
stress_output_sha256=47856f903016f89161ef7a3b712a6e5ab008bb18076395d4d132775dcdde75cd
null_output_sha256=d030c7f2421eef390f63ed0d77afc58c2953c44bcad6075a4aceb8cdebd0f430

## Tail/shadow audit

Compile policy includes -fno-optimize-sibling-calls and -Wshadow -Werror=shadow.
generator_named_tail_branches=0
recovery_named_tail_branches=0

This establishes the declared compiler-output audit. It is not a formal proof of all possible control-flow or hardware shadow-stack properties.

## ARMv7 physical route

Runner materialized:
scripts/run_rll_nonnull_split_armv7_physical_v3.sh

The runner builds three generator ELFs plus one recovery ELF under Termux, verifies undefined symbols/INTERP/NEEDED, executes exact/stress/null producer-consumer routes, freezes source/ELF/fixture/output/runner SHA-256 values, and writes schema rll.nonnull_split_armv7_physical.v3.

Current physical state: TOKEN_VAZIO
Reason: no active GitHub self-hosted ARMv7 runner is connected in this execution context.

## R3

F_ok = V2 merged + split generator/recovery + static provider ELFs + exact/stress/null reproduction + frozen provider hashes + ARMv7 object audit + named tail branches zero + identifier shadow compiler gate PASS.

F_gap = execute the V3 runner on physical moto e7/ARMv7 + ingest its physical receipt + materially independent reimplementation by a separate source/toolchain.

F_next = physical ARMv7 replay of this exact source state; freeze physical ELF hashes; compare provider and physical outputs byte-for-byte; then move to held-out observational discrimination.
