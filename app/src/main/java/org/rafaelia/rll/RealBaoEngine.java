package org.rafaelia.rll;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** No Android or third-party imports. Real DESI DR2 BAO data contract and full 13x13 covariance. */
public final class RealBaoEngine {
    public static final String DATA_COMMIT="bb0c1c9009dc76d1391300e169e8df38fd1096db";
    public static final String SOURCE="https://github.com/CobayaSampler/bao_data/tree/"+DATA_COMMIT+"/desi_bao_dr2";
    public static final String RAW_BASE="https://raw.githubusercontent.com/CobayaSampler/bao_data/"+DATA_COMMIT+"/desi_bao_dr2/";
    public static final String MEAN="desi_gaussian_bao_ALL_GCcomb_mean.txt";
    public static final String COV="desi_gaussian_bao_ALL_GCcomb_cov.txt";
    public static final String MEAN_BLOB="8aff444fdb42c0946342aa0011ab287eda097c4c";
    public static final String COV_BLOB="fd8e5697ab61379b07b52efb781ea6713417a4d9";
    public static final int N=13;
    public static final class Datum {
        public final double z,observed; public final String kind;
        Datum(double zz,double yy,String kk){z=zz;observed=yy;kind=kk;}
    }
    public static final class Data {
        public final List<Datum> points;
        public final double[][] covariance;
        public final String meanSha256,covSha256;
        Data(List<Datum> p,double[][] c,String mh,String ch){points=p;covariance=c;meanSha256=mh;covSha256=ch;}
    }
    private RealBaoEngine(){}
    public static String hex(byte[] b) {
        StringBuilder sb=new StringBuilder();for(byte x:b)sb.append(String.format(Locale.US,"%02x",x&255));return sb.toString();
    }
    public static String sha256(byte[] bytes)throws Exception {return hex(MessageDigest.getInstance("SHA-256").digest(bytes));}
    public static String gitBlobSha1(byte[] bytes)throws Exception {
        MessageDigest d=MessageDigest.getInstance("SHA-1");
        d.update(("blob "+bytes.length+"\u0000").getBytes(StandardCharsets.US_ASCII));
        d.update(bytes);return hex(d.digest());
    }
    public static Data parse(byte[] mean,byte[] cov)throws Exception {
        if(mean==null||cov==null||mean.length>64000||cov.length>64000)throw new IllegalArgumentException("bytes/size");
        if(!MEAN_BLOB.equals(gitBlobSha1(mean))||!COV_BLOB.equals(gitBlobSha1(cov)))
            throw new IllegalArgumentException("TOKEN_VAZIO_SOURCE_BLOB_MISMATCH");
        return parseTables(new String(mean,StandardCharsets.UTF_8),new String(cov,StandardCharsets.UTF_8),sha256(mean),sha256(cov));
    }
    public static Data parseTables(String mean,String cov,String mhash,String chash){
        List<Datum> ps=new ArrayList<>();
        for(String l:mean.split("\\R")){
            l=l.trim();if(l.isEmpty()||l.startsWith("#"))continue;
            String[] t=l.split("\\s+");
            if(t.length!=3)throw new IllegalArgumentException("mean cols");
            double z=Double.parseDouble(t[0]),v=Double.parseDouble(t[1]);
            if(!Double.isFinite(z)||z<=0||z>5||!Double.isFinite(v)||v<=0)
                throw new IllegalArgumentException("mean values");
            if(!("DV_over_rs".equals(t[2])||"DM_over_rs".equals(t[2])||"DH_over_rs".equals(t[2])))
                throw new IllegalArgumentException("mean observable");
            ps.add(new Datum(z,v,t[2]));
        }
        if(ps.size()!=N)throw new IllegalArgumentException("mean row count "+ps.size());
        double[][] matrix=new double[N][N];int row=0;
        for(String l:cov.split("\\R")){
            l=l.trim();if(l.isEmpty()||l.startsWith("#"))continue;
            if(row>=N)throw new IllegalArgumentException("cov > 13 rows");
            String[] t=l.split("\\s+");
            if(t.length!=N)throw new IllegalArgumentException("cov cols "+t.length);
            for(int c=0;c<N;c++){
                matrix[row][c]=Double.parseDouble(t[c]);
                if(!Double.isFinite(matrix[row][c]))throw new IllegalArgumentException("cov nonfinite");
            }
            row++;
        }
        if(row!=N)throw new IllegalArgumentException("cov rows "+row);
        cholesky(matrix);
        return new Data(ps,matrix,mhash,chash);
    }
    /** Factor C=L L^T with symmetry and positive definiteness fail-closed. */
    public static double[][] cholesky(double[][] a) {
        int n=a.length;if(n!=N)throw new IllegalArgumentException("dimension");
        double[][] l=new double[n][n];
        for(int i=0;i<n;i++){
            if(a[i]==null||a[i].length!=n)throw new IllegalArgumentException("matrix row");
            for(int j=0;j<n;j++) {
                if(!Double.isFinite(a[i][j])||!Double.isFinite(a[j][i])||
                    Math.abs(a[i][j]-a[j][i])>1e-8*Math.max(1.0,Math.abs(a[i][j])))
                    throw new IllegalArgumentException("asymmetric covariance");
            }
            for(int j=0;j<=i;j++) {
                double sum=a[i][j];
                for(int k=0;k<j;k++)sum-=l[i][k]*l[j][k];
                if(i==j){if(!(sum>1e-13))throw new IllegalArgumentException("covariance non-SPD");l[i][j]=Math.sqrt(sum);}
                else l[i][j]=sum/l[j][j];
            }
        }
        return l;
    }
    public static double chi2(double[] residual,double[][] cov) {
        if(residual.length!=N)throw new IllegalArgumentException("residual dimension");
        double[][] l=cholesky(cov);
        double[] y=new double[N];
        for(int i=0;i<N;i++){
            if(!Double.isFinite(residual[i]))throw new IllegalArgumentException("nonfinite residual");
            double t=residual[i];for(int j=0;j<i;j++)t-=l[i][j]*y[j];
            y[i]=t/l[i][i];
        }
        double result=0;for(double v:y)result+=v*v;
        if(!Double.isFinite(result))throw new IllegalArgumentException("nonfinite chi2");
        return result;
    }
    public static double prediction(double z,String kind,FormulaEngine.Model model,FormulaEngine.Input p) {
        double es=FormulaEngine.e2(z,model,p);
        if(!Double.isFinite(es)||es<=0)throw new IllegalArgumentException("E2 invalid");
        double hz=p.h0*Math.sqrt(es),dh=FormulaEngine.C_KMS/hz;
        double h=p.h0/100.0,omh2=p.om*h*h;
        if(!(omh2>0&&p.obh2>0))throw new IllegalArgumentException("baryons/omega invalid");
        double rd=147.78*Math.pow(omh2/.1432,-.255)*Math.pow(p.obh2/.02236,-.134);
        if(!Double.isFinite(rd)||rd<=0)throw new IllegalArgumentException("rd invalid");
        if("DH_over_rs".equals(kind))return dh/rd;
        final int steps=256;double dz=z/steps,sum=0;
        for(int i=0;i<=steps;i++){
            double v=FormulaEngine.e2(i*dz,model,p);
            if(!(v>0)||!Double.isFinite(v))throw new IllegalArgumentException("E2 path invalid");
            sum+=(i==0||i==steps?1:(i%2==0?2:4))/Math.sqrt(v);
        }
        double dm=FormulaEngine.C_KMS/p.h0*dz*sum/3;
        if("DM_over_rs".equals(kind))return dm/rd;
        if("DV_over_rs".equals(kind))return Math.cbrt(z*dm*dm*dh)/rd;
        throw new IllegalArgumentException("bad kind");
    }
    public static final class Score {
        public final FormulaEngine.Model model;
        public final double chi2, deltaOm, deltaH0, deltaZt, torusClosure;
        public final double[] prediction,residual;
        Score(FormulaEngine.Model m,double c,double om,double h,double zt,double tc,double[] y,double[] r){
            model=m;chi2=c;deltaOm=om;deltaH0=h;deltaZt=zt;torusClosure=tc;prediction=y;residual=r;
        }
        public String csv(){
            return String.format(Locale.US,"%s,%.12g,%.12g,%.12g,%.12g,%.12g,MODEL_DIAGNOSTIC_NOT_POSTERIOR",
                model.name(),chi2,deltaOm,deltaH0,deltaZt,torusClosure);
        }
    }
    public static FormulaEngine.Input baseline(FormulaEngine.Model m){
        FormulaEngine.Input p=new FormulaEngine.Input();
        p.ol=FormulaEngine.closedOl(p,m);
        return p;
    }
    public static double modelChi2(Data d,FormulaEngine.Model model,FormulaEngine.Input p){
        if(!FormulaEngine.valid(p))throw new IllegalArgumentException("bad model parameters");
        double[] residual=new double[N];
        for(int i=0;i<N;i++)residual[i]=prediction(d.points.get(i).z,d.points.get(i).kind,model,p)-d.points.get(i).observed;
        return chi2(residual,d.covariance);
    }
    public static Score score(Data d,FormulaEngine.Model m){
        FormulaEngine.Input p=baseline(m);
        double[] y=new double[N],r=new double[N];
        for(int i=0;i<N;i++){Datum a=d.points.get(i);y[i]=prediction(a.z,a.kind,m,p);r[i]=y[i]-a.observed;}
        double base=chi2(r,d.covariance);
        // Prespecified local sensitivity, not minimization/optimizing to force fit.
        FormulaEngine.Input pos=baseline(m);pos.om+=.005;pos.ol=FormulaEngine.closedOl(pos,m);
        FormulaEngine.Input neg=baseline(m);neg.om-=.005;neg.ol=FormulaEngine.closedOl(neg,m);
        double dom=Math.abs(modelChi2(d,m,pos)-modelChi2(d,m,neg))/0.010;
        pos=baseline(m);neg=baseline(m);
        pos.h0+=.5;neg.h0-=.5;
        double dh=Math.abs(modelChi2(d,m,pos)-modelChi2(d,m,neg))/1.0;
        double dzt=Double.NaN;
        if(m==FormulaEngine.Model.RLL){
            pos=baseline(m);neg=baseline(m);pos.zt+=.05;neg.zt-=.05;
            dzt=Math.abs(modelChi2(d,m,pos)-modelChi2(d,m,neg))/.10;
        }
        return new Score(m,base,dom,dh,dzt,torusClosure(2.0,.7),y,r);
    }
    public static double torusClosure(double radius,double minor){
        if(!(radius>minor&&minor>0))throw new IllegalArgumentException("torus radii domain");
        // Parameterized surface T². This is mathematical closure, not dynamical Poincaré recurrence.
        double[] a=torus(radius,minor,0,0),b=torus(radius,minor,2*Math.PI,2*Math.PI);
        double sum=0;for(int i=0;i<3;i++)sum+=(a[i]-b[i])*(a[i]-b[i]);
        return Math.sqrt(sum);
    }
    private static double[] torus(double R,double r,double u,double v){
        return new double[]{(R+r*Math.cos(v))*Math.cos(u),(R+r*Math.cos(v))*Math.sin(u),r*Math.sin(v)};
    }
}
