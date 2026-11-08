#ifndef RLL_CAD_V1_H
#define RLL_CAD_V1_H
/* Freestanding, no headers or system calls required by the kernel. */
typedef unsigned int r_u32;
typedef signed int r_i32;
typedef unsigned long long r_u64;
typedef signed long long r_i64;
typedef unsigned char r_u8;
#define R_Q16 65536
#define R_PI_OVER_4_Q16 51472
#define R_CAD_OK 0
#define R_CAD_INVALID_INPUT 1
#define R_CAD_NUMERIC_OVERFLOW 2
#define R_CAD_WARN_YIELD 4
#define R_CAD_WARN_BUCKLING 8
#define R_CAD_WARN_DEFLECTION 16
#define R_CAD_WARN_THERMAL_MODEL 32
#define R_CAD_NOT_CERTIFIED 1
/* Q16.16 units explicitly encoded in field names. */
typedef struct {
 r_i32 span_mm_q16; r_i32 rise_mm_q16;
 r_i32 area_diagonal_mm2_q16; r_i32 area_tie_mm2_q16;
 r_i32 downward_load_kN_q16; r_i32 young_GPa_q16;
 r_i32 yield_MPa_q16; r_i32 deltaT_K_q16;
 r_i32 alpha_micro_per_K; /* integer in 10^-6/K, avoids Q16 resolution loss */
} rll_cad_input;
typedef struct {
 r_i32 diagonal_length_mm_q16, tan_angle_q16;
 r_i32 diagonal_force_kN_q16, tie_force_kN_q16;
 r_i32 diagonal_stress_MPa_q16, tie_stress_MPa_q16;
 r_i32 apex_deflection_mm_q16, thermal_free_span_mm_q16;
 r_i32 buckling_limit_kN_q16, buckling_ratio_q16;
 r_i32 diagonal_diameter_mm_q16, tie_diameter_mm_q16;
 r_u32 flags;
} rll_cad_result;
typedef struct { r_i32 coord_q16[7]; r_u32 sample_index; } rll_t7_state;
/* All functions return 0 for successful bounded evaluation. Does NOT certify a bridge. */
int rll_cad_baseline(rll_cad_input *input);
int rll_cad_evaluate(const rll_cad_input *input, rll_cad_result *output);
int rll_cad_t7_sample(const rll_cad_input *base, r_u32 index, rll_t7_state *state, rll_cad_input *sample);
int rll_cad_emit_svg(const rll_cad_input *input, const rll_cad_result *result, char *dst, r_u32 cap);
r_u32 rll_crc32_sw(const r_u8 *data, r_u32 len);
void rll_add4_scalar(const r_i32 *a,const r_i32 *b,r_i32 *out);
void rll_add4_neon(const r_i32 *a,const r_i32 *b,r_i32 *out);
#endif
