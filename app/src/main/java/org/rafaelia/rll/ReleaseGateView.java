package org.rafaelia.rll;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import org.json.JSONArray;
import org.json.JSONObject;

/** Release update discovery, not a silent installer or updater without user consent. */
public final class ReleaseGateView {
    private static final String API="https://api.github.com/repos/instituto-Rafael/relativity-living-light/releases?per_page=25";
    private static final String WEB="https://github.com/instituto-Rafael/relativity-living-light/releases/tag/";
    private static final String NAME="rll-android-release.apk";
    private final Activity host;
    private TextView status;
    private Button open;
    private String pendingUrl;
    private boolean inFlight=false;
    public ReleaseGateView(Activity host){this.host=host;}
    static final class Candidate {
        final int version;
        final String tag, sha, url;
        Candidate(int v,String t,String s) {
            version=v;tag=t;sha=s;url=WEB+t;
        }
    }
    public static Candidate select(String json,int installed) throws Exception {
        JSONArray releases=new JSONArray(json);
        Candidate latest=null;
        for(int i=0;i<releases.length();i++){
            JSONObject r=releases.optJSONObject(i);
            if(r==null||r.optBoolean("draft",true)||r.optBoolean("prerelease",true))continue;
            String tag=r.optString("tag_name","");
            if(!tag.matches("android-rll-v[1-9][0-9]{0,8}"))continue;
            int revision;
            try{revision=Integer.parseInt(tag.substring("android-rll-v".length()));}
            catch(NumberFormatException ignored){continue;}
            if(revision<=installed)continue;
            JSONArray assets=r.optJSONArray("assets");
            if(assets==null)continue;
            for(int j=0;j<assets.length();j++){
                JSONObject asset=assets.optJSONObject(j);
                if(asset==null||!NAME.equals(asset.optString("name"))
                    ||!"uploaded".equals(asset.optString("state"))
                    ||asset.optLong("size",0)<5000)continue;
                String sha=asset.optString("digest","");
                if(!sha.matches("sha256:[0-9a-f]{64}"))continue;
                if(latest==null||revision>latest.version)latest=new Candidate(revision,tag,sha);
            }
        }
        return latest;
    }
    private int installedCode() throws Exception {
        PackageInfo info=host.getPackageManager().getPackageInfo(host.getPackageName(),0);
        if(Build.VERSION.SDK_INT>=28)return (int)info.getLongVersionCode();
        return info.versionCode;
    }
    private static String fetch() throws Exception {
        HttpURLConnection conn=(HttpURLConnection)new URL(API).openConnection();
        conn.setConnectTimeout(4000);conn.setReadTimeout(4000);
        conn.setRequestProperty("Accept","application/vnd.github+json");
        conn.setRequestProperty("User-Agent","RLL-Android-Release-Gate");
        try {
            if(conn.getResponseCode()!=200)throw new IllegalStateException("HTTP "+conn.getResponseCode());
            try(InputStream in=conn.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){
                byte[] buf=new byte[4096];int n;
                while((n=in.read(buf))!=-1){
                    if(out.size()+n>262144)throw new IllegalStateException("release index too large");
                    out.write(buf,0,n);
                }
                return new String(out.toByteArray(),StandardCharsets.UTF_8);
            }
        } finally {conn.disconnect();}
    }
    public void attach(LinearLayout root) {
        LinearLayout box=new LinearLayout(host);box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(16,12,16,14);box.setBackgroundColor(0xff1f2937);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,0,0,12);
        root.addView(box,lp);
        TextView title=new TextView(host);title.setText("06  Revisões e atualizações");
        title.setTextColor(0xfff9fafb);title.setTextSize(19);box.addView(title);
        status=new TextView(host);
        status.setTextColor(0xffd1d5db);status.setTextSize(14);
        try{
            PackageInfo info=host.getPackageManager().getPackageInfo(host.getPackageName(),0);
            status.setText("Versão instalada: "+info.versionName+" (code "+installedCode()+")\n"
                +"Busca HTTPS no GitHub ao abrir. Sem telemetria própria.\n"
                +"Instalação sempre depende de confirmação e assinatura compatível.");
        }catch(Exception ex){status.setText("TOKEN_VAZIO_INSTALLED_VERSION");}
        box.addView(status);
        Button check=new Button(host);check.setAllCaps(false);
        check.setText("Verificar nova revisão");box.addView(check);check.setOnClickListener(v->check(false));
        open=new Button(host);open.setAllCaps(false);open.setText("Abrir release verificada");open.setEnabled(false);
        box.addView(open);
        open.setOnClickListener(v->{
            if(pendingUrl==null)return;
            new AlertDialog.Builder(host).setTitle("Revisão Android")
                .setMessage("Abrir a página oficial no navegador? O Android exigirá instalação pelo usuário e certificado de assinatura compatível. O aplicativo não instala automaticamente.")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Abrir", (dialog,which)->{
                    Intent intent=new Intent(Intent.ACTION_VIEW,Uri.parse(pendingUrl));
                    if(intent.resolveActivity(host.getPackageManager())!=null)host.startActivity(intent);
                    else status.setText("TOKEN_VAZIO_NO_BROWSER");
                }).show();
        });
        check(true);
    }
    private void check(boolean automatic) {
        if(inFlight)return;inFlight=true;
        status.append("\nConsultando releases Android assinadas...");
        new Thread(()->{
            Candidate candidate=null;String failure=null;
            try{candidate=select(fetch(),installedCode());}
            catch(Exception ex){failure="TOKEN_VAZIO_UPDATE_NETWORK_OR_RESPONSE: "+ex.getClass().getSimpleName();}
            final Candidate result=candidate;final String error=failure;
            host.runOnUiThread(()->{
                inFlight=false;
                if(error!=null){status.setText(error+"\nVerifique a conexão e tente novamente.");return;}
                if(result==null){
                    pendingUrl=null;open.setEnabled(false);
                    status.setText("Nenhuma revisão Android mais recente com APK e SHA-256 publicados no GitHub.\n"
                        +"Outras releases científicas do RLL não são pacotes Android.");
                    return;
                }
                pendingUrl=result.url;open.setEnabled(true);
                status.setText("Revisão "+result.version+" encontrada no GitHub.\n"
                    +result.tag+"\nZIP/APK digest publicado: "+result.sha+"\n"
                    +"Assinatura compatível e conteúdo interno ainda não atestados neste dispositivo.");
                if(automatic){
                    new AlertDialog.Builder(host).setTitle("Nova revisão RLL disponível")
                        .setMessage("A revisão Android "+result.version+" está publicada com digest. Deseja abrir a página oficial para atualização manual?")
                        .setNegativeButton("Depois",null)
                        .setPositiveButton("Ver release",(dialog,which)->open.performClick()).show();
                }
            });
        },"rll-android-release-check").start();
    }
}
