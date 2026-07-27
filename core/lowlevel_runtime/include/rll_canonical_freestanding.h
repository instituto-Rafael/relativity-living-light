#ifndef RLL_CANONICAL_FREESTANDING_H
#define RLL_CANONICAL_FREESTANDING_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * RLL canonical freestanding ABI v1
 * - ISO C11 freestanding
 * - no libc, stdlib, stdio, string, math, heap, malloc or GC
 * - deterministic Q16.16 arithmetic
 * - canonical little-endian hashing independent of host padding/endian
 */

typedef unsigned char      rllc_u8;
typedef unsigned short     rllc_u16;
typedef unsigned int       rllc_u32;
typedef unsigned long long rllc_u64;
typedef signed int         rllc_i32;
typedef signed long long   rllc_i64;

_Static_assert(sizeof(rllc_u8)  == 1u, "rllc_u8 width");
_Static_assert(sizeof(rllc_u16) == 2u, "rllc_u16 width");
_Static_assert(sizeof(rllc_u32) == 4u, "rllc_u32 width");
_Static_assert(sizeof(rllc_u64) == 8u, "rllc_u64 width");
_Static_assert(sizeof(rllc_i32) == 4u, "rllc_i32 width");
_Static_assert(sizeof(rllc_i64) == 8u, "rllc_i64 width");

#define RLLC_ABI_VERSION             1u
#define RLLC_Q16_ONE                 65536
#define RLLC_CANONICAL_ROW_COUNT     33u
#define RLLC_CLAIM_ALLOWED_FALSE     0u

#define RLLC_SOURCE_CC_MORESCO_2022  1u
#define RLLC_SOURCE_CC_BAO_BOSS      2u
#define RLLC_SOURCE_BAO_LYA          3u

#define RLLC_BEST_TIE                0u
#define RLLC_BEST_LCDM               1u
#define RLLC_BEST_RLL                2u

#define RLLC_TV_FULL_COVARIANCE      (1u << 0)
#define RLLC_TV_INDEPENDENT_REPL     (1u << 1)
#define RLLC_TV_EXTERNAL_BIN_AUDIT   (1u << 2)

#define RLLC_NUMERIC_INVALID_SAMPLE  (1u << 0)
#define RLLC_NUMERIC_DIV_ZERO        (1u << 1)
#define RLLC_NUMERIC_SATURATED       (1u << 2)
#define RLLC_NUMERIC_NEGATIVE_E2     (1u << 3)

typedef struct rllc_hz_sample_q16 {
    rllc_i32 z_q16;
    rllc_i32 h_obs_q16;
    rllc_i32 sigma_h_q16;
    rllc_u32 source_id;
} rllc_hz_sample_q16;

typedef struct rllc_phase20_params_q16 {
    rllc_i32 h0_q16;
    rllc_i32 omega_m_q16;
    rllc_i32 omega_b_q16;   /* metadata: omega_m already includes baryons */
    rllc_i32 omega_s0_q16;
    rllc_i32 z_t_q16;
    rllc_i32 w_t_q16;
} rllc_phase20_params_q16;

typedef struct rllc_receipt_v1 {
    rllc_u32 abi_version;
    rllc_u32 row_count;
    rllc_u32 valid_count;
    rllc_u32 rejected_count;

    rllc_u32 data_crc32;
    rllc_u32 params_crc32;
    rllc_u64 data_fnv1a64;
    rllc_u64 params_fnv1a64;

    rllc_u32 phase20_summary_crc32;
    rllc_u32 phase20_n_total;
    rllc_i32 phase20_ln_b10_q16;
    rllc_i32 phase20_ln_b10_err_q16;
    rllc_i32 phase20_delta_bic_q16;
    rllc_i32 phase20_os0_upper95_q16;
    rllc_u32 phase20_joint_best_model;

    rllc_u64 chi2_rll_q16;
    rllc_u64 chi2_lcdm_q16;
    rllc_i64 delta_chi2_rll_minus_lcdm_q16;

    rllc_u32 best_model;
    rllc_u32 claim_allowed;
    rllc_u32 token_vazio_mask;
    rllc_u32 numeric_flags;
    rllc_u32 receipt_crc32;
} rllc_receipt_v1;

extern const rllc_hz_sample_q16 rllc_hz_canonical_data[RLLC_CANONICAL_ROW_COUNT];

void rllc_phase20_default_params(rllc_phase20_params_q16 *out);

rllc_i32 rllc_hubble_lcdm_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 *numeric_flags
);

rllc_i32 rllc_hubble_rll_q16(
    rllc_i32 z_q16,
    const rllc_phase20_params_q16 *params,
    rllc_u32 *numeric_flags
);

void rllc_evaluate_canonical_hz(
    const rllc_hz_sample_q16 *samples,
    rllc_u32 count,
    const rllc_phase20_params_q16 *params,
    rllc_receipt_v1 *out
);

rllc_u32 rllc_format_receipt_line(
    const rllc_receipt_v1 *receipt,
    char *out,
    rllc_u32 capacity
);

rllc_i64 rllc_raw_write_stdout(const void *buf, rllc_u64 len);
void rllc_raw_exit(rllc_i32 status);

#ifdef __cplusplus
}
#endif

#endif
