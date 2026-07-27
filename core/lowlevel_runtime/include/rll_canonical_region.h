#ifndef RLL_CANONICAL_REGION_H
#define RLL_CANONICAL_REGION_H

#ifdef __cplusplus
extern "C" {
#endif

/* Freestanding ABI: no stdint.h, libc, heap, file I/O or floating point. */
typedef unsigned char rllc_u8;
typedef unsigned int rllc_u32;
typedef unsigned long long rllc_u64;
typedef long long rllc_i64;

#define RLLC_SCHEMA_V1 0x524C4C31u /* "RLL1" */
#define RLLC_Q32_ONE 4294967296ll
#define RLLC_REQUIRED_DATASETS_MASK 0x0Fu
#define RLLC_SHA256_BYTES 32u
#define RLLC_DATASET_SLOTS 8u

/* Fail-closed status values. TOKEN_VAZIO is not success and is not zero data. */
enum rllc_status {
    RLLC_OK = 0,
    RLLC_TOKEN_VAZIO = 1,
    RLLC_E_NULL = -1,
    RLLC_E_SCHEMA = -2,
    RLLC_E_FORMAT = -3,
    RLLC_E_RANGE = -4,
    RLLC_E_PROVENANCE = -5,
    RLLC_E_SYNTHETIC = -6,
    RLLC_E_UNCERTAINTY = -7,
    RLLC_E_CLAIM = -8,
    RLLC_E_CAPACITY = -9,
    RLLC_E_COVARIANCE = -10
};

enum rllc_dataset {
    RLLC_DS_NONE = 0,
    RLLC_DS_HZ = 1,
    RLLC_DS_BAO = 2,
    RLLC_DS_FSIGMA8 = 3,
    RLLC_DS_CMB_SHIFT = 4,
    RLLC_DS_ADAPTER_LOCAL_PHYSICS = 5
};

enum rllc_observable {
    RLLC_OBS_NONE = 0,
    RLLC_OBS_H_KM_S_MPC = 1,
    RLLC_OBS_DV_OVER_RD = 2,
    RLLC_OBS_DM_OVER_RD = 3,
    RLLC_OBS_DH_OVER_RD = 4,
    RLLC_OBS_FSIGMA8 = 5,
    RLLC_OBS_CMB_R = 6,
    RLLC_OBS_CMB_LA = 7,
    RLLC_OBS_CMB_OB_H2 = 8,
    RLLC_OBS_ADAPTER_SCALAR = 9
};

enum rllc_unit {
    RLLC_UNIT_NONE = 0,
    RLLC_UNIT_DIMENSIONLESS = 1,
    RLLC_UNIT_KM_S_MPC = 2,
    RLLC_UNIT_SI_DECLARED_BY_ADAPTER = 3
};

enum rllc_flags {
    RLLC_F_REAL = 1u << 0,
    RLLC_F_PROVENANCE_VERIFIED = 1u << 1,
    RLLC_F_CLAIM_BLOCKED = 1u << 2,
    RLLC_F_SYNTHETIC = 1u << 3,
    RLLC_F_COVARIANCE_PRESENT = 1u << 4,
    RLLC_F_LOCAL_CONTEXT_ONLY = 1u << 5
};

enum rllc_violation {
    RLLC_V_NONE = 0u,
    RLLC_V_SCHEMA = 1u << 0,
    RLLC_V_FORMAT = 1u << 1,
    RLLC_V_RANGE = 1u << 2,
    RLLC_V_PROVENANCE = 1u << 3,
    RLLC_V_SYNTHETIC = 1u << 4,
    RLLC_V_UNCERTAINTY = 1u << 5,
    RLLC_V_CLAIM = 1u << 6,
    RLLC_V_COVARIANCE = 1u << 7
};

typedef struct rllc_source {
    rllc_u8 sha256[RLLC_SHA256_BYTES];
    rllc_u64 byte_count;
    rllc_u64 source_name_fnv1a64;
    rllc_u32 source_name_crc32;
} rllc_source;

typedef struct rllc_observation {
    rllc_u32 schema;
    rllc_u32 dataset;
    rllc_u32 observable;
    rllc_u32 unit;
    rllc_u32 flags;
    rllc_u32 reserved;
    rllc_u64 sequence;
    rllc_i64 x_q32;
    rllc_i64 value_q32;
    rllc_i64 sigma_q32;
    rllc_source source;
} rllc_observation;

typedef struct rllc_state {
    rllc_u32 schema;
    rllc_u32 claim_allowed;
    rllc_u32 violation_mask;
    rllc_u32 real_dataset_mask;
    rllc_u64 accepted;
    rllc_u64 rejected;
    rllc_u64 token_vazio_count;
    rllc_u64 dataset_counts[RLLC_DATASET_SLOTS];
    rllc_u64 rolling_fnv1a64;
    rllc_u32 rolling_crc32;
    rllc_u32 cmb_covariance_present;
    rllc_i64 cmb_covariance_q32[9];
} rllc_state;

typedef struct rllc_receipt {
    rllc_u32 schema;
    rllc_u32 status;
    rllc_u32 claim_allowed;
    rllc_u32 violation_mask;
    rllc_u32 real_dataset_mask;
    rllc_u32 required_dataset_mask;
    rllc_u64 accepted;
    rllc_u64 rejected;
    rllc_u64 hz_rows;
    rllc_u64 bao_rows;
    rllc_u64 fsigma8_rows;
    rllc_u64 cmb_rows;
    rllc_u64 rolling_fnv1a64;
    rllc_u32 rolling_crc32;
    rllc_u32 covariance_present;
} rllc_receipt;

void rllc_init(rllc_state *state);
int rllc_sha256_from_hex(const rllc_u8 *hex64, rllc_u8 out[32]);
int rllc_parse_q32(const rllc_u8 *text, rllc_u64 len, rllc_i64 *out_q32);
int rllc_ingest(rllc_state *state, const rllc_observation *obs);

int rllc_parse_hz_csv(
    rllc_state *state, const rllc_u8 *data, rllc_u64 len,
    const rllc_u8 sha256[32]);
int rllc_parse_bao_csv(
    rllc_state *state, const rllc_u8 *data, rllc_u64 len,
    const rllc_u8 sha256[32]);
int rllc_parse_fsigma8_csv(
    rllc_state *state, const rllc_u8 *data, rllc_u64 len,
    const rllc_u8 sha256[32]);
int rllc_parse_cmb_shift_json(
    rllc_state *state, const rllc_u8 *data, rllc_u64 len,
    const rllc_u8 sha256[32]);

/* Adapter bridge for geophysical/sensor receipts already validated upstream. */
int rllc_ingest_local_adapter_scalar(
    rllc_state *state,
    rllc_u64 sequence,
    rllc_i64 time_or_axis_q32,
    rllc_i64 value_q32,
    rllc_i64 sigma_q32,
    const rllc_u8 sha256[32],
    rllc_u64 adapter_name_fnv1a64,
    rllc_u32 adapter_name_crc32);

int rllc_finalize(const rllc_state *state, rllc_receipt *receipt);

#ifdef __cplusplus
}
#endif

#endif
