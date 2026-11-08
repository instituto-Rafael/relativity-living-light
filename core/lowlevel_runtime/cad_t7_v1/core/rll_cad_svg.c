#include "rll_cad.h"
/* Bounded append-only SVG serializer without sprintf, strlen, dynamic memory or OS calls. */
typedef struct {char *b;r_u32 pos,cap;int err;} wr;
static void c(wr *w,char ch){if(w->err)return;if(w->pos+1>=w->cap){w->err=1;return;}w->b[w->pos++]=ch;w->b[w->pos]=0;}
static void str(wr *w,const char *s){while(*s)c(w,*s++);}
static void u(wr *w,r_u32 n){char tmp[12];r_u32 i=0;do{tmp[i++]=(char)('0'+n%10);n/=10;}while(n&&i<12);while(i)c(w,tmp[--i]);}
static void fx(wr *w,r_i32 n){if(n<0){c(w,'-');n=-n;}u(w,(r_u32)n>>16);c(w,'.');r_u32 f=((r_u32)(n&65535)*1000u+32768u)/65536u;if(f==1000u){/* ignore carry: unreachable for defined fractions with round-nearest except >= .9995 */f=999u;}c(w,(char)('0'+f/100));c(w,(char)('0'+(f/10)%10));c(w,(char)('0'+f%10));}
static void attr(wr *w,const char *key,r_i32 q){c(w,' ');str(w,key);str(w,"=\"");fx(w,q);c(w,'"');}
static void line(wr *w,r_i32 x1,r_i32 y1,r_i32 x2,r_i32 y2,r_i32 diameter,const char *colour,const char *label,r_i32 area){str(w,"<line");attr(w,"x1",x1);attr(w,"y1",y1);attr(w,"x2",x2);attr(w,"y2",y2);attr(w,"stroke-width",diameter);attr(w,"data-area-mm2",area);str(w," stroke=\"");str(w,colour);str(w,"\" stroke-linecap=\"round\"><title>");str(w,label);str(w,"</title></line>\n");}
int rll_cad_emit_svg(const rll_cad_input *a,const rll_cad_result *r,char *dst,r_u32 cap){
 if(!a||!r||!dst||cap<100)return -R_CAD_INVALID_INPUT;
 wr w={dst,0,cap,0};w.b[0]=0;
 r_i32 x0=100*R_Q16,x1=x0+a->span_mm_q16,xm=x0+a->span_mm_q16/2;
 r_i32 y0=100*R_Q16,yb=y0+a->rise_mm_q16;
 r_i32 vieww=a->span_mm_q16+200*R_Q16,viewh=a->rise_mm_q16+200*R_Q16;
 str(&w,"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"");fx(&w,vieww);
 str(&w,"mm\" height=\"");fx(&w,viewh);
 str(&w,"mm\" viewBox=\"0 0 ");fx(&w,vieww);c(&w,' ');fx(&w,viewh);
 str(&w,"\" data-unit=\"mm\" data-model=\"2d-3bar-pinjoint\" data-certification=\"NONE\">\n");
 str(&w,"<title>RLL T7 Parametric three-bar bridge — illustrative only</title>\n");
 str(&w,"<desc>Physical units millimetres. Circular bar diameter determines stroke width; not a certified steel structure. No flexure, shear, torsion, thermal constraints or live-load combinations.</desc>\n");
 str(&w,"<rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>\n");
 line(&w,x0,yb,xm,y0,r->diagonal_diameter_mm_q16,"#3566a6","Left diagonal compression; circular bar",a->area_diagonal_mm2_q16);
 line(&w,xm,y0,x1,yb,r->diagonal_diameter_mm_q16,"#3566a6","Right diagonal compression; circular bar",a->area_diagonal_mm2_q16);
 line(&w,x0,yb,x1,yb,r->tie_diameter_mm_q16,"#b45d42","Tie tension; circular bar",a->area_tie_mm2_q16);
 str(&w,"<g fill=\"#171717\"><circle");attr(&w,"cx",x0);attr(&w,"cy",yb);str(&w," r=\"8\"/><circle");attr(&w,"cx",x1);attr(&w,"cy",yb);str(&w," r=\"8\"/><circle");attr(&w,"cx",xm);attr(&w,"cy",y0);str(&w," r=\"8\"/></g>\n");
 str(&w,"<path d=\"M ");fx(&w,xm);c(&w,' ');fx(&w,y0-45*R_Q16);str(&w," v 35 m -10 -10 l 10 10 l 10 -10\" fill=\"none\" stroke=\"#b32929\" stroke-width=\"3\"/>\n");
 str(&w,"<text x=\"15\" y=\"26\" font-size=\"18\" fill=\"#222\">P (kN)=");fx(&w,a->downward_load_kN_q16);str(&w,"</text>\n");
 str(&w,"<text x=\"15\" y=\"55\" font-size=\"14\" fill=\"#333\">span (mm)=");fx(&w,a->span_mm_q16);str(&w,"; rise (mm)=");fx(&w,a->rise_mm_q16);str(&w,"</text>\n");
 str(&w,"<text x=\"15\" y=\"78\" font-size=\"14\" fill=\"#333\">tan(theta)=");fx(&w,r->tan_angle_q16);str(&w,"; delta (mm)=");fx(&w,r->apex_deflection_mm_q16);str(&w,"</text>\n");
 str(&w,"</svg>\n");return w.err?-R_CAD_NUMERIC_OVERFLOW:(int)w.pos;
}
