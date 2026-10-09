package org.rafaelia.rll;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/** Replays the FormulaLab UI controls using a frozen click-time snapshot; never mutates UI fields. */
public final class OmegaUiEvidence {
    private OmegaUiEvidence(){}
    public static final String[] KEYS={"z","H0","Om","OL","Os0","zt","wt","w","w0","wa","Obh2","sigma8","Hobs","Hsigma"};
    public static final class Snapshot {
        public final String model,formula;
        public final Map<String,String> fields;
        public final long uiCapturedWallUtcMs;
        public Snapshot(String selected,String formulaId,Map<String,String> values,long utc){
            model=selected==null?"TOKEN_VAZIO_MODEL_UNSELECTED":selected;
            formula=formulaId==null?"TOKEN_VAZIO_FORMULA_UNSELECTED":formulaId;
            fields=new LinkedHashMap<>();
            for(String k:KEYS){
                String raw=values==null?null:values.get(k);
                fields.put(k,raw==null?"":raw.trim().substring(0,Math.min(80,raw.trim().length())));
            }
            uiCapturedWallUtcMs=utc;
        }
    }
    public static final class Result {
        public final Map<String,String> files=new LinkedHashMap<>();
        public int formulas=0,sweeps=0,normalized=0,failed=0;
        public String gate="TOKEN_VAZIO_NOT_RUN";
    }
    private static double numeric(Snapshot snap,String key){
        String v=snap.fields.get(key);
        if(v==null||v.length()==0)throw new IllegalArgumentException("MISSING_"+key);
        double d=Double.parseDouble(v.replace(',','.'));
        if(!Double.isFinite(d))throw new IllegalArgumentException("NONFINITE_"+key);
        return d;
    }
    private static FormulaEngine.Input inputs(Snapshot s){
        FormulaEngine.Input a=new FormulaEngine.Input();
        a.z=numeric(s,"z");a.h0=numeric(s,"H0");a.om=numeric(s,"Om");a.ol=numeric(s,"OL");
        a.os0=numeric(s,"Os0");a.zt=numeric(s,"zt");a.wt=numeric(s,"wt");a.w=numeric(s,"w");
        a.w0=numeric(s,"w0");a.wa=numeric(s,"wa");a.obh2=numeric(s,"Obh2");a.sigma8=numeric(s,"sigma8");
        String h=s.fields.get("Hobs"),sigma=s.fields.get("Hsigma");
        if(!h.isEmpty()||!sigma.isEmpty()){
            if(h.isEmpty()||sigma.isEmpty())throw new IllegalArgumentException("HOBS_SIGMA_INCOMPLETE");
            a.hObserved=numeric(s,"Hobs");a.hSigma=numeric(s,"Hsigma");
        }
        return a;
    }
    private static FormulaEngine.Input copy(FormulaEngine.Input p){
        FormulaEngine.Input a=new FormulaEngine.Input();
        a.z=p.z;a.h0=p.h0;a.om=p.om;a.ol=p.ol;a.os0=p.os0;a.zt=p.zt;a.wt=p.wt;
        a.w=p.w;a.w0=p.w0;a.wa=p.wa;a.obh2=p.obh2;a.sigma8=p.sigma8;
        a.hObserved=p.hObserved;a.hSigma=p.hSigma;
        return a;
    }
    private static String sha256(String v)throws Exception {
        return RealBaoEngine.hex(MessageDigest.getInstance("SHA-256").digest(v.getBytes(StandardCharsets.UTF_8)));
    }
    /** Not a clipboard read or mutation: reconstructs copy-equivalent receipt bytes locally. */
    public static Result replay(Snapshot snap) {
        Result out=new Result();
        StringBuilder inputs=new StringBuilder("schema=rll.omega.ui-frozen-snapshot.v1\n"
           +"authority=USER_ONE_CLICK_READ_ONLY\n"
           +"source=ACTUAL_UI_FIELDS_AT_CLICK_NOT_PREVIOUS_CACHED_CALCULATION\n"
           +"utc_ms=").append(snap.uiCapturedWallUtcMs).append('\n')
           .append("selected_model=").append(snap.model).append('\n')
           .append("selected_formula=").append(snap.formula).append('\n')
           .append("claim_allowed=false\n");
        for(String k:KEYS)inputs.append(k).append('=').append(snap.fields.get(k).isEmpty()?"TOKEN_VAZIO_NOT_PROVIDED":snap.fields.get(k)).append('\n');
        out.files.put("22_UI/frozen_inputs.txt",inputs.toString());
        out.files.put("22_UI/actions_contract.tsv",
            "ui_action\toperation_in_one_click\tartifact\tmutation\n"
           +"Calcular todas as formulas\tRECOMPUTE_EACH_MODEL_AT_CURRENT_Z\t22_UI/current_*/computed.receipt.txt\tNONE\n"
           +"Exibir formula selecionada\tRENDER_SNAPSHOT_EQUIVALENT\t22_UI/selected_formula.txt\tNONE\n"
           +"Varredura z0..3\tREPLAY_FOUR_MODELS_11_POINTS\t22_UI/current_*/sweep.csv\tNONE\n"
           +"Preencher OmegaLambda\tCOMPUTE_CLOSED_OL_ONLY\t22_UI/current_*/closure_preview.txt\tNO_UI_FIELD_CHANGE\n"
           +"Copiar recibo SHA256\tCOMPUTE_COPY_EQUIVALENT_HASH\t22_UI/copy_equivalent.txt\tNO_CLIPBOARD_CHANGE\n"
           +"Verificar revisao\tEXISTING_RELEASE_GATE\t10_DEVICE/release_discovery_receipt.txt\tNO_INSTALL\n"
           +"Estado execucao/JNI/fronteiras\tRECOMPUTE_JNI_AND_BOUNDARIES\t10_DEVICE+13_NATIVE\tNO_DEVICE_CHANGE\n");
        try {
            FormulaEngine.Input values=inputs(snap);
            if(!FormulaEngine.valid(values))throw new IllegalArgumentException("FORMULA_DOMAIN_INVALID");
            FormulaEngine.Model active=FormulaEngine.Model.valueOf(snap.model);
            StringBuilder catalog=new StringBuilder("model\tformulas\ttyped_gaps\tsweep_points\tclosure_after\tstate\n");
            FormulaEngine.Result selection=null;
            for(FormulaEngine.Model model:FormulaEngine.Model.values()) {
                String base="22_UI/current_"+model.name()+"/";
                FormulaEngine.Input current=copy(values);
                FormulaEngine.Result result=FormulaEngine.compute(current,model);
                out.files.put(base+"computed.receipt.txt",result.receipt(current));
                out.formulas++;
                if(model==active)selection=result;
                StringBuilder grid=new StringBuilder("z,e2,h_km_s_mpc,state\n");
                for(int i=0;i<=10;i++) {
                    FormulaEngine.Input sweep=copy(values);sweep.z=i*0.3;
                    FormulaEngine.Result row=FormulaEngine.compute(sweep,model);
                    Double e2=null,h=null;
                    for(FormulaEngine.Entry item:row.entries){
                        if(item.id.startsWith("COS-E2-")&&!item.id.equals("COS-E2-ZERO"))e2=item.value;
                        if("COS-HZ".equals(item.id))h=item.value;
                    }
                    grid.append(String.format(Locale.ROOT,"%.9g,%s,%s,%s\n",
                        sweep.z,e2==null?"TOKEN_VAZIO":Double.toString(e2),
                        h==null?"TOKEN_VAZIO":Double.toString(h),row.state));
                    out.sweeps++;
                }
                out.files.put(base+"sweep.csv",grid.toString());
                FormulaEngine.Input after=copy(values);
                double before=after.ol;
                after.ol=FormulaEngine.closedOl(after,model);
                FormulaEngine.Result norm=FormulaEngine.compute(after,model);
                out.files.put(base+"closure_preview.txt",
                    "operation=SIMULATE_PREVIOUS_OL_TO_CLOSED_OL_NOT_UI_MUTATION\n"
                   +"model="+model+"\nOL_before="+before+"\nOL_after="+after.ol
                   +"\nnormalized_state="+norm.state+"\nclaim_allowed=false\n"
                   +norm.receipt(after));
                out.normalized++;
                catalog.append(model).append('\t').append(result.computed).append('\t').append(result.gap)
                       .append("\t11\t").append(after.ol).append('\t').append(result.state).append('\n');
            }
            out.files.put("22_UI/current_models.tsv",catalog.toString());
            if(selection!=null) {
                String selected="TOKEN_VAZIO_SELECTED_FORMULA_NOT_AVAILABLE\n";
                for(FormulaEngine.Entry entry:selection.entries)if(entry.id.equals(snap.formula)){
                    selected="model="+active+"\nformula="+entry.id+"\nequation="+entry.expression
                      +"\nvalue="+(entry.value==null?entry.state:entry.value)+"\nunit="+entry.unit
                      +"\nsource="+entry.source+"\nstate="+entry.state+"\nnotes="+entry.note
                      +"\nclaim_allowed=false\n";
                    break;
                }
                out.files.put("22_UI/selected_formula.txt",selected);
                String receipt=selection.receipt(values)+"version_gate=SEE_RELEASE_CHECK\n";
                String scoped=receipt+"receipt_hash_scope=FORMULA_LAB_PAYLOAD_UTF8_ONLY\n";
                out.files.put("22_UI/copy_equivalent.txt",scoped+"receipt_sha256="+sha256(scoped)
                   +"\nclipboard_mutation=false\ncopy_equivalent_only=true\n");
            }
            out.gate=out.formulas==4&&out.sweeps==44&&out.normalized==4?
                "PASS_SCOPED_UI_ACTIONS_REPLAY":"FAIL_INCOMPLETE_ACTIONS";
        }catch(RuntimeException failure){
            out.failed++;
            out.gate="TOKEN_VAZIO_UI_INPUT_"+failure.getClass().getSimpleName();
            out.files.put("22_UI/TOKEN_VAZIO_INVALID_INPUT.txt",
                "gate="+out.gate+"\nreason="+failure.getMessage()+"\n"
              +"preservation=RAW_CLICK_TIME_UI_FIELDS_INCLUDED\n"
              +"baseline_can_still_be_computed_in_other_ZIP_SECTIONS=true\n");
        }catch(Exception failure){
            out.failed++;out.gate="FAIL_UI_RECEIPT_"+failure.getClass().getSimpleName();
            out.files.put("22_UI/FAIL_RECEIPT.txt","gate="+out.gate+"\n");
        }
        out.files.put("22_UI/UI_GATE.txt",
            "gate="+out.gate+"\nmodels="+out.formulas+"\nsweep_points="+out.sweeps
            +"\nclosure_previews="+out.normalized+"\nfailed="+out.failed
            +"\nexported_formulas_do_not_assert_scientific_validation=true\n");
        return out;
    }
}
