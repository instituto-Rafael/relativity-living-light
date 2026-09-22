#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTDIR="$ROOT/build/rll-armv7-physical"
INC="$ROOT/core/lowlevel_runtime/include"
SRC1="$ROOT/core/lowlevel_runtime/c/rll_canonical_freestanding.c"
SRC2="$ROOT/core/lowlevel_runtime/c/rll_canonical_hz_data.c"
SRC3="$ROOT/core/lowlevel_runtime/c/rll_canonical_entry.c"
OBJ1="$OUTDIR/rll_canonical_freestanding.o"
OBJ2="$OUTDIR/rll_canonical_hz_data.o"
OBJ3="$OUTDIR/rll_canonical_entry.o"
ELF="$OUTDIR/rll_canonical_armv7_static"
RECEIPT="$OUTDIR/rll_canonical_armv7_physical_receipt_v2.txt"

mkdir -p "$OUTDIR"

for f in "$SRC1" "$SRC2" "$SRC3" "$INC/rll_canonical_freestanding.h"; do
  [ -f "$f" ] || { echo "MISSING: $f"; exit 80; }
done

NM=llvm-nm
command -v "$NM" >/dev/null 2>&1 || NM=nm

CFLAGS="-std=c11 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-pie -fno-asynchronous-unwind-tables -fno-unwind-tables -Wall -Wextra -Werror"

clang $CFLAGS -I"$INC" -c "$SRC1" -o "$OBJ1" || exit 90
clang $CFLAGS -I"$INC" -c "$SRC2" -o "$OBJ2" || exit 91
clang $CFLAGS -I"$INC" -c "$SRC3" -o "$OBJ3" || exit 92
ld.lld -m armelf_linux_eabi -static -e _start -o "$ELF" "$OBJ1" "$OBJ2" "$OBJ3" || exit 93

UNDEF=$($NM -u "$ELF" | wc -l)
INTERP=$(readelf -l "$ELF" | grep -c INTERP || true)
NEEDED=$(readelf -d "$ELF" 2>&1 | grep -c NEEDED || true)
SUSPECT=$($NM "$ELF" | grep -Ec '__aeabi|__div|__udiv|printf|malloc|free|memcpy|memset|sqrt|stack_chk' || true)

EXPECTED='RLLCAN1 rows=33 valid=33 rejected=0 chi2_rll_q16=1541113 chi2_lcdm_q16=1541113 delta_q16=0 data_crc32=c7e56bca data_fnv64=f48a2db3d131c45f params_crc32=2505dec9 phase20_crc32=1b6c7c85 joint_n=1677 lnB10_q16=-405682 lnB10_err_q16=45263 delta_bic_q16=1459487 os0_ul95_q16=116 joint_best=LCDM receipt_crc32=34387926 best=TIE claim_allowed=0 token_vazio=7 numeric_flags=0'

chmod +x "$ELF"
OUTPUT=$("$ELF")
EXEC_RC=$?
printf '%s\n' "$OUTPUT"

OUTPUT_MATCH=0
[ "$OUTPUT" = "$EXPECTED" ] && OUTPUT_MATCH=1

CLAIM_FALSE=0
printf '%s\n' "$OUTPUT" | grep -q 'claim_allowed=0' && CLAIM_FALSE=1

NUMERIC_ZERO=0
printf '%s\n' "$OUTPUT" | grep -q 'numeric_flags=0' && NUMERIC_ZERO=1

STATUS=FAIL
if [ "$EXEC_RC" -eq 0 ] && [ "$UNDEF" -eq 0 ] &&
   [ "$INTERP" -eq 0 ] && [ "$NEEDED" -eq 0 ] && [ "$SUSPECT" -eq 0 ] &&
   [ "$OUTPUT_MATCH" -eq 1 ] && [ "$CLAIM_FALSE" -eq 1 ] && [ "$NUMERIC_ZERO" -eq 1 ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF2
schema=rll.canonical-armv7-physical-receipt.v2
timestamp=$(date -Iseconds)
arch=$(uname -m)
repo_commit=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)

source_freestanding_sha256=$(sha256sum "$SRC1" | awk '{print $1}')
source_hz_data_sha256=$(sha256sum "$SRC2" | awk '{print $1}')
source_entry_sha256=$(sha256sum "$SRC3" | awk '{print $1}')
header_sha256=$(sha256sum "$INC/rll_canonical_freestanding.h" | awk '{print $1}')
artifact_sha256=$(sha256sum "$ELF" | awk '{print $1}')
output_sha256=$(printf '%s\n' "$OUTPUT" | sha256sum | awk '{print $1}')

file=$(file "$ELF")
undefined_symbols=$UNDEF
interpreter_segments=$INTERP
needed_entries=$NEEDED
suspicious_runtime_symbols=$SUSPECT
execution_exit=$EXEC_RC
canonical_output_match=$OUTPUT_MATCH
claim_allowed_false=$CLAIM_FALSE
numeric_flags_zero=$NUMERIC_ZERO

receipt_line=$OUTPUT

compiler=$(clang --version | head -n1)
linker=$(ld.lld --version | head -n1)

rll_canonical_engine_armv7_physical=$STATUS
geometry_v5_evidence_transfer=FORBIDDEN
scientific_claim_promotion=FORBIDDEN
status=$STATUS
EOF2

cat "$RECEIPT"
echo "receipt_sha256=$(sha256sum "$RECEIPT" | awk '{print $1}')"
[ "$STATUS" = PASS ]
