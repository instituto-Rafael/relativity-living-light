#ifndef RLL_TEC_PHASE_H
#define RLL_TEC_PHASE_H
/* Apparent inter-station TEC disturbance phase speed, NOT tornado prediction. */
typedef unsigned char rllt_u8;
typedef unsigned short rllt_u16;
typedef unsigned int rllt_u32;
typedef signed short rllt_i16;
_Static_assert(sizeof(rllt_u8)==1 && sizeof(rllt_u16)==2 && sizeof(rllt_u32)==4 && sizeof(rllt_i16)==2,"ABI width");
#define RLLT_OK 0
#define RLLT_MISSING 1
#define RLLT_INVALID -1
typedef struct {
   rllt_u16 projected_separation_km; /* already projected along propagation axis */
   rllt_i16 arrival_delay_minutes;   /* later station minus earlier, positive */
   rllt_u8 valid_mask;                /* bit0 separation, bit1 delay */
} rllt_pair;
typedef struct {
   rllt_u16 apparent_speed_m_s;       /* integer floor, precision limited */
   rllt_u8 direction_identifiable;    /* 0: two sensors cannot identify 2D wave vector */
   rllt_u8 is_tornado_predictor;     /* ALWAYS 0 */
} rllt_result;
int rllt_phase_speed(const rllt_pair *p, rllt_result *out);
#endif
