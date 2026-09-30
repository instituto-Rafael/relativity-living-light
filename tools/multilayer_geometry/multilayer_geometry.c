#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.141592653589793238462643383279502884
#endif

typedef struct { double x, y; } Vec2;
typedef struct { double theta, side, apothem, perimeter, area; } PolyMetrics;

static int near(double a, double b, double eps) { return fabs(a-b) <= eps; }
static double norm2(Vec2 p) { return hypot(p.x,p.y); }
static double dist2(Vec2 a, Vec2 b) { return hypot(a.x-b.x,a.y-b.y); }
static long long choose2(long long n) { return n*(n-1)/2; }

static PolyMetrics polygon_metrics(unsigned n, double R) {
    PolyMetrics m;
    m.theta = 2.0*M_PI/(double)n;
    m.side = 2.0*R*sin(M_PI/(double)n);
    m.apothem = R*cos(M_PI/(double)n);
    m.perimeter = (double)n*m.side;
    m.area = 0.5*(double)n*R*R*sin(2.0*M_PI/(double)n);
    return m;
}
static double chord(unsigned n, unsigned k, double R) {
    return 2.0*R*sin((double)k*M_PI/(double)n);
}
static double layer_radius(double R0, double lambda, unsigned j) {
    return R0*pow(lambda,(double)j);
}
static double annulus_area(double Ra, double Rb) {
    return M_PI*(Ra*Ra-Rb*Rb);
}
static Vec2 rotate_v(Vec2 p,double t) {
    double c=cos(t), s=sin(t); Vec2 q={c*p.x-s*p.y,s*p.x+c*p.y}; return q;
}
static Vec2 reflect_axis(Vec2 p,double alpha) {
    Vec2 a=rotate_v(p,-alpha); a.y=-a.y; return rotate_v(a,alpha);
}
static Vec2 homothety(Vec2 p,double mu) { Vec2 q={mu*p.x,mu*p.y}; return q; }
static Vec2 radial_project(Vec2 p,double Rb) {
    double r=norm2(p); Vec2 q={Rb*p.x/r,Rb*p.y/r}; return q;
}
static Vec2 invert_circle(Vec2 p,double rho) {
    double r2=p.x*p.x+p.y*p.y; Vec2 q={rho*rho*p.x/r2,rho*rho*p.y/r2}; return q;
}
static double sphere_chord(double R,double gamma) { return 2.0*R*sin(gamma/2.0); }
static double sphere_arc(double R,double gamma) { return R*gamma; }
static double spherical_triangle_area(double R,double A,double B,double C) { return R*R*(A+B+C-M_PI); }

static int overlay_unique_vertices(int step_deg,int rotations) {
    int used[360]={0}; int count=0;
    for(int m=0;m<rotations;m++) {
        int phase=(m*step_deg)%360;
        for(int k=0;k<3;k++) {
            int a=(phase+120*k)%360;
            if(!used[a]) { used[a]=1; count++; }
        }
    }
    return count;
}

static int selftest(void) {
    int t=0, pass=0; const double e=1e-10;
#define CHECK(x) do { t++; if(x) pass++; else fprintf(stderr,"FAIL:%d:%s\n",t,#x); } while(0)
    PolyMetrics p8=polygon_metrics(8,1.0);
    CHECK(near(p8.side,2.0*sin(M_PI/8.0),e));
    CHECK(near(p8.area,2.0*sqrt(2.0),e));
    CHECK(near(chord(8,4,1.0),2.0,e));
    {
        double a=2.3, Rc=a/sqrt(3.0), ri=a/(2.0*sqrt(3.0));
        double At=sqrt(3.0)*a*a/4.0;
        CHECK(near(Rc,2.0*ri,e));
        CHECK(near(M_PI*ri*ri/At,M_PI/(3.0*sqrt(3.0)),e));
        CHECK(near(M_PI*Rc*Rc/At,4.0*M_PI/(3.0*sqrt(3.0)),e));
    }
    {
        PolyMetrics h=polygon_metrics(6,1.7);
        CHECK(near(h.side,1.7,e));
        CHECK(near(h.area,6.0*(sqrt(3.0)/4.0)*1.7*1.7,e));
    }
    {
        double lam=sqrt(2.0)-1.0, R0=2.0, r2=layer_radius(R0,lam,2), r3=layer_radius(R0,lam,3);
        CHECK(near(r3/r2,lam,e));
        CHECK(near(annulus_area(r2,r3),M_PI*r2*r2*(1.0-lam*lam),e));
    }
    {
        Vec2 a={0.7,1.4}, q=radial_project(a,3.1);
        CHECK(near(norm2(q),3.1,e));
        CHECK(near(atan2(a.y,a.x),atan2(q.y,q.x),e));
    }
    {
        Vec2 a={1.2,-0.4}, b={-0.2,1.1}; double mu=.37;
        CHECK(near(dist2(homothety(a,mu),homothety(b,mu)),mu*dist2(a,b),e));
        CHECK(near(norm2(rotate_v(a,.731)),norm2(a),e));
        CHECK(near(norm2(reflect_axis(a,.31)),norm2(a),e));
    }
    {
        Vec2 a={1.2,.7}; Vec2 q=invert_circle(a,2.0); Vec2 qq=invert_circle(q,2.0);
        CHECK(near(norm2(a)*norm2(q),4.0,e));
        CHECK(dist2(a,qq)<e);
    }
    {
        PolyMetrics p96=polygon_metrics(96,1.0);
        CHECK(p96.area/M_PI > .999);
        CHECK(p96.perimeter/(2.0*M_PI) > .999);
    }
    CHECK(overlay_unique_vertices(60,6)==6);
    CHECK(overlay_unique_vertices(30,6)==12);
    {
        double n1=1.0,n2=1.5,a=M_PI/6.0,b=asin(n1/n2*sin(a));
        CHECK(near(n1*sin(a),n2*sin(b),e));
        CHECK(1.5*sin(M_PI/3.0)>1.0);
    }
    {
        double R=2.4,g=M_PI/2.0;
        CHECK(near(sphere_chord(R,g),R*sqrt(2.0),e));
        CHECK(near(sphere_arc(R,g),R*M_PI/2.0,e));
        CHECK(near(spherical_triangle_area(R,M_PI/2,M_PI/2,M_PI/2),R*R*M_PI/2.0,e));
    }
    CHECK(choose2(8)==28);
    CHECK(choose2(16)==120);
    CHECK(8*8 + 2*choose2(8) == 120);
    CHECK(near(p8.area/M_PI,8.0*sin(M_PI/4.0)/(2.0*M_PI),e));
    for(int stab=1;stab<=16;stab*=2) CHECK((16/stab)*stab==16);
    printf("{\"status\":\"%s\",\"passed\":%d,\"tests\":%d,\"failed\":%d}\n",pass==t?"PASS":"FAIL",pass,t,t-pass);
    return pass==t?0:1;
#undef CHECK
}

static void usage(const char *p) {
    fprintf(stderr,"usage:\n  %s selftest\n  %s polygon N R [K]\n  %s layer R0 lambda J\n  %s triangle side\n  %s sphere R gamma_rad\n",p,p,p,p,p);
}

int main(int argc,char **argv) {
    if(argc<2) { usage(argv[0]); return 2; }
    if(strcmp(argv[1],"selftest")==0) return selftest();
    if(strcmp(argv[1],"polygon")==0 && argc>=4) {
        unsigned n=(unsigned)strtoul(argv[2],0,10); double R=strtod(argv[3],0); unsigned k=argc>=5?(unsigned)strtoul(argv[4],0,10):1;
        if(n<3 || R<=0 || k<1 || k>n/2) return 2;
        PolyMetrics m=polygon_metrics(n,R);
        printf("{\"n\":%u,\"R\":%.17g,\"theta\":%.17g,\"side\":%.17g,\"apothem\":%.17g,\"perimeter\":%.17g,\"area\":%.17g,\"chord_k\":%.17g}\n",n,R,m.theta,m.side,m.apothem,m.perimeter,m.area,chord(n,k,R));
        return 0;
    }
    if(strcmp(argv[1],"layer")==0 && argc==5) {
        double R0=strtod(argv[2],0), lam=strtod(argv[3],0); unsigned j=(unsigned)strtoul(argv[4],0,10);
        if(R0<=0 || lam<=0 || lam>=1) return 2;
        double r=layer_radius(R0,lam,j), rn=layer_radius(R0,lam,j+1);
        printf("{\"Rj\":%.17g,\"Rj1\":%.17g,\"annulus_area\":%.17g,\"scale\":%.17g}\n",r,rn,annulus_area(r,rn),rn/r);
        return 0;
    }
    if(strcmp(argv[1],"triangle")==0 && argc==3) {
        double a=strtod(argv[2],0); if(a<=0) return 2;
        double h=sqrt(3.0)*a/2.0, A=sqrt(3.0)*a*a/4.0, Rc=a/sqrt(3.0), ri=a/(2.0*sqrt(3.0));
        printf("{\"side\":%.17g,\"height\":%.17g,\"area\":%.17g,\"circumradius\":%.17g,\"inradius\":%.17g,\"R_over_r\":%.17g,\"incircle_area_ratio\":%.17g,\"circumcircle_area_ratio\":%.17g}\n",a,h,A,Rc,ri,Rc/ri,M_PI*ri*ri/A,M_PI*Rc*Rc/A);
        return 0;
    }
    if(strcmp(argv[1],"sphere")==0 && argc==4) {
        double R=strtod(argv[2],0), g=strtod(argv[3],0); if(R<=0 || g<0) return 2;
        printf("{\"R\":%.17g,\"gamma\":%.17g,\"chord\":%.17g,\"arc\":%.17g}\n",R,g,sphere_chord(R,g),sphere_arc(R,g));
        return 0;
    }
    usage(argv[0]); return 2;
}
