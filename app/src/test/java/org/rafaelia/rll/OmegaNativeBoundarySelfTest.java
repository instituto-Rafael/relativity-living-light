package org.rafaelia.rll;

/** JNI kernel score vectors are generated deterministically without loading Android JNI in hosted tests. */
public final class OmegaNativeBoundarySelfTest {
    public static void main(String[] args) {
        int[][] vectors=OmegaNativeBoundary.vectors();
        if(vectors.length!=80)throw new AssertionError("expected 80 deterministic boundary vectors");
        if(OmegaNativeBoundary.oracle(7,11,32)!=130)
            throw new AssertionError("ARM32 reference 7/11");
        if(OmegaNativeBoundary.oracle(0,0,64)!=64)
            throw new AssertionError("ARM64 reference 0/0");
        for(int[] row:vectors)if(row[0]<-10000||row[0]>10000||row[1]<-10000||row[1]>10000)
            throw new AssertionError("vector overflow risk");
        try {
            OmegaNativeBoundary.oracle(Integer.MIN_VALUE,1,32);
            throw new AssertionError("int min must be rejected");
        }catch(IllegalArgumentException expected) {}
        System.out.println("RLL_OMEGA_JNI_BOUNDARY_VECTOR_PLAN_PASS vectors=80 local JNI NOT_RUN");
    }
}
