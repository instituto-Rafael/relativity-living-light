#include "rll_canonical_freestanding.h"

/*
 * Canonical fixed-point materialization of data/real/Hz_data_real.csv.
 * Conversion: round(decimal * 65536), ties away from zero.
 * Source IDs preserve the CSV source column without string/runtime parsing.
 */
const rllc_hz_sample_q16 rllc_hz_canonical_data[RLLC_CANONICAL_ROW_COUNT] = {
    { 4588, 4521984, 1284506, 1u }, /* z=0.07, H=69.0, sigma=19.6, CC_Moresco2022 */
    { 5898, 4521984, 786432, 1u }, /* z=0.09, H=69.0, sigma=12.0, CC_Moresco2022 */
    { 7864, 4495770, 1717043, 1u }, /* z=0.12, H=68.6, sigma=26.2, CC_Moresco2022 */
    { 11141, 5439488, 524288, 1u }, /* z=0.17, H=83.0, sigma=8.0, CC_Moresco2022 */
    { 11731, 4915200, 262144, 1u }, /* z=0.179, H=75.0, sigma=4.0, CC_Moresco2022 */
    { 13042, 4915200, 327680, 1u }, /* z=0.199, H=75.0, sigma=5.0, CC_Moresco2022 */
    { 13107, 4777574, 1939866, 1u }, /* z=0.2, H=72.9, sigma=29.6, CC_Moresco2022 */
    { 17695, 5046272, 917504, 1u }, /* z=0.27, H=77.0, sigma=14.0, CC_Moresco2022 */
    { 18350, 5819597, 2398618, 1u }, /* z=0.28, H=88.8, sigma=36.6, CC_Moresco2022 */
    { 23069, 5439488, 917504, 1u }, /* z=0.352, H=83.0, sigma=14.0, CC_Moresco2022 */
    { 24904, 5439488, 884736, 2u }, /* z=0.38, H=83.0, sigma=13.5, CC+BAO_BOSS */
    { 26214, 6225920, 1114112, 1u }, /* z=0.4, H=95.0, sigma=17.0, CC_Moresco2022 */
    { 28836, 5413274, 511181, 1u }, /* z=0.44, H=82.6, sigma=7.8, CC_Moresco2022 */
    { 31457, 6356992, 4063232, 1u }, /* z=0.48, H=97.0, sigma=62.0, CC_Moresco2022 */
    { 33423, 5924454, 124518, 2u }, /* z=0.51, H=90.4, sigma=1.9, CC+BAO_BOSS */
    { 37356, 6343885, 222822, 2u }, /* z=0.57, H=96.8, sigma=3.4, CC+BAO_BOSS */
    { 38863, 6815744, 851968, 1u }, /* z=0.593, H=104.0, sigma=13.0, CC_Moresco2022 */
    { 39322, 5760614, 399770, 1u }, /* z=0.6, H=87.9, sigma=6.1, CC_Moresco2022 */
    { 39977, 6376653, 137626, 2u }, /* z=0.61, H=97.3, sigma=2.1, CC+BAO_BOSS */
    { 44564, 6029312, 524288, 1u }, /* z=0.68, H=92.0, sigma=8.0, CC_Moresco2022 */
    { 47841, 6376653, 458752, 1u }, /* z=0.73, H=97.3, sigma=7.0, CC_Moresco2022 */
    { 51184, 6881280, 786432, 1u }, /* z=0.781, H=105.0, sigma=12.0, CC_Moresco2022 */
    { 57344, 8192000, 1114112, 1u }, /* z=0.875, H=125.0, sigma=17.0, CC_Moresco2022 */
    { 57672, 5898240, 2621440, 1u }, /* z=0.88, H=90.0, sigma=40.0, CC_Moresco2022 */
    { 58982, 7667712, 1507328, 1u }, /* z=0.9, H=117.0, sigma=23.0, CC_Moresco2022 */
    { 67961, 10092544, 1310720, 1u }, /* z=1.037, H=154.0, sigma=20.0, CC_Moresco2022 */
    { 85197, 11010048, 1114112, 1u }, /* z=1.3, H=168.0, sigma=17.0, CC_Moresco2022 */
    { 89326, 10485760, 2202010, 1u }, /* z=1.363, H=160.0, sigma=33.6, CC_Moresco2022 */
    { 93716, 11599872, 1179648, 1u }, /* z=1.43, H=177.0, sigma=18.0, CC_Moresco2022 */
    { 100270, 9175040, 917504, 1u }, /* z=1.53, H=140.0, sigma=14.0, CC_Moresco2022 */
    { 114688, 13238272, 2621440, 1u }, /* z=1.75, H=202.0, sigma=40.0, CC_Moresco2022 */
    { 128778, 12222464, 3303014, 1u }, /* z=1.965, H=186.5, sigma=50.4, CC_Moresco2022 */
    { 153354, 14548992, 458752, 3u }, /* z=2.34, H=222.0, sigma=7.0, BAO_Lya */
};
