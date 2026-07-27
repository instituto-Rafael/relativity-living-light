#include <stdio.h>
#include "rll_canonical_real_inputs.h"

#define RUNNER_CAP 8192u

static rll_u8 hz_buffer[RUNNER_CAP];
static rll_u8 bao_buffer[RUNNER_CAP];
static rll_u8 fs8_buffer[RUNNER_CAP];
static rll_u8 cmb_buffer[RUNNER_CAP];

static int read_file(const char *path, rll_u8 *buffer, rll_u64 *length) {
    FILE *file;
    size_t count;
    file = fopen(path, "rb");
    if (file == (FILE *)0) return 1;
    count = fread(buffer, 1u, RUNNER_CAP, file);
    if (ferror(file) || !feof(file)) {
        fclose(file);
        return 2;
    }
    fclose(file);
    *length = (rll_u64)count;
    return 0;
}

static rll_u32 identity_model(
    void *context,
    const rll_real_model_request *request,
    rll_i64 *model_q16
) {
    (void)context;
    *model_q16 = request->observed_q16;
    return RLL_REAL_MODEL_OK;
}

int main(int argc, char **argv) {
    rll_real_input_bundle bundle;
    rll_real_ingest_receipt receipt;
    rll_real_model_callback callback;
    int rc;

    if (argc != 6) return 64;
    if (read_file(argv[1], hz_buffer, &bundle.hz_len) != 0) return 65;
    if (read_file(argv[2], bao_buffer, &bundle.bao_len) != 0) return 66;
    if (read_file(argv[3], fs8_buffer, &bundle.fsigma8_len) != 0) return 67;
    if (read_file(argv[4], cmb_buffer, &bundle.cmb_len) != 0) return 68;
    bundle.hz_csv = hz_buffer;
    bundle.bao_csv = bao_buffer;
    bundle.fsigma8_csv = fs8_buffer;
    bundle.cmb_json = cmb_buffer;

    callback = argv[5][0] == 'i' ? identity_model : (rll_real_model_callback)0;
    rc = rll_real_ingest_all(&bundle, callback, (void *)0, &receipt);

    printf(
        "RLL_REAL_INPUTS status=%d verified=%u rows=%u bound=%u token_vazio=%u "
        "hz=%u bao=%u fs8=%u cmb=%u covariance=%u total=%u evidence=%u "
        "blocked=%u chi2_q16=%lld claim_allowed=%u\n",
        rc,
        (unsigned)receipt.source_verified_mask,
        (unsigned)receipt.parsed_rows,
        (unsigned)receipt.model_bound_rows,
        (unsigned)receipt.model_token_vazio_rows,
        (unsigned)receipt.hz_rows,
        (unsigned)receipt.bao_rows,
        (unsigned)receipt.fsigma8_rows,
        (unsigned)receipt.cmb_rows,
        (unsigned)receipt.cmb_covariance_used,
        (unsigned)receipt.canonical.total,
        (unsigned)receipt.canonical.evidence,
        (unsigned)receipt.canonical.blocked,
        (long long)receipt.canonical.chi2_q16,
        (unsigned)receipt.claim_allowed
    );

    if (rc != RLL_REAL_OK) return 80;
    if (receipt.source_verified_mask != RLL_REAL_SOURCE_ALL) return 81;
    if (receipt.parsed_rows != 65u) return 82;
    if (receipt.hz_rows != 33u || receipt.bao_rows != 13u ||
        receipt.fsigma8_rows != 16u || receipt.cmb_rows != 3u) return 83;
    if (receipt.claim_allowed != 0u || receipt.canonical.claim_allowed != 0u) return 84;

    if (callback != (rll_real_model_callback)0) {
        if (receipt.model_bound_rows != 65u) return 85;
        if (receipt.canonical.total != 65u || receipt.canonical.evidence != 65u) return 86;
        if (receipt.canonical.blocked != 0u || receipt.cmb_covariance_used != 1u) return 87;
        if (receipt.canonical.chi2_q16 != 0ll) return 88;
    } else {
        if (receipt.model_token_vazio_rows != 65u) return 89;
        if (receipt.canonical.total != 65u || receipt.canonical.blocked != 65u) return 90;
        if (receipt.canonical.evidence != 0u || receipt.cmb_covariance_used != 0u) return 91;
    }
    return 0;
}
