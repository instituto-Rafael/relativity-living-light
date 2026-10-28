#ifndef RLL_GEOCYCLE_FALSIFIER_H
#define RLL_GEOCYCLE_FALSIFIER_H
/* Freestanding C11 deterministic screening ONLY, not a scientific periodogram.
   A 51-year series CANNOT validate a 51-year period. */
typedef unsigned char rllc_u8;
typedef unsigned short rllc_u16;
typedef unsigned int rllc_u32;
typedef signed short rllc_i16;
_Static_assert(sizeof(rllc_u8)==1 && sizeof(rllc_u16)==2 &&
               sizeof(rllc_u32)==4 && sizeof(rllc_i16)==2, "ABI");
#define RLLC_MAX_YEARS 256u
#define RLLC_OK 0
#define RLLC_INSUFFICIENT_SPAN 1
#define RLLC_INSUFFICIENT_PAIRS 2
#define RLLC_UNIDENTIFIABLE_CONSTANT 3
#define RLLC_INVALID -1
typedef struct {
  rllc_u16 first_year_utc;
  rllc_u16 count;
  rllc_i16 normalized[RLLC_MAX_YEARS];  /* explicitly normalized [-1000, 1000] */
  rllc_u8 valid[RLLC_MAX_YEARS];         /* 0 means missing; NOT measured zero */
} rllc_annual;
typedef struct {
  rllc_u16 candidate_period_years;
  rllc_u16 pair_count;
  rllc_u32 lag_mean_absolute_difference_milli; /* diagnostic, not a p-value */
  rllc_u8 is_verified_period; /* always zero */
  rllc_u8 is_earthquake_warning; /* always zero */
  rllc_u8 is_weather_warning; /* always zero */
} rllc_screen;
int rllc_screen_lag(const rllc_annual *a, rllc_u16 period_years,
                    rllc_screen *out);
#endif
