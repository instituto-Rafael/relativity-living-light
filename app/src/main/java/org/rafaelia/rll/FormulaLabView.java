package org.rafaelia.rll;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.graphics.Color;
import android.text.InputType;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

/** UI adapter only: authoritative calculation logic stays in FormulaEngine. */
public final class FormulaLabView {
    private final Activity host;
    private final Map<String,EditText> fields=new LinkedHashMap<>();
    private Spinner selector;
    private Spinner formulaPicker;
    private FormulaEngine.Result lastResult;
    private TextView output;
    private TextView state;
    private String lastReceipt="";
    private static final int FG=Color.rgb(244,246,251), SECOND=Color.rgb(203,213,225);
    public FormulaLabView(Activity host){this.host=host;}
    private int px(int value){return (int)(value*host.getResources().getDisplayMetrics().density+0.5f);}
    private TextView label(LinearLayout parent,String text,int sp,int color){
        TextView view=new TextView(host);view.setText(text);view.setTextSize(sp);view.setTextColor(color);
        view.setPadding(0,px(6),0,px(4));view.setTextIsSelectable(true);parent.addView(view);return view;
    }
    private Button button(LinearLayout parent,String title,View.OnClickListener click) {
        Button b=new Button(host);b.setText(title);b.setAllCaps(false);b.setOnClickListener(click);parent.addView(b);return b;
    }
    private void edit(LinearLayout root,String key,String hint,double value){
        label(root,hint,13,SECOND);
        EditText e=new EditText(host);e.setSingleLine(true);
        e.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        e.setText(String.format(Locale.US,"%.9g",value));
        e.setTextColor(FG);e.setTextSize(16);fields.put(key,e);
        root.addView(e,new LinearLayout.LayoutParams(-1,-2));
    }
    private void optional(LinearLayout root,String key,String hint){
        label(root,hint,13,SECOND);
        EditText e=new EditText(host);e.setSingleLine(true);
        e.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_SIGNED|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        e.setHint("Não fornecido — TOKEN_VAZIO");e.setHintTextColor(SECOND);e.setTextColor(FG);
        fields.put(key,e);root.addView(e,new LinearLayout.LayoutParams(-1,-2));
    }
    private double val(String key) {
        String s=fields.get(key).getText().toString().trim().replace(',','.');
        if(s.isEmpty())throw new IllegalArgumentException("Preencha "+key);
        return Double.parseDouble(s);
    }
    private FormulaEngine.Input read(){
        FormulaEngine.Input a=new FormulaEngine.Input();
        a.z=val("z");a.h0=val("H0");a.om=val("Om");a.ol=val("OL");
        a.os0=val("Os0");a.zt=val("zt");a.wt=val("wt");
        a.w=val("w");a.w0=val("w0");a.wa=val("wa");
        a.obh2=val("Obh2");a.sigma8=val("sigma8");
        String observed=fields.get("Hobs").getText().toString().trim();
        String sigma=fields.get("Hsigma").getText().toString().trim();
        if(!observed.isEmpty()||!sigma.isEmpty()){
            if(observed.isEmpty()||sigma.isEmpty())throw new IllegalArgumentException("H observado exige sigma e vice-versa");
            a.hObserved=Double.parseDouble(observed.replace(',','.'));
            a.hSigma=Double.parseDouble(sigma.replace(',','.'));
        }
        return a;
    }
    private FormulaEngine.Model selected(){return (FormulaEngine.Model)selector.getSelectedItem();}
    private void calculate(){
        try{
            FormulaEngine.Input a=read();
            FormulaEngine.Result r=FormulaEngine.compute(a,selected());
            lastResult=r;
            String[] choices=new String[r.entries.size()];
            for(int i=0;i<choices.length;i++)choices[i]=r.entries.get(i).id;
            ArrayAdapter<String> formulaOptions=new ArrayAdapter<>(host,android.R.layout.simple_spinner_item,choices);
            formulaOptions.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
            formulaPicker.setAdapter(formulaOptions);
            StringBuilder screen=new StringBuilder();
            screen.append("Estado: ").append(r.state).append("\n");
            screen.append("Calculadas: ").append(r.computed).append("  |  vazios tipados: ").append(r.gap).append("\n\n");
            for(FormulaEngine.Entry e:r.entries){
                screen.append(e.display()).append("\n\n");
            }
            screen.append("Limite: ").append(r.warning).append("\n");
            output.setText(screen.toString());
            state.setText(r.state+" · "+r.computed+" fórmulas");
            lastReceipt=r.receipt(a)+"version_gate=SEE_RELEASE_CHECK\n";
        }catch(NumberFormatException e){
            state.setText("TOKEN_VAZIO_DOMAIN_INPUT");
            output.setText("Número inválido. Use decimal com vírgula ou ponto.");
            lastReceipt="";
        }catch(IllegalArgumentException e){
            state.setText("TOKEN_VAZIO_DOMAIN_INPUT");
            output.setText(e.getMessage());lastReceipt="";
        }
    }
    private void showSelected() {
        if(lastResult==null||lastResult.entries.isEmpty())return;
        int index=formulaPicker.getSelectedItemPosition();
        if(index<0||index>=lastResult.entries.size())return;
        FormulaEngine.Entry e=lastResult.entries.get(index);
        String value=e.value==null?e.state:Double.toString(e.value)+" "+e.unit;
        output.setText("FÓRMULA: "+e.id+"\\n"+e.expression
          +"\\nValor: "+value+"\\nUnidade: "+e.unit
          +"\\nFonte: "+e.source+"\\nEstado: "+e.state
          +"\\nLimite: "+e.note+"\\n\\nclaim_allowed=false");
    }
    private void sweep(){
        try{
            FormulaEngine.Input p=read();
            StringBuilder lines=new StringBuilder("Varredura numérica 0 ≤ z ≤ 3, passo 0,3\\n");
            lines.append("z;E²;H(z) [km/s/Mpc]\\n");
            StringBuilder evidence=new StringBuilder();
            for(int i=0;i<=10;i++){
                p.z=0.3*i;
                FormulaEngine.Result result=FormulaEngine.compute(p,selected());
                if(!"SOURCE_SCOPED_DIAGNOSTIC".equals(result.state)){
                    lines.append(p.z).append(";TOKEN_VAZIO;").append(result.state).append("\\n");
                    evidence.append("z=").append(p.z).append(";state=").append(result.state).append("\\n");
                    continue;
                }
                Double e2=null,hz=null;
                for(FormulaEngine.Entry entry:result.entries){
                    if(entry.id.startsWith("COS-E2-")&&!entry.id.equals("COS-E2-ZERO"))e2=entry.value;
                    if(entry.id.equals("COS-HZ"))hz=entry.value;
                }
                String row=String.format(Locale.US,"%.2f;%.9g;%.9g\\n",p.z,e2,hz);
                lines.append(row);evidence.append("grid_").append(row);
            }
            output.setText(lines.toString()+"\\nSem dados observacionais: isto é uma curva calculada, não ajuste.");
            lastReceipt+=evidence.toString()+"grid_scope=MODEL_ONLY_NO_OBSERVATIONS\\n";
        }catch(RuntimeException ex){
            output.setText("TOKEN_VAZIO_DOMAIN_INPUT: não foi possível executar varredura.");
        }
    }
    private void normalize(){
        try{
            FormulaEngine.Input in=read();
            double corrected=FormulaEngine.closedOl(in,selected());
            fields.get("OL").setText(String.format(Locale.US,"%.10g",corrected));
            calculate();
        }catch(RuntimeException ex){state.setText("TOKEN_VAZIO_DOMAIN_INPUT");output.setText("Revise os parâmetros antes de normalizar.");}
    }
    private static String sha256(String s){
        try{
            byte[] bytes=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));
            StringBuilder h=new StringBuilder();
            for(byte b:bytes)h.append(String.format(Locale.US,"%02x",b&255));
            return h.toString();
        }catch(java.security.NoSuchAlgorithmException impossible){return "TOKEN_VAZIO_SHA256_UNAVAILABLE";}
    }
    private void copy(){
        if(lastReceipt.isEmpty()){
            Toast.makeText(host,"Execute as fórmulas antes",Toast.LENGTH_SHORT).show();
            return;
        }
        String receipt=lastReceipt+"receipt_sha256="+sha256(lastReceipt)+"\n";
        ClipboardManager manager=(ClipboardManager)host.getSystemService(Activity.CLIPBOARD_SERVICE);
        if(manager==null){Toast.makeText(host,"Clipboard indisponível",Toast.LENGTH_SHORT).show();return;}
        manager.setPrimaryClip(ClipData.newPlainText("RLL formula evidence v1",receipt));
        Toast.makeText(host,"Recibo de cálculo copiado",Toast.LENGTH_SHORT).show();
    }
    public void attach(LinearLayout outer){
        LinearLayout root=new LinearLayout(host);root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(px(16),px(16),px(16),px(16));root.setBackgroundColor(Color.rgb(31,41,55));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,0,0,px(12));outer.addView(root,lp);
        label(root,"05  Laboratório de fórmulas RLL",20,FG);
        label(root,"Fundo cosmológico e testes locais; resultados não são validação observacional.",13,SECOND);
        label(root,"Família do modelo",14,SECOND);
        selector=new Spinner(host);
        ArrayAdapter<FormulaEngine.Model> adapter=new ArrayAdapter<>(host,android.R.layout.simple_spinner_item,FormulaEngine.Model.values());
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        selector.setAdapter(adapter);selector.setSelection(3);root.addView(selector,new LinearLayout.LayoutParams(-1,-2));
        label(root,"Parâmetros sem fonte observacional por padrão; modifique e reproduza.",14,SECOND);
        FormulaEngine.Input a=new FormulaEngine.Input();
        edit(root,"z","z — redshift (0 a 10)",a.z);
        edit(root,"H0","H₀ — km/s/Mpc",a.h0);
        edit(root,"Om","Ωm — matéria",a.om);
        edit(root,"OL","ΩΛ — valor livre (fechamento opcional)",a.ol);
        edit(root,"Os0","Ωs0 — setor RLL",a.os0);
        edit(root,"zt","zt — redshift de transição",a.zt);
        edit(root,"wt","wt — largura > 0",a.wt);
        edit(root,"w","w — wCDM",a.w);
        edit(root,"w0","w₀ — CPL",a.w0);
        edit(root,"wa","wₐ — CPL",a.wa);
        edit(root,"Obh2","Ωb h² — proxy r_drag",a.obh2);
        edit(root,"sigma8","σ₈ — amplitude (proxy)",a.sigma8);
        optional(root,"Hobs","H(z) observado — opcional, km/s/Mpc");
        optional(root,"Hsigma","Erro σH positivo — obrigatório com Hobs");
        label(root,"Fórmula individual",14,SECOND);
        formulaPicker=new Spinner(host);root.addView(formulaPicker,new LinearLayout.LayoutParams(-1,-2));
        button(root,"Calcular todas as fórmulas deste modelo",v->calculate());
        button(root,"Exibir apenas a fórmula selecionada",v->showSelected());
        button(root,"Varredura z = 0 até 3 (11 pontos)",v->sweep());
        button(root,"Preencher ΩΛ para E²(0) = 1",v->normalize());
        button(root,"Copiar recibo SHA-256",v->copy());
        state=label(root,"SEM_EXECUÇÃO",16,FG);
        output=label(root,"Execute as fórmulas para ver valores, equações, unidades e lacunas.",14,FG);
        calculate();
    }
}
