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
        ok(s(items,"01_ATLAS.tsv").contains("20_FORMULAS/LCDM/grid.csv"),"Atlas points");
        ok(s(items,"00_START_HERE.txt").contains("SOURCE != ARTIFACT"),"governance");
        System.out.println("RLL_CANONICAL_OMEGA_ONE_CLICK_ZIP_PASS assertions="+checks+" files="+items.size()+" model_runs=44");
    }
}
