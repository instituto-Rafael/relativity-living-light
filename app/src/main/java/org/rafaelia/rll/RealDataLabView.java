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
        TextView title=new TextView(host);title.setText("07  Dados reais • BAO DR2 • pacote de provas");
        title.setTextSize(19);title.setTextColor(0xfff9fafb);p.addView(title);
        TextView detail=new TextView(host);
        detail.setText("Um toque: baixar 13 medidas DESI DR2 e matriz 13×13, calcular 4 modelos, sensibilidade de parâmetros, recibos de instalação e abrir salvamento de ZIP.\n"
            +"O Android solicitará onde salvar. Sem dados pessoais enviados. Nenhum parâmetro é ajustado para forçar um resultado.");
        detail.setTextColor(0xffd1d5db);detail.setTextSize(14);p.addView(detail);
        Button run=new Button(host);run.setText("Baixar dados reais + calcular + gerar ZIP");run.setAllCaps(false);p.addView(run);
        status=new TextView(host);status.setTextColor(0xffd1d5db);
        status.setText("Nenhum download efetuado. Gate de ciência: não validado.");p.addView(status);
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
    private void runOnce(){
        if(running)return;
        running=true;state("Baixando dados reais DESI DR2 de revisão Git imutável...");
        new Thread(()->{
            try{
                byte[] mean=download(RealBaoEngine.MEAN),cov=download(RealBaoEngine.COV);
                RealBaoEngine.Data d=RealBaoEngine.parse(mean,cov);
                state("Fonte verificada. Calculando χ² com covariância completa (4 modelos) ...");
                StringBuilder summary=new StringBuilder("model,chi2_cov_13,dchi2_dOmega_m_abs,dchi2_dH0_abs,dchi2_dzt_abs,torus_loop_close,claim\n");
                StringBuilder residual=new StringBuilder("model,index,z,observable,observed,predicted,model_minus_observed\n");
                int ok=0;
                for(FormulaEngine.Model m:FormulaEngine.Model.values()){
                    RealBaoEngine.Score score=RealBaoEngine.score(d,m);
                    summary.append(score.csv()).append("\n");
                    for(int i=0;i<RealBaoEngine.N;i++){
                        RealBaoEngine.Datum p=d.points.get(i);
                        residual.append(String.format(Locale.US,"%s,%d,%.8g,%s,%.12g,%.12g,%.12g\n",
                            m.name(),i,p.z,p.kind,p.observed,score.prediction[i],score.residual[i]));
                    }
                    ok++;
                }
                String install=installedReceipt();
                StringBuilder meta=new StringBuilder();
                meta.append("schema=rll.android.real-bao-archive.v1\n");
                meta.append("provenance=GITHUB_PINNED_PUBLIC_DESI_DR2_MEAN_COV\n");
                meta.append("source=").append(RealBaoEngine.SOURCE).append("\n");
                meta.append("mean_source_url=").append(RealBaoEngine.RAW_BASE).append(RealBaoEngine.MEAN).append("\n");
                meta.append("cov_source_url=").append(RealBaoEngine.RAW_BASE).append(RealBaoEngine.COV).append("\n");
                meta.append("mean_sha256=").append(d.meanSha256).append("\ncov_sha256=").append(d.covSha256).append("\n");
                meta.append("mean_git_blob_sha1=").append(RealBaoEngine.MEAN_BLOB).append("\n");
                meta.append("cov_git_blob_sha1=").append(RealBaoEngine.COV_BLOB).append("\n");
                meta.append("data_points=13\ncovariance_shape=13x13\n");
                meta.append("models_completed=").append(ok).append("\n");
                meta.append("objective=(prediction-observation)^T C^-1 (prediction-observation)\n");
                meta.append("parameters=FIXED_EXPLICIT_PRESET_NOT_FITTED\n");
                meta.append("lambda_closure=E2_Z0_EQUALS_ONE_BY_MODEL\n");
                meta.append("rd=EMPIRICAL_PROXY_NOT_BOLTZMANN_DERIVED\n");
                meta.append("omega_m_step=0.005\nH0_step=0.5\nRLL_zt_step=0.05\n");
                meta.append("Poincare_recurrence=TOKEN_VAZIO_NOT_APPLICABLE_NO_DYNAMICAL_TRAJECTORY\n");
                meta.append("RMRCTI_DeltaP=TOKEN_VAZIO_NO_STABLE_ANY_PEAK_TRACE\n");
                meta.append("toroid_R=2.0\ntoroid_r=0.7\ntoroid_check=PARAMETRIC_GEOMETRIC_CLOSURE_ONLY\n");
                meta.append("data_redistribution_license=TOKEN_VAZIO_VERIFY_RIGHTS_BEFORE_REPUBLISH\n");
                meta.append("claim_allowed=false\nindependent_scientific_validation=TOKEN_VAZIO_NOT_RUN\n");
                StringBuilder readme=new StringBuilder();
                readme.append("RLL REAL DESI DR2 BAO SOURCE-FIRST ARCHIVE\n\n");
                readme.append("Dataset: 13 correlated BAO data points and full 13x13 covariance.\n");
                readme.append("Source: CobayaSampler/bao_data pinned git commit ").append(RealBaoEngine.DATA_COMMIT).append("\n");
                readme.append("The data source is cited; redistribution rights must be reviewed before publication.\n");
                readme.append("CSV: measured vs predicted and covariance chi2 for four FIXED parameter choices.\n");
                readme.append("Sensitivity: numeric finite differences, not model calibration or an optimizer.\n");
                readme.append("Toroidal closure is geometry of parameterization only; no Poincare recurrence or CTI DeltaP is inferred from cosmology.\n");
                readme.append("Physical install is self-reported by app PackageManager; not hardware-attested.\n");
                readme.append("Full physical model comparison requires Boltzmann sound horizon, official priors, likelihood + validation.\n");
                readme.append("ZIP is standard Android/Java, not a RAR archive. Export requests system document approval.\n");
                Map<String,byte[]> entries=new LinkedHashMap<>();
                entries.put("README.txt",utf(readme.toString()));
                entries.put("raw/"+RealBaoEngine.MEAN,mean);
                entries.put("raw/"+RealBaoEngine.COV,cov);
                entries.put("results/model_scores.csv",utf(summary.toString()));
                entries.put("results/observed_vs_predicted.csv",utf(residual.toString()));
                entries.put("receipts/source_and_scope.txt",utf(meta.toString()));
                entries.put("receipts/android_install_self_report.txt",utf(install));
                entries.put("references/primary_sources.txt",utf(
                   "DESI DR2 primary: https://arxiv.org/abs/2503.14738\n"+
                   "Dynamical DE DR2 analysis: https://arxiv.org/abs/2504.06118\n"+
                   "CMBComp late-universe likelihood benchmark: https://arxiv.org/abs/2606.18455\n"+
                   "RMRCTI stable_any DeltaP source: llamaRafaelia/rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md\n"+
                   "No external paper is evidence of RLL physical validation.\n"));
                StringBuilder hashes=new StringBuilder("sha256  path\n");
                for(Map.Entry<String,byte[]> entry:entries.entrySet())
                    hashes.append(RealBaoEngine.sha256(entry.getValue())).append("  ").append(entry.getKey()).append("\n");
                entries.put("MANIFEST_SHA256.txt",utf(hashes.toString()));
                File out=new File(host.getCacheDir(),"rll_real_desi_dr2_evidence.zip");
                try(ZipOutputStream zip=new ZipOutputStream(new FileOutputStream(out))){
                    for(Map.Entry<String,byte[]> entry:entries.entrySet())put(zip,entry.getKey(),entry.getValue());
                }
                stagedZip=out;
                try(InputStream in=new FileInputStream(out)){
                    MessageDigest dig=MessageDigest.getInstance("SHA-256");
                    byte[] bytes=new byte[4096];int n;while((n=in.read(bytes))!=-1)dig.update(bytes,0,n);
                    zipDigest=RealBaoEngine.hex(dig.digest());
                }
                state("SUCESSO ESCOPO COMPUTACIONAL • 13 pontos BAO reais, 13×13 covariância, 4 modelos.\n"
                     +"ZIP SHA-256: "+zipDigest+"\nAguardando escolha de local de salvamento.");
                host.runOnUiThread(()->{
                    Intent save=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    save.addCategory(Intent.CATEGORY_OPENABLE);
                    save.setType("application/zip");
                    save.putExtra(Intent.EXTRA_TITLE,"RLL_DESI_DR2_EVIDENCE.zip");
                    host.startActivityForResult(save,SAVE_REQUEST);
                });
            }catch(Exception ex){
                stagedZip=null;state("FALHA TIPADA: "+ex.getClass().getSimpleName()+": "+ex.getMessage()
                    +"\nNenhum χ² publicado sem fonte, integridade e covariância válidas.");
            }finally{running=false;}
        },"rll-real-desi-zip").start();
    }
    public void writeTo(Uri uri){
        if(uri==null||stagedZip==null){state("TOKEN_VAZIO_SAVE_CANCELLED");return;}
        try(InputStream input=new FileInputStream(stagedZip);
            OutputStream output=host.getContentResolver().openOutputStream(uri)){
            if(output==null)throw new IllegalStateException("no destination stream");
            byte[] buf=new byte[8192];int n;while((n=input.read(buf))!=-1)output.write(buf,0,n);
            output.flush();
            state("ZIP SALVO • conteúdo rastreável\nSHA-256: "+zipDigest
                +"\nNão é prova científica independente; instalação autoatestada pelo app.");
        }catch(Exception ex){state("TOKEN_VAZIO_SAVE_FAILED: "+ex.getClass().getSimpleName());}
    }
}
