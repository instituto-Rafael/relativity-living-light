#ifndef RLL_CLIMATE_30MIN_H
#define RLL_CLIMATE_30MIN_H
/* Pure freestanding C11; hosted ingestion/JSON/radar decoding are out of scope. */
typedef unsigned char rll_u8;
typedef unsigned short rll_u16;
typedef unsigned int rll_u32;
typedef signed int rll_i32;
_Static_assert(sizeof(rll_u8)==1 && sizeof(rll_u16)==2 && sizeof(rll_u32)==4 && sizeof(rll_i32)==4,"RLL requires 8/16/32-bit ABI");
#define RLL30_MAX_SAMPLES 8u
#define RLL30_RADAR 1u
#define RLL30_TEC 2u
#define RLL30_KP 4u
#define RLL30_OK 0
#define RLL30_MISSING 1
#define RLL30_INVALID -1
/* TEC residual is in centi-TECU, relative to a separately verified baseline.
   Radar rotation is a UNIT-LESS, pre-normalized 0..1000 diagnostic, not Doppler shear.
   Kp in deci-units; these experimental thresholds are NOT calibrated. */
typedef struct {
    rll_i32 minute_utc;
    rll_u16 radar_norm_1000;
    rll_i32 tec_residual_centi_tecu;
    rll_u8 kp_deci;
    rll_u8 valid_mask;
} rll30_sample;
typedef struct {
    rll_i32 issue_minute_utc;
    rll_u8 count;
    rll30_sample sample[RLL30_MAX_SAMPLES]; /* chronological, oldest first */
} rll30_window;
typedef struct {
    rll_u8 radar_only_diagnostic;
    rll_u8 tec_perturbation_diagnostic;
    rll_u8 combined_diagnostic;
    rll_u8 geomagnetic_confounded;
    rll_u8 available_30min;
    rll_u8 is_operational_warning; /* ALWAYS 0 by contract */
} rll30_result;
/* No event labels enter evaluation. Missing is NEVER encoded as zero. */
int rll30_evaluate(const rll30_window *w, rll30_result *r);
#endif
