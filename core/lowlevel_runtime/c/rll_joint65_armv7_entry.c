#include "rll_canonical_real_models.h"

#if defined(__GNUC__) || defined(__clang__)
#define RLLJ_NORETURN __attribute__((noreturn))
#else
#define RLLJ_NORETURN
#endif

extern const rll_u8 rll_blob_hz_start[];
extern const rll_u8 rll_blob_hz_end[];
extern const rll_u8 rll_blob_bao_start[];
extern const rll_u8 rll_blob_bao_end[];
extern const rll_u8 rll_blob_fs8_start[];
extern const rll_u8 rll_blob_fs8_end[];
extern const rll_u8 rll_blob_cmb_start[];
extern const rll_u8 rll_blob_cmb_end[];

static RLLJ_NORETURN void rllj_exit(rll_u32 status)
{
#if defined(__linux__) && defined(__arm__)
    register rll_u32 r0 __asm__("r0") = status;
    register rll_u32 r7 __asm__("r7") = 1u;
    __asm__ volatile("svc 0" : : "r"(r0), "r"(r7) : "memory");
#else
    (void)status;
#endif
    for (;;) {
#if defined(__GNUC__) || defined(__clang__)
        __asm__ volatile("" : : : "memory");
#endif
    }
}

static rll_u32 receipt_shape_ok(const rll_real_ingest_receipt *r)
{
    return
        r->status == RLL_REAL_OK &&
        r->source_verified_mask == RLL_REAL_SOURCE_ALL &&
        r->parsed_rows == 65u &&
        r->model_bound_rows == 65u &&
        r->model_token_vazio_rows == 0u &&
        r->hz_rows == 33u &&
        r->bao_rows == 13u &&
        r->fsigma8_rows == 16u &&
        r->cmb_rows == 3u &&
        r->cmb_covariance_used == 1u &&
        r->canonical.total == 65u &&
        r->canonical.evidence == 65u &&
        r->canonical.blocked == 0u;
}

RLLJ_NORETURN void _start(void)
{
    static rll_real_input_bundle bundle;
    static rll_real_ingest_receipt lcdm_receipt;
    static rll_real_ingest_receipt rll_receipt;
    static rll_real_model_context lcdm_context;
    static rll_real_model_context rll_context;
    int rc_lcdm;
    int rc_rll;
    rll_u32 fail = 0u;

    bundle.hz_csv = rll_blob_hz_start;
    bundle.hz_len = (rll_u64)(rll_blob_hz_end - rll_blob_hz_start);
    bundle.bao_csv = rll_blob_bao_start;
    bundle.bao_len = (rll_u64)(rll_blob_bao_end - rll_blob_bao_start);
    bundle.fsigma8_csv = rll_blob_fs8_start;
    bundle.fsigma8_len = (rll_u64)(rll_blob_fs8_end - rll_blob_fs8_start);
    bundle.cmb_json = rll_blob_cmb_start;
    bundle.cmb_len = (rll_u64)(rll_blob_cmb_end - rll_blob_cmb_start);

    lcdm_context = rll_real_model_lcdm_joint_fase18e();
    rll_context = rll_real_model_rll_joint_fase18e();

    rc_lcdm = rll_real_ingest_all(
        &bundle,
        rll_real_canonical_model_callback,
        &lcdm_context,
        &lcdm_receipt
    );

    rc_rll = rll_real_ingest_all(
        &bundle,
        rll_real_canonical_model_callback,
        &rll_context,
        &rll_receipt
    );

    if (rc_lcdm != RLL_REAL_OK || rc_rll != RLL_REAL_OK)
        fail |= 1u << 0;

    if (!receipt_shape_ok(&lcdm_receipt) || !receipt_shape_ok(&rll_receipt))
        fail |= 1u << 1;

    if (lcdm_receipt.canonical.chi2_q16 != 4641555ll)
        fail |= 1u << 2;

    if (rll_receipt.canonical.chi2_q16 != 4261420ll)
        fail |= 1u << 3;

    if ((rll_i64)rll_receipt.canonical.chi2_q16 -
        (rll_i64)lcdm_receipt.canonical.chi2_q16 != -380135ll)
        fail |= 1u << 4;

    if (lcdm_receipt.claim_allowed != 0u ||
        rll_receipt.claim_allowed != 0u ||
        lcdm_receipt.canonical.claim_allowed != 0u ||
        rll_receipt.canonical.claim_allowed != 0u)
        fail |= 1u << 5;

    rllj_exit(fail & 0xffu);
}
