package org.rafaelia.rll;

/** Pure Java regression, no Android framework required. */
public final class OmegaScientificChecksSelfTest {
    public static void main(String[] args) {
        OmegaScientificChecks.Result r=OmegaScientificChecks.run();
        if(r.failed!=0)throw new AssertionError("NUMERIC_FAIL "+r.failed+"\n"+r.tsv);
        if(r.passed<24)throw new AssertionError("Incomplete quantitative gates: "+r.passed);
        if(!r.tsv.contains("TOKEN_VAZIO_NO_TRAJECTORY")||
           !r.tsv.contains("TOKEN_VAZIO_NO_PEAK_STABLE_TRACE")||
           !r.tsv.contains("RLL_CONSERVED_IDENTITY\tPASS_SCOPED")||
           !r.tsv.contains("SIMPSON_128_256\tPASS_SCOPED"))
            throw new AssertionError("Missing scientific boundary or core formulas");
        if(r.tsv.split("\n").length<30)throw new AssertionError("Gates not complete");
        System.out.println("RLL_OMEGA_SCIENCE_CHECKS_PASS checks="+r.passed+" typed=5 physical_validation=NOT_RUN");
    }
}
