package org.rafaelia.rll;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Hosted pure-Java numeric reference, no Android classes and no external libraries.
 *  Ported algebra from checked RLL source; NOT a freestanding core, Boltzmann engine or independent physics proof.
 */
public final class FormulaEngine {
    public static final double ORAD = 9.0e-5;
    public static final double C_KMS = 299792.458;
    public static final String SOURCE_JOINT = "data/pipelines/structure_d/joint_real_likelihood.py";
    public static final String SOURCE_BACKGROUND = "scripts/check_rll_background.py";
    public static final String SCHEMA = "rll.android.formula-lab.v1";
    public enum Model { LCDM, WCDM, CPL, RLL }
    public static final class Input {
        public double z=0.57, h0=67.4, om=0.315, os0=0.059, zt=1.164, wt=0.405;
        public double ol=1.0-om-os0-ORAD, w=-1.0, w0=-0.9, wa=0.2;
        public double obh2=0.0224, sigma8=0.8;
        public double hObserved=Double.NaN, hSigma=Double.NaN;
    }
    public static final class Entry {
        public final String id, expression, unit, source, state, note;
        public final Double value;
        Entry(String id,String expression,String unit,String source,String state,Double value,String note) {
            this.id=id; this.expression=expression; this.unit=unit;
            this.source=source; this.state=state; this.value=value; this.note=note;
        }
        public String display() {
            return id+" = "+(value==null?state:String.format(Locale.US,"%.10g",value))
                +(unit.isEmpty()?"":" "+unit)+"\n  "+note;
        }
    }
    public static final class Result {
        public final List<Entry> entries=new ArrayList<>();
        public String state="SOURCE_SCOPED_DIAGNOSTIC";
        public String warning="";
        public String model="";
        public int computed=0, gap=0;
        void add(String id,String equation,String unit,String source,double value,String note) {
            if (!Double.isFinite(value)) {
                entries.add(new Entry(id,equation,unit,source,"TOKEN_VAZIO_NONFINITE",null,note));
                gap++;
            } else {
                entries.add(new Entry(id,equation,unit,source,"COMPUTED_NOT_VALIDATED",value,note));
                computed++;
            }
        }
        void missing(String id,String equation,String note) {
            entries.add(new Entry(id,equation,"","TOKEN_VAZIO","TOKEN_VAZIO_NOT_RUN",null,note));gap++;
        }
        public String receipt(Input a) {
            StringBuilder sb=new StringBuilder();
            sb.append("schema=").append(SCHEMA).append("\nmodel=").append(model)
              .append("\nstate=").append(state).append("\nclaim_allowed=false\n")
              .append("provenance=USER_INPUT_NOT_REAL_OBSERVATION\n");
            sb.append(String.format(Locale.US,
              "z=%.12g;H0=%.12g;Om=%.12g;OL=%.12g;Os0=%.12g;zt=%.12g;wt=%.12g;w=%.12g;w0=%.12g;wa=%.12g;Obh2=%.12g;sigma8=%.12g\n",
              a.z,a.h0,a.om,a.ol,a.os0,a.zt,a.wt,a.w,a.w0,a.wa,a.obh2,a.sigma8));
            for (Entry item:entries) {
                sb.append("formula=").append(item.id).append(";state=").append(item.state)
                  .append(";value=").append(item.value==null?"TOKEN_VAZIO":Double.toString(item.value))
                  .append(";unit=").append(item.unit).append(";source=").append(item.source)
                  .append(";equation=").append(item.expression).append("\n");
            }
            sb.append("computed=").append(computed).append(";typed_gaps=").append(gap).append("\n")
              .append("warning=").append(warning).append("\n")
              .append("proof_level=ALGEBRAIC_AND_NUMERICAL_SELF_CHECK_ONLY\n")
              .append("full_data_covariance=TOKEN_VAZIO_NOT_RUN\n")
              .append("boltzmann_camb_class=TOKEN_VAZIO_NOT_RUN\n")
              .append("physical_validation=TOKEN_VAZIO_NOT_RUN\n");
            return sb.toString();
        }
    }
    private FormulaEngine() {}
    public static double closedOl(Input x,Model model) {
        return 1.0-x.om-ORAD-(model==Model.RLL?x.os0:0.0);
    }
    public static boolean valid(Input x) {
        return finite(x.z,x.h0,x.om,x.ol,x.os0,x.zt,x.wt,x.w,x.w0,x.wa,x.obh2,x.sigma8)
            && x.z>=0 && x.z<=10 && x.h0>=1 && x.h0<=200
            && x.om>=0 && x.om<=1.5 && x.ol>=-2 && x.ol<=2
            && x.os0>=0 && x.os0<=1 && x.zt>=0 && x.zt<=20
            && x.wt>=0.001 && x.wt<=5 && x.w>=-4 && x.w<=2
            && x.w0>=-4 && x.w0<=2 && x.wa>=-5 && x.wa<=5
            && x.obh2>0 && x.obh2<=0.1 && x.sigma8>0 && x.sigma8<=3
            && ((Double.isNaN(x.hObserved)&&Double.isNaN(x.hSigma))
                || (Double.isFinite(x.hObserved)&&Double.isFinite(x.hSigma)
                   && x.hObserved>0&&x.hSigma>0));
    }
    private static boolean finite(double... xs) {
        for(double v:xs) if(!Double.isFinite(v))return false;
        return true;
    }
    public static double transition(double z,double zt,double wt) {
        double t=Math.max(-500.0,Math.min(500.0,(z-zt)/wt));
        return 1.0/(1.0+Math.exp(t));
    }
    public static double rho(double z,double zt,double wt) {
        double f=transition(z,zt,wt);
        return f+(1-f)*Math.pow(1+z,3);
    }
    public static double e2(double z,Model m,Input a) {
        double zp1=1.0+z;
        double zp3=zp1*zp1*zp1;
        double matter=a.om*zp3+ORAD*zp3*zp1;
        if (m==Model.LCDM) return matter+a.ol;
        if (m==Model.WCDM) return matter+a.ol*Math.pow(zp1,3*(1+a.w));
        if (m==Model.CPL) return matter+a.ol*Math.pow(zp1,3*(1+a.w0+a.wa))
            *Math.exp(-3*a.wa*z/zp1);
        return matter+a.ol+a.os0*rho(z,a.zt,a.wt);
    }
    private static double dfDlna(double z,Input a) {
        double f=transition(z,a.zt,a.wt);
        return f*(1-f)*(1+z)/a.wt;
    }
    private static double drhoDlna(double z,Input a) {
        double f=transition(z,a.zt,a.wt), fp=dfDlna(z,a);
        double a3=Math.pow(1+z,3);
        return fp*(1-a3)-3*(1-f)*a3;
    }
    private static double dc(double z,Model m,Input a,int n) {
        double dz=z/n;
        double weighted=0;
        for(int i=0;i<=n;i++){
            double zz=dz*i, square=e2(zz,m,a);
            if(!(square>0)||!Double.isFinite(square))return Double.NaN;
            weighted+=(i==0||i==n?1:(i%2==0?2:4))/Math.sqrt(square);
        }
        return C_KMS/a.h0*dz*weighted/3.0;
    }
    /** Compares the same user parameters; never interprets this as matched-prior model comparison. */
    public static Result compute(Input a, Model m) {
        Result r=new Result();r.model=m.name();
        if(!valid(a)){
            r.state="TOKEN_VAZIO_DOMAIN_INPUT";
            r.warning="Valores não finitos, faixa inválida ou observação e sigma incompletos.";
            r.missing("INPUT","DOMAIN","Corrija todos os parâmetros; cálculo não executado");
            return r;
        }
        final String J=SOURCE_JOINT, B=SOURCE_BACKGROUND;
        double z=a.z,e0=e2(0,m,a),es=e2(z,m,a);
        if(!finite(e0,es)||e0<=0||es<=0){
            r.state="TOKEN_VAZIO_E2_NONPOSITIVE";
            r.missing("E2_DOMAIN","E²(z)>0","E² não físico; nenhum H(z) estimado");
            return r;
        }
        double hz=a.h0*Math.sqrt(es), omz=a.om*Math.pow(1+z,3)/es;
        r.add("COS-E2-"+m,"Ωm(1+z)^3+Ωr(1+z)^4+dark_sector","1",J,es,"Fundo, sem perturbações");
        r.add("COS-HZ","H0 sqrt(E²)","km/s/Mpc",J,hz,"Não confundir parâmetro H0 com H(0) sem fechamento");
        r.add("COS-E2-ZERO","E²(z=0)","1",J,e0,Math.abs(e0-1)>1e-8?"GATE_REVIEW_H0_NORMALIZATION":"NORMALIZATION_SCOPED_PASS");
        r.add("COS-OMZ","Ωm(1+z)^3/E²(z)","1",J,omz,"Fração de matéria no fundo");
        double shortcut=a.sigma8*Math.pow(omz,0.55);
        r.add("COS-FSIGMA8-PROXY","sigma8 Ωm(z)^0.55","1",J,shortcut,"PROXY: não inclui D(z); não é crescimento validado");
        r.add("COS-OM-LAMBDA-CLOSURE","1-Om-Ωr-Os0(RLL)","1",J,closedOl(a,m),"Valor de OL para E²(0)=1; não aplicado automaticamente");
        double omh2=a.om*Math.pow(a.h0/100,2);
        double rd=147.78*Math.pow(omh2/0.1432,-0.255)*Math.pow(a.obh2/0.02236,-0.134);
        if(omh2>0&&Double.isFinite(rd)&&rd>0){
            r.add("COS-RD-PROXY","147.78 (Om h²/.1432)^-.255 (Ob h²/.02236)^-.134","Mpc",J,rd,"Aproximação calibrada r_drag; não equivale a r_s(z*)");
        } else {
            r.missing("COS-RD-PROXY","r_drag","Densidade física de matéria nula ou não finita");
        }
        double dc128=dc(z,m,a,128),dc256=dc(z,m,a,256);
        if(Double.isFinite(dc128)&&Double.isFinite(dc256)&&dc256>=0) {
            r.add("COS-DM-FLAT","c/H0 integral[0,z] dz/E(z)","Mpc",J,dc256,"Somente Ωk=0; Simpson 256 subintervalos");
            r.add("COS-DM-QUADRATURE-DELTA","abs(DM_256-DM_128)","Mpc",J,Math.abs(dc256-dc128),
                  "Diferença interna de integração, NÃO incerteza observacional");
            r.add("COS-DH","c/H(z)","Mpc",J,C_KMS/hz,"Horizonte radial BAO");
            if(rd>0&&Double.isFinite(rd)){
                r.add("COS-DM-RD","DM/r_drag","1",J,dc256/rd,"Flat, proxy drag; sem covariância DESI");
                r.add("COS-DH-RD","DH/r_drag","1",J,C_KMS/hz/rd,"Proxy sem likelihood");
                if(z>0)r.add("COS-DV-RD","(z c DM²/H)^1/3/r_drag","1",J,
                    Math.cbrt(z*C_KMS*dc256*dc256/hz)/rd,"Somente z>0");
            }
        } else r.missing("COS-DM-FLAT","comoving integral","E² negativo/não finito no caminho da integral");
        if(m==Model.RLL){
            double f=transition(z,a.zt,a.wt), rr=rho(z,a.zt,a.wt),fp=dfDlna(z,a),dr=drhoDlna(z,a);
            double p=-rr-dr/3.0, document=-f;
            r.add("RLL-F-TRANSITION","1/(1+exp((z-zt)/wt))","1",B,f,"Largura wt>0; regularização numérica de exp");
            r.add("RLL-RHO-FACTOR","f+(1-f)(1+z)^3","1",B,rr,"Fator de densidade normalizada");
            if(a.os0>0){
                r.add("RLL-OMEGA-S","Os0 rho_factor/E²","1",B,a.os0*rr/es,"Setor não nulo");
                r.add("RLL-W-DOC","-f/rho_factor","1",B,document/rr,"Pressão documentada; não conservada separadamente");
                r.add("RLL-W-CONSERVED","(-rho-rho'/3)/rho","1",B,p/rr,"Reconstrução impondo conservação separada");
                r.add("RLL-CONTINUITY-DOC","d rho/d ln a + 3 (rho - f)","1",B,
                      dr+3*(rr+document),"Residual documentado não precisa ser zero");
                r.add("RLL-CONTINUITY-CONS","d rho/d ln a+3(rho+p_conserved)","1",B,
                      dr+3*(rr+p),"Identidade algébrica; não prova dinâmica física");
                double f0=transition(0,a.zt,a.wt),fp0=f0*(1-f0)/a.wt;
                r.add("RLL-CPL-W0-LOCAL","-f(0)","1",B,-f0,"Mapeamento local, não equivalência CPL global");
                r.add("RLL-CPL-WA-DOC","f'(0)+3 f0(1-f0)","1",B,
                      fp0+3*f0*(1-f0),"Convenção da pressão documentada");
                r.add("RLL-CPL-WA-CONS","2 f'(0)+3 f0(1-f0)","1",B,
                      2*fp0+3*f0*(1-f0),"Convenção da pressão conservada");
            } else r.missing("RLL-NULL-SECTOR","Os0=0","zt,wt/w físicos não identificáveis quando setor nulo");
        }
        if(Double.isFinite(a.hObserved)&&Double.isFinite(a.hSigma)){
            double residual=(a.hObserved-hz)/a.hSigma;
            r.add("COS-H-RESIDUAL","(H_obs-H_model)/sigma","1","USER_INPUT",residual,
                  "Uma observação fornecida manualmente, procedência não atestada");
            r.add("COS-H-CHI2-ONE","residual²","1","USER_INPUT",residual*residual,
                  "Chi² de UM ponto sob sigma independente, sem covariância");
        } else r.missing("COS-H-OBSERVATION","Hobs +/- sigma","Nenhum H(z) observado fornecido; não inventar dados");
        r.missing("COS-CMB-RS","r_s(z*)","Recombinação CLASS/CAMB não executada no aparelho");
        r.missing("COS-GROWTH-ODE","f D(z) sigma8","Integração física de crescimento independente não executada");
        r.missing("COS-JOINT-FIT","joint likelihood","Dados oficiais, covariância e otimização não executados");
        if(Math.abs(e0-1)>1e-8)r.warning="E²(0) difere de 1: revisar H0, OL e convenção de fechamento.";
        else r.warning="Fundo fechado E²(0)≈1 no parâmetro informado; observação independente ausente.";
        return r;
    }
}
