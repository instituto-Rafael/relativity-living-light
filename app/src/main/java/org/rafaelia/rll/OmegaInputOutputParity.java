package org.rafaelia.rll;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

/**
 * Deterministic input-to-output coverage. A missing scientific measurement is
 * an explicit result with a cause, never a made-up floating-point number.
 * Timestamps and process telemetry are deliberately excluded from replay hashes.
 */
public final class OmegaInputOutputParity {
    private OmegaInputOutputParity(){}
    public static final String SCHEMA="rll.omega.input-output-parity.v1";
    public static final class Result {
        public final Map<String,String> files=new LinkedHashMap<>();
        public String gate="FAIL_NOT_EXECUTED";
        public int expected=0,verified=0,missing=0,unknownNumeric=0;
        public String inputSha256="",outputSha256="";
    }
    private static String text(String value){
        if(value==null||value.length()==0)return "NOT_PROVIDED";
        return value.replace('\t',' ').replace('\r',' ').replace('\n',' ');
    }
    private static String number(String original) {
        if(original==null||original.trim().isEmpty())return "NOT_PROVIDED";
        try {
            return new BigDecimal(original.trim().replace(',','.'))
                .stripTrailingZeros().toPlainString();
        }catch(NumberFormatException problem){
            return "INVALID_NUMBER:"+text(original.trim());
        }
    }
    private static String hash(String value)throws Exception {
        byte[] bytes=MessageDigest.getInstance("SHA-256").digest(
            value.getBytes(StandardCharsets.UTF_8));
        StringBuilder hex=new StringBuilder();
        for(byte b:bytes)hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));
        return hex.toString();
    }
    private static double read(OmegaUiEvidence.Snapshot snap,String key) {
        String raw=snap.fields.get(key);
        if(raw==null||raw.trim().isEmpty())throw new IllegalArgumentException("REQUIRED_"+key);
        double d=Double.parseDouble(raw.trim().replace(',','.'));
        if(!Double.isFinite(d))throw new IllegalArgumentException("NONFINITE_"+key);
        return d;
    }
    private static FormulaEngine.Input parameters(OmegaUiEvidence.Snapshot s){
        FormulaEngine.Input p=new FormulaEngine.Input();
        p.z=read(s,"z");p.h0=read(s,"H0");p.om=read(s,"Om");p.ol=read(s,"OL");
        p.os0=read(s,"Os0");p.zt=read(s,"zt");p.wt=read(s,"wt");
        p.w=read(s,"w");p.w0=read(s,"w0");p.wa=read(s,"wa");
        p.obh2=read(s,"Obh2");p.sigma8=read(s,"sigma8");
        String obs=s.fields.get("Hobs"), sigma=s.fields.get("Hsigma");
        if(obs!=null&&!obs.isEmpty() || sigma!=null&&!sigma.isEmpty()){
            if(obs==null||obs.isEmpty()||sigma==null||sigma.isEmpty())
                throw new IllegalArgumentException("OBSERVATION_PAIR_INCOMPLETE");
            p.hObserved=read(s,"Hobs");p.hSigma=read(s,"Hsigma");
        }
        if(!FormulaEngine.valid(p))throw new IllegalArgumentException("PHYSICAL_PARAMETER_DOMAIN");
        return p;
    }
    private static void record(Result r,StringBuilder matrix,String id,String outputPath,
                  String outcome,String reason,boolean ok) {
        r.expected++;
        if(ok)r.verified++;else r.missing++;
        matrix.append(text(id)).append('\t')
              .append(text(outputPath)).append('\t')
              .append(ok?"RECEIPT_PRESENT":"MISSING_RECEIPT").append('\t')
              .append(text(outcome)).append('\t')
              .append(text(reason)).append('\n');
    }
    public static Result reconcile(OmegaUiEvidence.Snapshot snap, OmegaUiEvidence.Result ui){
        Result r=new Result();
        StringBuilder input=new StringBuilder("id\tnormalized_value\tinput_state\treason\n");
        StringBuilder output=new StringBuilder("id\tpath\tcoverage\toutcome\treason\n");
        StringBuilder canonical=new StringBuilder("schema=").append(SCHEMA).append('\n')
            .append("selected_model=").append(text(snap.model)).append('\n')
            .append("selected_formula=").append(text(snap.formula)).append('\n');
        boolean inputRequired=true;
        for(String key:OmegaUiEvidence.KEYS){
            String raw=snap.fields.get(key);
            String normalized=number(raw);
            boolean provided=!normalized.equals("NOT_PROVIDED");
            boolean required=!key.equals("Hobs")&&!key.equals("Hsigma");
            String outcome=!provided?(required?"REQUIRED_INPUT_MISSING":"OPTIONAL_OBSERVATION_NOT_PROVIDED")
                         :normalized.startsWith("INVALID_NUMBER:")?"INVALID_INPUT":"PRESENT";
            input.append(key).append('\t').append(text(normalized)).append('\t')
                 .append(outcome).append('\t')
                 .append(outcome.equals("PRESENT")?"VALUE_CAPTURED":"DO_NOT_INVENT_OBSERVATIONS").append('\n');
            canonical.append(key).append('=').append(normalized).append('\n');
            record(r,output,"INPUT_"+key,"22_UI/frozen_inputs.txt",outcome,
                    required?"USER_DEFINED_INPUT":"USER_OBSERVATION_UNVERIFIED",
                    ui!=null && ui.files.containsKey("22_UI/frozen_inputs.txt"));
            if(required&&!outcome.equals("PRESENT"))inputRequired=false;
        }
        r.files.put("23_IO_PARITY/inputs.tsv",input.toString());
        try {r.inputSha256=hash(canonical.toString());}
        catch(Exception ex){r.gate="FAIL_SHA256_UNAVAILABLE";}
        if(ui==null||!ui.gate.equals("PASS_SCOPED_UI_ACTIONS_REPLAY")||!inputRequired){
            r.gate="FAIL_INPUT_OR_UI_REPLAY";
            r.files.put("23_IO_PARITY/outputs.tsv",output.toString());
            r.files.put("23_IO_PARITY/closure_receipt.txt",
                "schema="+SCHEMA+"\ngate="+r.gate+"\n"
               +"input_receipts="+r.verified+"/"+r.expected+"\n"
               +"missing_data_is_not_numeric_zero=true\n"
               +"claim_allowed=false\n");
            return r;
        }
        try{
            FormulaEngine.Input p=parameters(snap);
            for(FormulaEngine.Model model:FormulaEngine.Model.values()){
                FormulaEngine.Result calculated=FormulaEngine.compute(p,model);
                String base="22_UI/current_"+model.name()+"/";
                String[] requiredPaths={base+"computed.receipt.txt",
                    base+"sweep.csv",base+"closure_preview.txt"};
                for(String path:requiredPaths){
                    String payload=ui.files.get(path);
                    record(r,output,model+"_"+path,path,"MODEL_OUTPUT",
                        "RECOMPUTED_FROM_CLICK_TIME_PARAMETERS",payload!=null&&!payload.isEmpty());
                }
                for(FormulaEngine.Entry entry:calculated.entries){
                    String path=base+"individual/"+entry.id+".receipt.txt";
                    String payload=ui.files.get(path);
                    boolean present=payload!=null
                        &&payload.contains("\nmodel="+model.name()+"\n")
                        &&payload.contains("\nid="+entry.id+"\n")
                        &&payload.contains("\nstate="+entry.state+"\n");
                    if(entry.value==null){
                        r.unknownNumeric++;
                        present=present&&payload.contains("\nvalue=TOKEN_VAZIO\n")
                            &&payload.contains("\nnote="+entry.note+"\n");
                    } else {
                        present=present&&payload.contains("\nvalue="+entry.value+"\n");
                    }
                    String result=entry.value==null
                        ?"VALUE_UNDETERMINED_BY_SOURCE_BOUNDARY"
                        :"VALUE_PRESENT_NOT_INDEPENDENTLY_PHYSICS_VALIDATED";
                    record(r,output,model+"_"+entry.id,path,result,
                        entry.value==null?entry.note:"FORMULA_VALUE_MATCHES_CURRENT_INPUT",
                        present);
                }
            }
            for(String path:Arrays.asList("22_UI/selected_formula.txt",
                    "22_UI/copy_equivalent.txt","22_UI/current_models.tsv",
                    "22_UI/actions_contract.tsv","22_UI/UI_GATE.txt")){
                String payload=ui.files.get(path);
                record(r,output,path,path,"UI_ACTION_OUTPUT",
                    "CURRENT_CLICK_SNAPSHOT",(payload!=null&&!payload.isEmpty()));
            }
            TreeMap<String,String> stable=new TreeMap<>(ui.files);
            stable.remove("22_UI/frozen_inputs.txt"); // wall UTC snapshot varies per click
            StringBuilder bytes=new StringBuilder("schema=").append(SCHEMA).append('\n');
            for(Map.Entry<String,String> e:stable.entrySet()){
                bytes.append(e.getKey()).append('\n')
                     .append(e.getValue().getBytes(StandardCharsets.UTF_8).length)
                     .append('\n').append(e.getValue()).append('\n');
            }
            r.outputSha256=hash(bytes.toString());
            r.gate=r.missing==0?"PASS_ZERO_OMITTED_OUTPUT_RECEIPTS":"FAIL_MISSING_OUTPUT_RECEIPTS";
        }catch(Exception ex){
            r.gate="FAIL_PARITY_"+ex.getClass().getSimpleName();
            output.append("RECONCILIATION_ERROR\t23_IO_PARITY/closure_receipt.txt\tFAIL\t")
                .append(r.gate).append("\t").append(text(ex.getMessage())).append('\n');
        }
        r.files.put("23_IO_PARITY/outputs.tsv",output.toString());
        r.files.put("23_IO_PARITY/closure_receipt.txt",
            "schema="+SCHEMA+"\ngate="+r.gate+"\n"
           +"input_sha256_deterministic="+r.inputSha256+"\n"
           +"output_sha256_deterministic="+r.outputSha256+"\n"
           +"expected_output_records="+r.expected+"\n"
           +"verified_output_records="+r.verified+"\n"
           +"omitted_output_receipts="+r.missing+"\n"
           +"source_bound_numeric_unknowns="+r.unknownNumeric+"\n"
           +"numeric_unknowns_are_not_silent_omissions=true\n"
           +"digest_excludes_wall_clock_and_process_telemetry=true\n"
           +"same_normalized_input_same_output_in_host_replay=true\n"
           +"hardware_and_science_attestation=NOT_ESTABLISHED_BY_THIS_GATE\n"
           +"claim_allowed=false\n");
        return r;
    }
}
