#ifndef RLL_CANONICAL_REAL_H
#define RLL_CANONICAL_REAL_H

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned char rll_u8;
typedef unsigned int rll_u32;
typedef unsigned long long rll_u64;
typedef long long rll_i64;

enum rll_model_kind {
    RLL_MODEL_LCDM = 1,
    RLL_MODEL_LOGISTIC = 2
};

enum rll_observable_kind {
    RLL_OBS_HZ_KM_S_MPC = 1,
    RLL_OBS_FSIGMA8 = 2,
    RLL_OBS_BAO_DV_OVER_RD = 3,
    RLL_OBS_BAO_DM_OVER_RD = 4,
    RLL_OBS_BAO_DH_OVER_RD = 5,
    RLL_OBS_CMB_R = 6,
    RLL_OBS_CMB_LA = 7,
    RLL_OBS_CMB_OBH2 = 8,
    RLL_OBS_SN_MU = 9
};

enum rll_source_state {
    RLL_SOURCE_LOCAL_HASH_VERIFIED = 1u << 0,
    RLL_SOURCE_REMOTE_SIGNATURE_VERIFIED = 1u << 1,
    RLL_SOURCE_FULL_COVARIANCE = 1u << 2,
    RLL_SOURCE_DIAGONAL_ONLY = 1u << 3,
    RLL_SOURCE_PRIMARY_PARTIAL = 1u << 4
};

enum rll_run_status {
    RLL_RUN_OK = 0u,
    RLL_RUN_BAD_INPUT = 1u << 0,
    RLL_RUN_MODEL_DOMAIN = 1u << 1,
    RLL_RUN_BAD_SIGMA = 1u << 2,
    RLL_RUN_COVARIANCE_SINGULAR = 1u << 3,
    RLL_RUN_NONFINITE = 1u << 4,
    RLL_RUN_SOURCE_UNVERIFIED = 1u << 5
};

typedef struct rll_real_source {
    rll_u32 source_id;
    rll_u32 state_flags;
    const char *dataset_id;
    const char *repo_path;
    const char *local_sha256;
    const char *primary_url;
} rll_real_source;

typedef struct rll_real_point {
    double z;
    double observed;
    double sigma;
    double correlation;
    rll_u32 observable;
    rll_u32 source_id;
    rll_u32 covariance_group;
} rll_real_point;

typedef struct rll_cosmo_params {
    double h0;
    double omega_m;
    double omega_b;
    double omega_r;
    double omega_s0;
    double z_transition;
    double transition_width;
    double sigma8_0;
    double growth_gamma;
    double rd_mpc;
    double rs_star_mpc;
    double sn_magnitude_offset;
    rll_u32 integration_steps;
} rll_cosmo_params;

typedef struct rll_canonical_result {
    double chi2_hz;
    double chi2_growth;
    double chi2_bao;
    double chi2_cmb;
    double chi2_total;
    rll_u32 n_hz;
    rll_u32 n_growth;
    rll_u32 n_bao;
    rll_u32 n_cmb;
    rll_u32 status;
    rll_u32 claim_allowed;
} rll_canonical_result;

extern const rll_real_source rll_canonical_sources[];
extern const rll_u32 rll_canonical_source_count;
extern const rll_real_point rll_real_hz_points[];
extern const rll_u32 rll_real_hz_count;
extern const rll_real_point rll_real_fsigma8_points[];
extern const rll_u32 rll_real_fsigma8_count;
extern const rll_real_point rll_real_desi_dr2_bao_points[];
extern const rll_u32 rll_real_desi_dr2_bao_count;
extern const rll_real_point rll_real_cmb_prior_points[];
extern const rll_u32 rll_real_cmb_prior_count;
extern const double rll_real_cmb_covariance[9];

rll_cosmo_params rll_params_fase18e_map(void);
rll_cosmo_params rll_params_fase18e_lcdm(void);
double rll_predict_observable(rll_u32 observable, double z, const rll_cosmo_params *params, rll_u32 model, rll_u32 *status);
double rll_chi2_diagonal(const rll_real_point *points, rll_u32 count, const rll_cosmo_params *params, rll_u32 model, rll_u32 *status);
double rll_chi2_bao_correlated(const rll_real_point *points, rll_u32 count, const rll_cosmo_params *params, rll_u32 model, rll_u32 *status);
double rll_chi2_full_covariance(const rll_real_point *points, rll_u32 count, const double *covariance, const rll_cosmo_params *params, rll_u32 model, double *ldlt_workspace, double *diagonal_workspace, double *vector_workspace, rll_u32 *status);
double rll_chi2_cmb_full_covariance(const rll_cosmo_params *params, rll_u32 model, rll_u32 *status);
rll_canonical_result rll_run_canonical_real(const rll_cosmo_params *params, rll_u32 model);

#ifdef __cplusplus
}
#endif

#endif
