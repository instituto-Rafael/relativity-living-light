package org.rafaelia.rll;

import java.util.Locale;

/** Independent algebraic, numerical and domain checks for implemented hosted formulas.
 * Checks are verification controls, not independent physical cosmology.
 */
public final class OmegaScientificChecks {
    private OmegaScientificChecks(){}
    public static final class Result {
        public final String tsv;
        public final int passed,failed;
        Result(String text,int p,int f){tsv=text;passed=p;failed=f;}
    }
    private static final class Collector {
        final StringBuilder b=new StringBuilder("check_id\tstate\tmeasured\ttolerance\tscope\n");
        int passed=0,failed=0;
        void measure(String id,boolean ok,double x,double tol,String scope) {
            b.append(id).append('\t').append(ok?"PASS_SCOPED":"FAIL_NUMERIC").append('\t')
                .append(Double.toString(x)).append('\t').append(Double.toString(tol))
                .append('\t').append(scope).append('\n');
            if(ok)passed++;else failed++;
        }
        void typed(String id,String state,String why){
            b.append(id).append('\t').append(state).append("\tTOKEN_VAZIO\tTOKEN_VAZIO\t")
                .append(why).append('\n');
        }
    }
    private static double entry(FormulaEngine.Result r,String id) {
        for(FormulaEngine.Entry f:r.entries) if(id.equals(f.id)) return f.value==null?Double.NaN:f.value;
        return Double.NaN;
    }
    public static Result run(){
        Collector c=new Collector();
        FormulaEngine.Input p=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
        for(FormulaEngine.Model m:FormulaEngine.Model.values()){
            p=RealBaoEngine.baseline(m);
            double e0=FormulaEngine.e2(0,m,p);
            c.measure(m+"_E2_AT_Z0",Double.isFinite(e0)&&Math.abs(e0-1)<1e-12,
                Math.abs(e0-1),1e-12,"ALGEBRAIC_NORMALIZATION_ONLY");
            p.z=0.0; // H(z=0) must equal the input H0 after E²(0) closure.
            FormulaEngine.Result r=FormulaEngine.compute(p,m);
            c.measure(m+"_H0_AT_Z0",Math.abs(entry(r,"COS-HZ")-p.h0)<1e-10,
                Math.abs(entry(r,"COS-HZ")-p.h0),1e-10,"BACKGROUND_NUMERIC");
            // First-order Hubble law, evaluated with exactly the same r_drag convention.
            double h=p.h0/100.0;
            double rd=147.78*Math.pow((p.om*h*h)/.1432,-.255)
                           *Math.pow(p.obh2/.02236,-.134);
            double predicted=RealBaoEngine.prediction(1e-6,"DM_over_rs",m,p);
            double firstOrder=FormulaEngine.C_KMS/p.h0/rd*1e-6;
            double relative=Math.abs(predicted-firstOrder)/Math.max(1e-16,Math.abs(firstOrder));
            c.measure(m+"_LOW_Z_DISTANCE",Double.isFinite(relative)&&relative<1e-5,
                      relative,1e-5,"SMALL_Z_HUBBLE_LIMIT_ONLY");
        }
        p=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
        p.z=.57;
        double lc=FormulaEngine.e2(.57,FormulaEngine.Model.LCDM,p);
        p.w=-1;
        c.measure("WCDM_W_MINUS_ONE_LCDM",Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.WCDM,p))<1e-13,
                  Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.WCDM,p)),1e-13,"NESTED_MODEL_EQUIVALENCE");
        p.w0=-1;p.wa=0;
        c.measure("CPL_NULL_REDUCES_LCDM",Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.CPL,p))<1e-13,
                  Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.CPL,p)),1e-13,"NESTED_MODEL_EQUIVALENCE");
        p.os0=0;
        c.measure("RLL_NULL_SECTOR_REDUCES_LCDM",Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.RLL,p))<1e-13,
                  Math.abs(lc-FormulaEngine.e2(.57,FormulaEngine.Model.RLL,p)),1e-13,"NESTED_MODEL_EQUIVALENCE");
        p=RealBaoEngine.baseline(FormulaEngine.Model.RLL);p.z=.57;
        FormulaEngine.Result r=FormulaEngine.compute(p,FormulaEngine.Model.RLL);
        double continuity=entry(r,"RLL-CONTINUITY-CONS");
        c.measure("RLL_CONSERVED_IDENTITY",Double.isFinite(continuity)&&Math.abs(continuity)<1e-12,
                  Math.abs(continuity),1e-12,"ALGEBRAIC_RECONSTRUCTION_ONLY");
        double mismatch=entry(r,"RLL-CONTINUITY-DOC");
        c.measure("RLL_DOCUMENTED_PRESSURE_DIFFERENCE_RETAINED",
                  Double.isFinite(mismatch)&&Math.abs(mismatch)>1e-6,mismatch,1e-6,"FALSIFIABLE_CONVENTION_DIFFERENCE");
        for(FormulaEngine.Model m:FormulaEngine.Model.values()){
            p=RealBaoEngine.baseline(m);p.z=.57;
            r=FormulaEngine.compute(p,m);
            double quadrature=entry(r,"COS-DM-QUADRATURE-DELTA");
            c.measure(m+"_SIMPSON_128_256",Double.isFinite(quadrature)&&quadrature<1e-4,
                      quadrature,1e-4,"NUMERICAL_QUADRATURE_ONLY");
        }
        p=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
        p.wt=0;
        r=FormulaEngine.compute(p,FormulaEngine.Model.RLL);
        c.measure("REJECT_WIDTH_ZERO","TOKEN_VAZIO_DOMAIN_INPUT".equals(r.state),r.computed,0,"FAIL_CLOSED_DOMAIN");
        p=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
        p.z=Double.NaN;
        r=FormulaEngine.compute(p,FormulaEngine.Model.LCDM);
        c.measure("REJECT_NONFINITE_REDSHIFT","TOKEN_VAZIO_DOMAIN_INPUT".equals(r.state),r.computed,0,"FAIL_CLOSED_DOMAIN");
        double closure=RealBaoEngine.torusClosure(2.0,.7);
        c.measure("TORUS_PARAMETRIC_LOOP_CLOSED",closure<1e-12,closure,1e-12,"GEOMETRY_ONLY_NOT_POINCARE_RECURRENCE");
        c.typed("COSMBO_CMB_RS","TOKEN_VAZIO_NOT_RUN","BOLTZMANN_R_S");
        c.typed("DYNAMIC_POINCARE","TOKEN_VAZIO_NO_TRAJECTORY","NO_TIME_SERIES");
        c.typed("RMRCTI_DELTA_P","TOKEN_VAZIO_NO_PEAK_STABLE_TRACE","NO_CTIC_DATA");
        c.typed("OFFICIAL_DESI_POSTERIOR","TOKEN_VAZIO_NOT_RUN","MODEL_SPECIFIC_PRIORS");
        c.typed("INDEPENDENT_ANDROID_ATTESTATION","TOKEN_VAZIO_NOT_RUN","NEEDS_EXTERNAL_WITNESS");
        return new Result(c.b.toString(),c.passed,c.failed);
    }
}
