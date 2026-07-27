#ifndef RLL_HZ_FREESTANDING_H
#define RLL_HZ_FREESTANDING_H

#include "rll_canonical_coupling.h"

#ifdef __cplusplus
extern "C" {
#endif

#define RLL_HZ_SOURCE_CC_MORESCO2022 1u
#define RLL_HZ_SOURCE_CC_BAO_BOSS 2u
#define RLL_HZ_DATASET_FNV1A64 0x7bcbeeaf770538d3ull
#define RLL_HZ_DATASET_CRC32 0xdad619bdu
#define RLL_HZ_DATASET_BYTES 1033ull
#define RLL_HZ_DATASET_ROWS 33u

typedef struct rll_hz_sample_q16 {
    rll_i64 z_q16;
    rll_i64 h_obs_q16;
    rll_i64 sigma_q16;
    rll_u32 source_id;
    rll_u32 sequence_id;
} rll_hz_sample_q16;

typedef struct rll_hz_params_q16 {
    rll_i64 h0_q16;
    rll_i64 omega_m_q16;
    rll_i64 omega_s0_q16;
    rll_i64 z_t_q16;
    rll_i64 w_t_q16;
} rll_hz_params_q16;

typedef struct rll_hz_dual_receipt {
    rll_canonical_receipt lcdm;
    rll_canonical_receipt rll;
    rll_i64 delta_chi2_q16;
    rll_u32 rows;
    rll_u64 dataset_fnv1a64;
    rll_u32 dataset_crc32;
    rll_u32 claim_allowed;
} rll_hz_dual_receipt;

extern const rll_hz_sample_q16 rll_hz_moresco_2022_q16[RLL_HZ_DATASET_ROWS];
extern const rll_u8 rll_hz_moresco_2022_sha256_hex[65];

rll_hz_params_q16 rll_hz_nominal_planck_params_q16(void);
rll_i64 rll_hz_lcdm_q16(rll_i64 z_q16, const rll_hz_params_q16 *params);
rll_i64 rll_hz_rll_q16(rll_i64 z_q16, const rll_hz_params_q16 *params);
rll_hz_dual_receipt rll_hz_run_canonical_q16(
    const rll_hz_sample_q16 *samples,
    rll_u32 count,
    const rll_hz_params_q16 *params,
    rll_u64 dataset_fnv1a64,
    rll_u32 dataset_crc32
);
rll_hz_dual_receipt rll_hz_run_moresco_nominal_q16(void);

#ifdef __cplusplus
}
#endif

#endif
