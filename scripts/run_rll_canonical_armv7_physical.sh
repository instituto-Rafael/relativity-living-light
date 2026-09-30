#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTDIR="$ROOT/build/rll_armv7_physical"
mkdir -p "$OUTDIR"

INC="$ROOT/core/lowlevel_runtime/include"
A="$ROOT/core/lowlevel_runtime/c/rll_canonical_freestanding.c"
B="$ROOT/core/lowlevel_runtime/c/rll_canonical_hz_data.c"
C="$ROOT/core/lowlevel_runtime/c/rll_canonical_entry.c"

OA="$OUTDIR/rll_canonical_freestanding.o"
OB="$OUTDIR/rll_canonical_hz_data.o"
OC="$OUTDIR/rll_canonical_entry.o"
ELF="$OUTDIR/rll_canonical_armv7_physical"
RECEIPT="$OUTDIR/rll_canonical_armv7_physical_receipt.txt"
STDOUT="$OUTDIR/rll_canonical_armv7_stdout.txt"

NM=llvm-nm
command -v "$NM" >/dev/null 2>&1 || NM=nm

CFLAGS="-std=c11 -Os -Wall -Wextra -Werror -ffreestanding -fno-builtin -fno-stack-protector -fno-unwind-tables -fno-asynchronous-unwind-tables"

echo "=== RLL ARMv7 PHYSICAL BUILD ==="
echo "arch=$(uname -m)"
echo "compiler=$(clang --version | head -n1)"
echo "linker=$(ld.lld --version | head -n1)"

clang $CFLAGS -I"$INC" -c "$A" -o "$OA" || exit 90
clang $CFLAGS -I"$INC" -c "$B" -o "$OB" || exit 91
clang $CFLAGS -I"$INC" -c "$C" -o "$OC" || exit 92

ld.lld -m armelf_linux_eabi -static -e _start -o "$ELF" "$OA" "$OB" "$OC" || exit 93

UNDEF=$("$NM" -u "$ELF" | wc -l)
INTERP=$(readelf -l "$ELF" | grep -c INTERP || true)
NEEDED=$(readelf -d "$ELF" 2>&1 | grep -c NEEDED || true)
SUSPECT=$("$NM" "$ELF" | grep -Ec '__aeabi|__div|__udiv|printf|malloc|free|memcpy|memset|pow|exp|sqrt|stack_chk' || true)

chmod +x "$ELF"
set +e
"$ELF" >"$STDOUT" 2>&1
RC=$?
set -e

cat "$STDOUT"

PREFIX=$(grep -c '^RLLCAN1 rows=33 valid=33 rejected=0 ' "$STDOUT" || true)
NUMERIC=$(grep -c ' numeric_flags=0' "$STDOUT" || true)
CLAIM=$(grep -c ' claim_allowed=0' "$STDOUT" || true)
TOKEN=$(grep -c ' token_vazio=7' "$STDOUT" || true)

STATUS=FAIL
if [ "$RC" -eq 0 ] && [ "$UNDEF" -eq 0 ] && [ "$INTERP" -eq 0 ] &&
   [ "$NEEDED" -eq 0 ] && [ "$SUSPECT" -eq 0 ] &&
   [ "$PREFIX" -eq 1 ] && [ "$NUMERIC" -eq 1 ] &&
   [ "$CLAIM" -eq 1 ] && [ "$TOKEN" -eq 1 ]; then STATUS=PASS; fi

COMMIT=TOKEN_VAZIO
command -v git >/dev/null 2>&1 && COMMIT=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)

cat > "$RECEIPT" <<EOF
receipt_version=1
kind=rll_canonical_engine_armv7_physical
timestamp=$(date -Iseconds)
arch=$(uname -m)
repo_commit=$COMMIT
source_model_sha256=$(sha256sum "$A" | awk '{print $1}')
source_data_sha256=$(sha256sum "$B" | awk '{print $1}')
source_entry_sha256=$(sha256sum "$C" | awk '{print $1}')
object_model_sha256=$(sha256sum "$OA" | awk '{print $1}')
object_data_sha256=$(sha256sum "$OB" | awk '{print $1}')
object_entry_sha256=$(sha256sum "$OC" | awk '{print $1}')
artifact=$ELF
artifact_sha256=$(sha256sum "$ELF" | awk '{print $1}')
stdout_sha256=$(sha256sum "$STDOUT" | awk '{print $1}')
file=$(file "$ELF")
undefined_symbols=$UNDEF
interpreter_segments=$INTERP
needed_entries=$NEEDED
suspicious_runtime_symbols=$SUSPECT
execution_exit=$RC
receipt_prefix_ok=$PREFIX
numeric_flags_zero=$NUMERIC
claim_allowed_zero=$CLAIM
token_vazio_7=$TOKEN
compiler=$(clang --version | head -n1)
linker=$(ld.lld --version | head -n1)
status=$STATUS
EOF

cat "$RECEIPT"
echo "=== RLL PHYSICAL RECEIPT SHA256 ==="
sha256sum "$RECEIPT"
exit $([ "$STATUS" = PASS ] && echo 0 || echo 1)
