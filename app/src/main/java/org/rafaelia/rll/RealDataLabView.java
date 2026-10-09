package org.rafaelia.rll;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.content.pm.SigningInfo;
import android.net.Uri;
import android.os.Build;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/** User-triggered, local ZIP evidence export; no telemetry or remote upload. */
public final class RealDataLabView {
    public static final int SAVE_REQUEST=5042;
    private static final int MAX_DATA=65536;
    private final Activity host;
    private final TextView status;
    private File stagedZip;
    private String zipDigest="";
    private volatile boolean running=false;
    public RealDataLabView(Activity activity,LinearLayout root){
        host=activity;
        LinearLayout p=new LinearLayout(host);p.setOrientation(LinearLayout.VERTICAL);
        p.setPadding(16,12,16,16);p.setBackgroundColor(0xff1f2937);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);
        lp.setMargins(0,0,0,16);root.addView(p,lp);
        TextView title=new TextView(host);title.setText("00  Ω v0.6 • TESTAR TUDO EM UM CLIQUE");
        title.setTextSize(19);title.setTextColor(0xfff9fafb);p.addView(title);
        TextView detail=new TextView(host);
        detail.setText("Um toque: JNI/C, 4 modelos × 11 pontos, 6 diferenças pareadas × 11, falsificadores, DESI DR2, APK/DEX/ELF, CPU, RAM, armazenamento, NUMA quando permitido, gates e ZIP SHA-256.\n"
            +"Mesmo sem rede, o ZIP guarda os testes locais e os TOKEN_VAZIO. O Android solicitará apenas onde salvar. Logs coletados: somente processo RLL, se permitido. Sem READ_LOGS/root; nada é enviado, além do download solicitado.");
        detail.setTextColor(0xffd1d5db);detail.setTextSize(14);p.addView(detail);
        Button run=new Button(host);run.setText("UM CLIQUE Ω v0.6: TESTAR MODELOS + HW + APK + GERAR ZIP");run.setAllCaps(false);p.addView(run);
        status=new TextView(host);status.setTextColor(0xffd1d5db);
        status.setText("Pronto para gerar uma única evidência canônica; validação física independente não atestada.");p.addView(status);
        run.setOnClickListener(v->runOnce());
    }
    private void state(String s){host.runOnUiThread(()->status.setText(s));}
    private static byte[] download(String filename)throws Exception {
        URL url=new URL(RealBaoEngine.RAW_BASE+filename);
        if(!"https".equals(url.getProtocol())||
           !"raw.githubusercontent.com".equals(url.getHost()))
            throw new IllegalArgumentException("remote origin blocked");
        HttpURLConnection c=(HttpURLConnection)url.openConnection();
        c.setInstanceFollowRedirects(false);
        c.setConnectTimeout(10000);c.setReadTimeout(12000);
        c.setRequestProperty("Accept","text/plain");
        c.setRequestProperty("User-Agent","RLL-Formula-Lab-RealData/1");
        try{
            if(c.getResponseCode()!=200)throw new IllegalStateException("data_http_"+c.getResponseCode());
            try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){
                byte[] b=new byte[4096];int n;
                while((n=in.read(b))!=-1){
                    if(out.size()+n>MAX_DATA)throw new IllegalArgumentException("data too large");
                    out.write(b,0,n);
                }
                return out.toByteArray();
            }
        }finally{c.disconnect();}
    }
    private String installedReceipt() {
        StringBuilder s=new StringBuilder();
        s.append("source=APP_OWN_PACKAGE_MANAGER_NOT_INDEPENDENT_DEVICE_ATTESTATION\n");
        s.append("source_git_head_build_label=").append(BuildConfig.RLL_GITHUB_HEAD).append("\n");
        s.append("provider_ci_run_id_build_label=").append(BuildConfig.RLL_GITHUB_RUN_ID).append("\n");
        s.append("sdk=").append(Build.VERSION.SDK_INT).append("\n");
        s.append("device_abi=").append(Build.SUPPORTED_ABIS.length==0?"TOKEN_VAZIO":Build.SUPPORTED_ABIS[0]).append("\n");
        s.append("manufacturer=").append(Build.MANUFACTURER).append("\nmodel=").append(Build.MODEL).append("\n");
        try{
            PackageManager pm=host.getPackageManager();
            int flags=Build.VERSION.SDK_INT>=28?PackageManager.GET_SIGNING_CERTIFICATES:PackageManager.GET_SIGNATURES;
            PackageInfo p=pm.getPackageInfo(host.getPackageName(),flags);
            s.append("package=").append(p.packageName).append("\nversion_name=").append(p.versionName).append("\n");
            long v=Build.VERSION.SDK_INT>=28?p.getLongVersionCode():p.versionCode;
            s.append("version_code=").append(v).append("\nfirst_install_utc_ms=").append(p.firstInstallTime)
              .append("\nlast_update_utc_ms=").append(p.lastUpdateTime).append("\n");
            Signature[] certificates;
            if(Build.VERSION.SDK_INT>=28) {
                SigningInfo si=p.signingInfo;
                certificates=si==null?null:(si.hasMultipleSigners()?si.getApkContentsSigners():si.getSigningCertificateHistory());
            } else certificates=p.signatures;
            if(certificates==null||certificates.length==0)s.append("signer_sha256=TOKEN_VAZIO\n");
            else for(Signature cert:certificates)s.append("signer_sha256=").append(RealBaoEngine.sha256(cert.toByteArray())).append("\n");
            String path=p.applicationInfo==null?null:p.applicationInfo.sourceDir;
            if(path==null)s.append("installed_apk_sha256=TOKEN_VAZIO\n");
            else {
                try(InputStream in=new FileInputStream(path)){
                    MessageDigest dig=MessageDigest.getInstance("SHA-256");
                    byte[] buf=new byte[8192];int n;long size=0;
                    while((n=in.read(buf))!=-1){size+=n;dig.update(buf,0,n);}
                    s.append("installed_apk_bytes=").append(size).append("\ninstalled_apk_sha256=")
                       .append(RealBaoEngine.hex(dig.digest())).append("\n");
                }catch(Exception ex){s.append("installed_apk_sha256=TOKEN_VAZIO_").append(ex.getClass().getSimpleName()).append("\n");}
            }
        }catch(Exception ex){s.append("package_proof=TOKEN_VAZIO_").append(ex.getClass().getSimpleName()).append("\n");}
        s.append("physical_install_observation=APP_SELF_REPORT_ONLY\n")
         .append("hardware_attestation=TOKEN_VAZIO_NOT_RUN\n");
        return s.toString();
    }
    private static void put(ZipOutputStream zip,String name,byte[] data)throws Exception {
        ZipEntry entry=new ZipEntry(name);
        entry.setTime(0L);
        zip.putNextEntry(entry);zip.write(data);zip.closeEntry();
    }
    private static byte[] utf(String s){return s.getBytes(StandardCharsets.UTF_8);}
    private String nativeReceipt(){
        StringBuilder s=new StringBuilder("RLL_NATIVE_ANDROID_JNI_SELF_TEST\n"
          +"source=APP_RUNTIME_LOCAL_JNI_NOT_INDEPENDENT_DEVICE_ATTESTATION\n");
        try{
            int arch=KernelBridge.archDetect();
            int[][] vectors={{0,0},{7,11},{1,1},{12,21}};
            int pass=0;
            for(int[] v:vectors){
                int actual=KernelBridge.kernelScore(v[0],v[1]);
                int expected=((v[0]*31)^(v[1]*17))+arch;
                boolean same=expected==actual && (arch==32||arch==64);
                if(same)pass++;
                s.append("vector=").append(v[0]).append(',').append(v[1])
                 .append(";C=").append(actual).append(";Java=").append(expected)
                 .append(";pass=").append(same).append('\n');
            }
            s.append("arch=").append(arch).append("\nandroid_abi=")
             .append(Build.SUPPORTED_ABIS.length==0?"TOKEN_VAZIO":Build.SUPPORTED_ABIS[0])
             .append("\ngate=").append(pass==4?"PASS_SCOPED":"FAIL_SCOPED")
             .append("\npass_count=").append(pass).append("/4\n");
        }catch(LinkageError|RuntimeException ex){
            s.append("gate=FAIL_JNI\nerror_class=").append(ex.getClass().getSimpleName()).append('\n');
        }
        s.append("scientific_validation=TOKEN_VAZIO_NOT_RUN\n");
        return s.toString();
    }
    private String releaseReceipt(){
        StringBuilder out=new StringBuilder("source=OFFICIAL_GITHUB_RELEASE_API\n"
                 +"release_asset_expected=rll-android-release.apk\n");
        try{
            android.content.pm.PackageInfo p=host.getPackageManager()
                .getPackageInfo(host.getPackageName(),0);
            int installed=Build.VERSION.SDK_INT>=28?(int)p.getLongVersionCode():p.versionCode;
            ReleaseGateView.Candidate candidate=ReleaseGateView.select(ReleaseGateView.fetch(),installed);
            out.append("installed_version_code=").append(installed).append('\n');
            if(candidate==null){
                out.append("gate=CHECKED_NO_NEW_ANDROID_RELEASE\n")
                   .append("new_release=NONE_MATCHING_SIGNED_DIGEST_CONTRACT\n");
            }else{
                out.append("gate=CHECKED_NEW_ANDROID_RELEASE_METADATA\n")
                    .append("tag=").append(candidate.tag)
                    .append("\nversion_code=").append(candidate.version)
                    .append("\npublic_digest=").append(candidate.sha).append('\n')
                    .append("url=").append(candidate.url).append('\n')
                    .append("signer_compatibility=TOKEN_VAZIO_NOT_ATTESTED\n");
            }
        }catch(Exception ex){
            out.append("gate=TOKEN_VAZIO_PROVIDER_RELEASE_DISCOVERY\n")
               .append("failure_type=").append(ex.getClass().getSimpleName()).append('\n');
        }
        out.append("auto_install=false\n");
        return out.toString();
    }
    private void runOnce(){
        if(running)return;
        running=true;
        stagedZip=null;
        state("Ω • Coletando proveniência, modelos, logs e gates automaticamente...");
        new Thread(()->{
            OmegaRuntimeEvidence trace=new OmegaRuntimeEvidence();
            long stage=android.os.SystemClock.elapsedRealtime();
            try{
                trace.event("USER_ONE_CLICK","START",0);
                String install=installedReceipt();
                trace.event("PACKAGE_MANAGER","OBSERVED_SELF_REPORT",
                            android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                String jni=nativeReceipt();
                trace.event("JNI_C_FOUR_VECTORS",
                    jni.contains("gate=PASS_SCOPED")?"PASS_SCOPED":"FAIL_SCOPED",
                    android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                String osContext=trace.context(host);
                trace.event("OS_PROCESS_CONTEXT","RECORDED_LOCAL",
                    android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                state("Ω • Medindo hardware acessível e verificando APK, DEX e ELF...");
                String hardwareProbe;
                try { hardwareProbe=OmegaDeepDiagnostics.capture(host); }
                catch(Exception ex){
                    hardwareProbe="gate=TOKEN_VAZIO_HW_PROBE_"+ex.getClass().getSimpleName()+"\\n";
                }
                trace.event("HW_CPU_RAM_STORAGE_NUMA",
                    hardwareProbe.contains("gate=RECORDED_APP_SCOPED")
                      ?"RECORDED_APP_SCOPED":"TOKEN_VAZIO_RESTRICTED",
                    android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                String binaryInspection;
                try {
                    String ownApk=host.getApplicationInfo().sourceDir;
                    binaryInspection=OmegaBinaryInspector.inspect(
                        ownApk==null?null:new File(ownApk));
                }catch(Exception ex){
                    binaryInspection="gate=TOKEN_VAZIO_APK_INSPECT_"
                        +ex.getClass().getSimpleName()+"\\n";
                }
                trace.event("OWN_APK_DEX_ELF",
                    binaryInspection.contains("gate=PASS_SCOPED_APK_DEX_ELF_CRC")
                     ?"PASS_SCOPED_SELF_INSPECTION":"FAIL_OR_TOKEN_VAZIO",
                    android.os.SystemClock.elapsedRealtime()-stage);
                byte[] mean=null,cov=null;
                String downloadStatus="PASS_SOURCE_BYTES_RETRIEVED";
                stage=android.os.SystemClock.elapsedRealtime();
                try{
                    state("Ω • Baixando e verificando dados DESI DR2 e matriz 13×13...");
                    mean=download(RealBaoEngine.MEAN);
                    cov=download(RealBaoEngine.COV);
                    trace.event("DESI_DOWNLOAD","BYTES_RECEIVED",
                         android.os.SystemClock.elapsedRealtime()-stage);
                }catch(Exception failure){
                    mean=null;cov=null;
                    downloadStatus="TOKEN_VAZIO_DOWNLOAD_"+failure.getClass().getSimpleName();
                    trace.event("DESI_DOWNLOAD","TOKEN_VAZIO_PROVIDER",
                         android.os.SystemClock.elapsedRealtime()-stage);
                }
                stage=android.os.SystemClock.elapsedRealtime();
                state("Ω • Testando identidades, limites e parâmetros de todos os modelos...");
                OmegaScientificChecks.Result controls=OmegaScientificChecks.run();
                trace.event("EXTENDED_FORMULA_CHECKS",
                    controls.failed==0?"PASS_SCOPED":"FAIL_NUMERIC",
                    android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                state("Ω • Conferindo versões, assinatura e origem do APK...");
                String release=releaseReceipt();
                trace.event("GITHUB_RELEASE_DISCOVERY",
                    release.contains("gate=CHECKED")?"CHECKED_SCOPE":"TOKEN_VAZIO_PROVIDER",
                    android.os.SystemClock.elapsedRealtime()-stage);
                stage=android.os.SystemClock.elapsedRealtime();
                state("Ω • Capturando eventos locais e logcat do próprio processo...");
                String logcat=trace.ownPidLogcat();
                trace.event("OWN_PID_LOGCAT",
                    logcat.contains("gate=CAPTURED_OWN_PROCESS_BEST_EFFORT")
                        ?"CAPTURED_SCOPED":"TOKEN_VAZIO_RESTRICTED",
                    android.os.SystemClock.elapsedRealtime()-stage);
                trace.event("CANONICAL_ZIP_ASSEMBLY","START",0);
                state("Ω • Gerando os 44 recibos, todas as fórmulas e o ZIP único...");
                CanonicalOmegaBundle.Result result=CanonicalOmegaBundle.build(
                    mean,cov,downloadStatus,jni,install,release,trace.trace(),
                    osContext,logcat,controls.tsv,binaryInspection,hardwareProbe);
                File out=new File(host.getCacheDir(),"rll_canonical_omega_evidence.zip");
                try(FileOutputStream stream=new FileOutputStream(out)){
                    stream.write(result.zip);
                    stream.getFD().sync();
                }
                stagedZip=out;
                zipDigest=result.sha256;
                state("ZIP Ω GERADO: "+result.files+" arquivos. Dados: "+result.dataState
                    +"\nChecagens "+controls.passed+" PASS / "+controls.failed+" FAIL."
                    +"\nSHA-256: "+zipDigest
                    +"\nEscolha apenas onde salvar o único ZIP.");
                host.runOnUiThread(()->{
                    Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    save.addCategory(Intent.CATEGORY_OPENABLE);
                    save.setType("application/zip");
                    save.putExtra(Intent.EXTRA_TITLE,"RLL_CANONICAL_OMEGA_ALL_EVIDENCE.zip");
                    try{host.startActivityForResult(save,SAVE_REQUEST);}
                    catch(RuntimeException ex){
                        state("TOKEN_VAZIO_SAVE_PICKER_UNAVAILABLE: "+ex.getClass().getSimpleName());
                    }
                });
            }catch(Exception ex){
                stagedZip=null;
                state("FALHA_CANONICAL_ZIP: "+ex.getClass().getSimpleName()
                    +". Nenhuma aprovação presumida.");
            }finally{running=false;}
        },"rll-canonical-omega-v06").start();
    }
    public void writeTo(Uri uri){
        if(uri==null||stagedZip==null){state("TOKEN_VAZIO_SAVE_CANCELLED");return;}
        // The system provider owns the target. Verify exported bytes after close.
        try(InputStream input=new FileInputStream(stagedZip);
            OutputStream output=host.getContentResolver().openOutputStream(uri,"wt")){
            if(output==null)throw new IllegalStateException("no destination stream");
            byte[] buf=new byte[8192];int n;while((n=input.read(buf))!=-1)output.write(buf,0,n);
            output.flush();
        }catch(Exception ex){
            state("TOKEN_VAZIO_SAVE_FAILED: "+ex.getClass().getSimpleName());return;
        }
        try(InputStream saved=host.getContentResolver().openInputStream(uri)){
            if(saved==null)throw new IllegalStateException("no readback stream");
            MessageDigest dig=MessageDigest.getInstance("SHA-256");
            byte[] buf=new byte[8192];int n;while((n=saved.read(buf))!=-1)dig.update(buf,0,n);
            String observed=RealBaoEngine.hex(dig.digest());
            if(!observed.equals(zipDigest)){
                state("FALHA_SAVE_READBACK_SHA256: arquivo exportado diverge da origem!");
                return;
            }
            state("PASS_SAVE_READBACK_SHA256 • ZIP CANÔNICO SALVO\nSHA-256: "+observed
                 +"\nRecibos físicos são auto-relato do app, não atestado independente.");
        }catch(Exception ex){
            state("ZIP ENVIADO AO DESTINO • TOKEN_VAZIO_SAVE_READBACK_"
                  +ex.getClass().getSimpleName()+"\nSHA-256 local: "+zipDigest);
        }
    }
}
