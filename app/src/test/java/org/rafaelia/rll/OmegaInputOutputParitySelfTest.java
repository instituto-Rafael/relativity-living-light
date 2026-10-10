package org.rafaelia.rll;

import java.util.LinkedHashMap;
import java.util.Map;

/** Hosted source-side falsifiers: same inputs -> same deterministic outputs, no silent omissions. */
public final class OmegaInputOutputParitySelfTest {
    private static int checks=0;
    private static void ok(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    private static Map<String,String> fields(){
        FormulaEngine.Input p=new FormulaEngine.Input();
        Map<String,String> f=new LinkedHashMap<>();
        f.put("z",Double.toString(p.z));f.put("H0",Double.toString(p.h0));
        f.put("Om",Double.toString(p.om));f.put("OL",Double.toString(p.ol));
        f.put("Os0",Double.toString(p.os0));f.put("zt",Double.toString(p.zt));
        f.put("wt",Double.toString(p.wt));f.put("w",Double.toString(p.w));
        f.put("w0",Double.toString(p.w0));f.put("wa",Double.toString(p.wa));
        f.put("Obh2",Double.toString(p.obh2));f.put("sigma8",Double.toString(p.sigma8));
        f.put("Hobs","");f.put("Hsigma","");
        return f;
    }
    private static OmegaInputOutputParity.Result parity(OmegaUiEvidence.Snapshot s){
        return OmegaInputOutputParity.reconcile(s,OmegaUiEvidence.replay(s));
    }
    public static void main(String[] args){
        Map<String,String> f=fields();
        OmegaUiEvidence.Snapshot a=new OmegaUiEvidence.Snapshot("RLL","COS-HZ",f,1L);
        OmegaUiEvidence.Snapshot b=new OmegaUiEvidence.Snapshot("RLL","COS-HZ",f,9999999L);
        OmegaInputOutputParity.Result p=parity(a),q=parity(b);
        ok(p.gate.equals("PASS_ZERO_OMITTED_OUTPUT_RECEIPTS"),"expected complete coverage");
        ok(p.expected==109&&p.verified==109&&p.missing==0,
             "14 inputs + 4x3 output artifacts + 78 formula receipts + 5 UI actions");
        ok(p.unknownNumeric==16,"four scientifically missing numerical values per model are explicit");
        ok(p.inputSha256.equals(q.inputSha256),"wall clock must not alter normalized input hash");
        ok(p.outputSha256.equals(q.outputSha256),"wall clock must not alter deterministic outputs");
        ok(p.files.get("23_IO_PARITY/outputs.tsv").contains("VALUE_UNDETERMINED_BY_SOURCE_BOUNDARY"),
             "no fabricated observational/cosmological values");
        ok(p.files.get("23_IO_PARITY/closure_receipt.txt").contains("omitted_output_receipts=0"),
             "no silently dropped formula");
        f.put("z","0.570000000");
        OmegaInputOutputParity.Result normalized=parity(new OmegaUiEvidence.Snapshot("RLL","COS-HZ",f,7L));
        ok(p.inputSha256.equals(normalized.inputSha256),"equivalent decimal input spelling");
        ok(p.outputSha256.equals(normalized.outputSha256),"equivalent inputs yield identical outputs");
        f.put("z","0.58");
        OmegaInputOutputParity.Result changed=parity(new OmegaUiEvidence.Snapshot("RLL","COS-HZ",f,8L));
        ok(!p.inputSha256.equals(changed.inputSha256),"modified numeric input changes identity");
        ok(!p.outputSha256.equals(changed.outputSha256),"modified numeric input changes calculations");
        OmegaUiEvidence.Result truncated=OmegaUiEvidence.replay(a);
        truncated.files.remove("22_UI/current_RLL/individual/COS-HZ.receipt.txt");
        OmegaInputOutputParity.Result missing=OmegaInputOutputParity.reconcile(a,truncated);
        ok(missing.gate.equals("FAIL_MISSING_OUTPUT_RECEIPTS")&&missing.missing==1,
            "a single missing individual formula must fail the parity gate");
        OmegaUiEvidence.Result switched=OmegaUiEvidence.replay(a);
        switched.files.put("22_UI/frozen_inputs.txt",
             switched.files.get("22_UI/frozen_inputs.txt").replace("z=0.57","z=0.58"));
        OmegaInputOutputParity.Result tampered=OmegaInputOutputParity.reconcile(a,switched);
        ok(tampered.gate.equals("FAIL_MISSING_OUTPUT_RECEIPTS")&&tampered.missing>=1,
            "tampered frozen input must fail even when all formula files still exist");
        Map<String,String> exponent=fields();exponent.put("z","1e1000000000");
        OmegaInputOutputParity.Result huge=parity(
            new OmegaUiEvidence.Snapshot("RLL","COS-HZ",exponent,4));
        ok(!huge.gate.startsWith("PASS"),"untrusted huge exponent must fail safely");
        ok(huge.files.get("23_IO_PARITY/inputs.tsv").contains(
            "INVALID_NUMBER:MAGNITUDE_OR_PRECISION_BOUND"),
            "huge exponent normalized as bounded invalid input, not OOM");
        Map<String,String> bad=fields();bad.put("Hobs","93.4");bad.put("Hsigma","");
        OmegaInputOutputParity.Result invalid=parity(
            new OmegaUiEvidence.Snapshot("RLL","COS-HZ",bad,3L));
        ok(!invalid.gate.startsWith("PASS"),"incomplete physical observation must fail");
        ok(invalid.files.get("23_IO_PARITY/inputs.tsv").contains("Hobs\t93.4"),
            "the original incomplete input must remain observable");
        System.out.println("RLL_OMEGA_INPUT_OUTPUT_PARITY_PASS assertions="+checks+
             " expected="+p.expected+" verified="+p.verified+" numeric_unknowns="+p.unknownNumeric);
    }
}
