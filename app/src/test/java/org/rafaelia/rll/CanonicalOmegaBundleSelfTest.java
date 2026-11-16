package org.rafaelia.rll;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Standalone JVM regression for full offline/fail-closed canonical ZIP, no Android deps. */
public final class CanonicalOmegaBundleSelfTest {
    static int checks=0;
    static void ok(boolean test,String why){checks++;if(!test)throw new AssertionError(why);}
    static Map<String,byte[]> unzip(byte[] zip)throws Exception {
        Map<String,byte[]> result=new HashMap<>();
        try(ZipInputStream in=new ZipInputStream(new ByteArrayInputStream(zip),StandardCharsets.UTF_8)){
            ZipEntry en;while((en=in.getNextEntry())!=null){
                ByteArrayOutputStream bytes=new ByteArrayOutputStream();
                byte[] buf=new byte[4096];int n;
                while((n=in.read(buf))!=-1)bytes.write(buf,0,n);
                ok(result.put(en.getName(),bytes.toByteArray())==null,"duplicate ZIP entry");
                in.closeEntry();
            }
        }
        return result;
    }
    static String s(Map<String,byte[]> m,String path) {
        byte[] data=m.get(path);if(data==null)throw new AssertionError("missing "+path);
        return new String(data,StandardCharsets.UTF_8);
    }
    static void manifest(Map<String,byte[]> files)throws Exception {
        String manifest=s(files,"MANIFEST_SHA256.txt");
        for(String row:manifest.split("\n")){
            if(row.isEmpty())continue;
            String[] tokens=row.split("  ",2);
            ok(tokens.length==2,"manifest shape");
            ok(tokens[0].equals(RealBaoEngine.sha256(files.get(tokens[1]))),"digest "+tokens[1]);
        }
        ok(!manifest.contains("MANIFEST_SHA256.txt"),"non-circular manifest");
    }
    public static void main(String[] args)throws Exception {
        String jni="gate=PASS_SCOPED\nvector=7,11;C=130;Java=130;pass=true\n";
        String install="package=org.rafaelia.rll.debug\nversion_code=4\n"
               +"physical_install_observation=APP_SELF_REPORT_ONLY\n";
        CanonicalOmegaBundle.Result off=CanonicalOmegaBundle.build(
            null,null,"TOKEN_VAZIO_NO_NETWORK",jni,install);
        Map<String,byte[]> items=unzip(off.zip);
        ok(items.size()==off.files,"entry count");
        ok(items.size()>=58,"complete 44 point receipts");
        ok(RealBaoEngine.sha256(off.zip).equals(off.sha256),"full ZIP SHA");
        ok(s(items,"02_GATES.tsv").contains("TOKEN_VAZIO_DOWNLOAD_FAILED"),"offline typed source");
        ok(s(items,"02_GATES.tsv").contains("ANDROID_JNI_C\tPASS_SCOPED"),"JNI preserved");
        ok(s(items,"03_RECEIPT.txt").contains("claim_allowed=false"),"claim gate");
        ok(s(items,"10_DEVICE/installed_package_self_report.txt").contains("APP_SELF_REPORT_ONLY"),"install self boundary");
        ok(s(items,"20_FORMULAS/RLL/point_02.receipt.txt").contains("RLL-CONTINUITY-CONS"),"RLL formulas included");
        ok(s(items,"20_FORMULAS/CPL/point_10.receipt.txt").contains("COS-E2-CPL"),"CPL 11-point sweep");
        ok(s(items,"31_REAL_DATA_CALCULATIONS/TOKEN_VAZIO.txt").contains("No chi2"),"no fake chi2");
        ok(s(items,"40_STABILITY/rmrcti_delta_p_source_boundary.txt").contains("TOKEN_VAZIO_NO_RMRCTI_REAL_TRACE"),"no fake CTI");
        ok(s(items,"40_STABILITY/toroid_geometry.txt").contains("PASS_GEOMETRY_ONLY"),"mathematics separate");
        ok(!items.containsKey("30_DATA/raw/"+RealBaoEngine.MEAN),"no fake raw");
        manifest(items);
        CanonicalOmegaBundle.Result wrong=CanonicalOmegaBundle.build(
             new byte[]{1},new byte[]{2},"PARTIAL_SOURCE",jni,install);
        Map<String,byte[]> bad=unzip(wrong.zip);
        ok(s(bad,"02_GATES.tsv").contains("FAIL_CLOSED_PINNED_SOURCE_OR_COVARIANCE"),"untrusted data blocked");
        ok(!bad.containsKey("30_DATA/raw/"+RealBaoEngine.MEAN),"do not bundle corrupted source");
        ok(!bad.containsKey("31_REAL_DATA_CALCULATIONS/observed_vs_predicted.csv"),"do not fake predictions");
        manifest(bad);
        OmegaScientificChecks.Result controls=OmegaScientificChecks.run();
        ok(controls.failed==0 && controls.passed>=24,"expanded selfchecks");
        CanonicalOmegaBundle.Result enhanced=CanonicalOmegaBundle.build(null,null,
            "TOKEN_VAZIO_NO_NETWORK",jni,install,"gate=CHECKED_NO_NEW_ANDROID_RELEASE\n",
            "schema=rll.omega.runtime-trace.v1\n",
            "schema=rll.omega.runtime-context.v1\n",
            "scope=OWN_PROCESS_PID_ONLY\ngate=TOKEN_VAZIO_LOGCAT_RESTRICTED\n",
            controls.tsv,
            "schema=rll.omega.apk-binary-inspection.v1\ngate=PASS_SCOPED_APK_DEX_ELF_CRC\n",
            "schema=rll.omega.hw-process-probe.v1\ngate=RECORDED_APP_SCOPED\n");
        Map<String,byte[]> enhancedFiles=unzip(enhanced.zip);
        ok(s(enhancedFiles,"02_GATES.tsv").contains("EXPANDED_FORMULA_FALSIFIERS\tPASS_SCOPED_NUMERIC"),
           "new expanded checks gate");
        ok(s(enhancedFiles,"02_GATES.tsv").contains("TOKEN_VAZIO_RESTRICTED_OR_NOT_RUN"),
           "logcat denied is typed");
        ok(s(enhancedFiles,"11_DIAGNOSTICS/expanded_formula_selfchecks.tsv").contains("RLL_CONSERVED_IDENTITY"),
           "expanded scientific selfchecks included");
        ok(s(enhancedFiles,"11_DIAGNOSTICS/own_pid_logcat.txt").contains("TOKEN_VAZIO"),
           "logcat never fabricated");
        ok(s(enhancedFiles,"02_GATES.tsv").contains("OWN_APK_DEX_ELF\tPASS_SCOPED_SELF_INSPECTION"),
           "APK ELF DEX diagnostic gate in same ZIP");
        ok(s(enhancedFiles,"02_GATES.tsv").contains("HW_CPU_RAM_STORAGE_NUMA\tRECORDED_SELF_REPORT"),
           "hardware probe preserved without claiming physical attestation");
        ok(s(enhancedFiles,"12_BINARY/apk_dex_elf_integrity.txt").contains("PASS_SCOPED_APK_DEX_ELF_CRC"),
           "APK source report archived");
        ok(s(enhancedFiles,"21_CROSS_MODEL/six_pairwise_model_differences.csv").split("\n").length==67,
           "66 differential comparisons in archive");
        ok(s(enhancedFiles,"21_CROSS_MODEL/nested_model_falsifiers.csv").contains("PASS_SCOPED_NESTED"),
           "33 nested scientific falsifiers");
        ok(s(enhancedFiles,"02_GATES.tsv").contains("INDEPENDENT_INSTALL_WITNESS\tTOKEN_VAZIO_NOT_ATTESTED"),
           "no false physical witness");
        manifest(enhancedFiles);
        // Full 0.7 path: all individual formula controls, deep JNI and kernel build receipt.
        java.util.Map<String,String> inputs=new java.util.LinkedHashMap<>();
        FormulaEngine.Input p=new FormulaEngine.Input();
        inputs.put("z",Double.toString(p.z));inputs.put("H0",Double.toString(p.h0));
        inputs.put("Om",Double.toString(p.om));inputs.put("OL",Double.toString(p.ol));
        inputs.put("Os0",Double.toString(p.os0));inputs.put("zt",Double.toString(p.zt));
        inputs.put("wt",Double.toString(p.wt));inputs.put("w",Double.toString(p.w));
        inputs.put("w0",Double.toString(p.w0));inputs.put("wa",Double.toString(p.wa));
        inputs.put("Obh2",Double.toString(p.obh2));
        inputs.put("sigma8",Double.toString(p.sigma8));
        OmegaUiEvidence.Snapshot clicked=
            new OmegaUiEvidence.Snapshot("RLL","COS-HZ",inputs,1791580000000L);
        OmegaUiEvidence.Result uiEvidence=OmegaUiEvidence.replay(clicked);
        OmegaInputOutputParity.Result parity=OmegaInputOutputParity.reconcile(clicked,uiEvidence);
        ok(parity.gate.equals("PASS_ZERO_OMITTED_OUTPUT_RECEIPTS"),
             "full input/output parity gate");
        ok(parity.missing==0&&parity.expected==109,"every 14 input and 95 result contracts");
        CanonicalOmegaBundle.Result newFull=CanonicalOmegaBundle.build(null,null,
            "TOKEN_VAZIO_NO_NETWORK",jni,install,"gate=CHECKED_NO_NEW_ANDROID_RELEASE\n",
            "schema=rll.omega.runtime-trace.v1\n",
            "schema=rll.omega.runtime-context.v1\n",
            "gate=TOKEN_VAZIO_LOGCAT_RESTRICTED\n",controls.tsv,
            "gate=TOKEN_VAZIO_BINARY_INSPECTION_NOT_RUN\n",
            "gate=TOKEN_VAZIO_HARDWARE_PROBE_NOT_RUN\n",
            "schema=rll.omega.kernel-platform-build.v1\ngate=RECORDED_SCOPED_KERNEL_AND_BUILD_CONTEXT\n",
            "schema=rll.omega.jni-c-boundary.v1\ngate=PASS_SCOPED_JNI_BOUNDARIES\n",
            uiEvidence,parity);
        Map<String,byte[]> newFiles=unzip(newFull.zip);
        ok(s(newFiles,"02_GATES.tsv").contains("REPLAY_ALL_FORMULA_UI_ACTIONS\tPASS_SCOPED_UI_ACTIONS_REPLAY"),
            "all UI controls are bound in same archive");
        ok(s(newFiles,"02_GATES.tsv").contains("JNI_80_BOUNDARIES_AND_MANUAL\tPASS_SCOPED"),
            "extended real JNI scope in ZIP");
        ok(s(newFiles,"12_BINARY/kernel_and_compilation_context.txt").contains("kernel-platform-build.v1"),
            "kernel release and build context");
        ok(s(newFiles,"22_UI/current_RLL/individual/COS-HZ.receipt.txt").contains("id=COS-HZ"),
            "individual formula exported, not only full text");
        ok(s(newFiles,"22_UI/current_LCDM/individual/COS-HZ.receipt.txt").contains("model=LCDM"),
            "all models independently exported");
        ok(s(newFiles,"22_UI/copy_equivalent.txt").contains("clipboard_mutation=false"),
            "copy-equivalent is not hidden clipboard mutation");
        ok(s(newFiles,"02_GATES.tsv").contains("INPUT_OUTPUT_PARITY\tPASS_ZERO_OMITTED_OUTPUT_RECEIPTS"),
            "100 percent per-input output coverage is a first-class gate");
        ok(s(newFiles,"23_IO_PARITY/closure_receipt.txt").contains("omitted_output_receipts=0"),
            "zero silent output omission");
        ok(s(newFiles,"23_IO_PARITY/closure_receipt.txt").contains("source_bound_numeric_unknowns=16"),
            "scientific unknowns explicit, no invented values");
        ok(s(newFiles,"24_COMPLETENESS/observed_domain_matrix.tsv").contains("missing_domains=0"),
            "twelve system evidence domains are indexed");
        ok(s(newFiles,"02_GATES.tsv").contains("SYSTEM_DOMAIN_OUTPUT_COVERAGE\tPASS_NO_SILENT_DOMAIN_OMISSIONS"),
            "all system domains represented with receipts");
        ok(s(newFiles,"03_RECEIPT.txt").contains("archive_schema=rll.canonical.omega.zip.v5"),
            "new APK produces schema v5");
        ok(s(newFiles,"02_GATES.tsv").contains("INDEPENDENT_INSTALL_WITNESS\tTOKEN_VAZIO_NOT_ATTESTED"),
            "no fake external hardware witness");
        manifest(newFiles);
        ok(s(items,"01_ATLAS.tsv").contains("20_FORMULAS/LCDM/grid.csv"),"Atlas points");
        ok(s(items,"00_START_HERE.txt").contains("SOURCE != ARTIFACT"),"governance");
        System.out.println("RLL_CANONICAL_OMEGA_ONE_CLICK_ZIP_PASS assertions="+checks+" files="+items.size()+" model_runs=44");
    }
}
