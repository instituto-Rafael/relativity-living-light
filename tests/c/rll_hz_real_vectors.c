#include "rll_hz_freestanding.h"

int main(void) {
    rll_hz_params_q16 params = rll_hz_nominal_planck_params_q16();
    rll_hz_dual_receipt receipt = rll_hz_run_moresco_nominal_q16();

    if (receipt.rows != RLL_HZ_DATASET_ROWS) return 1;
    if (receipt.lcdm.total != 33u || receipt.rll.total != 33u) return 2;
    if (receipt.lcdm.evidence != 33u || receipt.rll.evidence != 33u) return 3;
    if (receipt.lcdm.blocked != 0u || receipt.rll.blocked != 0u) return 4;
    if (receipt.lcdm.degrees_of_freedom != 33u) return 5;
    if (receipt.rll.degrees_of_freedom != 33u) return 6;
    if (receipt.lcdm.chi2_q16 != 1491916ll) return 7;
    if (receipt.rll.chi2_q16 != 1800068ll) return 8;
    if (receipt.delta_chi2_q16 != 308152ll) return 9;
    if (receipt.dataset_fnv1a64 != RLL_HZ_DATASET_FNV1A64) return 10;
    if (receipt.dataset_crc32 != RLL_HZ_DATASET_CRC32) return 11;
    if (receipt.claim_allowed != 0u) return 12;
    if (receipt.lcdm.claim_allowed != 0u || receipt.rll.claim_allowed != 0u) return 13;
    if (rll_hz_lcdm_q16(0ll, &params) != params.h0_q16) return 14;
    if (rll_hz_rll_q16(0ll, &params) <= 0ll) return 15;
    if (rll_hz_moresco_2022_sha256_hex[64] != 0u) return 16;
    if (rll_hz_moresco_2022_q16[0].sequence_id != 1u) return 17;
    if (rll_hz_moresco_2022_q16[32].sequence_id != 33u) return 18;

    return 0;
}
