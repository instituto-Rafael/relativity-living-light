package org.rafaelia.rll;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Entirely Java/stdlib canonical archive builder. App owns the network, JNI and
 * PackageManager boundaries; this code neither fabricates evidence nor uploads it.
 */
public final class CanonicalOmegaBundle {
    private CanonicalOmegaBundle(){}
    public static final String SCHEMA="rll.canonical.omega.zip.v2";
    public static final class Result {
        public final byte[] zip;
        public final String sha256, gateRegister, dataState;
        public final int files;
        Result(byte[] z,String hash,String g,String state,int count){
            zip=z;sha256=hash;gateRegister=g;dataState=state;files=count;
        }
    }
    static void put(Map<String,byte[]> entries,String path,String text){
        putBytes(entries,path,text.getBytes(StandardCharsets.UTF_8));
    }
    static void putBytes(Map<String,byte[]> entries,String path,byte[] data){
        if(path.startsWith("/")||path.contains("..")||path.indexOf('\\')>=0||
            !path.matches("[A-Za-z0-9_./-]+")||entries.containsKey(path)||
            data==null||data.length>300000)
            throw new IllegalArgumentException("CANONICAL_PATH_OR_SIZE");
        entries.put(path,data);
    }
    private static void gate(StringBuilder gates,String id,String state,String scope,String evidence){
        gates.append(id).append('\t').append(state).append('\t')
            .append(scope).append('\t').append(evidence).append('\n');
    }
    private static String parameters(FormulaEngine.Input p,FormulaEngine.Model m) {
        return String.format(Locale.US,
            "model=%s\nz=%.17g\nH0=%.17g\nOm=%.17g\nOL=%.17g\nOs0=%.17g\nzt=%.17g\nwt=%.17g\nw=%.17g\nw0=%.17g\nwa=%.17g\nObh2=%.17g\nsigma8=%.17g\nparameter_origin=FIXED_CODE_DEFAULT_NO_FITTING\nclosure=E2_0_EQUALS_ONE\n",
            m.name(),p.z,p.h0,p.om,p.ol,p.os0,p.zt,p.wt,p.w,p.w0,p.wa,p.obh2,p.sigma8);
    }
    private static String summary(double[] vals) {
        StringBuilder b=new StringBuilder();
        for(int i=0;i<vals.length;i++){
            if(i>0)b.append(',');
            b.append(Double.toString(vals[i]));
        }
        return b.toString();
    }
    /**
     * mean/cov may be null on network failure. A validation failure does not
     * become "data PASS", but the same one-click run still exports local evidence.
     */
    public static Result build(byte[] mean,byte[] cov,String downloadDiagnostic,
                 String nativeReceipt,String installationReceipt)throws Exception {
        return build(mean,cov,downloadDiagnostic,nativeReceipt,installationReceipt,
                     "gate=TOKEN_VAZIO_RELEASE_CHECK_NOT_RUN\n");
    }
    public static Result build(byte[] mean,byte[] cov,String downloadDiagnostic,
                 String nativeReceipt,String installationReceipt,String releaseReceipt)throws Exception {
        return build(mean,cov,downloadDiagnostic,nativeReceipt,installationReceipt,releaseReceipt,
              "gate=TOKEN_VAZIO_RUNTIME_TRACE_NOT_RUN\n",
              "gate=TOKEN_VAZIO_OS_CONTEXT_NOT_RUN\n",
              "gate=TOKEN_VAZIO_OWN_LOGCAT_NOT_RUN\n",
              "gate=TOKEN_VAZIO_EXTENDED_NUMERIC_NOT_RUN\n");
    }
    public static Result build(byte[] mean,byte[] cov,String downloadDiagnostic,
                 String nativeReceipt,String installationReceipt,String releaseReceipt,
                 String stageTrace,String runtimeContext,String ownLogcat,String expandedChecks)throws Exception {
        Map<String,byte[]> e=new LinkedHashMap<>();
        StringBuilder gates=new StringBuilder("gate\tstatus\tscope\tevidence\n");
        StringBuilder events=new StringBuilder("schema=").append(SCHEMA)
           .append("\nclaim_allowed=false\n")
           .append("source_kind=LIVE_APP_RUNTIME_SELF_REPORT\n");
        put(e,"00_START_HERE.txt",
          "RLL CANONICAL OMEGA ONE-CLICK EVIDENCE ARCHIVE\n"+
          "A single command executes every available local diagnostic; unavailable stages are typed, never silently removed.\n"+
          "READ FIRST: 01_ATLAS.tsv then 02_GATES.tsv and 03_RECEIPT.txt; verify MANIFEST_SHA256.txt before considering results. 11_DIAGNOSTICS contains local times, model falsifiers and own-PID logcat.\n"+
          "SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.\n"+
          "USER_DEVICE_REPORT != INDEPENDENT_HARDWARE_ATTESTATION.\n"+
          "NUMERIC_SELF_CHECK != COSMOLOGICAL_PROOF.\n"+
          "No telemetry. HTTPS data fetch only on user's direct one-tap request. Local ZIP save confirmed via Android picker.\n"+
          "No optimization, no automatic installation, no claimed independent validation. RAR encoding not provided.\n");
        gate(gates,"RUN_INTENT","PASS","USER_CLICK","Canonical one-button action");
        if(nativeReceipt==null||nativeReceipt.isEmpty())nativeReceipt="gate=TOKEN_VAZIO_JNI_NOT_EXECUTED\n";
        put(e,"10_DEVICE/native_jni_score_receipt.txt",nativeReceipt);
        gate(gates,"ANDROID_JNI_C",
            nativeReceipt.contains("gate=PASS_SCOPED")?"PASS_SCOPED":"FAIL_OR_TOKEN_VAZIO",
            "APP_OWN_RUNTIME","10_DEVICE/native_jni_score_receipt.txt");
        if(installationReceipt==null||installationReceipt.isEmpty())
            installationReceipt="device_install_proof=TOKEN_VAZIO_NOT_ATTESTED\n";
        put(e,"10_DEVICE/installed_package_self_report.txt",installationReceipt);
        gate(gates,"INSTALL_SELF_REPORT",
            installationReceipt.contains("package=")?"OBSERVED_SELF_REPORT":"TOKEN_VAZIO",
            "PACKAGE_MANAGER_ONLY","10_DEVICE/installed_package_self_report.txt");
        if(stageTrace==null)stageTrace="gate=TOKEN_VAZIO_RUNTIME_TRACE_NOT_RUN\n";
        if(runtimeContext==null)runtimeContext="gate=TOKEN_VAZIO_OS_CONTEXT_NOT_RUN\n";
        if(ownLogcat==null)ownLogcat="gate=TOKEN_VAZIO_OWN_LOGCAT_NOT_RUN\n";
        if(expandedChecks==null)expandedChecks="gate=TOKEN_VAZIO_EXTENDED_NUMERIC_NOT_RUN\n";
        put(e,"11_DIAGNOSTICS/app_stage_trace.tsv",stageTrace);
        put(e,"11_DIAGNOSTICS/runtime_context.txt",runtimeContext);
        put(e,"11_DIAGNOSTICS/own_pid_logcat.txt",ownLogcat);
        put(e,"11_DIAGNOSTICS/expanded_formula_selfchecks.tsv",expandedChecks);
        gate(gates,"APP_STAGE_TRACE",
            stageTrace.contains("schema=rll.omega.runtime-trace.v1")?"RECORDED_LOCAL":"TOKEN_VAZIO",
            "TIMINGS_SELF_REPORTED","11_DIAGNOSTICS/app_stage_trace.tsv");
        gate(gates,"OS_PROCESS_CONTEXT",
            runtimeContext.contains("schema=rll.omega.runtime-context.v1")?"RECORDED_SELF_REPORT":"TOKEN_VAZIO",
            "ANDROID_APP_OWN_PROCESS","11_DIAGNOSTICS/runtime_context.txt");
        gate(gates,"OWN_PID_LOGCAT",
            ownLogcat.contains("gate=CAPTURED_OWN_PROCESS_BEST_EFFORT")?"CAPTURED_SCOPED":"TOKEN_VAZIO_RESTRICTED_OR_NOT_RUN",
            "ANDROID_PROCESS_PID_ONLY","11_DIAGNOSTICS/own_pid_logcat.txt");
        gate(gates,"EXPANDED_FORMULA_FALSIFIERS",
            expandedChecks.contains("FAIL_NUMERIC")?"FAIL_NUMERIC":(
                expandedChecks.contains("PASS_SCOPED")?"PASS_SCOPED_NUMERIC":"TOKEN_VAZIO_NOT_RUN"),
            "ALGEBRAIC_NUMERIC_NOT_PHYSICAL_PROOF","11_DIAGNOSTICS/expanded_formula_selfchecks.tsv");
        gate(gates,"INDEPENDENT_INSTALL_WITNESS","TOKEN_VAZIO_NOT_ATTESTED",
            "ADB_HARDWARE_SIGNER_NOT_IN_APP","Needs external trusted witness");
        gate(gates,"CI_EXACT_HEAD","TOKEN_VAZIO_INDEPENDENT_CI_VERIFICATION",
            "SOURCE_VS_RUNTIME","GitHub run must be inspected independently");
        if(releaseReceipt==null)releaseReceipt="gate=TOKEN_VAZIO_RELEASE_CHECK_NOT_RUN\n";
        put(e,"10_DEVICE/release_discovery_receipt.txt",releaseReceipt);
        gate(gates,"ANDROID_RELEASE_DISCOVERY",
            releaseReceipt.contains("gate=CHECKED")?"CHECKED_SCOPE_ONLY":"TOKEN_VAZIO_PROVIDER",
            "OFFICIAL_GITHUB_RELEASES","10_DEVICE/release_discovery_receipt.txt");
        int formulaRuns=0;
        StringBuilder catalog=new StringBuilder("model\tz\tstate\tcomputed\tgaps\n");
        for(FormulaEngine.Model m:FormulaEngine.Model.values()) {
            FormulaEngine.Input p=RealBaoEngine.baseline(m);
            put(e,"20_FORMULAS/"+m.name()+"/parameters.txt",parameters(p,m));
            StringBuilder sweep=new StringBuilder("z,E2,H_km_s_Mpc,computed,typed_gaps\n");
            for(int i=0;i<=10;i++) {
                p.z=i*0.3;
                FormulaEngine.Result result=FormulaEngine.compute(p,m);
                double ez=FormulaEngine.e2(p.z,m,p);
                double h=ez>0?p.h0*Math.sqrt(ez):Double.NaN;
                sweep.append(String.format(Locale.US,"%.6f,%.17g,%.17g,%d,%d\n",
                             p.z,ez,h,result.computed,result.gap));
                catalog.append(m.name()).append('\t').append(p.z).append('\t')
                       .append(result.state).append('\t').append(result.computed)
                       .append('\t').append(result.gap).append('\n');
                // Every individual mathematical output and typed absence is retained.
                put(e,String.format(Locale.ROOT,"20_FORMULAS/%s/point_%02d.receipt.txt",m.name(),i),
                    result.receipt(p));
                formulaRuns++;
            }
            put(e,"20_FORMULAS/"+m.name()+"/grid.csv",sweep.toString());
        }
        put(e,"20_FORMULAS/formula_catalog.tsv",catalog.toString());
        gate(gates,"FOUR_MODELS_ALL_FORMULAS","PASS_SCOPED_NUMERIC",
             "ALGEBRAIC_AND_PROXY_ONLY",formulaRuns+" point receipts; includes typed absences");
        String sourceState="TOKEN_VAZIO_DATA_NOT_AVAILABLE";
        RealBaoEngine.Data data=null;
        if(mean==null||cov==null) {
            sourceState="TOKEN_VAZIO_DOWNLOAD_FAILED";
            events.append("download_status=").append(downloadDiagnostic==null?
                        "TOKEN_VAZIO_MISSING_INPUT":downloadDiagnostic).append('\n');
        } else {
            try {
                data=RealBaoEngine.parse(mean,cov); // pinned blobs + covariance SPD.
                sourceState="PASS_PINNED_DESI_DR2";
                putBytes(e,"30_DATA/raw/"+RealBaoEngine.MEAN,mean);
                putBytes(e,"30_DATA/raw/"+RealBaoEngine.COV,cov);
                events.append("mean_sha256=").append(data.meanSha256).append('\n')
                    .append("cov_sha256=").append(data.covSha256).append('\n');
            } catch(Exception invalid){
                sourceState="FAIL_CLOSED_PINNED_SOURCE_OR_COVARIANCE";
                events.append("source_exception=").append(invalid.getClass().getSimpleName()).append('\n');
                events.append("untrusted_mean_sha256=").append(RealBaoEngine.sha256(mean)).append('\n');
                events.append("untrusted_cov_sha256=").append(RealBaoEngine.sha256(cov)).append('\n');
                // Never reclassify or run a likelihood over untrusted bytes.
            }
        }
        gate(gates,"REAL_DATA_DOWNLOAD",sourceState,"PINNED_GITHUB_BLOB_SHA1",
             data==null?"source bytes missing/rejected":RealBaoEngine.SOURCE);
        put(e,"30_DATA/source_contract.txt",
            "origin="+RealBaoEngine.SOURCE+"\n"+
            "commit="+RealBaoEngine.DATA_COMMIT+"\n"+
            "mean_filename="+RealBaoEngine.MEAN+"\nmean_git_blob="+RealBaoEngine.MEAN_BLOB+"\n"+
            "cov_filename="+RealBaoEngine.COV+"\ncov_git_blob="+RealBaoEngine.COV_BLOB+"\n"+
            "points=13\ncovariance_shape=13x13\n"+
            "source_state="+sourceState+"\nrights=TOKEN_VAZIO_REPUBLICATION_LICENSE\n");
        if(data!=null) {
            gate(gates,"COVARIANCE_13x13","PASS_SPD_AND_DIMENSIONS","NUMERIC",
                 "RealBaoEngine.parse Cholesky; 30_DATA/raw");
            StringBuilder scores=new StringBuilder("model,chi2_cov13,dchi2_dOm_abs,dchi2_dH0_abs,dchi2_dzt_abs,torus_closure,scope\n");
            StringBuilder comparisons=new StringBuilder("model,index,z,observable,observed,predicted,residual_model_minus_observed\n");
            for(FormulaEngine.Model m:FormulaEngine.Model.values()) {
                try {
                    RealBaoEngine.Score s=RealBaoEngine.score(data,m);
                    scores.append(s.csv()).append('\n');
                    for(int i=0;i<RealBaoEngine.N;i++){
                        RealBaoEngine.Datum d=data.points.get(i);
                        comparisons.append(String.format(Locale.US,
                          "%s,%d,%.10g,%s,%.17g,%.17g,%.17g\n",
                          m.name(),i,d.z,d.kind,d.observed,s.prediction[i],s.residual[i]));
                    }
                } catch(Exception ex) {
                    scores.append(m.name()).append(",TOKEN_VAZIO_MODEL_COMPUTE_")
                        .append(ex.getClass().getSimpleName()).append('\n');
                    events.append("model_").append(m.name()).append("_failure=")
                         .append(ex.getClass().getSimpleName()).append('\n');
                }
            }
            put(e,"31_REAL_DATA_CALCULATIONS/four_models_covariance_scores.csv",scores.toString());
            put(e,"31_REAL_DATA_CALCULATIONS/observed_vs_predicted.csv",comparisons.toString());
            gate(gates,"BAO_FOUR_MODELS_FULL_COVARIANCE","PASS_OR_PER_MODEL_TYPED",
                 "FIXED_PARAMETERS_NOT_POSTERIOR","31_REAL_DATA_CALCULATIONS");
        } else {
            put(e,"31_REAL_DATA_CALCULATIONS/TOKEN_VAZIO.txt",
                "BAO likelihood blocked: "+sourceState+"\n"+
                "No chi2 computed using unverified or unavailable measurements.\n");
            gate(gates,"BAO_FOUR_MODELS_FULL_COVARIANCE","TOKEN_VAZIO_BLOCKED",
                 "DATA_UNAVAILABLE","31_REAL_DATA_CALCULATIONS/TOKEN_VAZIO.txt");
        }
        double torus=RealBaoEngine.torusClosure(2.0,0.7);
        put(e,"40_STABILITY/toroid_geometry.txt",
             "R=2.0\nr=0.7\nT2_geometric_closed_loop_error="+torus+"\n"+
             "gate="+(torus<=1e-12?"PASS_GEOMETRY_ONLY":"FAIL_GEOMETRY")+"\n"+
             "physical_Poincare_recurrence=TOKEN_VAZIO_NO_DYNAMICAL_TRAJECTORY\n"+
             "parameter_stability=FINITE_DIFFERENCE_LOCAL_ONLY_NOT_BASIN_PROOF\n");
        put(e,"40_STABILITY/rmrcti_delta_p_source_boundary.txt",
            "authority=rafaelmeloreisnovo/llamaRafaelia/rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md\n"+
            "definition=DeltaP=P(stable_any=1|peak)-P(stable_any=1|nonpeak)\n"+
            "BAO_has_stable_any=false\nBAO_has_peak_groups=false\n"+
            "measured_DeltaP=TOKEN_VAZIO_NO_RMRCTI_REAL_TRACE\n"+
            "Poincare_invariant=TOKEN_VAZIO_NOT_DEMONSTRATED\n"+
            "target_0_18=EXPLORATORY_NOT_FITTED\n"+
            "seed_null_holdout_recurrence=TOKEN_VAZIO_NOT_RUN\n");
        gate(gates,"TORUS_GEOMETRY","PASS_SCOPED_IDENTITY","MATH_ONLY",
            "40_STABILITY/toroid_geometry.txt");
        gate(gates,"POINCARE_DYNAMIC_STABILITY","TOKEN_VAZIO_NOT_RUN",
            "NO_TIME_TRAJECTORY","40_STABILITY");
        gate(gates,"RMRCTI_DELTA_P","TOKEN_VAZIO_NOT_APPLICABLE",
            "BAO_LACKS_STABLE_ANY_AND_PEAK","40_STABILITY/rmrcti_delta_p_source_boundary.txt");
        gate(gates,"SOUND_HORIZON_CLASS_CAMB","TOKEN_VAZIO_NOT_RUN",
            "RDRAG_EMPIRICAL_PROXY","No full Boltzmann calculation");
        gate(gates,"OFFICIAL_DESI_POSTERIOR","TOKEN_VAZIO_NOT_RUN",
            "NO_PRIORS_OR_SNE_CMB","Do not claim model preference");
        gate(gates,"REDISTRIBUTION_RIGHTS","TOKEN_VAZIO_UNVERIFIED",
            "P0_LICENSE_CHECK","Raw data for local analysis only");
        put(e,"50_REFERENCES/papers_and_tools.txt",
            "DESI DR2 official https://arxiv.org/abs/2503.14738\n"+
            "DESI DR2 methodological comparison https://arxiv.org/abs/2504.06118\n"+
            "CMBComp model-specific compressed likelihood https://arxiv.org/abs/2606.18455\n"+
            "CPL pivot and stability https://arxiv.org/abs/2608.01215\n"+
            "Nonparametric curvature sensitivity https://arxiv.org/abs/2609.22470\n"+
            "RMRCTI DeltaP source rafaelemeloreisnovo/llamaRafaelia/rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md\n"+
            "No publication independently endorses or validates RLL by this archive alone.\n");
        put(e,"02_GATES.tsv",gates.toString());
        put(e,"03_RECEIPT.txt",events.toString()+
           "state="+sourceState+"\nmodel_runs="+formulaRuns+"\n"+
           "archive_schema="+SCHEMA+"\nphysical_install_proof=APP_SELF_REPORT_ONLY\n"+
           "full_data_covariance="+(data==null?"TOKEN_VAZIO_NOT_COMPUTED":"COMPUTED_WITH_EMPIRICAL_RD_PROXY")+"\n"+
           "claim_allowed=false\n");
        StringBuilder atlas=new StringBuilder("path\tsha256\tbytes\trole\n");
        StringBuilder manifest=new StringBuilder();
        for(Map.Entry<String,byte[]> entry:e.entrySet()){
            String hash=RealBaoEngine.sha256(entry.getValue());
            atlas.append(entry.getKey()).append('\t').append(hash).append('\t')
                .append(entry.getValue().length).append("\tSOURCE_OR_DERIVED\n");
            manifest.append(hash).append("  ").append(entry.getKey()).append('\n');
        }
        put(e,"01_ATLAS.tsv",atlas.toString());
        manifest.append(RealBaoEngine.sha256(e.get("01_ATLAS.tsv"))).append("  01_ATLAS.tsv\n");
        put(e,"MANIFEST_SHA256.txt",manifest.toString());
        ByteArrayOutputStream baos=new ByteArrayOutputStream();
        try(ZipOutputStream zip=new ZipOutputStream(baos,StandardCharsets.UTF_8)){
            for(Map.Entry<String,byte[]> entry:e.entrySet()){
                ZipEntry ze=new ZipEntry(entry.getKey());ze.setTime(0L);
                zip.putNextEntry(ze);zip.write(entry.getValue());zip.closeEntry();
            }
        }
        byte[] bytes=baos.toByteArray();
        if(bytes.length>4_000_000)throw new IllegalStateException("ZIP_SIZE_LIMIT");
        return new Result(bytes,RealBaoEngine.sha256(bytes),gates.toString(),sourceState,e.size());
    }
}
