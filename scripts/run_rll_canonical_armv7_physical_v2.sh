#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTDIR="$ROOT/build/armv7_physical_v2"
mkdir -p "$OUTDIR"

INC="$ROOT/core/lowlevel_runtime/include"
SRC_MODEL="$ROOT/core/lowlevel_runtime/c/rll_canonical_freestanding.c"
SRC_DATA="$ROOT/core/lowlevel_runtime/c/rll_canonical_hz_data.c"
SRC_ENTRY="$ROOT/core/lowlevel_runtime/c/rll_canonical_entry.c"
HDR="$INC/rll_canonical_freestanding.h"

OBJ_MODEL="$OUTDIR/rll_canonical_freestanding.o"
OBJ_DATA="$OUTDIR/rll_canonical_hz_data.o"
OBJ_ENTRY="$OUTDIR/rll_canonical_entry.o"
ELF="$OUTDIR/rll_canonical_armv7_physical"
OUTPUT="$OUTDIR/rll_canonical_armv7_output.txt"
RECEIPT="$OUTDIR/rll_canonical_armv7_physical_receipt_v2.txt"

for f in "$SRC_MODEL" "$SRC_DATA" "$SRC_ENTRY" "$HDR"; do
  [ -f "$f" ] || { echo "missing: $f" >&2; exit 80; }
done

command -v clang >/dev/null 2>&1 || { echo "clang missing" >&2; exit 81; }
command -v ld.lld >/dev/null 2>&1 || { echo "ld.lld missing" >&2; exit 82; }
command -v readelf >/dev/null 2>&1 || { echo "readelf missing" >&2; exit 83; }

NM=llvm-nm
command -v "$NM" >/dev/null 2>&1 || NM=nm

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
-I$INC
"

echo "=== RLL ARMv7 PHYSICAL BUILD ==="
clang $CFLAGS -c "$SRC_MODEL" -o "$OBJ_MODEL" || exit 90
clang $CFLAGS -c "$SRC_DATA"  -o "$OBJ_DATA"  || exit 91
clang $CFLAGS -c "$SRC_ENTRY" -o "$OBJ_ENTRY" || exit 92

echo "=== RLL ARMv7 STATIC LINK ==="
ld.lld -m armelf_linux_eabi -static -e _start   -o "$ELF" "$OBJ_MODEL" "$OBJ_DATA" "$OBJ_ENTRY" || exit 93

CORE_UNDEF=$(
  { "$NM" -u "$OBJ_MODEL"; "$NM" -u "$OBJ_DATA"; "$NM" -u "$OBJ_ENTRY"; } |
  grep -v ' rllc_' |
  sed '/^[[:space:]]*$/d' |
  wc -l
)
UNDEF=$("$NM" -u "$ELF" | sed '/^[[:space:]]*$/d' | wc -l)
INTERP=$(readelf -l "$ELF" | grep -c INTERP || true)
NEEDED=$(readelf -d "$ELF" 2>&1 | grep -c NEEDED || true)
SUSPECT=$(
  "$NM" -u "$ELF" |
  grep -Ec '__aeabi|__div|__udiv|(^|[[:space:]])(printf|malloc|free|memcpy|memset|sqrt|stack_chk_fail)([[:space:]]|$)' ||
  true
)

echo "=== RLL ARMv7 PHYSICAL EXECUTION ==="
chmod +x "$ELF"
"$ELF" > "$OUTPUT"
RUN_RC=$?
cat "$OUTPUT"

LINE_OK=0
grep -q '^RLLCAN1 ' "$OUTPUT" &&
grep -q 'rows=33 ' "$OUTPUT" &&
grep -q 'valid=33 ' "$OUTPUT" &&
grep -q 'rejected=0 ' "$OUTPUT" &&
grep -q 'claim_allowed=0 ' "$OUTPUT" &&
grep -q 'numeric_flags=0' "$OUTPUT" &&
LINE_OK=1

STATUS=FAIL
if [ "$RUN_RC" -eq 0 ] &&
   [ "$UNDEF" -eq 0 ] &&
   [ "$INTERP" -eq 0 ] &&
   [ "$NEEDED" -eq 0 ] &&
   [ "$SUSPECT" -eq 0 ] &&
   [ "$LINE_OK" -eq 1 ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF
receipt_version=2
kind=RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL
timestamp=$(date -Iseconds)
arch=$(uname -m)

model_source_sha256=$(sha256sum "$SRC_MODEL" | awk '{print $1}')
data_source_sha256=$(sha256sum "$SRC_DATA" | awk '{print $1}')
entry_source_sha256=$(sha256sum "$SRC_ENTRY" | awk '{print $1}')
header_sha256=$(sha256sum "$HDR" | awk '{print $1}')

model_object_sha256=$(sha256sum "$OBJ_MODEL" | awk '{print $1}')
data_object_sha256=$(sha256sum "$OBJ_DATA" | awk '{print $1}')
entry_object_sha256=$(sha256sum "$OBJ_ENTRY" | awk '{print $1}')
artifact_sha256=$(sha256sum "$ELF" | awk '{print $1}')
output_sha256=$(sha256sum "$OUTPUT" | awk '{print $1}')

file=$(file "$ELF")
core_external_undefined=$CORE_UNDEF
undefined_symbols=$UNDEF
interpreter_segments=$INTERP
needed_entries=$NEEDED
suspicious_undefined_runtime_symbols=$SUSPECT
receipt_line_gate=$LINE_OK
run_exit=$RUN_RC

compiler=$(clang --version | head -n1)
linker=$(ld.lld --version | head -n1)

scientific_claim_allowed=false
status=$STATUS
EOF

cat "$RECEIPT"
echo "=== RLL PHYSICAL RECEIPT SHA256 ==="
sha256sum "$RECEIPT"

[ "$STATUS" = PASS ]
