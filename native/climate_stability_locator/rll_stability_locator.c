#include "rll_stability_locator.h"
static rl_u8 position_valid(const rl_tile *t) {
    return (rl_u8)(t->latitude_e4>=-900000 && t->latitude_e4<=900000 &&
                   t->longitude_e4>=-1800000 && t->longitude_e4<=1800000);
}
static rl_u8 obs_valid(const rl_observation *o, rl_i32 issue) {
    if(!o->valid) return 0u;
    return (rl_u8)(o->observation_minute>=0 && o->available_minute>=o->observation_minute &&
        o->observation_minute<=issue && o->available_minute<=issue &&
        o->pressure_hpa10>=8000 && o->pressure_hpa10<=11000 &&
        o->wind_ms10>=0 && o->wind_ms10<=1500);
}
static rl_u8 rapid_trend(const rl_tile *t, rl_i32 issue) {
    rl_i32 dt;
    if(!obs_valid(&t->older,issue)||!obs_valid(&t->newer,issue)) return 0u;
    dt=t->newer.observation_minute-t->older.observation_minute;
    if(dt<1 || dt>30 || issue-t->newer.observation_minute>5) return 0u;
    return (rl_u8)((t->older.pressure_hpa10-t->newer.pressure_hpa10>=30 &&
                    t->newer.wind_ms10-t->older.wind_ms10>=50)?2u:1u);
}
int rl_locate_stability(const rl_locator_input *in,rl_locator_output *out) {
    rl_u8 i,j,found=0u;
    rl_i32 delta;
    if(!out) return RL_INVALID;
    out->selected_tile_id=0u;out->candidate_score_0_600=0u;
    out->evaluated_tiles=0u;out->missing_tiles=0u;out->rapid_30min_state=0u;
    out->forecast_skill_validated=0u;out->is_hurricane_warning=0u;
    if(!in || in->count==0u || in->count>RL_MAX_CELLS ||
       in->issue_minute<=0 || in->forecast_target_minute<in->issue_minute) return RL_INVALID;
    delta=in->forecast_target_minute-in->issue_minute;
    if(delta<0 || (rl_u32)delta>RL_HORIZON_MAX_MIN) return RL_INVALID;
    for(i=0;i<in->count;i++) {
        const rl_tile *t=&in->tiles[i];
        rl_u32 sum=0u;
        rl_u8 complete=1u;
        if(!position_valid(t)) return RL_INVALID;
        for(j=0;j<RL_N_FEATURES;j++) {
            const rl_forecast_feature *f=&t->forecast[j];
            rl_i32 z;
            if(f->is_valid>1u) return RL_INVALID;
            if(!f->is_valid){complete=0u;continue;}
            if(f->z100< -600 || f->z100>600 || f->model_issue_minute<0 ||
               f->available_minute<f->model_issue_minute ||
               f->model_issue_minute>in->issue_minute ||
               f->available_minute>in->issue_minute ||
               f->valid_target_minute!=in->forecast_target_minute) return RL_INVALID;
            z=(j>=3u)?-f->z100:f->z100;
            if(z>0) sum+=(rl_u32)z;
        }
        if(!complete){++out->missing_tiles;continue;}
        ++out->evaluated_tiles;
        {
            rl_u16 score=(rl_u16)(sum/5u);
            if(!found || score>out->candidate_score_0_600 ||
               (score==out->candidate_score_0_600 && t->tile_id<out->selected_tile_id)) {
                found=1u;out->selected_tile_id=t->tile_id;
                out->candidate_score_0_600=score;
                out->rapid_30min_state=rapid_trend(t,in->issue_minute);
            }
        }
    }
    return found?RL_OK:RL_MISSING;
}
