#include "rll_cad.h"
/* Only compile with -target aarch64-none-elf -march=armv8-a+crc; host must probe HWCAP_CRC32. */
#if !defined(__aarch64__) || !defined(__ARM_FEATURE_CRC32)
#error hardware_CRC32_requires_AArch64_feature_and_explicit_dispatch
#endif
r_u32 rll_crc32_hw_capability_required(const r_u8 *p,r_u32 n){
 r_u32 crc=0xffffffffu;
 for(r_u32 i=0;i<n;i++){r_u32 v=(r_u32)p[i];__asm__ volatile("crc32b %w0, %w0, %w1" : "+r"(crc) : "r"(v));}
 return ~crc;
}
