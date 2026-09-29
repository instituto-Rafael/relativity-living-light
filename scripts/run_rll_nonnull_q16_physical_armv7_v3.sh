#!/data/data/com.termux/files/usr/bin/sh
set -eu

SRC="${1:-core/lowlevel_runtime/c/rll_nonnull_blind_q16_freestanding.c}"
OUTDIR="${2:-build/rll-q16-physical-armv7-v3}"
mkdir -p "$OUTDIR"

CC="${CC:-clang}"
LD="${LD:-ld.lld}"

"$CC" -std=c11 -O2 -Wall -Wextra -Wshadow -Werror \
  -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-unwind-tables -fno-asynchronous-unwind-tables \
  -fomit-frame-pointer -fno-optimize-sibling-calls \
  -fno-pic -fno-pie -nostdlib -ffunction-sections -fdata-sections \
  -c "$SRC" -o "$OUTDIR/kernel.o"

"$LD" -static --gc-sections -e _start -o "$OUTDIR/kernel.elf" "$OUTDIR/kernel.o"

UNDEF="$(nm -u "$OUTDIR/kernel.elf" || true)"
[ -z "$UNDEF" ]
! readelf -l "$OUTDIR/kernel.elf" | grep -q INTERP
! readelf -d "$OUTDIR/kernel.elf" 2>/dev/null | grep -q NEEDED

PROGRAM_OUT="$("$OUTDIR/kernel.elf")"
PROGRAM_RC=$?
printf '%s\n' "$PROGRAM_OUT"
printf '%s\n' "$PROGRAM_OUT" | grep -F 'state=PASS'

SRC_SHA="$(sha256sum "$SRC" | cut -d' ' -f1)"
OBJ_SHA="$(sha256sum "$OUTDIR/kernel.o" | cut -d' ' -f1)"
ELF_SHA="$(sha256sum "$OUTDIR/kernel.elf" | cut -d' ' -f1)"
ABI="$(uname -m)"
DATE_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

RECEIPT="$OUTDIR/PHYSICAL_ARMV7_RECEIPT.txt"
{
  echo "RLL_Q16_PHYSICAL_ARMV7_V3"
  echo "date_utc=$DATE_UTC"
  echo "abi=$ABI"
  echo "source_sha256=$SRC_SHA"
  echo "object_sha256=$OBJ_SHA"
  echo "elf_sha256=$ELF_SHA"
  echo "nm_undefined=NONE"
  echo "interp=NONE"
  echo "needed=NONE"
  echo "shadow_gate=PASS"
  echo "sibling_call_optimization=DISABLED"
  echo "program_rc=$PROGRAM_RC"
  echo "program_output=$PROGRAM_OUT"
  echo "physical_execution=PASS"
  echo "claim_allowed=false"
} > "$RECEIPT"

cat "$RECEIPT"
