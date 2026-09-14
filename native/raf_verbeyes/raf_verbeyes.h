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
