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
