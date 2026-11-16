package org.rafaelia.rll;

import java.util.Locale;

/** Audit-only cross-model comparisons; no fitting, no posterior and no claims of new physics. */
public final class OmegaCrossModelComparison {
    private OmegaCrossModelComparison(){}
    public static final class Result {
        public final String modelRows,pairRows,nestedChecks;
        public final int comparisons,passed,failed;
        Result(String a,String b,String c,int d,int p,int f){
            modelRows=a;pairRows=b;nestedChecks=c;comparisons=d;passed=p;failed=f;
        }
    }
    public static Result run() {
        FormulaEngine.Model[] models=FormulaEngine.Model.values();
        double[][] h=new double[models.length][11];
        StringBuilder model=new StringBuilder("model,z,e2,h_km_s_Mpc,source,gate\n");
        StringBuilder pair=new StringBuilder("model_a,model_b,z,delta_h_a_minus_b,relative_delta,gate\n");
        StringBuilder nested=new StringBuilder("nested_model,z,abs_e2_minus_LCDM,tolerance,gate\n");
        int compared=0,pass=0,fail=0;
        for(int m=0;m<models.length;m++){
            FormulaEngine.Input p=RealBaoEngine.baseline(models[m]);
            for(int i=0;i<11;i++){
                double z=i*0.3;
                double e=FormulaEngine.e2(z,models[m],p);
                double hh=e>0?p.h0*Math.sqrt(e):Double.NaN;
                h[m][i]=hh;
                boolean ok=Double.isFinite(e)&&Double.isFinite(hh)&&e>0;
                if(ok)pass++;else fail++;
                model.append(String.format(Locale.ROOT,"%s,%.8f,%.17g,%.17g,FIXED_PARAMETERS_BACKGROUND_ONLY,%s\n",
                    models[m].name(),z,e,hh,ok?"PASS_SCOPED":"FAIL_NONFINITE"));
            }
        }
        for(int a=0;a<models.length;a++)for(int b=a+1;b<models.length;b++)
            for(int i=0;i<11;i++){
                double za=h[a][i],zb=h[b][i],delta=za-zb;
                double relative=delta/Math.max(1.0,Math.abs(zb));
                boolean ok=Double.isFinite(delta)&&Double.isFinite(relative);
                pair.append(String.format(Locale.ROOT,"%s,%s,%.8f,%.17g,%.17g,%s\n",
                    models[a],models[b],i*0.3,delta,relative,ok?"RECORDED_DIFFERENCE":"FAIL_NONFINITE"));
                if(ok)pass++;else fail++;
                compared++;
            }
        for(int i=0;i<11;i++){
            double z=i*0.3;
            FormulaEngine.Input p=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
            double ref=FormulaEngine.e2(z,FormulaEngine.Model.LCDM,p);
            p.w=-1; double w=FormulaEngine.e2(z,FormulaEngine.Model.WCDM,p);
            p.w0=-1;p.wa=0;double c=FormulaEngine.e2(z,FormulaEngine.Model.CPL,p);
            p.os0=0;double r=FormulaEngine.e2(z,FormulaEngine.Model.RLL,p);
            double[] e={w,c,r}; String[] labels={"WCDM_W_MINUS_1","CPL_W0_MINUS_1_WA_ZERO","RLL_OS0_ZERO"};
            for(int k=0;k<3;k++){
                double delta=Math.abs(e[k]-ref);
                boolean ok=Double.isFinite(delta)&&delta<=1e-11;
                if(ok)pass++;else fail++;
                nested.append(String.format(Locale.ROOT,"%s,%.8f,%.17g,1e-11,%s\n",
                    labels[k],z,delta,ok?"PASS_SCOPED_NESTED":"FAIL_NESTED_FALSIFIER"));
            }
        }
        return new Result(model.toString(),pair.toString(),nested.toString(),compared,pass,fail);
    }
}
