#!/data/data/com.termux/files/usr/bin/bash
set -u

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
WORK="$HOME/rll_nonnull_split_v3"
rm -rf "$WORK"
mkdir -p "$WORK"

G="$ROOT/core/lowlevel_runtime/c/rll_nonnull_fixture_generator_q16.c"
R="$ROOT/core/lowlevel_runtime/c/rll_nonnull_recovery_q16.c"
RECEIPT="$WORK/rll_nonnull_split_armv7_physical_v3_receipt.txt"

for X in clang ld.lld readelf sha256sum; do
  command -v "$X" >/dev/null 2>&1 || { echo "MISSING_TOOL=$X"; exit 80; }
done
NM=llvm-nm
command -v "$NM" >/dev/null 2>&1 || NM=nm

CFLAGS="-std=c11 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fno-optimize-sibling-calls -fno-pic -fno-pie -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -Wshadow -Werror=shadow -Wall -Wextra -Werror"

for M in 0 1 2; do
  clang $CFLAGS -DGEN_MODE=$M -c "$G" -o "$WORK/g$M.o" || exit $((90+M))
  ld.lld -m armelf_linux_eabi -static --gc-sections -e _start -o "$WORK/g$M.elf" "$WORK/g$M.o" || exit $((100+M))
done

clang $CFLAGS -c "$R" -o "$WORK/recovery.o" || exit 110
ld.lld -m armelf_linux_eabi -static --gc-sections -e _start -o "$WORK/recovery.elf" "$WORK/recovery.o" || exit 111

for E in "$WORK/g0.elf" "$WORK/g1.elf" "$WORK/g2.elf" "$WORK/recovery.elf"; do
  test -z "$("$NM" -u "$E")" || exit 120
  ! readelf -l "$E" | grep -q INTERP || exit 121
  ! readelf -d "$E" 2>/dev/null | grep -q NEEDED || exit 122
  chmod +x "$E"
done

clang $CFLAGS -DGEN_MODE=0 -S "$G" -o "$WORK/g-arm.s" || exit 123
clang $CFLAGS -S "$R" -o "$WORK/r-arm.s" || exit 124
GT=$(grep -Ec '^[[:space:]]*b[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' "$WORK/g-arm.s" || true)
RT=$(grep -Ec '^[[:space:]]*b[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' "$WORK/r-arm.s" || true)

"$WORK/g0.elf" > "$WORK/exact.rlf"
"$WORK/recovery.elf" < "$WORK/exact.rlf" > "$WORK/exact.txt"
EXACT_RC=$?
"$WORK/g1.elf" > "$WORK/stress.rlf"
"$WORK/recovery.elf" < "$WORK/stress.rlf" > "$WORK/stress.txt"
STRESS_RC=$?
"$WORK/g2.elf" > "$WORK/null.rlf"
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
if [ "$EXACT_RC" -eq 0 ] && [ "$STRESS_RC" -eq 0 ] && [ "$NULL_RC" -eq 0 ] &&
   [ "$EXACT_OK" -eq 1 ] && [ "$STRESS_OK" -eq 1 ] && [ "$NULL_OK" -eq 1 ] &&
   [ "$GT" -eq 0 ] && [ "$RT" -eq 0 ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF
schema=rll.nonnull_split_armv7_physical.v3
timestamp=$(date -Iseconds)
arch=$(uname -m)
git_head=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo TOKEN_VAZIO)

generator_source_sha256=$(sha256sum "$G" | awk '{print $1}')
recovery_source_sha256=$(sha256sum "$R" | awk '{print $1}')
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

exact_exit=$EXACT_RC
stress_exit=$STRESS_RC
null_exit=$NULL_RC
exact_gate=$EXACT_OK
stress_gate=$STRESS_OK
null_gate=$NULL_OK
claim_allowed=false
status=$STATUS
EOF

cat "$RECEIPT"
echo "receipt_sha256=$(sha256sum "$RECEIPT" | awk '{print $1}')"
[ "$STATUS" = PASS ]
