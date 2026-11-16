#ifndef RLL_QUANTIZED_ORBIT_U32_H
#define RLL_QUANTIZED_ORBIT_U32_H
/* RAFAELIA RLL formal integer geometry. Header is standalone/freestanding. */
typedef unsigned int rll_q_u32;
typedef unsigned long long rll_q_u64;

enum {
    RLL_Q_OK = 0u,
    RLL_Q_INVALID_INPUT = 1u,
    RLL_Q_UNREPRESENTABLE = 2u
};

typedef struct {
    rll_q_u32 status;           /* typed state, not an observed zero */
    rll_q_u32 base;
    rll_q_u32 exponent;
    rll_q_u32 exact_step;
    rll_q_u32 boundary_integer;
    rll_q_u32 cycles;
    rll_q_u32 vertices_per_cycle;
    int permutation_sign;
} rll_q_orbit_result;

rll_q_orbit_result rll_q_orbit_u32(rll_q_u32 base, rll_q_u32 exponent);
#endif
