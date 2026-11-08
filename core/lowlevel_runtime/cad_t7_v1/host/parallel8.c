/* Hosted Android/Linux worker boundary; freestanding kernels remain thread/OS agnostic.
 * Eight threads do NOT imply eight physical cores, SIMD acceleration or cache residency. */
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include "../core/rll_cad.h"
#define SHARDS 8
#define N 42
/* <64KiB shared contiguous storage; 42 × (36+52+32) = 5040 bytes */
static struct {rll_cad_input a;rll_cad_result r;rll_t7_state s;int rc;} work[N];
static rll_cad_input b;
static void *worker(void *opaque){
 unsigned lane=(unsigned)(uintptr_t)opaque;
 for(unsigned i=lane;i<N;i+=SHARDS){
   work[i].rc=rll_cad_t7_sample(&b,i,&work[i].s,&work[i].a);
   if(!work[i].rc)work[i].rc=rll_cad_evaluate(&work[i].a,&work[i].r);
 }
 return 0;
}
int main(void){
 if(rll_cad_baseline(&b))return 2;
 pthread_t threads[SHARDS];
 for(unsigned t=0;t<SHARDS;t++)if(pthread_create(&threads[t],0,worker,(void*)(uintptr_t)t))return 3;
 for(unsigned t=0;t<SHARDS;t++)if(pthread_join(threads[t],0))return 4;
 for(unsigned i=0;i<N;i++){
  rll_cad_input a;rll_cad_result r;rll_t7_state s;
  if(work[i].rc||rll_cad_t7_sample(&b,i,&s,&a)||rll_cad_evaluate(&a,&r))return 5;
  if(s.sample_index!=work[i].s.sample_index)return 6;
  for(unsigned k=0;k<7;k++)if(s.coord_q16[k]!=work[i].s.coord_q16[k])return 7;
  const r_i32 *x=(const r_i32*)&r;const r_i32*y=(const r_i32*)&work[i].r;
  for(unsigned k=0;k<13;k++)if(x[k]!=y[k])return 8;
 }
 printf("PASS_SCOPED_HOST_8_THREADS_SERIAL_BIT_EXACT cases=%d shared_bytes=%zu\n",N,sizeof(work));
 return 0;
}
