.syntax unified

.section .rodata.rll_joint65_blobs,"a",%progbits
.balign 4

.global rll_blob_hz_start
.global rll_blob_hz_end
rll_blob_hz_start:
    .incbin "data/real/Hz_data_real.csv"
rll_blob_hz_end:
.balign 4

.global rll_blob_bao_start
.global rll_blob_bao_end
rll_blob_bao_start:
    .incbin "data/real/cosmology/desi_dr2_bao_primary_points.csv"
rll_blob_bao_end:
.balign 4

.global rll_blob_fs8_start
.global rll_blob_fs8_end
rll_blob_fs8_start:
    .incbin "data/real/cosmology/fsigma8_growth_real.csv"
rll_blob_fs8_end:
.balign 4

.global rll_blob_cmb_start
.global rll_blob_cmb_end
rll_blob_cmb_start:
    .incbin "data/real/CMB_shift_real.json"
rll_blob_cmb_end:
.balign 4
