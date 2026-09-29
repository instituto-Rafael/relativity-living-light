#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK="$HOME/rll_nonnull_split_v3"
rm -rf "$WORK"
mkdir -p "$WORK"

G="$ROOT/core/lowlevel_runtime/c/rll_nonnull_fixture_generator_q16.c"
R="$ROOT/core/lowlevel_runtime/c/rll_nonnull_recovery_q16.c"
CONTRACT="$ROOT/data/contracts/rll_nonnull_split_binary_q16.v3.json"
RECEIPT="$WORK/rll_nonnull_split_armv7_physical_v3_receipt.txt"

for X in clang ld.lld readelf sha256sum getprop; do
  command -v "$X" >/dev/null 2>&1 || { echo "MISSING_TOOL=$X"; exit 80; }
done

ANDROID_ABI=$(getprop ro.product.cpu.abi 2>/dev/null || true)
[ "$ANDROID_ABI" = "armeabi-v7a" ] || {
  echo "UNSUPPORTED_ANDROID_ABI=${ANDROID_ABI:-TOKEN_VAZIO}"
  exit 83
}
ANDROID_SDK=$(getprop ro.build.version.sdk 2>/dev/null || echo TOKEN_VAZIO)

if command -v llvm-nm >/dev/null 2>&1; then
  NM=llvm-nm
elif command -v nm >/dev/null 2>&1; then
  NM=nm
else
  echo "MISSING_TOOL=llvm-nm_or_nm"
  exit 81
fi
NM_PATH=$(command -v "$NM") || exit 82

CFLAGS="--target=armv7-linux-gnueabihf -march=armv7-a -marm -std=c11 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fno-optimize-sibling-calls -fno-pic -fno-pie -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -Wshadow -Werror=shadow -Wall -Wextra -Werror"

for M in 0 1 2; do
  clang $CFLAGS -DGEN_MODE=$M -c "$G" -o "$WORK/g$M.o" || exit $((90+M))
  ld.lld -m armelf_linux_eabi -static --gc-sections -e _start -o "$WORK/g$M.elf" "$WORK/g$M.o" || exit $((100+M))
done

clang $CFLAGS -c "$R" -o "$WORK/recovery.o" || exit 110
ld.lld -m armelf_linux_eabi -static --gc-sections -e _start -o "$WORK/recovery.elf" "$WORK/recovery.o" || exit 111

for E in "$WORK/g0.elf" "$WORK/g1.elf" "$WORK/g2.elf" "$WORK/recovery.elf"; do
  UNDEFINED=$("$NM" -u "$E") || exit 120
  test -z "$UNDEFINED" || exit 120
  readelf -h "$E" | grep -Fq 'ELF32' || exit 121
  readelf -h "$E" | grep -Fq 'ARM' || exit 121
  ! readelf -l "$E" | grep -q INTERP || exit 122
  ! readelf -d "$E" 2>/dev/null | grep -q NEEDED || exit 123
  chmod +x "$E"
done

clang $CFLAGS -DGEN_MODE=0 -S "$G" -o "$WORK/g-arm.s" || exit 124
clang $CFLAGS -S "$R" -o "$WORK/r-arm.s" || exit 125
GT=$(grep -Ec '^[[:space:]]*b[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' "$WORK/g-arm.s" || true)
RT=$(grep -Ec '^[[:space:]]*b[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' "$WORK/r-arm.s" || true)

"$WORK/g0.elf" > "$WORK/exact.rlf"
EXACT_GEN_RC=$?
"$WORK/recovery.elf" < "$WORK/exact.rlf" > "$WORK/exact.txt"
EXACT_RC=$?
"$WORK/g1.elf" > "$WORK/stress.rlf"
STRESS_GEN_RC=$?
"$WORK/recovery.elf" < "$WORK/stress.rlf" > "$WORK/stress.txt"
STRESS_RC=$?
"$WORK/g2.elf" > "$WORK/null.rlf"
NULL_GEN_RC=$?
"$WORK/recovery.elf" < "$WORK/null.rlf" > "$WORK/null.txt"
NULL_RC=$?

cat "$WORK/exact.txt"
cat "$WORK/stress.txt"
cat "$WORK/null.txt"

EXACT_OK=0
STRESS_OK=0
NULL_OK=0
grep -Fq 'best=1311,65536,19661' "$WORK/exact.txt" && EXACT_OK=1
grep -Fq 'best=1311,65536,21299' "$WORK/stress.txt" && STRESS_OK=1
grep -Fq 'best=0,' "$WORK/null.txt" && NULL_OK=1

STATUS=FAIL
if [ "$EXACT_GEN_RC" -eq 0 ] && [ "$STRESS_GEN_RC" -eq 0 ] && [ "$NULL_GEN_RC" -eq 0 ] &&
   [ "$EXACT_RC" -eq 0 ] && [ "$STRESS_RC" -eq 0 ] && [ "$NULL_RC" -eq 0 ] &&
   [ "$EXACT_OK" -eq 1 ] && [ "$STRESS_OK" -eq 1 ] && [ "$NULL_OK" -eq 1 ] &&
   [ "$GT" -eq 0 ] && [ "$RT" -eq 0 ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF
schema=rll.nonnull_split_armv7_physical.v3
timestamp=$(date -Iseconds)
arch=$(uname -m)
android_abi=$ANDROID_ABI
android_sdk=$ANDROID_SDK
git_head=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)
nm_tool=$NM
nm_path=$NM_PATH
nm_version=$("$NM" --version 2>/dev/null | head -n 1 || echo TOKEN_VAZIO)
clang_path=$(command -v clang)
clang_version=$(clang --version 2>/dev/null | head -n 1 || echo TOKEN_VAZIO)
clang_sha256=$(sha256sum "$(command -v clang)" | awk '{print $1}')
ld_lld_path=$(command -v ld.lld)
ld_lld_version=$(ld.lld --version 2>/dev/null | head -n 1 || echo TOKEN_VAZIO)
ld_lld_sha256=$(sha256sum "$(command -v ld.lld)" | awk '{print $1}')
nm_sha256=$(sha256sum "$NM_PATH" | awk '{print $1}')

generator_source_sha256=$(sha256sum "$G" | awk '{print $1}')
recovery_source_sha256=$(sha256sum "$R" | awk '{print $1}')
contract_sha256=$(sha256sum "$CONTRACT" | awk '{print $1}')
generator_exact_elf_sha256=$(sha256sum "$WORK/g0.elf" | awk '{print $1}')
generator_stress_elf_sha256=$(sha256sum "$WORK/g1.elf" | awk '{print $1}')
generator_null_elf_sha256=$(sha256sum "$WORK/g2.elf" | awk '{print $1}')
recovery_elf_sha256=$(sha256sum "$WORK/recovery.elf" | awk '{print $1}')
exact_fixture_sha256=$(sha256sum "$WORK/exact.rlf" | awk '{print $1}')
stress_fixture_sha256=$(sha256sum "$WORK/stress.rlf" | awk '{print $1}')
null_fixture_sha256=$(sha256sum "$WORK/null.rlf" | awk '{print $1}')
exact_output_sha256=$(sha256sum "$WORK/exact.txt" | awk '{print $1}')
stress_output_sha256=$(sha256sum "$WORK/stress.txt" | awk '{print $1}')
null_output_sha256=$(sha256sum "$WORK/null.txt" | awk '{print $1}')
runner_sha256=$(sha256sum "$0" | awk '{print $1}')

generator_named_tail_branches=$GT
recovery_named_tail_branches=$RT
identifier_shadow_gate=PASS_WSHADOW_WERROR
stack_protector=DISABLED_BY_FLAG
undefined_symbols=0
interpreter_segments=0
needed_entries=0
symbol_audit=PASS_FAIL_CLOSED
target_elf=ELF32_ARM
independent_reimplementation=TOKEN_VAZIO
held_out_real_data=TOKEN_VAZIO

exact_generator_exit=$EXACT_GEN_RC
stress_generator_exit=$STRESS_GEN_RC
null_generator_exit=$NULL_GEN_RC
exact_recovery_exit=$EXACT_RC
stress_recovery_exit=$STRESS_RC
null_recovery_exit=$NULL_RC
exact_gate=$EXACT_OK
stress_gate=$STRESS_OK
null_gate=$NULL_OK
claim_allowed=false
status=$STATUS
EOF

cat "$RECEIPT"
echo "receipt_sha256=$(sha256sum "$RECEIPT" | awk '{print $1}')"
[ "$STATUS" = PASS ]
