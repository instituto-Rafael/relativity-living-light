#ifndef RLL_STABILITY_LOCATOR_H
#define RLL_STABILITY_LOCATOR_H
/* RLL research diagnostic; pure freestanding C11, integer-only. */
typedef unsigned char rl_u8;
typedef unsigned short rl_u16;
typedef unsigned int rl_u32;
typedef signed int rl_i32;
_Static_assert(sizeof(rl_u8)==1 && sizeof(rl_u16)==2 && sizeof(rl_u32)==4 && sizeof(rl_i32)==4, "unsupported ABI");
#define RL_MAX_CELLS 16u
#define RL_N_FEATURES 5u
#define RL_OK 0
#define RL_MISSING 1
#define RL_INVALID -1
#define RL_HORIZON_MAX_MIN 20160u
/* External z-scores *100, range [-600,600] in order:
   sea temperature, moist air, relative vorticity, shear, sea-level pressure.
   Fixed experimental orientation; not probabilities or cyclone predictions. */
typedef struct {
    rl_i32 z100;
    rl_i32 model_issue_minute;
    rl_i32 available_minute;
    rl_i32 valid_target_minute;
    rl_u8 is_valid;
} rl_forecast_feature;
typedef struct {
    rl_i32 observation_minute;
    rl_i32 available_minute;
    rl_i32 pressure_hpa10;
    rl_i32 wind_ms10;
    rl_u8 valid;
} rl_observation;
typedef struct {
    rl_u16 tile_id;
    rl_i32 latitude_e4;
    rl_i32 longitude_e4;
    rl_forecast_feature forecast[RL_N_FEATURES];
    rl_observation older;
    rl_observation newer;
} rl_tile;
typedef struct {
    rl_i32 issue_minute;
    rl_i32 forecast_target_minute;
    rl_u8 count;
    rl_tile tiles[RL_MAX_CELLS];
} rl_locator_input;
typedef struct {
    rl_u16 selected_tile_id;
    rl_u16 candidate_score_0_600;
    rl_u8 evaluated_tiles;
    rl_u8 missing_tiles;
    rl_u8 rapid_30min_state; /* 0 missing, 1 no threshold crossing, 2 crossing */
    rl_u8 forecast_skill_validated; /* always 0 */
    rl_u8 is_hurricane_warning;     /* always 0 */
} rl_locator_output;
int rl_locate_stability(const rl_locator_input *in, rl_locator_output *out);
#endif
