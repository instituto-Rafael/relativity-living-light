package org.rafaelia.rll;

/** No Android deps, reproducible deterministic algebraic/negative falsifiers. */
public final class FormulaEngineSelfTest {
    private static int assertions=0;
    private static void check(boolean pass,String detail) {
        assertions++;if(!pass)throw new AssertionError(detail);
    }
    private static void near(double actual,double expected,double tol,String detail) {
        check(Double.isFinite(actual)&&Math.abs(actual-expected)<=tol,detail+" actual="+actual+" expected="+expected);
    }
    private static FormulaEngine.Entry entry(FormulaEngine.Result result,String id) {
        for(FormulaEngine.Entry e:result.entries)if(id.equals(e.id))return e;
        throw new AssertionError("Missing entry: "+id);
    }
    public static void main(String[] args) {
        FormulaEngine.Input a=new FormulaEngine.Input();
        near(FormulaEngine.closedOl(a,FormulaEngine.Model.RLL),a.ol,1e-12,"RLL default closure");
        near(FormulaEngine.e2(0,FormulaEngine.Model.RLL,a),1.0,1e-12,"RLL E2(0)");
        a.ol=FormulaEngine.closedOl(a,FormulaEngine.Model.LCDM);
        near(FormulaEngine.e2(0,FormulaEngine.Model.LCDM,a),1.0,1e-12,"LCDM E2(0)");
        near(FormulaEngine.e2(a.z,FormulaEngine.Model.LCDM,a),FormulaEngine.e2(a.z,FormulaEngine.Model.WCDM,a),1e-12,"wCDM w=-1 reduction");
        a.w0=-1.0;a.wa=0.0;
        near(FormulaEngine.e2(a.z,FormulaEngine.Model.LCDM,a),FormulaEngine.e2(a.z,FormulaEngine.Model.CPL,a),1e-12,"CPL LCDM null");
        a.os0=0;
        near(FormulaEngine.e2(a.z,FormulaEngine.Model.LCDM,a),FormulaEngine.e2(a.z,FormulaEngine.Model.RLL,a),1e-12,"RLL Os0=0 LCDM null");
        FormulaEngine.Result nullRll=FormulaEngine.compute(a,FormulaEngine.Model.RLL);
        check(entry(nullRll,"RLL-NULL-SECTOR").value==null,"null sector unidentifiable");
        check(nullRll.receipt(a).contains("claim_allowed=false"),"no scientific claim");
        a.os0=0.059;a.ol=FormulaEngine.closedOl(a,FormulaEngine.Model.RLL);
        FormulaEngine.Result r=FormulaEngine.compute(a,FormulaEngine.Model.RLL);
        check(r.computed>=20,"RLL formula coverage");
        check(r.gap>=4,"typed gaps");
        near(entry(r,"COS-E2-ZERO").value,1,1e-12,"normalization");
        near(entry(r,"RLL-CONTINUITY-CONS").value,0,1e-12,"conserved residual identity");
        check(Math.abs(entry(r,"RLL-CONTINUITY-DOC").value)>1e-3,"documented residual must not be falsely zero");
        check(entry(r,"COS-RD-PROXY").value>100,"rd positive");
        check(entry(r,"COS-DM-FLAT").value>0,"distance positive");
        check(entry(r,"COS-DM-QUADRATURE-DELTA").value<1e-4,"Simpson refinement");
        check(entry(r,"COS-DH-RD").value>0,"dh/rd");
        check(entry(r,"COS-CMB-RS").value==null,"CMB must not be faked");
        check(entry(r,"COS-JOINT-FIT").value==null,"joint fit not executed");
        check(entry(r,"COS-H-OBSERVATION").value==null,"no observed data invented");
        String receipt=r.receipt(a);
        check(receipt.contains("observation_status=TOKEN_VAZIO_NOT_PROVIDED"),"typed missing observation");
        check(receipt.contains("Hobs=TOKEN_VAZIO;Hsigma=TOKEN_VAZIO"),"missing pair explicit");
        check(receipt.contains("provenance=USER_INPUT_NOT_REAL_OBSERVATION"),"typed provenance");
        check(receipt.contains("boltzmann_camb_class=TOKEN_VAZIO_NOT_RUN"),"typed Boltzmann gap");
        double hz=entry(r,"COS-HZ").value;
        a.hObserved=hz;a.hSigma=4.0;
        FormulaEngine.Result measured=FormulaEngine.compute(a,FormulaEngine.Model.RLL);
        String measuredReceipt=measured.receipt(a);
        check(measuredReceipt.contains("schema=rll.android.formula-lab.v2"),"v2 receipt contract");
        check(measuredReceipt.contains("observation_status=USER_ENTERED_UNVERIFIED"),"observation input typed");
        check(measuredReceipt.contains("Hobs="+Double.toString(hz)+";Hsigma=4.0"),
              "observed H and sigma can be reconstructed exactly");
        near(entry(measured,"COS-H-CHI2-ONE").value,0,1e-20,"manual point exact fit");
        a.hObserved=hz+8;
        measured=FormulaEngine.compute(a,FormulaEngine.Model.RLL);
        near(entry(measured,"COS-H-RESIDUAL").value,2,1e-10,"standardized residual");
        near(entry(measured,"COS-H-CHI2-ONE").value,4,1e-10,"chi squared one point");
        a.hSigma=Double.NaN;
        FormulaEngine.Result invalidPair=FormulaEngine.compute(a,FormulaEngine.Model.RLL);
        check(invalidPair.state.equals("TOKEN_VAZIO_DOMAIN_INPUT"),"partial observation rejected");
        check(invalidPair.receipt(a).contains("observation_status=TOKEN_VAZIO_INVALID_PAIR"),
              "partial pair evidence must not be typed as absent");
        a.hObserved=Double.NaN;
        a.h0=Double.NaN;
        check(FormulaEngine.compute(a,FormulaEngine.Model.LCDM).state.equals("TOKEN_VAZIO_DOMAIN_INPUT"),"NaN rejected");
        a.h0=67.4;a.wt=0;
        check(FormulaEngine.compute(a,FormulaEngine.Model.RLL).state.equals("TOKEN_VAZIO_DOMAIN_INPUT"),"zero width rejected");
        a.wt=.405;a.z=-.01;
        check(FormulaEngine.compute(a,FormulaEngine.Model.RLL).state.equals("TOKEN_VAZIO_DOMAIN_INPUT"),"negative redshift rejected");
        a.z=0.57;a.om=0.315;a.ol=-2.0;
        check(FormulaEngine.compute(a,FormulaEngine.Model.LCDM).state.equals("TOKEN_VAZIO_E2_NONPOSITIVE"),"no sqrt floor for nonpositive E2");
        a.ol=FormulaEngine.closedOl(a,FormulaEngine.Model.LCDM);
        a.z=1e-5;
        FormulaEngine.Result nearZero=FormulaEngine.compute(a,FormulaEngine.Model.LCDM);
        double dc=entry(nearZero,"COS-DM-FLAT").value;
        near(dc,FormulaEngine.C_KMS/a.h0*a.z,0.001,"small-z Hubble distance");
        a.z=0;
        check(entry(FormulaEngine.compute(a,FormulaEngine.Model.LCDM),"COS-DM-FLAT").value==0,"z0 distance zero");
        // Same manually supplied observation and uncertainty imply the same residual definition.
        // It is invalid to rank models by chi2 from different user-input pairs.
        FormulaEngine.Input compare=new FormulaEngine.Input();
        compare.hObserved=91.2;
        compare.hSigma=4.0;
        compare.ol=FormulaEngine.closedOl(compare,FormulaEngine.Model.RLL);
        FormulaEngine.Result compareR=FormulaEngine.compute(compare,FormulaEngine.Model.RLL);
        double hR=entry(compareR,"COS-HZ").value;
        double resR=entry(compareR,"COS-H-RESIDUAL").value;
        compare.ol=FormulaEngine.closedOl(compare,FormulaEngine.Model.WCDM);
        FormulaEngine.Result compareW=FormulaEngine.compute(compare,FormulaEngine.Model.WCDM);
        double hW=entry(compareW,"COS-HZ").value;
        double resW=entry(compareW,"COS-H-RESIDUAL").value;
        near((resR-resW)*compare.hSigma,hW-hR,1e-11,"shared Hobs/sigma cross-model invariant");
        check(compareR.receipt(compare).contains("Hobs=91.2;Hsigma=4.0"),"user source retained");
        check(compareW.receipt(compare).contains("observation_status=USER_ENTERED_UNVERIFIED"),
              "paired provenance retained");
        check(!compareR.receipt(compare).contains("physical_validation=PASS"),"claim gate remains closed");
        System.out.println("RLL_FORMULA_ENGINE_SELFTEST_PASS assertions="+assertions
            +" families=4 source=joint_real_likelihood+check_rll_background");
    }
}
