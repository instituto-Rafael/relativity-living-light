#ifndef RLL_AIR_MASS_H
#define RLL_AIR_MASS_H
/* RLL Climate gas-phase, single-parcel thermodynamics. C11 freestanding. */
typedef unsigned char rlla_u8;
typedef unsigned int rlla_u32;
typedef signed int rlla_i32;
typedef unsigned long long rlla_u64;
_Static_assert(sizeof(rlla_u8)==1 && sizeof(rlla_u32)==4 && sizeof(rlla_i32)==4 && sizeof(rlla_u64)==8,"unsupported integer ABI");
#define RLLA_OK 0
#define RLLA_MISSING 1
#define RLLA_UNSUPPORTED_PHASE 2
#define RLLA_INVALID -1
#define RLLA_PHASE_VAPOR_ONLY 0u
#define RLLA_PHASE_CLOUD_OR_PRECIP 1u
#define RLLA_VALID_PRESSURE 1u
#define RLLA_VALID_TEMPERATURE 2u
#define RLLA_VALID_VAPOR 4u
#define RLLA_VALID_PHASE 8u
#define RLLA_VALID_ALL 15u
typedef struct {
    rlla_u32 pressure_pa;         /* 20000..110000 Pa */
    rlla_u32 temperature_ck;      /* centikelvin (K * 100), 18000..34000 */
    rlla_u32 vapor_volume_ppm;    /* mole/volume fraction, 0..40000 ppm */
    rlla_u8 phase;                /* vapor-only or unresolved condensate */
    rlla_u8 valid_mask;
} rlla_air;
typedef struct {
    rlla_u32 rho_dry_mg_m3;
    rlla_u32 rho_moist_mg_m3;
    rlla_u32 virtual_temperature_ck;
    rlla_u32 vapor_mass_ppm;
    rlla_u8 is_weather_warning;  /* always 0 */
} rlla_properties;
typedef struct {
    rlla_i32 buoyancy_milli_m_s2; /* gravity * (rho_env - rho_parcel)/rho_env */
    rlla_u8 is_weather_warning;
} rlla_buoyancy;
typedef struct {
    rlla_i32 virtual_temp_gradient_ck_per_km;
    rlla_i32 dry_lapse_screen_ck_per_km; /* ΔTv/Δz + 9.8 K/km, simplified */
    rlla_i32 class_code; /* +1 dry-screen stable, 0 neutral, -1 unstable */
    rlla_u8 is_weather_warning;
} rlla_layer_screen;
int rlla_air_properties(const rlla_air *a, rlla_properties *out);
int rlla_parcel_buoyancy(const rlla_air *env, const rlla_air *parcel, rlla_buoyancy *out);
int rlla_layer_dry_screen(const rlla_air *lower, const rlla_air *upper,
                          rlla_u32 height_lower_m, rlla_u32 height_upper_m,
                          rlla_layer_screen *out);
#endif
