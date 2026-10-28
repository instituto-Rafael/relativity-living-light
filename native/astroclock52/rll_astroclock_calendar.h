#ifndef RLL_ASTROCLOCK_CALENDAR_H
#define RLL_ASTROCLOCK_CALENDAR_H
/* Freestanding C11, relative day epoch, no historical correlation assumed. */
typedef unsigned int rac_u32;
typedef unsigned short rac_u16;
typedef unsigned char rac_u8;
_Static_assert(sizeof(rac_u32)==4 && sizeof(rac_u16)==2 && sizeof(rac_u8)==1,"ABI");
#define RAC_OK 0
#define RAC_MISSING 1
#define RAC_INVALID (-1)
#define RAC_ROUND_DAYS 18980u
#define RAC_VALID_DAY 1u
#define RAC_VALID_EPOCH 2u
#define RAC_VALID_ALL 3u
typedef struct {rac_u32 day_index;rac_u8 valid_mask;} rac_input;
typedef struct {
rac_u16 tzolkin_day_index;
rac_u16 haab_day_index;
rac_u16 calendar_round_day;
rac_u16 long_count_kin;
rac_u16 long_count_winal;
rac_u16 long_count_tun;
rac_u8 model_sector_12;
rac_u8 historical_date_claim;
} rac_output;
int rac_calendar(const rac_input *input,rac_output *output);
#endif
