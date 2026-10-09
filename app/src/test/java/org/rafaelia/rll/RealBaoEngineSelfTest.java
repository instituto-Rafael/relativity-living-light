package org.rafaelia.rll;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
public final class RealBaoEngineSelfTest {
    static int checks=0;
    static void ok(boolean v,String why){checks++;if(!v)throw new AssertionError(why);}
    static boolean bad(Runnable action){try{action.run();return false;}catch(IllegalArgumentException e){return true;}}
    public static void main(String[] args)throws Exception {
        FormulaEngine.Input par=RealBaoEngine.baseline(FormulaEngine.Model.LCDM);
        StringBuilder observed=new StringBuilder(),cov=new StringBuilder();
        String[] kinds={"DM_over_rs","DH_over_rs","DV_over_rs"};
        for(int i=0;i<13;i++){
            double z=(i+1)/10.0;
            String kind=kinds[i%3];
            observed.append(String.format(Locale.US,"%.6g %.17g %s\n",z,RealBaoEngine.prediction(z,kind,FormulaEngine.Model.LCDM,par),kind));
            for(int j=0;j<13;j++)cov.append(i==j?"1.0":"0.0").append(j==12?"\n":" ");
        }
        RealBaoEngine.Data d=RealBaoEngine.parseTables(observed.toString(),cov.toString(),"SYNTHETIC","SYNTHETIC");
        ok(d.points.size()==13,"points");
        ok(d.covariance.length==13,"matrix size");
        ok(RealBaoEngine.modelChi2(d,FormulaEngine.Model.LCDM,par)<1e-17,"synthetic zero error");
        for(FormulaEngine.Model model:FormulaEngine.Model.values()){
            RealBaoEngine.Score s=RealBaoEngine.score(d,model);
            ok(Double.isFinite(s.chi2)&&s.chi2>=0,model+" chi2");
            ok(Double.isFinite(s.deltaOm)&&s.deltaOm>=0,model+" omega derivative");
            ok(Double.isFinite(s.deltaH0)&&s.deltaH0>=0,model+" H derivative");
            ok(s.csv().contains("MODEL_DIAGNOSTIC_NOT_POSTERIOR"),"claim");
            ok(s.prediction.length==13&&s.residual.length==13,"observables");
        }
        ok(RealBaoEngine.torusClosure(2,.7)<1e-12,"parametric torus closure");
        ok(bad(()->RealBaoEngine.torusClosure(.3,.7)),"torus invalid R");
        ok(bad(()->RealBaoEngine.parseTables(observed.toString(),cov+"1 1 1\n","","")),"13x13 constraint");
        double[][] wrong=new double[13][13];
        for(int i=0;i<13;i++)wrong[i][i]=1;
        wrong[1][0]=.5;
        ok(bad(()->RealBaoEngine.cholesky(wrong)),"asymmetric reject");
        wrong[0][1]=.5;wrong[0][0]=-1;
        ok(bad(()->RealBaoEngine.cholesky(wrong)),"nonSPD reject");
        ok(bad(()->{try{RealBaoEngine.parse(new byte[]{1},new byte[]{2});}catch(IllegalArgumentException e){throw e;}catch(Exception e){throw new IllegalArgumentException(e);}}),"mismatched scientific source");
        ok(RealBaoEngine.MEAN_BLOB.length()==40&&RealBaoEngine.COV_BLOB.length()==40,"git pin");
        System.out.println("RLL_REAL_BAO_ENGINE_PASS checks="+checks+" covariance=13x13");
    }
}
