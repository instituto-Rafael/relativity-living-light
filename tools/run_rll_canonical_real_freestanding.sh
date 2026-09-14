#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CC=${CC:-cc}
OUT=${TMPDIR:-/tmp}/rll_canonical_real.elf

"$CC" \
  -std=c11 -Wall -Wextra -Werror -pedantic \
  -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-pie -no-pie -nostdlib -static \
  -ffunction-sections -fdata-sections \
  -DRLL_FREESTANDING_ENTRY \
  -I"$ROOT/core/lowlevel_runtime/include" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_real.c" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_real_data.c" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_real_selftest.c" \
  -Wl,--gc-sections,--build-id=none \
  -o "$OUT"

"$OUT"

if command -v nm >/dev/null 2>&1; then
  UNDEFINED=$(nm -u "$OUT" || true)
  test -z "$UNDEFINED" || {
    printf '%s\n' "$UNDEFINED" >&2
    exit 91
  }
fi

printf 'PASS freestanding ELF: %s\n' "$OUT"
