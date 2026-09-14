#!/bin/sh
# RAF_VERBEYES freestanding YML path scanner — x86_64 Linux
# build_raf_verbeyes.sh
#
# Gera um ELF64 freestanding sem libc, sem malloc, sem heap, sem GC,
# sem dependencias internas ou externas. Apenas syscalls Linux diretas
# via inline ASM. Aritmetica branchless onde aplicavel.
#
# Syscalls usados: SYS_write(1) SYS_close(3) SYS_openat(257)
#                  SYS_getdents64(217) SYS_exit(60)
#
# O scanner analisa TODOS os caminhos .yml em:
#   RAF_VERBEYES/IN  RAF_VERBEYES/PROCESSO
#   RAF_VERBEYES/DONE  RAF_VERBEYES/ESPIRAL
# antes de reportar o estado do pipeline.
#
# Executar a partir de: native/raf_verbeyes/
# O binario deve ser invocado a partir da raiz do repositorio.
set -eu
export LC_ALL=C

need(){ command -v "$1" >/dev/null 2>&1 || { printf '[FALHA] Ferramenta ausente: %s\n' "$1" >&2; exit 127; }; }
for _t in readelf sha256sum awk wc; do need "$_t"; done

# Detect clang (accepts versioned fallbacks: clang-18, clang-17, ...)
if   command -v clang    >/dev/null 2>&1; then CLANG=clang
elif command -v clang-18 >/dev/null 2>&1; then CLANG=clang-18
elif command -v clang-17 >/dev/null 2>&1; then CLANG=clang-17
elif command -v clang-16 >/dev/null 2>&1; then CLANG=clang-16
else echo "[FALHA] clang nao encontrado." >&2; exit 127; fi

# Detect ld.lld (accepts versioned fallbacks: ld.lld-18, ld.lld-17, ...)
if   command -v ld.lld    >/dev/null 2>&1; then LLD=ld.lld
elif command -v ld.lld-18 >/dev/null 2>&1; then LLD=ld.lld-18
elif command -v ld.lld-17 >/dev/null 2>&1; then LLD=ld.lld-17
elif command -v ld.lld-16 >/dev/null 2>&1; then LLD=ld.lld-16
else echo "[FALHA] ld.lld nao encontrado." >&2; exit 127; fi

if   command -v llvm-strip >/dev/null 2>&1; then STRIP_TOOL=llvm-strip
elif command -v strip      >/dev/null 2>&1; then STRIP_TOOL=strip
else echo "[FALHA] llvm-strip ou strip necessario." >&2; exit 127; fi

echo "[*] Gerando RAF_VERBEYES scanner freestanding (x86_64)..."

# ---- raf_verbeyes.h --------------------------------------------------------
cat <<'EOFH' > raf_verbeyes.h
/* RAF_VERBEYES — freestanding YML path scanner
 * Tipos, constantes e declaracoes publicas.
 * Sem libc. Sem malloc. Sem heap. Sem GC. Apenas void e syscalls. */
#ifndef RAF_VERBEYES_H
#define RAF_VERBEYES_H

typedef unsigned int       u32;
typedef unsigned long long u64;
typedef long long          s64;
typedef unsigned short     u16;
typedef unsigned char      u8;

/* Syscall numbers — x86_64 Linux */
#define SYS_WRITE       1ULL
#define SYS_CLOSE       3ULL
#define SYS_OPENAT    257ULL
#define SYS_GETDENTS64 217ULL
#define SYS_EXIT       60ULL

/* Linux open/dirent constants */
#define AT_FDCWD       (-100LL)
#define O_RDONLY        0
#define O_DIRECTORY     0200000
#define DT_REG          8u

/* Scanner constants */
#define DIRENT_BUF      4096u
#define STAGE_COUNT     4u

/* Compile-time string byte length (excludes null terminator) */
#define SLEN(x) ((u32)(sizeof(x) - 1u))

/* Public interface */
void rvb_write(const char *s, u32 n);
s64  rvb_opendir(const char *path);
s64  rvb_getdents(s64 fd, void *buf, u32 sz);
void rvb_close(s64 fd);
__attribute__((noreturn)) void rvb_exit(int code);
u32  rvb_scan_stage(const char *path, u32 plen);

#endif /* RAF_VERBEYES_H */
EOFH

# ---- raf_scanner.c ---------------------------------------------------------
cat <<'EOFS' > raf_scanner.c
/* RAF_VERBEYES — raf_scanner.c
 * Varredura de diretorios e analise de caminhos YML.
 * Sem libc. Sem malloc. Buffer estatico em BSS (sem heap).
 *
 * linux_dirent64 offsets (x86_64):
 *   offset  0: d_ino    u64
 *   offset  8: d_off    s64
 *   offset 16: d_reclen u16
 *   offset 18: d_type   u8
 *   offset 19: d_name   char[] (null-terminated)
 */
#include "raf_verbeyes.h"

/* Buffer estatico — zero heap, zero malloc */
static u8 _rvb_dbuf[DIRENT_BUF];

/* Acesso bruto aos campos dirent64 por offset fixo */
#define DENT_RECLEN(p) (*(const u16 *)((const u8 *)(p) + 16u))
#define DENT_TYPE(p)   (*((const u8 *)(p) + 18u))
#define DENT_NAME(p)   ((const char *)((const u8 *)(p) + 19u))

/* Comprimento de string sem libc */
static u32 rvb_strlen(const char *s){
    u32 n = 0u;
    while(s[n]) n++;
    return n;
}

/* Verifica sufixo ".yml" (4 bytes finais).
 * Estrutura: guarda de comprimento (1 branch, necessario para evitar OOB),
 * seguida de comparacao branchless via OR-reduction dos 4 mismatches;
 * d==0 significa match exato — nenhum branch apos a guarda. */
static u32 rvb_ends_yml(const char *name, u32 len){
    /* guarda de comprimento: necessaria para acesso seguro aos 4 bytes finais */
    if(len < 4u) return 0u;
    /* branchless: OR de todos os mismatches; zero => ".yml" exato */
    u32 d = ((u32)(u8)name[len - 4u] ^ (u32)'.')
          | ((u32)(u8)name[len - 3u] ^ (u32)'y')
          | ((u32)(u8)name[len - 2u] ^ (u32)'m')
          | ((u32)(u8)name[len - 1u] ^ (u32)'l');
    return (u32)(d == 0u);
}

/* Varre um diretorio de estagio, imprime todos os .yml encontrados
 * e retorna a contagem. */
u32 rvb_scan_stage(const char *path, u32 plen){
    static const char _err[] = "[ERR] openat falhou: ";
    s64 fd;
    s64 n;
    u32 off, count, nlen;
    u8  dtype;
    u16 reclen;
    const char *name;

    fd = rvb_opendir(path);
    if(fd < 0){
        rvb_write(_err, SLEN(_err));
        rvb_write(path, plen);
        rvb_write("\n", 1u);
        return 0u;
    }

    count = 0u;
    for(;;){
        n = rvb_getdents(fd, _rvb_dbuf, DIRENT_BUF);
        if(n <= 0) break;
        off = 0u;
        while(off < (u32)n){
            reclen = DENT_RECLEN(_rvb_dbuf + off);
            dtype  = DENT_TYPE(_rvb_dbuf + off);
            name   = DENT_NAME(_rvb_dbuf + off);
            nlen   = rvb_strlen(name);
            if(dtype == DT_REG && rvb_ends_yml(name, nlen)){
                rvb_write("    ", 4u);
                rvb_write(path, plen);
                rvb_write("/", 1u);
                rvb_write(name, nlen);
                rvb_write("\n", 1u);
                count++;
            }
            off += (u32)reclen;
        }
    }

    rvb_close(fd);
    return count;
}
EOFS

# ---- main.c ----------------------------------------------------------------
cat <<'EOFM' > main.c
/* RAF_VERBEYES — main.c
 * Camada de syscalls x86_64 Linux e ponto de entrada _start.
 * Sem libc. Sem malloc. Sem heap. Sem GC. Sem PT_INTERP.
 * Convencao de syscall x86_64:
 *   nr->rax  a->rdi  b->rsi  c->rdx  d->r10  e->r8  f->r9
 *   retorno: rax  (rcx e r11 destruidos pelo syscall)
 */
#include "raf_verbeyes.h"

/* ---- Primitivas de syscall (inline ASM) ---- */

static s64 sc3(u64 nr, s64 a, s64 b, s64 c){
    s64 r;
    __asm__ volatile("syscall"
        : "=a"(r)
        : "0"(nr), "D"(a), "S"(b), "d"(c)
        : "rcx", "r11", "memory");
    return r;
}

static s64 sc4(u64 nr, s64 a, s64 b, s64 c, s64 d){
    s64 r;
    register s64 r10 __asm__("r10") = d;
    __asm__ volatile("syscall"
        : "=a"(r)
        : "0"(nr), "D"(a), "S"(b), "d"(c), "r"(r10)
        : "rcx", "r11", "memory");
    return r;
}

/* ---- Interface publica (declarada em raf_verbeyes.h) ---- */

void rvb_write(const char *s, u32 n){
    const char *p = s;
    u32 rem = n;
    while(rem){
        s64 w = sc3(SYS_WRITE, 1LL, (s64)p, (s64)rem);
        if(w <= 0) return;
        p   += (u32)w;
        rem -= (u32)w;
    }
}

s64 rvb_opendir(const char *path){
    return sc4(SYS_OPENAT, AT_FDCWD, (s64)path,
               (s64)(O_RDONLY | O_DIRECTORY), 0LL);
}

s64 rvb_getdents(s64 fd, void *buf, u32 sz){
    return sc3(SYS_GETDENTS64, fd, (s64)buf, (s64)sz);
}

void rvb_close(s64 fd){
    sc3(SYS_CLOSE, fd, 0LL, 0LL);
}

__attribute__((noreturn)) void rvb_exit(int code){
    sc3(SYS_EXIT, (s64)code, 0LL, 0LL);
    __builtin_unreachable();
}

/* ---- Formatacao de inteiro sem libc ---- */
static void write_u32(u32 v){
    char b[10];
    u32 pos = 10u, val = v;
    do {
        u32 q = val / 10u;
        b[--pos] = (char)('0' + (val - q * 10u));
        val = q;
    } while(val);
    rvb_write(b + pos, 10u - pos);
}

/* ---- Relatorio de estagio ---- */
static void stage_report(const char *label, u32 llen, u32 count){
    static const char _lb[] = "  [";
    static const char _rb[] = "]  : ";
    static const char _ys[] = " yml\n";
    rvb_write(_lb,    SLEN(_lb));
    rvb_write(label,  llen);
    rvb_write(_rb,    SLEN(_rb));
    write_u32(count);
    rvb_write(_ys,    SLEN(_ys));
}

/* ---- Ponto de entrada freestanding ---- */
__attribute__((noreturn, used, visibility("default"))) void _start(void){

    /* Caminhos dos estagios — relativos a raiz do repositorio */
    static const char P_IN[]      = "RAF_VERBEYES/IN";
    static const char P_PROC[]    = "RAF_VERBEYES/PROCESSO";
    static const char P_DONE[]    = "RAF_VERBEYES/DONE";
    static const char P_ESP[]     = "RAF_VERBEYES/ESPIRAL";

    /* Labels */
    static const char L_IN[]      = "IN";
    static const char L_PROC[]    = "PROCESSO";
    static const char L_DONE[]    = "DONE";
    static const char L_ESP[]     = "ESPIRAL";

    /* Cabecalho e separador */
    static const char HDR[]  =
        "\n[RAF_VERBEYES] YML Path Scanner - freestanding x86_64\n";
    static const char SEP[]  =
        "=======================================================\n";
    static const char SFND[] = "  Paths encontrados:\n";
    static const char STOT[] = "  TOTAL          : ";
    static const char SYML[] = " yml\n";
    static const char SOK[]  =
        "[OK] PATH_SCAN concluido - pipeline pronto.\n";

    u32 c0, c1, c2, c3;

    rvb_write(HDR,  SLEN(HDR));
    rvb_write(SEP,  SLEN(SEP));
    rvb_write(SFND, SLEN(SFND));

    /* Fase 1: varredura de todos os caminhos YML */
    c0 = rvb_scan_stage(P_IN,   SLEN(P_IN));
    c1 = rvb_scan_stage(P_PROC, SLEN(P_PROC));
    c2 = rvb_scan_stage(P_DONE, SLEN(P_DONE));
    c3 = rvb_scan_stage(P_ESP,  SLEN(P_ESP));

    /* Fase 2: relatorio de estado do pipeline */
    rvb_write(SEP,  SLEN(SEP));
    stage_report(L_IN,   SLEN(L_IN),   c0);
    stage_report(L_PROC, SLEN(L_PROC), c1);
    stage_report(L_DONE, SLEN(L_DONE), c2);
    stage_report(L_ESP,  SLEN(L_ESP),  c3);

    rvb_write(STOT, SLEN(STOT));
    write_u32(c0 + c1 + c2 + c3);
    rvb_write(SYML, SLEN(SYML));
    rvb_write(SOK,  SLEN(SOK));

    rvb_exit(0);
}
EOFM

# ---- Hashes das fontes ----
SHA_H=$(sha256sum raf_verbeyes.h | awk '{print $1}')
SHA_S=$(sha256sum raf_scanner.c  | awk '{print $1}')
SHA_M=$(sha256sum main.c         | awk '{print $1}')
SHA_SCRIPT=$(sha256sum "$0"      | awk '{print $1}')

# CFLAGS: multiplas flags separadas por espaco.
# A expansao sem aspas abaixo ($CFLAGS) e INTENCIONAL: queremos
# word-splitting para que cada flag chegue como argumento separado
# ao compilador. Nao altere para "$CFLAGS".
# shellcheck disable=SC2089
CFLAGS="-O2 -m64 -march=x86-64 -ffreestanding -fno-builtin -fno-stack-protector \
-fno-unwind-tables -fno-asynchronous-unwind-tables \
-ffunction-sections -fdata-sections -fno-pic -fno-pie"

CLANG_VER=$("$CLANG" --version | awk 'NR==1{print;exit}')
LLD_VER=$("$LLD" --version | awk 'NR==1{print;exit}')

echo "[*] Compilando objetos..."
# shellcheck disable=SC2086,SC2090
"$CLANG" $CFLAGS -c raf_scanner.c -o raf_scanner.o
# shellcheck disable=SC2086,SC2090
"$CLANG" $CFLAGS -c main.c        -o main.o

echo "[*] Ligando (estatico, sem loader)..."
"$LLD" -m elf_x86_64 -static -e _start \
    --gc-sections --build-id=none -z noexecstack \
    -o raf_verbeyes_scanner main.o raf_scanner.o

chmod 700 raf_verbeyes_scanner

# ---- Validacao do contrato ELF loaderless ----
ELF_STATUS=0
echo "[*] Validando contrato ELF loaderless..."

readelf -l raf_verbeyes_scanner | grep -q INTERP \
    && { echo "[FALHA] PT_INTERP presente."; ELF_STATUS=1; } \
    || echo "[OK] Nenhum PT_INTERP."

readelf -l raf_verbeyes_scanner | grep -q DYNAMIC \
    && { echo "[FALHA] PT_DYNAMIC presente."; ELF_STATUS=1; } \
    || echo "[OK] Nenhum PT_DYNAMIC."

readelf -d raf_verbeyes_scanner 2>&1 | grep -q NEEDED \
    && { echo "[FALHA] DT_NEEDED presente."; ELF_STATUS=1; } \
    || echo "[OK] Nenhuma DT_NEEDED."

if readelf -Ws raf_verbeyes_scanner | awk '$7=="UND"&&$8!=""{f=1}END{exit f?0:1}'; then
    echo "[FALHA] Simbolos externos indefinidos."; ELF_STATUS=1
else
    echo "[OK] Nenhum simbolo externo indefinido."
fi

ELF_TYPE=$(readelf -h raf_verbeyes_scanner | awk '/Type:/{print $2;exit}')
[ "$ELF_TYPE" = "EXEC" ] \
    && echo "[OK] ELF tipo EXEC." \
    || { echo "[FALHA] Tipo ELF: $ELF_TYPE"; ELF_STATUS=1; }

[ "$ELF_STATUS" -eq 0 ] || exit "$ELF_STATUS"

# ---- Execucao do scanner a partir da raiz do repositorio ----
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
echo "[*] Executando scanner em: $REPO_ROOT"
cd "$REPO_ROOT"
set +e
"$SCRIPT_DIR/raf_verbeyes_scanner"
RUN_STATUS=$?
set -e
cd "$SCRIPT_DIR"

# ---- Tamanho e hash do binario ----
BIN_SIZE=$(wc -c < raf_verbeyes_scanner)
BIN_SHA=$(sha256sum raf_verbeyes_scanner | awk '{print $1}')

# ---- Manifesto de artefato ----
cat <<MANIFEST > raf_verbeyes_scanner.manifest
schema=raf.verbeyes.scanner.v1
architecture=$(uname -m)
compiler.version=$CLANG_VER
linker.version=$LLD_VER
build.flags=$CFLAGS
build.script.sha256=$SHA_SCRIPT
source.raf_verbeyes_h.sha256=$SHA_H
source.raf_scanner_c.sha256=$SHA_S
source.main_c.sha256=$SHA_M
binary.name=raf_verbeyes_scanner
binary.size_bytes=$BIN_SIZE
binary.sha256=$BIN_SHA
binary.exit_status=$RUN_STATUS
contract.freestanding=true
contract.no_malloc=true
contract.no_heap=true
contract.no_gc=true
contract.no_libc=true
contract.syscalls_only=true
contract.no_interp=true
contract.no_dynamic=true
contract.no_dt_needed=true
contract.no_undef_sym=true
elf.type=EXEC
pipeline.stages=IN,PROCESSO,DONE,ESPIRAL
MANIFEST

cat raf_verbeyes_scanner.manifest
echo ""
[ "$RUN_STATUS" -eq 0 ] \
    && echo "[OK] raf_verbeyes_scanner — freestanding, sem libc, sem malloc, sem heap, sem GC." \
    || { echo "[FALHA] scanner retornou status $RUN_STATUS"; exit "$RUN_STATUS"; }
