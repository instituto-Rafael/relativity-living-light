package org.rafaelia.rll;

/** Pure JVM differential/falsifier scope, no Android or network. */
public final class OmegaCrossModelComparisonSelfTest {
    public static void main(String[] args) {
        OmegaCrossModelComparison.Result r=OmegaCrossModelComparison.run();
        if(r.comparisons!=66)throw new AssertionError("six pairs x 11 z");
        if(r.failed!=0)throw new AssertionError("numeric or nested falsifier failed: "+r.failed+"\n"+r.nestedChecks);
        if(r.passed!=143)throw new AssertionError("44 model + 66 paired + 33 nested checks, got "+r.passed);
        for(String id:new String[]{"LCDM","WCDM","CPL","RLL"})
            if(!r.modelRows.contains(id+","))
                throw new AssertionError("missing model "+id);
        if(r.pairRows.split("\n").length!=67)
            throw new AssertionError("all pairwise deltas required");
        if(r.nestedChecks.split("\n").length!=34)
            throw new AssertionError("33 nested falsifiers required");
        if(!r.nestedChecks.contains("PASS_SCOPED_NESTED"))
            throw new AssertionError("no nested results");
        System.out.println("RLL_OMEGA_CROSS_MODEL_PASS paired="+r.comparisons+" checks="+r.passed+" failed=0");
    }
}
