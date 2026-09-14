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
