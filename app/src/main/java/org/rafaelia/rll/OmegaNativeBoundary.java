package org.rafaelia.rll;

/** Real JNI/C score boundary tests, limited to overflow-safe x/y and independent Java expectation. */
public final class OmegaNativeBoundary {
    private OmegaNativeBoundary(){}
    private static final int LIMIT=10000;
    public static int[][] vectors() {
        final int[][] fixed={{0,0},{7,11},{1,1},{12,21},{-1,0},{0,-1},
          {-1,-1},{LIMIT,LIMIT},{-LIMIT,-LIMIT},{LIMIT,-LIMIT},{-LIMIT,LIMIT},
          {LIMIT,0},{0,-LIMIT},{0,LIMIT},{LIMIT,-1},{-LIMIT,1}};
        int[][] rows=new int[fixed.length+64][2];
        for(int i=0;i<fixed.length;i++){rows[i][0]=fixed[i][0];rows[i][1]=fixed[i][1];}
        long seed=0x524C4C31L;
        for(int i=fixed.length;i<rows.length;i++){
            seed=(seed*1664525L+1013904223L)&0xffffffffL;
            rows[i][0]=(int)(seed%20001L)-10000;
            seed=(seed*1664525L+1013904223L)&0xffffffffL;
            rows[i][1]=(int)(seed%20001L)-10000;
        }
        return rows;
    }
    public static int oracle(int x,int y,int arch){
        if(x < -LIMIT || x > LIMIT || y < -LIMIT || y > LIMIT)
            throw new IllegalArgumentException("OUT_OF_SAFE_BOUNDARY");
        return ((x*31)^(y*17))+arch;
    }
    public static final class Result {
        public final String receipt;
        public final int attempted,passed,failed;
        public final String state;
        Result(String receipt,int attempted,int passed,int failed,String state){
            this.receipt=receipt;this.attempted=attempted;this.passed=passed;
            this.failed=failed;this.state=state;
        }
    }
    public static Result run(String uiX,String uiY) {
        StringBuilder rows=new StringBuilder("schema=rll.omega.jni-c-boundary.v1\n"
          +"origin=LIVE_ANDROID_JNI_SCORE_CALL_NOT_INDEPENDENT_ATTESTATION\n"
          +"model=C_KERNEL_SCORE_NOT_COSMOLOGY\n"
          +"vector_kind\tx\ty\tarch\tC_score\tJava_reference\tstate\n");
        int attempted=0,passed=0,failed=0;
        try {
            int arch=KernelBridge.archDetect();
            if(arch!=32&&arch!=64){
                rows.append("gate=FAIL_ARCH_UNKNOWN\n");
                return new Result(rows.toString(),0,0,1,"FAIL_ARCH_UNKNOWN");
            }
            for(int[] xy:vectors()){
                int actual=KernelBridge.kernelScore(xy[0],xy[1]);
                int oracle=oracle(xy[0],xy[1],arch);
                boolean ok=actual==oracle;
                attempted++;if(ok)passed++;else failed++;
                rows.append("DETERMINISTIC_BOUNDARY\t").append(xy[0]).append('\t')
                 .append(xy[1]).append('\t').append(arch).append('\t')
                 .append(actual).append('\t').append(oracle)
                 .append('\t').append(ok?"PASS_SCOPED":"FAIL_NUMERIC").append('\n');
            }
            try {
                int x=Integer.parseInt(uiX.trim()),y=Integer.parseInt(uiY.trim());
                if(x < -LIMIT || x > LIMIT || y < -LIMIT || y > LIMIT)
                    throw new IllegalArgumentException("UI_INPUT_OUT_OF_SAFE_RANGE");
                int value=KernelBridge.kernelScore(x,y),ref=oracle(x,y,arch);
                boolean ok=value==ref;
                attempted++;if(ok)passed++;else failed++;
                rows.append("USER_UI_MANUAL\t").append(x).append('\t').append(y).append('\t')
                 .append(arch).append('\t').append(value).append('\t').append(ref)
                 .append('\t').append(ok?"PASS_SCOPED":"FAIL_NUMERIC").append('\n');
            }catch(RuntimeException ex){
                rows.append("USER_UI_MANUAL\tTOKEN_VAZIO\tTOKEN_VAZIO\t")
                 .append(arch).append("\tTOKEN_VAZIO\tTOKEN_VAZIO\tTOKEN_VAZIO_")
                 .append(ex.getClass().getSimpleName()).append('\n');
            }
            String state=failed==0&&attempted>=80?"PASS_SCOPED_JNI_BOUNDARIES":"FAIL_JNI_BOUNDARIES";
            rows.append("attempted=").append(attempted).append("\npassed=").append(passed)
                .append("\nfailed=").append(failed).append("\ngate=").append(state)
                .append("\nexternal_hardware_attestation=TOKEN_VAZIO_NOT_RUN\n");
            return new Result(rows.toString(),attempted,passed,failed,state);
        }catch(LinkageError|RuntimeException ex){
            rows.append("gate=FAIL_JNI_BRIDGE_").append(ex.getClass().getSimpleName()).append('\n');
            return new Result(rows.toString(),attempted,passed,failed+1,"FAIL_JNI_BRIDGE");
        }
    }
}
