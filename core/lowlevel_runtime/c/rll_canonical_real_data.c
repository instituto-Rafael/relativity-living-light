#include "rll_canonical_real.h"

const rll_real_source rll_canonical_sources[] = {
    {1u, RLL_SOURCE_LOCAL_HASH_VERIFIED | RLL_SOURCE_REMOTE_SIGNATURE_VERIFIED | RLL_SOURCE_DIAGONAL_ONLY,
     "real_hz", "data/real/Hz_data_real.csv", "1194fe2066dc3d92b4870cfb03d2cdbe2a316deae2e1355943f7f2ccca6d52b6", "https://arxiv.org/abs/2205.05701"},
    {2u, RLL_SOURCE_LOCAL_HASH_VERIFIED | RLL_SOURCE_REMOTE_SIGNATURE_VERIFIED | RLL_SOURCE_DIAGONAL_ONLY | RLL_SOURCE_PRIMARY_PARTIAL,
     "real_fsigma8_compilation", "data/real/cosmology/fsigma8_growth_real.csv", "3781a2fa7bce9ea600060f9feb6e74ba49f4baa4ce2e7344803295c912318211", "https://arxiv.org/abs/1204.4725"},
    {3u, RLL_SOURCE_LOCAL_HASH_VERIFIED | RLL_SOURCE_REMOTE_SIGNATURE_VERIFIED | RLL_SOURCE_FULL_COVARIANCE,
     "real_desi_dr2_bao", "data/real/cosmology/desi_dr2_bao_primary_points.csv", "5ab328705937c69cedb662bbb35888df20c6cabf3810ec3c5e7376d69ccb0a69", "https://arxiv.org/abs/2503.14738"},
    {4u, RLL_SOURCE_LOCAL_HASH_VERIFIED | RLL_SOURCE_REMOTE_SIGNATURE_VERIFIED | RLL_SOURCE_FULL_COVARIANCE,
     "real_cmb_shift", "data/real/CMB_shift_real.json", "e86d996131cf4b3758f4fe0319b6c7da752a38ab2f141abaa81bec66d8e6d979", "https://arxiv.org/abs/1808.05724"}
};
const rll_u32 rll_canonical_source_count = 4u;

const rll_real_point rll_real_hz_points[] = {
    {0.070,69.0,19.6,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.090,69.0,12.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.120,68.6,26.2,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.170,83.0,8.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.179,75.0,4.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.199,75.0,5.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.200,72.9,29.6,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.270,77.0,14.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.280,88.8,36.6,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.352,83.0,14.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.380,83.0,13.5,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.400,95.0,17.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.440,82.6,7.8,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.480,97.0,62.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.510,90.4,1.9,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.570,96.8,3.4,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.593,104.0,13.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.600,87.9,6.1,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.610,97.3,2.1,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.680,92.0,8.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.730,97.3,7.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.781,105.0,12.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.875,125.0,17.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{0.880,90.0,40.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {0.900,117.0,23.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{1.037,154.0,20.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {1.300,168.0,17.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{1.363,160.0,33.6,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {1.430,177.0,18.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{1.530,140.0,14.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {1.750,202.0,40.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},{1.965,186.5,50.4,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u},
    {2.340,222.0,7.0,0.0,RLL_OBS_HZ_KM_S_MPC,1u,0u}
};
const rll_u32 rll_real_hz_count = 33u;

const rll_real_point rll_real_fsigma8_points[] = {
    {0.020,0.360,0.040,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.067,0.423,0.055,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.100,0.370,0.130,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.170,0.510,0.060,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.220,0.420,0.070,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.250,0.351,0.058,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.300,0.407,0.055,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.350,0.440,0.050,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.370,0.460,0.038,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.400,0.419,0.041,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.410,0.450,0.040,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.570,0.427,0.066,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.600,0.430,0.040,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.600,0.433,0.067,0.0,RLL_OBS_FSIGMA8,2u,0u},
    {0.770,0.490,0.180,0.0,RLL_OBS_FSIGMA8,2u,0u},{0.780,0.380,0.040,0.0,RLL_OBS_FSIGMA8,2u,0u}
};
const rll_u32 rll_real_fsigma8_count = 16u;

const rll_real_point rll_real_desi_dr2_bao_points[] = {
    {0.295,7.942,0.075,0.0,RLL_OBS_BAO_DV_OVER_RD,3u,0u},
    {0.510,13.588,0.167,-0.459,RLL_OBS_BAO_DM_OVER_RD,3u,1u},{0.510,21.863,0.425,-0.459,RLL_OBS_BAO_DH_OVER_RD,3u,1u},
    {0.706,17.351,0.177,-0.404,RLL_OBS_BAO_DM_OVER_RD,3u,2u},{0.706,19.455,0.330,-0.404,RLL_OBS_BAO_DH_OVER_RD,3u,2u},
    {0.934,21.576,0.152,-0.416,RLL_OBS_BAO_DM_OVER_RD,3u,3u},{0.934,17.641,0.193,-0.416,RLL_OBS_BAO_DH_OVER_RD,3u,3u},
    {1.321,27.601,0.318,-0.434,RLL_OBS_BAO_DM_OVER_RD,3u,4u},{1.321,14.176,0.221,-0.434,RLL_OBS_BAO_DH_OVER_RD,3u,4u},
    {1.484,30.512,0.760,-0.500,RLL_OBS_BAO_DM_OVER_RD,3u,5u},{1.484,12.817,0.516,-0.500,RLL_OBS_BAO_DH_OVER_RD,3u,5u},
    {2.330,38.988,0.531,-0.431,RLL_OBS_BAO_DM_OVER_RD,3u,6u},{2.330,8.632,0.101,-0.431,RLL_OBS_BAO_DH_OVER_RD,3u,6u}
};
const rll_u32 rll_real_desi_dr2_bao_count = 13u;

const rll_real_point rll_real_cmb_prior_points[] = {
    {1089.92,1.7502,0.0046,0.0,RLL_OBS_CMB_R,4u,7u},
    {1089.92,301.471,0.090,0.0,RLL_OBS_CMB_LA,4u,7u},
    {0.0,0.02236,0.00015,0.0,RLL_OBS_CMB_OBH2,4u,7u}
};
const rll_u32 rll_real_cmb_prior_count = 3u;

const double rll_real_cmb_covariance[9] = {
    2.116e-05, 0.000189382, -4.554e-07,
    0.000189382, 0.00801025, -4.43025e-06,
    -4.554e-07, -4.43025e-06, 2.25e-08
};
