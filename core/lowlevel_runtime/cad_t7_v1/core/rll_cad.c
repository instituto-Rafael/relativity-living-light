#include "rll_cad.h"
/* Fixed point operations explicitly guarded; never silently saturate. */
#define RMAX 2147483647
#define RMIN (-2147483647-1)
/* ARMv7 freestanding does not provide a 64-bit hardware divide instruction.
 * A bounded long-division fallback avoids hidden __aeabi_ldivmod libgcc calls. */
static r_u64 r_udiv64(r_u64 n,r_u64 d){
 r_u64 q=0,rem=0;
 if(!d)return 0; /* All public division paths reject denominator zero. */
 for(r_i32 bit=63;bit>=0;--bit){
  rem=(rem<<1)|((n>>(r_u32)bit)&1u);
  if(rem>=d){rem-=d;q|=((r_u64)1<<(r_u32)bit);}
 }
 return q;
}
static r_i64 r_sdiv64(r_i64 n,r_i64 d){
 r_u64 an=n<0?(r_u64)(-(n+1))+1u:(r_u64)n;
 r_u64 ad=d<0?(r_u64)(-(d+1))+1u:(r_u64)d;
 r_u64 q=r_udiv64(an,ad);
 return (n<0)!=(d<0)?-(r_i64)q:(r_i64)q;
}
static int checked(r_i64 n,r_i32 *out){ if(n>RMAX||n<RMIN)return R_CAD_NUMERIC_OVERFLOW;*out=(r_i32)n;return 0; }
static int qm(r_i32 a,r_i32 b,r_i32 *out){return checked(r_sdiv64(((r_i64)a*b),R_Q16),out);}
static int qd(r_i32 a,r_i32 b,r_i32 *out){if(!b)return R_CAD_INVALID_INPUT;return checked(r_sdiv64(((r_i64)a*R_Q16),b),out);}
static r_u64 isqrt64(r_u64 x){r_u64 r=0,bit=(r_u64)1<<62;while(bit>x)bit>>=2;while(bit){if(x>=r+bit){x-=r+bit;r=(r>>1)+bit;}else r>>=1;bit>>=2;}return r;}
static int qs(r_i32 q,r_i32 *out){if(q<0)return R_CAD_INVALID_INPUT;return checked((r_i64)isqrt64((r_u64)(r_u32)q*R_Q16),out);}
static int bigdiv(r_i32 num,r_i64 den,r_i32 *out){if(den<=0)return R_CAD_INVALID_INPUT;return checked(r_sdiv64(((r_i64)num*R_Q16),den),out);}
static int stress(r_i32 force_kN,r_i32 area_mm2,r_i32 *out){if(area_mm2<=0)return R_CAD_INVALID_INPUT;return checked(r_sdiv64((r_i64)force_kN*1000*R_Q16,area_mm2),out);}
static int dim_validate(const rll_cad_input *a){
 if(!a||a->span_mm_q16<100*R_Q16||a->span_mm_q16>2000*R_Q16)return 0;
 if(a->rise_mm_q16<100*R_Q16||a->rise_mm_q16>1000*R_Q16)return 0;
 if(a->area_diagonal_mm2_q16<10*R_Q16||a->area_diagonal_mm2_q16>1000*R_Q16)return 0;
 if(a->area_tie_mm2_q16<10*R_Q16||a->area_tie_mm2_q16>1000*R_Q16)return 0;
 if(a->downward_load_kN_q16<1||a->downward_load_kN_q16>10*R_Q16)return 0;
 if(a->young_GPa_q16<1*R_Q16||a->young_GPa_q16>400*R_Q16)return 0;
 if(a->yield_MPa_q16<10*R_Q16||a->yield_MPa_q16>1000*R_Q16)return 0;
 if(a->deltaT_K_q16<(-100*R_Q16)||a->deltaT_K_q16>100*R_Q16)return 0;
 if(a->alpha_micro_per_K<0||a->alpha_micro_per_K>200)return 0;
 return 1;
}
int rll_cad_baseline(rll_cad_input *a){if(!a)return R_CAD_INVALID_INPUT;
 a->span_mm_q16=1000*R_Q16;a->rise_mm_q16=500*R_Q16;
 a->area_diagonal_mm2_q16=500*R_Q16;a->area_tie_mm2_q16=300*R_Q16;
 a->downward_load_kN_q16=1*R_Q16;a->young_GPa_q16=200*R_Q16;
 a->yield_MPa_q16=250*R_Q16;a->deltaT_K_q16=20*R_Q16;
 a->alpha_micro_per_K=12;return 0;
}
int rll_cad_evaluate(const rll_cad_input *a,rll_cad_result *o){
 if(!o||!dim_validate(a))return R_CAD_INVALID_INPUT;
 rll_cad_result r={0};r_i32 half=a->span_mm_q16/2,diag,ratd,ratt,rsq,tmp,top,tie,pr,pq; r_i64 denarea;
 r_u64 len2=(r_u64)(r_i64)half*half+(r_u64)(r_i64)a->rise_mm_q16*a->rise_mm_q16;
 if(checked((r_i64)isqrt64(len2),&diag))return R_CAD_NUMERIC_OVERFLOW;
 if(qd(a->rise_mm_q16,half,&r.tan_angle_q16))return R_CAD_NUMERIC_OVERFLOW;
 /* N_diagonal = P * diagonal_length/(2*rise), T_tie=P*span/(4*rise). */
 if(qd(diag,a->rise_mm_q16*2,&ratd)||qd(half,a->rise_mm_q16*2,&ratt))return R_CAD_NUMERIC_OVERFLOW;
 if(qm(a->downward_load_kN_q16,ratd,&r.diagonal_force_kN_q16)||qm(a->downward_load_kN_q16,ratt,&r.tie_force_kN_q16))return R_CAD_NUMERIC_OVERFLOW;
 if(stress(r.diagonal_force_kN_q16,a->area_diagonal_mm2_q16,&r.diagonal_stress_MPa_q16)||stress(r.tie_force_kN_q16,a->area_tie_mm2_q16,&r.tie_stress_MPa_q16))return R_CAD_NUMERIC_OVERFLOW;
 /* Castigliano vertical compliance; simplified pin-jointed 3-bar triangle. */
 if(qm(ratd,ratd,&rsq)||qm(rsq,diag,&tmp)||qm(tmp,a->downward_load_kN_q16,&tmp))return R_CAD_NUMERIC_OVERFLOW;
 if(checked((r_i64)tmp*2,&top))return R_CAD_NUMERIC_OVERFLOW;
 denarea=r_sdiv64(((r_i64)a->young_GPa_q16*a->area_diagonal_mm2_q16),R_Q16);
 if(bigdiv(top,denarea,&top))return R_CAD_NUMERIC_OVERFLOW;
 if(qm(ratt,ratt,&rsq)||qm(rsq,a->span_mm_q16,&tmp)||qm(tmp,a->downward_load_kN_q16,&tmp))return R_CAD_NUMERIC_OVERFLOW;
 denarea=r_sdiv64(((r_i64)a->young_GPa_q16*a->area_tie_mm2_q16),R_Q16);
 if(bigdiv(tmp,denarea,&tie)||checked((r_i64)top+tie,&r.apex_deflection_mm_q16))return R_CAD_NUMERIC_OVERFLOW;
 /* free expansion mm = span_mm * alpha[1e-6/K] * deltaT[K]. No thermal restraint stress claimed. */
 if(checked(r_sdiv64(((r_i64)a->span_mm_q16*a->deltaT_K_q16*a->alpha_micro_per_K),(1000000LL*R_Q16)),&r.thermal_free_span_mm_q16))return R_CAD_NUMERIC_OVERFLOW;
 /* Pcr Euler kN circular solid bar, pinned-pinned K=1, I=A^2/(4pi). */
 if(qd(a->area_diagonal_mm2_q16,diag,&tmp)||qm(tmp,tmp,&rsq)||qm(a->young_GPa_q16,R_PI_OVER_4_Q16,&pq)||qm(pq,rsq,&r.buckling_limit_kN_q16))return R_CAD_NUMERIC_OVERFLOW;
 if(qd(r.buckling_limit_kN_q16,r.diagonal_force_kN_q16,&r.buckling_ratio_q16))return R_CAD_NUMERIC_OVERFLOW;
 if(qd(a->area_diagonal_mm2_q16,205887,&pr)||checked((r_i64)pr*4,&pr)||qs(pr,&r.diagonal_diameter_mm_q16))return R_CAD_NUMERIC_OVERFLOW;
 if(qd(a->area_tie_mm2_q16,205887,&pr)||checked((r_i64)pr*4,&pr)||qs(pr,&r.tie_diameter_mm_q16))return R_CAD_NUMERIC_OVERFLOW;
 r.diagonal_length_mm_q16=diag;
 if(r.diagonal_stress_MPa_q16>=a->yield_MPa_q16||r.tie_stress_MPa_q16>=a->yield_MPa_q16)r.flags|=R_CAD_WARN_YIELD;
 if(r.buckling_ratio_q16<2*R_Q16)r.flags|=R_CAD_WARN_BUCKLING;
 if(r.apex_deflection_mm_q16>a->span_mm_q16/500)r.flags|=R_CAD_WARN_DEFLECTION;
 /* The free expansion can change compatibility; thermal loads are deliberately NOT computed. */
 r.flags|=R_CAD_WARN_THERMAL_MODEL;
 *o=r;return 0;
}
/* Periodic triangular coordinate: parameter space (S^1)^7, not physical 7D space. */
static r_i32 saw(r_u32 ph){r_u32 x=ph&65535u;return x<32768u ? (r_i32)(-R_Q16+((r_i64)x*4)) : (r_i32)(3*R_Q16-((r_i64)x*4));}
int rll_cad_t7_sample(const rll_cad_input *b,r_u32 i,rll_t7_state *s,rll_cad_input *o){
 static const r_u32 primes[7]={997u,1361u,1999u,2789u,3581u,4441u,5651u};
 static const r_i32 amp[7]={6554,9830,13107,13107,13107,3277,3277};
 r_i32 *d[7];rll_cad_input v; r_i32 f,delta;
 if(!b||!s||!o||i>=42u)return R_CAD_INVALID_INPUT;
 v=*b;d[0]=&v.span_mm_q16;d[1]=&v.rise_mm_q16;d[2]=&v.area_diagonal_mm2_q16;d[3]=&v.area_tie_mm2_q16;
 d[4]=&v.downward_load_kN_q16;d[5]=&v.young_GPa_q16;d[6]=&v.deltaT_K_q16;
 for(r_u32 k=0;k<7;k++){s->coord_q16[k]=saw((i*primes[k])&65535u);if(qm(s->coord_q16[k],amp[k],&delta))return R_CAD_NUMERIC_OVERFLOW;
  if(k==6){if(checked((r_i64)*d[k]+r_sdiv64(((r_i64)delta*(20*R_Q16)),R_Q16),d[k]))return R_CAD_NUMERIC_OVERFLOW;}
  else{if(checked((r_i64)R_Q16+delta,&f)||qm(*d[k],f,d[k]))return R_CAD_NUMERIC_OVERFLOW;}
 }
 s->sample_index=i;if(!dim_validate(&v))return R_CAD_INVALID_INPUT;*o=v;return 0;
}
r_u32 rll_crc32_sw(const r_u8 *data,r_u32 n){r_u32 crc=0xffffffffu; if(!data&&n)return 0;
 for(r_u32 i=0;i<n;i++){crc^=data[i];for(r_u32 j=0;j<8;j++)crc=(crc>>1)^(0xedb88320u&(-(crc&1u)));}return ~crc;}
void rll_add4_scalar(const r_i32 *a,const r_i32 *b,r_i32 *out){for(r_u32 i=0;i<4;i++)out[i]=a[i]+b[i];}
#if defined(__ARM_NEON) || defined(__ARM_NEON__)
#include <arm_neon.h>
void rll_add4_neon(const r_i32 *a,const r_i32 *b,r_i32 *out){vst1q_s32(out,vaddq_s32(vld1q_s32(a),vld1q_s32(b)));}
#else
void rll_add4_neon(const r_i32 *a,const r_i32 *b,r_i32 *out){rll_add4_scalar(a,b,out);}
#endif
