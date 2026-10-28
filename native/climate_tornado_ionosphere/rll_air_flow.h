#ifndef RLL_AIR_FLOW_H
#define RLL_AIR_FLOW_H
/* Pure freestanding C11: 3D air mass flux, vertical shear and shallow hydrostatic load. */
typedef signed int rllf_i32;
typedef unsigned int rllf_u32;
typedef unsigned char rllf_u8;
typedef unsigned long long rllf_u64;
_Static_assert(sizeof(rllf_i32)==4 && sizeof(rllf_u32)==4 && sizeof(rllf_u8)==1 && sizeof(rllf_u64)==8,"ABI");
#define RLLF_OK 0
#define RLLF_MISSING 1
#define RLLF_INVALID -1
#define RLLF_WIND_EAST 1u
#define RLLF_WIND_NORTH 2u
#define RLLF_WIND_UP 4u
#define RLLF_WIND_ALL 7u
typedef struct {
    rllf_i32 east_cm_s;
    rllf_i32 north_cm_s;
    rllf_i32 up_cm_s;
    rllf_u8 valid_mask;
} rllf_wind;
typedef struct {
    rllf_i32 east_g_m2_s;
    rllf_i32 north_g_m2_s;
    rllf_i32 up_g_m2_s;
    rllf_u32 hydrostatic_drop_pa; /* shallow constant-density approximation */
    rllf_u8 is_weather_warning; /* always 0 */
} rllf_transport;
typedef struct {
    rllf_i32 east_shear_cm_s_km;
    rllf_i32 north_shear_cm_s_km;
    rllf_i32 up_shear_cm_s_km;
    rllf_u8 is_weather_warning;
} rllf_shear;
int rllf_mass_transport(rllf_u32 rho_mg_m3, rllf_u8 rho_valid,
                        const rllf_wind *wind, rllf_u32 dz_m,
                        rllf_transport *out);
int rllf_vertical_shear(const rllf_wind *lower, const rllf_wind *upper,
                         rllf_u32 dz_m, rllf_shear *out);
#endif
