#!/bin/sh
# RAFAELIA Ω: HOSTED runner adapter validating an AUTHORIAL FREESTANDING C core.
# This shell script is not freestanding; its subject is core/lowlevel_runtime/c.
set -eu
LC_ALL=C
export LC_ALL

ROOT=${GITHUB_WORKSPACE:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}
cd "$ROOT"
OUT=${RLL_OMEGA_RECEIPT_DIR:-artifacts/ci/rll-omega-freestanding}
mkdir -p "$OUT"
RECEIPT="$OUT/receipt.txt"
CORE=core/lowlevel_runtime/c/rll_canonical_coupling.c
HEADER=core/lowlevel_runtime/include/rll_canonical_coupling.h
HARNESS=tests/c/rll_canonical_coupling_vectors.c
SIGNED_VECTORS=tests/c/rll_omega_canonical_signed_division_vectors.c
TRANSITIVE_HEADER=core/lowlevel_runtime/include/pantheon_freestanding.h
LICENSE=LICENSE.md
STAGE=00_SOURCE_AND_RIGHTS

printf '%s\n' \
  'schema=rll.omega.canonical_freestanding_receipt.v1' \
  "source_head=${RLL_SOURCE_HEAD_SHA:-${GITHUB_SHA:-LOCAL_UNVERIFIED_HEAD}}" \
  "event_sha=${GITHUB_SHA:-LOCAL_UNVERIFIED_EVENT}" \
  "run_id=${GITHUB_RUN_ID:-LOCAL_RUN}" \
  'claim_allowed=false' \
  'scientific_confirmation=false' \
  'kernel=PURE_C_FREESTANDING' \
  'orchestrator=HOSTED_SHELL_COMPILER_GITHUB' \
  'execution_armv7=NOT_RUN_PHYSICAL' \
  'execution_aarch64=NOT_RUN_PHYSICAL' \
  'ws01_inference=NOT_APPLICABLE_THIS_GATE' > "$RECEIPT"

finalize() {
  rc=$?
  trap - 0
  if [ "$rc" -eq 0 ]; then state=PASS_SCOPED; else state=FAIL_CLOSED; fi
  printf 'state=%s\nfailed_or_last_stage=%s\nexit_code=%s\n' "$state" "$STAGE" "$rc" >> "$RECEIPT"
  if [ -f "$CORE" ] && [ -f "$HEADER" ] && [ -f "$HARNESS" ] && [ -f "$SIGNED_VECTORS" ] && [ -f "$TRANSITIVE_HEADER" ] && [ -f "$LICENSE" ]; then
    sha256sum "$CORE" "$HEADER" "$TRANSITIVE_HEADER" "$HARNESS" "$SIGNED_VECTORS" "$LICENSE" > "$OUT/source_checksums.sha256" || :
  fi
  cat "$RECEIPT"
  exit "$rc"
}
trap finalize 0

for f in "$CORE" "$HEADER" "$TRANSITIVE_HEADER" "$HARNESS" "$SIGNED_VECTORS" "$LICENSE"; do
  if [ ! -f "$f" ]; then
    printf 'gap=TOKEN_VAZIO_MISSING_SOURCE:%s\n' "$f" >> "$RECEIPT"
    exit 21
  fi
done

# Missing or conflicted license is a P0; do not alter or substitute the original.
grep -Fq 'CC-BY-SA-4.0' "$LICENSE" || {
  printf '%s\n' 'gap=TOKEN_VAZIO_LICENSE_AUTHORITY' >> "$RECEIPT"
  exit 22
}
# No libc headers, hosted function calls or in-source OS calls in the PURE core.
if grep -nE '^[[:space:]]*#[[:space:]]*include[[:space:]]*<' "$CORE" "$HEADER" "$TRANSITIVE_HEADER" ; then
  printf '%s\n' 'gap=FAIL_HOSTED_INCLUDE_IN_FREESTANDING_CORE' >> "$RECEIPT"
  exit 23
fi
if grep -nE '(malloc|calloc|realloc|free|printf|fprintf|puts|fopen|fread|fwrite|syscall)[[:space:]]*\(' "$CORE" ; then
  printf '%s\n' 'gap=FAIL_EXTERNAL_OR_OS_CALL_IN_FREESTANDING_CORE' >> "$RECEIPT"
  exit 24
fi
printf '%s\n' '00_source_rights=PASS_IN_SCOPE' >> "$RECEIPT"

STAGE=10_TOOLCHAIN_AND_FREESTANDING_OBJECTS
for command_name in clang nm readelf sha256sum; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf 'gap=TOKEN_VAZIO_TOOLCHAIN_%s\n' "$command_name" >> "$RECEIPT"
    exit 25
  fi
done

COMMON='-std=c11 -O2 -Wall -Wextra -Werror -ffreestanding -fno-builtin -fno-stack-protector -fno-unwind-tables -fno-asynchronous-unwind-tables -nostdlib'
# Split is intentional; there are no paths or untrusted values in COMMON.
# shellcheck disable=SC2086
clang $COMMON -Icore/lowlevel_runtime/include -c "$CORE" -o "$OUT/host_x86_64.o"
# shellcheck disable=SC2086
clang $COMMON --target=armv7a-none-eabi -march=armv7-a -mfloat-abi=soft -Icore/lowlevel_runtime/include -c "$CORE" -o "$OUT/armv7.o"
# shellcheck disable=SC2086
clang $COMMON --target=aarch64-none-elf -Icore/lowlevel_runtime/include -c "$CORE" -o "$OUT/aarch64.o"

STAGE=20_SYMBOLS_ELF_AND_ABI
for t in host_x86_64 armv7 aarch64; do
  nm -u "$OUT/$t.o" > "$OUT/$t.undefined.txt" || {
    printf 'gap=TOKEN_VAZIO_SYMBOL_TOOL_FOR_%s\n' "$t" >> "$RECEIPT"
    exit 30
  }
  if [ -s "$OUT/$t.undefined.txt" ]; then
    printf 'gap=SOURCE_SIDE_UNDEFINED_SYMBOL_%s\n' "$t" >> "$RECEIPT"
    cat "$OUT/$t.undefined.txt"
    exit 31
  fi
  readelf -h "$OUT/$t.o" > "$OUT/$t.elf_header.txt"
done
grep -q 'Machine:.*ARM' "$OUT/armv7.elf_header.txt" || exit 32
grep -q 'Class:.*ELF32' "$OUT/armv7.elf_header.txt" || exit 33
grep -q 'Machine:.*AArch64' "$OUT/aarch64.elf_header.txt" || exit 34
grep -q 'Class:.*ELF64' "$OUT/aarch64.elf_header.txt" || exit 35
printf '%s\n' '10_cross_objects=PASS_COMPILED' '20_unresolved_symbols=ZERO_OBSERVED' >> "$RECEIPT"

STAGE=30_HOSTED_HARNESS_BOUNDARY
# The test entry uses the HOST OS to exit; this is explicitly NOT a freestanding
# executable and is never used as evidence of ARM physical execution.
clang -std=c11 -O2 -Wall -Wextra -Werror -fno-builtin \
  -Icore/lowlevel_runtime/include "$HARNESS" "$CORE" \
  -o "$OUT/hosted_c_vectors"
"$OUT/hosted_c_vectors"
clang -std=c11 -O2 -Wall -Wextra -Werror -fno-builtin \
  -Icore/lowlevel_runtime/include "$SIGNED_VECTORS" "$CORE" \
  -o "$OUT/hosted_signed_vectors"
"$OUT/hosted_signed_vectors"
printf '%s\n' '30_hosted_vector_test=PASS_SCOPED' '30_token_vazio_ne_numeric_zero=ASSERTED_BY_EXISTING_HARNESS' >> "$RECEIPT"

STAGE=90_EVIDENCE_AND_RECEIPT
sha256sum "$OUT/host_x86_64.o" "$OUT/armv7.o" "$OUT/aarch64.o" > "$OUT/object_checksums.sha256"
printf '%s\n' '90_source_objects_hashes=RECORDED' 'rollback=REVERT_THIS_ADDITIVE_CI_ONLY' >> "$RECEIPT"
