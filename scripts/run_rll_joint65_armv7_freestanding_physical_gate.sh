#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT="$ROOT/build/rll-joint65-armv7-freestanding"
mkdir -p "$OUT"

INC="$ROOT/core/lowlevel_runtime/include"
ENTRY="$ROOT/core/lowlevel_runtime/c/rll_joint65_armv7_entry.c"
BLOBS="$ROOT/core/lowlevel_runtime/asm/rll_joint65_embedded_blobs.S"
ELF="$OUT/rll_joint65_armv7_static"
RECEIPT="$OUT/rll_joint65_armv7_physical_receipt.txt"

SOURCES="
$ROOT/core/lowlevel_runtime/c/rll_canonical_coupling.c
$ROOT/core/lowlevel_runtime/c/rll_canonical_real_inputs.c
$ROOT/core/lowlevel_runtime/c/rll_canonical_real_models.c
$ROOT/core/lowlevel_runtime/c/rll_canonical_real.c
$ROOT/core/lowlevel_runtime/c/rll_canonical_real_data.c
$ROOT/core/lowlevel_runtime/c/rll_hz_freestanding.c
$ROOT/core/lowlevel_runtime/c/rll_hz_moresco_2022_q16.c
"

NM=llvm-nm
command -v "$NM" >/dev/null 2>&1 || NM=nm

CFLAGS="-std=c11 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-pie -fno-asynchronous-unwind-tables -fno-unwind-tables -Wall -Wextra -Werror -pedantic"

OBJECTS=""
i=0
for src in $SOURCES; do
  [ -f "$src" ] || { echo "MISSING: $src"; exit 80; }
  obj="$OUT/prod_$i.o"
  clang $CFLAGS -I"$INC" -c "$src" -o "$obj" || exit $((90+i))
  OBJECTS="$OBJECTS $obj"
  i=$((i+1))
done

clang $CFLAGS -I"$INC" -c "$ENTRY" -o "$OUT/entry.o" || exit 110
(
  cd "$ROOT" &&
  clang -c "$BLOBS" -o "$OUT/blobs.o"
) || exit 111

ld.lld -m armelf_linux_eabi -static -e _start -o "$ELF" $OBJECTS "$OUT/entry.o" "$OUT/blobs.o" || {
  echo "STATIC_LINK=FAIL"
  exit 112
}

UNDEF=$($NM -u "$ELF" | wc -l)
INTERP=$(readelf -l "$ELF" | grep -c INTERP || true)
NEEDED=$(readelf -d "$ELF" 2>&1 | grep -c NEEDED || true)
SUSPECT=$($NM "$ELF" | grep -Ec '__aeabi|__div|__udiv|printf|malloc|free|fopen|fread|fclose|memcpy|memset|sqrt|pow|exp|log|stack_chk' || true)

chmod +x "$ELF"
"$ELF"
EXEC_RC=$?

STATUS=FAIL
if [ "$EXEC_RC" -eq 0 ] && [ "$UNDEF" -eq 0 ] &&
   [ "$INTERP" -eq 0 ] && [ "$NEEDED" -eq 0 ] && [ "$SUSPECT" -eq 0 ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF2
schema=rll.joint65-armv7-freestanding-physical.v1
timestamp=$(date -Iseconds)
arch=$(uname -m)
repo_commit=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)

artifact_sha256=$(sha256sum "$ELF" | awk '{print $1}')
entry_sha256=$(sha256sum "$ENTRY" | awk '{print $1}')
blobs_asm_sha256=$(sha256sum "$BLOBS" | awk '{print $1}')
hz_sha256=$(sha256sum "$ROOT/data/real/Hz_data_real.csv" | awk '{print $1}')
bao_sha256=$(sha256sum "$ROOT/data/real/cosmology/desi_dr2_bao_primary_points.csv" | awk '{print $1}')
fs8_sha256=$(sha256sum "$ROOT/data/real/cosmology/fsigma8_growth_real.csv" | awk '{print $1}')
cmb_sha256=$(sha256sum "$ROOT/data/real/CMB_shift_real.json" | awk '{print $1}')

file=$(file "$ELF")
undefined_symbols=$UNDEF
interpreter_segments=$INTERP
needed_entries=$NEEDED
suspicious_runtime_symbols=$SUSPECT
execution_exit=$EXEC_RC

rows=65
bound_rows=65
model_token_vazio_rows=0
cmb_covariance_used=1
lcdm_chi2_q16_expected=4641555
rll_chi2_q16_expected=4261420
delta_q16_expected=-380135
claim_allowed_expected=0

geometry_evidence_transfer=FORBIDDEN
status=$STATUS
EOF2

cat "$RECEIPT"
echo "receipt_sha256=$(sha256sum "$RECEIPT" | awk '{print $1}')"
[ "$STATUS" = PASS ]
