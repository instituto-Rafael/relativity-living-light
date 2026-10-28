#ifndef RLL_CLIMATE_8X8_H
#define RLL_CLIMATE_8X8_H
/* 8 sectors, 1 gate + 7 physical entries per sector; freestanding C11. */
typedef signed int rll8_i32;
typedef unsigned char rll8_u8;
typedef unsigned int rll8_u32;
_Static_assert(sizeof(rll8_i32)==4 && sizeof(rll8_u8)==1 && sizeof(rll8_u32)==4,"32-bit ABI required");
#define RLL8_OK 0
#define RLL8_INCOMPLETE 1
#define RLL8_INVALID -1
typedef struct {
    rll8_i32 q16[8][8]; /* [sector][row]; row0 gate, rows1-7 physical */
    rll8_u8 gate_valid_mask; /* bit per sector */
    rll8_u8 physical_valid_mask[8]; /* bits0..6 for rows1..7 */
} rll8_matrix;
typedef struct {
    rll8_u8 valid_gates;
    rll8_u8 valid_physical;
    rll8_u8 missing_physical;
    rll8_u8 above_three_sigma; /* candidate standardized anomalies, NOT warnings */
    rll8_u8 missing_sector_mask;
    rll8_u8 is_operational_warning; /* ALWAYS ZERO */
} rll8_audit;
int rll8_validate(const rll8_matrix *m, rll8_audit *out);
#endif
