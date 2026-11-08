/* Android hosted ABI (Bionic/JNI); NOT part of the freestanding core.
 * Compile with Android NDK JNI headers, link freestanding core objects and Bionic.
 * Android ART loads native ELF .so through JNI; DEX is NOT itself an ELF executable.
 */
#include <jni.h>
#include "../core/rll_cad.h"
JNIEXPORT jint JNICALL Java_org_rafaelia_rllcad_RllCadBridge_evaluate(
 JNIEnv *env, jclass ignored, jintArray input, jintArray output){
 (void)ignored;
 if(!input||!output||(*env)->GetArrayLength(env,input)!=9||(*env)->GetArrayLength(env,output)<13)
     return R_CAD_INVALID_INPUT;
 jint a[9],b[13];
 (*env)->GetIntArrayRegion(env,input,0,9,a);
 if((*env)->ExceptionCheck(env))return R_CAD_INVALID_INPUT;
 rll_cad_input in={a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8]};
 rll_cad_result out;
 int rc=rll_cad_evaluate(&in,&out);if(rc)return rc;
 b[0]=out.diagonal_length_mm_q16;b[1]=out.tan_angle_q16;
 b[2]=out.diagonal_force_kN_q16;b[3]=out.tie_force_kN_q16;
 b[4]=out.diagonal_stress_MPa_q16;b[5]=out.tie_stress_MPa_q16;
 b[6]=out.apex_deflection_mm_q16;b[7]=out.thermal_free_span_mm_q16;
 b[8]=out.buckling_limit_kN_q16;b[9]=out.buckling_ratio_q16;
 b[10]=out.diagonal_diameter_mm_q16;b[11]=out.tie_diameter_mm_q16;
 b[12]=(jint)out.flags;
 (*env)->SetIntArrayRegion(env,output,0,13,b);
 return (*env)->ExceptionCheck(env)?R_CAD_INVALID_INPUT:R_CAD_OK;
}
