#include <stdio.h>
#include <stdlib.h>
#include "rll_canonical_region.h"

#define BUF_CAP (1024u * 1024u)
static unsigned char g_buf[BUF_CAP];

static int read_file(const char *path, unsigned char **data, unsigned long long *len) {
    FILE *fp = fopen(path, "rb");
    size_t n;
    if (!fp) return 1;
    n = fread(g_buf, 1u, BUF_CAP, fp);
    if (ferror(fp) || !feof(fp)) {
        fclose(fp);
        return 2;
    }
    fclose(fp);
    *data = g_buf;
    *len = (unsigned long long)n;
    return 0;
}

static int parse_one(
    rllc_state *state,
    const char *path,
    const char *sha_hex,
    int (*parser)(rllc_state *, const rllc_u8 *, rllc_u64, const rllc_u8[32])) {
    unsigned char *data = NULL;
    unsigned long long len = 0ull;
    rllc_u8 sha[32];
    int rc = read_file(path, &data, &len);
    if (rc != 0) return 10 + rc;
    rc = rllc_sha256_from_hex((const rllc_u8 *)sha_hex, sha);
    if (rc != RLLC_OK) return 20;
    rc = parser(state, data, len, sha);
    return rc == RLLC_OK ? 0 : 30 - rc;
}

int main(int argc, char **argv) {
    rllc_state state;
    rllc_receipt receipt;
    int rc;
    if (argc != 5) return 64;
    rllc_init(&state);

    rc = parse_one(&state, argv[1],
        "1194fe2066dc3d92b4870cfb03d2cdbe2a316deae2e1355943f7f2ccca6d52b6",
        rllc_parse_hz_csv);
    if (rc != 0) return rc;
    rc = parse_one(&state, argv[2],
        "5ab328705937c69cedb662bbb35888df20c6cabf3810ec3c5e7376d69ccb0a69",
        rllc_parse_bao_csv);
    if (rc != 0) return rc;
    rc = parse_one(&state, argv[3],
        "3781a2fa7bce9ea600060f9feb6e74ba49f4baa4ce2e7344803295c912318211",
        rllc_parse_fsigma8_csv);
    if (rc != 0) return rc;
    rc = parse_one(&state, argv[4],
        "e86d996131cf4b3758f4fe0319b6c7da752a38ab2f141abaa81bec66d8e6d979",
        rllc_parse_cmb_shift_json);
    if (rc != 0) return rc;

    rc = rllc_finalize(&state, &receipt);
    if (rc != RLLC_OK) return 80;
    if (receipt.claim_allowed != 0u) return 81;
    if (receipt.violation_mask != 0u) return 82;
    if (receipt.hz_rows != 33ull) return 83;
    if (receipt.bao_rows != 13ull) return 84;
    if (receipt.fsigma8_rows != 16ull) return 85;
    if (receipt.cmb_rows != 3ull) return 86;
    if (receipt.accepted != 65ull) return 87;
    if (receipt.covariance_present != 1u) return 88;

    printf("RLL_CANONICAL_REGION_V1 PASS accepted=%llu hz=%llu bao=%llu fs8=%llu cmb=%llu fnv=%016llx crc=%08x claim_allowed=%u\n",
        (unsigned long long)receipt.accepted,
        (unsigned long long)receipt.hz_rows,
        (unsigned long long)receipt.bao_rows,
        (unsigned long long)receipt.fsigma8_rows,
        (unsigned long long)receipt.cmb_rows,
        (unsigned long long)receipt.rolling_fnv1a64,
        (unsigned)receipt.rolling_crc32,
        (unsigned)receipt.claim_allowed);
    return 0;
}
