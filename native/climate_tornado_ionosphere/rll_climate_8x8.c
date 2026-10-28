#include "rll_climate_8x8.h"
int rll8_validate(const rll8_matrix *m, rll8_audit *out) {
    rll8_u8 s,r;
    if (!out) return RLL8_INVALID;
    out->valid_gates=0;out->valid_physical=0;out->missing_physical=0;
    out->above_three_sigma=0;out->missing_sector_mask=0;out->is_operational_warning=0;
    if (!m) return RLL8_INVALID;
    for(s=0;s<8u;++s) {
        if(m->physical_valid_mask[s] & 0x80u) return RLL8_INVALID;
        if(m->gate_valid_mask & (1u<<s)) {
            rll8_i32 g=m->q16[s][0];
            if(g < -1048576 || g > 1048576) return RLL8_INVALID;
            ++out->valid_gates;
        } else out->missing_sector_mask|=(rll8_u8)(1u<<s);
        for(r=1;r<8u;++r) {
            if(m->physical_valid_mask[s] & (1u<<(r-1u))) {
                rll8_i32 x=m->q16[s][r];
                if(x < -1048576 || x > 1048576) return RLL8_INVALID;
                ++out->valid_physical;
                if(x >= 196608 || x <= -196608)++out->above_three_sigma;
            } else {
                ++out->missing_physical;
                out->missing_sector_mask|=(rll8_u8)(1u<<s);
            }
        }
    }
    return out->missing_sector_mask? RLL8_INCOMPLETE:RLL8_OK;
}
