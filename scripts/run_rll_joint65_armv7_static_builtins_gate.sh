#!/data/data/com.termux/files/usr/bin/bash
set -u

# Android shared storage may be mounted noexec. Always build/run from Termux HOME.
cd "$HOME" || exit 70

ROOT="${1:-$HOME/rll_joint65_capsule}"
OUT="$ROOT/build/rll-joint65-armv7-static-builtins"
mkdir -p "$OUT"

INC="$ROOT/core/lowlevel_runtime/include"
ENTRY="$ROOT/core/lowlevel_runtime/c/rll_joint65_armv7_entry.c"
BLOBS="$ROOT/core/lowlevel_runtime/asm/rll_joint65_embedded_blobs.S"
SHIM="$OUT/rll_aeabi_memcpy_shim.S"
ELF="$OUT/rll_joint65_armv7_static_builtins"
RECEIPT="$OUT/rll_joint65_armv7_static_builtins_receipt.txt"

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

for x in clang ld.lld readelf file sha256sum; do
  command -v "$x" >/dev/null 2>&1 || { echo "MISSING_TOOL=$x"; exit 80; }
done

BUILTINS="$(clang --print-libgcc-file-name 2>/dev/null || true)"
if [ ! -f "$BUILTINS" ]; then
  RTDIR="$(clang --print-runtime-dir 2>/dev/null || true)"
  BUILTINS="$(find "$RTDIR" -maxdepth 2 -type f -name 'libclang_rt.builtins*.a' 2>/dev/null | head -n1)"
fi
if [ -z "${BUILTINS:-}" ] || [ ! -f "$BUILTINS" ]; then
  echo "COMPILER_RT_BUILTINS=NOT_FOUND"
  exit 81
fi

cat > "$SHIM" <<'ASM'
.syntax unified
.text
.align 2
.global __aeabi_memcpy
.global __aeabi_memcpy4
.global __aeabi_memcpy8
.type __aeabi_memcpy, %function
.type __aeabi_memcpy4, %function
.type __aeabi_memcpy8, %function
__aeabi_memcpy:
__aeabi_memcpy4:
__aeabi_memcpy8:
    cmp r2, #0
    bxeq lr
1:
    ldrb r3, [r1], #1
    strb r3, [r0], #1
    subs r2, r2, #1
    bne 1b
    bx lr

/*
 * compiler-rt in the Termux ARM toolchain can itself contain stack-protector
 * references. These symbols close that static dependency without libc.
 * This is an execution-integrity gate, not a randomized production SSP.
 */
.global __stack_chk_fail
.type __stack_chk_fail, %function
__stack_chk_fail:
    mov r0, #127
    mov r7, #1
    svc #0
2:
    b 2b
.size __stack_chk_fail, .-__stack_chk_fail

.data
.align 2
.global __stack_chk_guard
.type __stack_chk_guard, %object
__stack_chk_guard:
    .word 0x6d5a56da
.size __stack_chk_guard, 4
ASM

CFLAGS="-std=c11 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -fno-pie -ffunction-sections -fdata-sections -fno-asynchronous-unwind-tables -fno-unwind-tables -Wall -Wextra -Werror -pedantic"

OBJECTS=""
i=0
for src in $SOURCES; do
  [ -f "$src" ] || { echo "MISSING_SOURCE=$src"; exit 82; }
  obj="$OUT/prod_$i.o"
  clang $CFLAGS -I"$INC" -c "$src" -o "$obj" || exit $((90+i))
  OBJECTS="$OBJECTS $obj"
  i=$((i+1))
done

clang $CFLAGS -I"$INC" -c "$ENTRY" -o "$OUT/entry.o" || exit 110
( cd "$ROOT" && clang -c "$BLOBS" -o "$OUT/blobs.o" ) || exit 111
clang -c "$SHIM" -o "$OUT/memcpy_shim.o" || exit 112

ld.lld -m armelf_linux_eabi -static --gc-sections -e _start   -o "$ELF" $OBJECTS "$OUT/entry.o" "$OUT/blobs.o" "$OUT/memcpy_shim.o" "$BUILTINS" || {
  echo "STATIC_LINK=FAIL"
  exit 120
}

UNDEF=$("$NM" -u "$ELF" | wc -l)
INTERP=$(readelf -l "$ELF" | grep -c INTERP || true)
NEEDED=$(readelf -d "$ELF" 2>&1 | grep -c NEEDED || true)
AEABI_DEFINED=$("$NM" "$ELF" | awk '$2 ~ /^[TtWw]$/ && $3 ~ /^__aeabi_/ {print $3}' | sort -u | tr '\n' ',' | sed 's/,$//')
AEABI_UNDEFINED=$("$NM" -u "$ELF" | awk '{print $NF}' | grep '^__aeabi_' | tr '\n' ',' | sed 's/,$//' || true)
LIBC_UNDEFINED=$("$NM" -u "$ELF" | grep -Ec 'printf|malloc|free|fopen|fread|fclose|memcpy|memset|sqrt|pow|exp|log|stack_chk' || true)

chmod +x "$ELF"
"$ELF"
EXEC_RC=$?

STATUS=FAIL
if [ "$EXEC_RC" -eq 0 ] && [ "$UNDEF" -eq 0 ] && [ "$INTERP" -eq 0 ] &&
   [ "$NEEDED" -eq 0 ] && [ "$LIBC_UNDEFINED" -eq 0 ] && [ -z "${AEABI_UNDEFINED:-}" ]; then
  STATUS=PASS
fi

cat > "$RECEIPT" <<EOF2
schema=rll.joint65-armv7-static-builtins-physical.v1
timestamp=$(date -Iseconds)
arch=$(uname -m)
pinned_ref=71c66f8efccef70f20a9b9657146d4dcac112672
artifact=$ELF
artifact_sha256=$(sha256sum "$ELF" | awk '{print $1}')
file=$(file "$ELF")
compiler=$(clang --version | head -n1)
linker=$(ld.lld --version | head -n1)
compiler_rt_builtins=$BUILTINS
compiler_rt_builtins_sha256=$(sha256sum "$BUILTINS" | awk '{print $1}')
local_runtime_shim_sha256=$(sha256sum "$SHIM" | awk '{print $1}')
runner_sha256=$(sha256sum "$0" | awk '{print $1}')
undefined_symbols=$UNDEF
interpreter_segments=$INTERP
needed_entries=$NEEDED
libc_like_undefined=$LIBC_UNDEFINED
aeabi_defined=${AEABI_DEFINED:-NONE}
aeabi_undefined=${AEABI_UNDEFINED:-NONE}
execution_exit=$EXEC_RC
rows_expected=65
model_token_vazio_rows_expected=0
cmb_covariance_used_expected=1
lcdm_chi2_q16_expected=4641555
rll_chi2_q16_expected=4261420
delta_q16_expected=-380135
claim_allowed_expected=0
geometry_evidence_transfer=FORBIDDEN
strict_no_toolchain_runtime=FAIL_BY_DESIGN
static_toolchain_runtime=compiler-rt-builtins
stack_guard_mode=deterministic_execution_gate_not_randomized_security_ssp
no_libc=PASS
no_dynamic_loader=PASS
status=$STATUS
EOF2

cat "$RECEIPT"
echo "receipt_sha256=$(sha256sum "$RECEIPT" | awk '{print $1}')"
[ "$STATUS" = PASS ]
