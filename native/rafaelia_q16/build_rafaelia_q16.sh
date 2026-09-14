#!/data/data/com.termux/files/usr/bin/sh
set -eu
export LC_ALL=C

# RAFAELIA Q16 ARM32 loaderless runtime v2
# Generates a libc-free, CRT-free, PT_INTERP-free ELF32 executable and
# validates recurrence, fixed band, first fixed iteration and stripped parity.
# Verified ARMv7 baseline: original=4740, stripped=3660, x96=1517719,
# fixed-band=1517719..1517725, first-fixed-iteration=90.

need(){ command -v "$1" >/dev/null 2>&1 || { echo "[FALHA] Ferramenta ausente: $1" >&2; exit 127; }; }
for tool in clang ld.lld readelf sha256sum awk wc cmp diff cp chmod grep uname cat; do need "$tool"; done
if command -v llvm-strip >/dev/null 2>&1; then STRIP_TOOL=llvm-strip; elif command -v strip >/dev/null 2>&1; then STRIP_TOOL=strip; else echo "[FALHA] llvm-strip ou strip necessario." >&2; exit 127; fi

echo "[*] Gerando RAFAELIA Q16 freestanding (loaderless, v2)..."
cat <<'EOF_H' > rafaelia.h
#ifndef RAFAELIA_H
#define RAFAELIA_H
typedef unsigned int u32;
typedef int s32;
typedef unsigned long long u64;
typedef long long s64;
#define TOKEN_VAZIO 0
#define Q16_SHIFT 16
#define Q16_ONE (1u << Q16_SHIFT)
#define OP_GEOM_SQRT3_2 56756
#define CONST_FORCE 203333
#define OMEGA_TARGET 1517675
#define OMEGA_TOLERANCE_Q16 64
#define FRAF_ITERATIONS 96u
#define FIXED_SCAN_RADIUS 256
#define ARRAY_LEN_LITERAL(x) ((u32)(sizeof(x) - 1u))
s32 fraf_step(s32 current);
s32 fraf_iterate(s32 seed, u32 iterations);
u32 fraf_find_fixed_band(s32 center, s32 radius, s32 *minimum, s32 *maximum);
u32 fraf_first_fixed_iteration(s32 seed, u32 limit, s32 *fixed_value);
void bare_write(const char *text, u32 length);
void bare_print_s32(s32 value);
void bare_print_q16_decimal(s32 value);
__attribute__((noreturn)) void bare_exit(int code);
#endif
EOF_H
cat <<'EOF_M' > fraf_math.c
#include "rafaelia.h"
s32 fraf_step(s32 current){ s64 product=(s64)current*(s64)OP_GEOM_SQRT3_2; return (s32)(product>>Q16_SHIFT)+CONST_FORCE; }
s32 fraf_iterate(s32 seed,u32 iterations){ s32 current=seed; u32 i; for(i=0u;i<iterations;++i) current=fraf_step(current); return current; }
u32 fraf_find_fixed_band(s32 center,s32 radius,s32 *minimum,s32 *maximum){ s32 start=center-radius,end=center+radius,value; u32 count=0u; for(value=start;value<=end;++value){ if(fraf_step(value)==value){ if(count==0u)*minimum=value; *maximum=value; ++count; } } return count; }
u32 fraf_first_fixed_iteration(s32 seed,u32 limit,s32 *fixed_value){ s32 current=seed; u32 iteration; for(iteration=1u;iteration<=limit;++iteration){ current=fraf_step(current); if(fraf_step(current)==current){ *fixed_value=current; return iteration; } } *fixed_value=current; return 0u; }
EOF_M
cat <<'EOF_C' > main.c
#include "rafaelia.h"
static long bare_sys_write(u32 fd,const char *text,u32 length){ register long r0 __asm__("r0")=(long)fd; register long r1 __asm__("r1")=(long)text; register long r2 __asm__("r2")=(long)length; register long r7 __asm__("r7")=4; __asm__ volatile("svc #0":"+r"(r0):"r"(r1),"r"(r2),"r"(r7):"memory","cc"); return r0; }
void bare_write(const char *text,u32 length){ while(length>0u){ long written=bare_sys_write(1u,text,length); if(written<=0)return; text+=(u32)written; length-=(u32)written; } }
__attribute__((noreturn)) void bare_exit(int code){ register long r0 __asm__("r0")=(long)code; register long r7 __asm__("r7")=1; __asm__ volatile("svc #0"::"r"(r0),"r"(r7):"memory","cc"); __builtin_unreachable(); }
static void bare_print_u32(u32 value){ char buffer[10]; u32 position=(u32)sizeof(buffer); do{ u32 quotient=value/10u; u32 digit=value-quotient*10u; buffer[--position]=(char)('0'+digit); value=quotient; }while(value!=0u); bare_write(&buffer[position],(u32)sizeof(buffer)-position); }
void bare_print_s32(s32 value){ u32 magnitude; if(value<0){ bare_write("-",1u); magnitude=0u-(u32)value; }else magnitude=(u32)value; bare_print_u32(magnitude); }
static void bare_print_fraction6(u32 fraction){ char digits[6]; u32 i; for(i=6u;i>0u;--i){ u32 q=fraction/10u; digits[i-1u]=(char)('0'+(fraction-q*10u)); fraction=q; } bare_write(digits,6u); }
void bare_print_q16_decimal(s32 value){ u32 magnitude,integer_part,fractional_bits,fractional_decimal; if(value<0){ bare_write("-",1u); magnitude=0u-(u32)value; }else magnitude=(u32)value; integer_part=magnitude>>Q16_SHIFT; fractional_bits=magnitude&(Q16_ONE-1u); fractional_decimal=(u32)((((u64)fractional_bits*1000000u)+32768u)>>Q16_SHIFT); if(fractional_decimal>=1000000u){ ++integer_part; fractional_decimal-=1000000u; } bare_print_u32(integer_part); bare_write(".",1u); bare_print_fraction6(fractional_decimal); }
static s32 bare_abs_diff(s32 a,s32 b){ s64 d=(s64)a-(s64)b; return (s32)(d<0?-d:d); }
static void print_integer_line(const char *l,u32 n,s32 v){ bare_write(l,n); bare_print_s32(v); bare_write("\n",1u); }
static void print_q16_line(const char *l,u32 n,s32 v){ bare_write(l,n); bare_print_s32(v); bare_write(" (",2u); bare_print_q16_decimal(v); bare_write(")\n",2u); }
__attribute__((noreturn,used,visibility("default"))) void _start(void){
static const char msg_init[]="[RAFAELIA CORE] Init Vazio Util...\n";
static const char msg_mode[]="[MODO] ARM32 ring-3 freestanding; syscalls Linux diretas.\n";
static const char l48[]="[RESULTADO Q16 / 48] ",l96[]="[RESULTADO Q16 / 96] ",lt[]="[ALVO OMEGA Q16] ",le[]="[ERRO ABSOLUTO Q16] ",ltol[]="[TOLERANCIA Q16] ",lc[]="[PONTOS FIXOS ENCONTRADOS] ",lmin[]="[FAIXA FIXA MIN Q16] ",lmax[]="[FAIXA FIXA MAX Q16] ",li[]="[PRIMEIRA ITERACAO FIXA] ",lv[]="[VALOR FIXO ALCANCADO Q16] ";
static const char ok[]="[STATUS] Convergencia dentro da tolerancia Q16.\n",gap[]="[STATUS] TOKEN_VAZIO: tolerancia ainda nao atingida.\n",band[]="[STATUS] TOKEN_VAZIO: faixa fixa nao encontrada.\n";
s32 r48=fraf_iterate(TOKEN_VAZIO,48u),r96=fraf_iterate(TOKEN_VAZIO,FRAF_ITERATIONS),err=bare_abs_diff(r96,OMEGA_TARGET),fmin=0,fmax=0,fval=0; u32 fcnt=fraf_find_fixed_band(OMEGA_TARGET,FIXED_SCAN_RADIUS,&fmin,&fmax),first=fraf_first_fixed_iteration(TOKEN_VAZIO,256u,&fval);
bare_write(msg_init,ARRAY_LEN_LITERAL(msg_init)); bare_write(msg_mode,ARRAY_LEN_LITERAL(msg_mode)); print_q16_line(l48,ARRAY_LEN_LITERAL(l48),r48); print_q16_line(l96,ARRAY_LEN_LITERAL(l96),r96); print_q16_line(lt,ARRAY_LEN_LITERAL(lt),OMEGA_TARGET); print_q16_line(le,ARRAY_LEN_LITERAL(le),err); print_q16_line(ltol,ARRAY_LEN_LITERAL(ltol),OMEGA_TOLERANCE_Q16); print_integer_line(lc,ARRAY_LEN_LITERAL(lc),(s32)fcnt); if(fcnt>0u){ print_q16_line(lmin,ARRAY_LEN_LITERAL(lmin),fmin); print_q16_line(lmax,ARRAY_LEN_LITERAL(lmax),fmax); }else bare_write(band,ARRAY_LEN_LITERAL(band)); print_integer_line(li,ARRAY_LEN_LITERAL(li),(s32)first); if(first>0u)print_q16_line(lv,ARRAY_LEN_LITERAL(lv),fval); if(err<=OMEGA_TOLERANCE_Q16&&fcnt==7u&&first>0u){ bare_write(ok,ARRAY_LEN_LITERAL(ok)); bare_exit(0); } bare_write(gap,ARRAY_LEN_LITERAL(gap)); bare_exit(1); }
EOF_C
SHA_SRC_H=$(sha256sum rafaelia.h|awk '{print $1}'); SHA_SRC_MATH=$(sha256sum fraf_math.c|awk '{print $1}'); SHA_SRC_MAIN=$(sha256sum main.c|awk '{print $1}'); SHA_BUILD_SCRIPT=$(sha256sum "$0"|awk '{print $1}')
COMMON_CFLAGS="-O3 -marm -march=armv7-a -ffreestanding -fno-builtin -fno-stack-protector -fno-unwind-tables -fno-asynchronous-unwind-tables -ffunction-sections -fdata-sections -fno-pic -fno-pie"
CLANG_VERSION=$(clang --version|awk 'NR==1{print;exit}'); LLD_VERSION=$(ld.lld --version|awk 'NR==1{print;exit}')
echo "[*] Compilando objetos..."
# shellcheck disable=SC2086
clang $COMMON_CFLAGS -c main.c -o main.o
# shellcheck disable=SC2086
clang $COMMON_CFLAGS -c fraf_math.c -o fraf_math.o
echo "[*] Ligando com ld.lld (estatico, sem loader)..."
ld.lld -m armelf_linux_eabi -static -e _start --gc-sections --build-id=none -z noexecstack -o rafaelia_node main.o fraf_math.o
chmod 700 rafaelia_node
ELF_CONTRACT_STATUS=0
echo "[*] Validando contrato ELF loaderless..."
readelf -l rafaelia_node|grep -q INTERP&&{ echo "[FALHA] PT_INTERP."; ELF_CONTRACT_STATUS=1; }||echo "[OK] Nenhum PT_INTERP."
readelf -l rafaelia_node|grep -q DYNAMIC&&{ echo "[FALHA] PT_DYNAMIC."; ELF_CONTRACT_STATUS=1; }||echo "[OK] Nenhum PT_DYNAMIC."
readelf -d rafaelia_node 2>&1|grep -q NEEDED&&{ echo "[FALHA] DT_NEEDED."; ELF_CONTRACT_STATUS=1; }||echo "[OK] Nenhuma DT_NEEDED."
if readelf -Ws rafaelia_node|awk '$7=="UND"&&$8!=""{f=1}END{exit f?0:1}'; then echo "[FALHA] Simbolos indefinidos."; ELF_CONTRACT_STATUS=1; else echo "[OK] Nenhum simbolo externo indefinido."; fi
ELF_TYPE=$(readelf -h rafaelia_node|awk '/Type:/{print $2;exit}'); [ "$ELF_TYPE" = EXEC ]&&echo "[OK] ELF tipo EXEC."||{ echo "[FALHA] Tipo ELF: $ELF_TYPE"; ELF_CONTRACT_STATUS=1; }
readelf -r rafaelia_node|grep -q 'There are no relocations'&&echo "[OK] Nenhuma relocacao dinamica."||{ echo "[FALHA] Relocacoes presentes."; ELF_CONTRACT_STATUS=1; }
[ "$ELF_CONTRACT_STATUS" -eq 0 ]||exit "$ELF_CONTRACT_STATUS"
set +e; ./rafaelia_node > original.output.txt 2>&1; RUN_STATUS=$?; set -e; cat original.output.txt
cp rafaelia_node rafaelia_node.stripped; "$STRIP_TOOL" --strip-all rafaelia_node.stripped; chmod 700 rafaelia_node.stripped
set +e; ./rafaelia_node.stripped > stripped.output.txt 2>&1; STRIP_STATUS=$?; set -e; cat stripped.output.txt
if cmp -s original.output.txt stripped.output.txt; then OUTPUT_STATUS=0; echo "[OK] Saidas identicas (byte a byte)."; else OUTPUT_STATUS=1; diff -u original.output.txt stripped.output.txt||true; fi
[ "$RUN_STATUS" -eq 0 ]||exit "$RUN_STATUS"; [ "$STRIP_STATUS" -eq 0 ]||exit "$STRIP_STATUS"; [ "$OUTPUT_STATUS" -eq 0 ]||exit "$OUTPUT_STATUS"
ORIG_SIZE=$(wc -c < rafaelia_node); STRIP_SIZE=$(wc -c < rafaelia_node.stripped); ORIG_SHA=$(sha256sum rafaelia_node|awk '{print $1}'); STRIP_SHA=$(sha256sum rafaelia_node.stripped|awk '{print $1}')
cat <<MANIFEST > rafaelia_q16_artifacts.manifest
schema=rafaelia.q16.dual-artifact.v2
architecture=$(uname -m)
compiler.version=$CLANG_VERSION
linker.version=$LLD_VERSION
build.flags=$COMMON_CFLAGS
build.script.sha256=$SHA_BUILD_SCRIPT
source.rafaelia_h.sha256=$SHA_SRC_H
source.fraf_math_c.sha256=$SHA_SRC_MATH
source.main_c.sha256=$SHA_SRC_MAIN
original.name=rafaelia_node
original.size_bytes=$ORIG_SIZE
original.sha256=$ORIG_SHA
original.exit_status=$RUN_STATUS
stripped.name=rafaelia_node.stripped
stripped.size_bytes=$STRIP_SIZE
stripped.sha256=$STRIP_SHA
stripped.exit_status=$STRIP_STATUS
reduction_bytes=$((ORIG_SIZE-STRIP_SIZE))
outputs_identical=true
contract_passed=true
elf.type=EXEC
elf.interp=false
elf.dynamic=false
elf.dt_needed_count=0
elf.undefined_symbol_count=0
elf.relocation_count=0
MANIFEST
cat rafaelia_q16_artifacts.manifest
echo "[OK] Contrato duplo satisfeito - RAFAELIA Q16 executavel, estatico, loaderless."
