#include "rll_climate_30min.h"

int rll30_evaluate(const rll30_window *w, rll30_result *r) {
    rll_u8 i;
    rll_u8 rv = 0, tv = 0, kv = 0;
    rll_i32 rfirst = 0, tfirst = 0, rlast = 0, tlast = 0;
    rll_u16 radar_previous = 0, radar_latest = 0;
    rll_i32 tec_previous = 0, tec_latest = 0;
    rll_u8 kp_latest = 0;
    rll_i32 previous_time = 0;
    if (!r) return RLL30_INVALID;
    r->radar_only_diagnostic = 0;
    r->tec_perturbation_diagnostic = 0;
    r->combined_diagnostic = 0;
    r->geomagnetic_confounded = 0;
    r->available_30min = 0;
    r->is_operational_warning = 0;
    if (!w || w->count < 2u || w->count > RLL30_MAX_SAMPLES) return RLL30_INVALID;
    for (i=0; i<w->count; ++i) {
        const rll30_sample *s=&w->sample[i];
        if ((s->valid_mask & ~7u) != 0u) return RLL30_INVALID;
        if (i && s->minute_utc <= previous_time) return RLL30_INVALID;
        /* Prevent future leakage and stale samples before 30-min evaluation. */
        if (s->minute_utc > w->issue_minute_utc ||
            ((rll_u32)w->issue_minute_utc - (rll_u32)s->minute_utc) > 30u)
            return RLL30_INVALID;
        previous_time = s->minute_utc;
        if (s->valid_mask & RLL30_RADAR) {
            if (s->radar_norm_1000 > 1000u) return RLL30_INVALID;
            if (!rv) rfirst=s->minute_utc;
            radar_previous=radar_latest;
            radar_latest=s->radar_norm_1000;
            rlast=s->minute_utc;
            ++rv;
        }
        if (s->valid_mask & RLL30_TEC) {
            /* Explicit bounded TEC domain; outside => invalid normalization. */
            if (s->tec_residual_centi_tecu < -20000 ||
                s->tec_residual_centi_tecu > 20000) return RLL30_INVALID;
            if (!tv) tfirst=s->minute_utc;
            tec_previous=tec_latest;
            tec_latest=s->tec_residual_centi_tecu;
            tlast=s->minute_utc;
            ++tv;
        }
        if (s->valid_mask & RLL30_KP) {
            if (s->kp_deci > 90u) return RLL30_INVALID;
            kp_latest=s->kp_deci;
            ++kv;
        }
    }
    if (rv < 2u || tv < 2u || !kv) return RLL30_MISSING;
    if (w->issue_minute_utc - rlast > 5 ||
        w->issue_minute_utc - tlast > 5) return RLL30_MISSING;
    if (rlast - rfirst < 10 || tlast - tfirst < 10) return RLL30_MISSING;
    r->available_30min=1;
    /* Only a diagnostic with uncalibrated thresholds, never an alert. */
    r->radar_only_diagnostic =
        (rll_u8)((radar_latest >= 600u) && (radar_previous >= 400u));
    r->geomagnetic_confounded = (rll_u8)(kp_latest >= 50u);
    r->tec_perturbation_diagnostic =
        (rll_u8)(!r->geomagnetic_confounded &&
                 tec_latest >= 30 && tec_latest - tec_previous >= 20);
    r->combined_diagnostic =
        (rll_u8)(r->radar_only_diagnostic && r->tec_perturbation_diagnostic);
    return RLL30_OK;
}
