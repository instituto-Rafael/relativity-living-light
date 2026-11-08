/* Hosted I/O harness. ALL mathematical operations are in freestanding core. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "../core/rll_cad.h"
static char svg[12288];
static double f(r_i32 x){return (double)x/65536.;}
int main(int argc,char**argv){
 if(argc!=3){fprintf(stderr,"usage: runner drawing.svg models.json\n");return 2;}
 rll_cad_input b,v;rll_cad_result y;rll_t7_state st;
 if(rll_cad_baseline(&b)||rll_cad_evaluate(&b,&y)){fputs("BASELINE_FAIL\n",stderr);return 3;}
 int n=rll_cad_emit_svg(&b,&y,svg,sizeof(svg));if(n<0){fputs("SVG_BUFFER_FAIL\n",stderr);return 4;}
 FILE *out=fopen(argv[1],"wb");if(!out)return 5;
 if(fwrite(svg,1,(size_t)n,out)!=(size_t)n){fclose(out);return 6;}fclose(out);
 FILE *json=fopen(argv[2],"wb");if(!json)return 7;
 fprintf(json,"{\"schema\":\"rll.t7_cad_truss.v1\",\"units\":{\"length\":\"mm\",\"force\":\"kN\",\"stress\":\"MPa\",\"young\":\"GPa\"},\"claim_allowed\":false,\"certified\":false,\"physics\":\"2D_PIN_JOINT_AXIALLY_LOADED_TRUSS_ONLY\",\"baseline\":{");
 fprintf(json,"\"L_mm\":%.8f,\"H_mm\":%.8f,\"Ad_mm2\":%.8f,\"At_mm2\":%.8f,\"P_kN\":%.8f,\"E_GPa\":%.8f,\"yield_MPa\":%.8f,\"deltaT_K\":%.8f,\"alpha_micro_per_K\":%d,",
 f(b.span_mm_q16),f(b.rise_mm_q16),f(b.area_diagonal_mm2_q16),f(b.area_tie_mm2_q16),f(b.downward_load_kN_q16),f(b.young_GPa_q16),f(b.yield_MPa_q16),f(b.deltaT_K_q16),b.alpha_micro_per_K);
 fprintf(json,"\"diag_kN\":%.8f,\"tie_kN\":%.8f,\"stress_diag_MPa\":%.8f,\"deflection_mm\":%.8f,\"free_expansion_mm\":%.8f,\"euler_kN\":%.8f,\"buckling_ratio\":%.8f,\"flags\":%u},\"samples\":[",
 f(y.diagonal_force_kN_q16),f(y.tie_force_kN_q16),f(y.diagonal_stress_MPa_q16),f(y.apex_deflection_mm_q16),f(y.thermal_free_span_mm_q16),f(y.buckling_limit_kN_q16),f(y.buckling_ratio_q16),y.flags);
 for(unsigned i=0;i<42;i++){
  if(rll_cad_t7_sample(&b,i,&st,&v)||rll_cad_evaluate(&v,&y)){fclose(json);fputs("T7_FAIL\n",stderr);return 8;}
  fprintf(json,"%s{\"sample\":%u,\"t7_q16\":[",i?",":"",i);
  for(int j=0;j<7;j++)fprintf(json,"%s%d",j?",":"",st.coord_q16[j]);
  fprintf(json,"],\"in_q16\":[%d,%d,%d,%d,%d,%d,%d,%d],\"alpha_micro\":%d,",
 v.span_mm_q16,v.rise_mm_q16,v.area_diagonal_mm2_q16,v.area_tie_mm2_q16,v.downward_load_kN_q16,v.young_GPa_q16,v.yield_MPa_q16,v.deltaT_K_q16,v.alpha_micro_per_K);
  fprintf(json,"\"out_q16\":[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d],\"flags\":%u}",
 y.diagonal_length_mm_q16,y.tan_angle_q16,y.diagonal_force_kN_q16,y.tie_force_kN_q16,
 y.diagonal_stress_MPa_q16,y.tie_stress_MPa_q16,y.apex_deflection_mm_q16,y.thermal_free_span_mm_q16,
 y.buckling_limit_kN_q16,y.buckling_ratio_q16,y.diagonal_diameter_mm_q16,y.tie_diameter_mm_q16,y.flags);
 }
 fprintf(json,"],\"claim_state\":\"ILLUSTRATIVE_NOT_A_PHYSICAL_7D_SPACE\",\"missing\":[\"beam_shear\",\"torsion\",\"bending\",\"restrained_thermal_load\",\"dynamic_seismic\",\"nonlinear_buckling\",\"connection_failure\",\"soil_foundation\",\"code_compliance\"]}\n");
 fclose(json);r_u32 crc=rll_crc32_sw((const r_u8*)svg,(r_u32)n);
 printf("SVG_BYTES=%d SVG_CRC32=%08x\n",n,crc);
 return 0;
}
