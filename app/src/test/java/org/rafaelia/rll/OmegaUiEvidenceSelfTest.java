package org.rafaelia.rll;

import java.util.LinkedHashMap;
import java.util.Map;

/** Exact frozen UI inputs must become receipts for every named FormulaLab action. */
public final class OmegaUiEvidenceSelfTest {
    public static void main(String[] args)throws Exception {
        Map<String,String> fields=new LinkedHashMap<>();
        FormulaEngine.Input p=new FormulaEngine.Input();
        String[] keys={"z","H0","Om","OL","Os0","zt","wt","w","w0","wa","Obh2","sigma8","Hobs","Hsigma"};
        double[] nums={p.z,p.h0,p.om,p.ol,p.os0,p.zt,p.wt,p.w,p.w0,p.wa,p.obh2,p.sigma8};
        for(int i=0;i<nums.length;i++)fields.put(keys[i],Double.toString(nums[i]));
        fields.put("Hobs","");fields.put("Hsigma","");
        OmegaUiEvidence.Result good=OmegaUiEvidence.replay(
            new OmegaUiEvidence.Snapshot("RLL","COS-HZ",fields,123456789L));
        if(!good.gate.equals("PASS_SCOPED_UI_ACTIONS_REPLAY"))
            throw new AssertionError("UI gate "+good.gate);
        if(good.formulas!=4||good.sweeps!=44||good.normalized!=4)
            throw new AssertionError("incomplete UI action replay");
        if(good.files.size()<19)throw new AssertionError("missing action artifacts");
        if(!good.files.get("22_UI/selected_formula.txt").contains("formula=COS-HZ"))
            throw new AssertionError("selected formula not exported");
        if(!good.files.get("22_UI/copy_equivalent.txt").contains("receipt_sha256="))
            throw new AssertionError("hash copy equivalence missing");
        if(!good.files.get("22_UI/current_RLL/sweep.csv").contains("0.00000000"))
            throw new AssertionError("sweep not persisted");
        if(!good.files.get("22_UI/current_RLL/closure_preview.txt").contains("NO_UI_MUTATION"))
            throw new AssertionError("normalization cannot silently mutate UI");
        if(!good.files.get("22_UI/frozen_inputs.txt").contains("utc_ms=123456789"))
            throw new AssertionError("timestamp missing");
        fields.put("Hobs","93.1");fields.put("Hsigma","");
        OmegaUiEvidence.Result bad=OmegaUiEvidence.replay(
            new OmegaUiEvidence.Snapshot("RLL","COS-HZ",fields,2));
        if(!bad.gate.startsWith("TOKEN_VAZIO_UI_INPUT_"))
            throw new AssertionError("incomplete observational pair must fail typed");
        if(!bad.files.get("22_UI/frozen_inputs.txt").contains("Hobs=93.1"))
            throw new AssertionError("invalid user evidence lost");
        System.out.println("RLL_OMEGA_UI_ACTIONS_PASS 4 models x 11 + selected + normalized + hash, invalid typed");
    }
}
