#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${1:-"$ROOT/build/rll-canonical-freestanding"}
CC=${CC:-cc}

mkdir -p "$(dirname -- "$OUT")"

CFLAGS="
-std=c11
-O2
-ffreestanding
-fno-builtin
-fno-stack-protector
-fno-pic
-fno-pie
-fno-asynchronous-unwind-tables
-fno-unwind-tables
-Wall
-Wextra
-Werror
"

"$CC" $CFLAGS \
  -nostdlib \
  -static \
  -no-pie \
  -Wl,--build-id=none \
  -Wl,-e,_start \
  -I"$ROOT/core/lowlevel_runtime/include" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_freestanding.c" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_hz_data.c" \
  "$ROOT/core/lowlevel_runtime/c/rll_canonical_entry.c" \
  -o "$OUT"

# A freestanding final ELF must not retain unresolved dynamic imports.
if command -v nm >/dev/null 2>&1; then
  if nm -u "$OUT" | grep . >/dev/null 2>&1; then
    echo "error: unresolved symbols remain in $OUT" >&2
    nm -u "$OUT" >&2
    exit 1
  fi
fi

"$OUT"
