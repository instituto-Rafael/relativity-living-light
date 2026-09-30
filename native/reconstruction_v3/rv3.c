#include "rv3.h"
typedef struct {
    const unsigned char *s; rv3_size n,p,count,cap;
    rv3_token *t; unsigned status,limit;
} parser;
static int bad(parser *p, unsigned status) { p->status=status; return 0; }
static void ws(parser *p) {
    while(p->p<p->n && (p->s[p->p]==' ' || p->s[p->p]=='\n' || p->s[p->p]=='\r' || p->s[p->p]=='\t')) ++p->p;
}
static int digit(unsigned c) { return c>='0' && c<='9'; }
static int hex(unsigned c) {
    if(c>='0' && c<='9') return (int)(c-'0');
    if(c>='a' && c<='f') return (int)(c-'a'+10);
    if(c>='A' && c<='F') return (int)(c-'A'+10);
    return -1;
}
static int u16(parser *p, unsigned *out) {
    unsigned v=0,i; int h;
    for(i=0;i<4;i++) {
        if(p->p==p->n || (h=hex(p->s[p->p]))<0) return bad(p,RV3_INVALID);
        v=v*16+(unsigned)h; ++p->p;
    }
    *out=v; return 1;
}
static int string(parser *p) {
    unsigned c,u,v,k,min,cp,x;
    if(p->p==p->n || p->s[p->p++]!='"') return bad(p,RV3_INVALID);
    while(p->p<p->n) {
        c=p->s[p->p++];
        if(c=='"') return 1;
        if(c<32) return bad(p,RV3_INVALID);
        if(c=='\\') {
            if(p->p==p->n) return bad(p,RV3_INVALID);
            c=p->s[p->p++];
            if(c=='u') {
                if(!u16(p,&u)) return 0;
                if(u>=0xdc00 && u<=0xdfff) return bad(p,RV3_INVALID);
                if(u>=0xd800 && u<=0xdbff) {
                    if(p->n-p->p<2 || p->s[p->p]!='\\' || p->s[p->p+1]!='u') return bad(p,RV3_INVALID);
                    p->p+=2;
                    if(!u16(p,&v)) return 0;
                    if(v<0xdc00 || v>0xdfff) return bad(p,RV3_INVALID);
                }
            } else if(c!='"' && c!='\\' && c!='/' && c!='b' && c!='f' && c!='n' && c!='r' && c!='t') return bad(p,RV3_INVALID);
        } else if(c>=128) {
            if(c>=0xc2 && c<=0xdf) { k=1; cp=c&31; min=128; }
            else if(c>=0xe0 && c<=0xef) { k=2; cp=c&15; min=2048; }
            else if(c>=0xf0 && c<=0xf4) { k=3; cp=c&7; min=65536; }
            else return bad(p,RV3_INVALID);
            while(k--) {
                if(p->p==p->n) return bad(p,RV3_INVALID);
                x=p->s[p->p++]; if((x&192)!=128) return bad(p,RV3_INVALID);
                cp=(cp<<6)|(x&63);
            }
            if(cp<min || cp>0x10ffff || (cp>=0xd800 && cp<=0xdfff)) return bad(p,RV3_INVALID);
        }
    }
    return bad(p,RV3_INVALID);
}
static int number(parser *p) {
    if(p->s[p->p]=='-') ++p->p;
    if(p->p==p->n) return bad(p,RV3_INVALID);
    if(p->s[p->p]=='0') ++p->p;
    else {
        if(p->s[p->p]<'1' || p->s[p->p]>'9') return bad(p,RV3_INVALID);
        while(p->p<p->n && digit(p->s[p->p])) ++p->p;
    }
    if(p->p<p->n && p->s[p->p]=='.') {
        ++p->p; if(p->p==p->n || !digit(p->s[p->p])) return bad(p,RV3_INVALID);
        while(p->p<p->n && digit(p->s[p->p])) ++p->p;
    }
    if(p->p<p->n && (p->s[p->p]=='e' || p->s[p->p]=='E')) {
        ++p->p;
        if(p->p<p->n && (p->s[p->p]=='+' || p->s[p->p]=='-')) ++p->p;
        if(p->p==p->n || !digit(p->s[p->p])) return bad(p,RV3_INVALID);
        while(p->p<p->n && digit(p->s[p->p])) ++p->p;
    }
    return 1;
}
static int literal(parser *p,const char *s) {
    while(*s) {
        if(p->p==p->n || p->s[p->p]!=(unsigned char)*s) return bad(p,RV3_INVALID);
        ++p->p; ++s;
    }
    return 1;
}
static int value(parser *p,rv3_size parent,rv3_size ks,rv3_size ke,unsigned depth) {
    rv3_size id; unsigned c,close,object;
    ws(p);
    if(p->p==p->n) return bad(p,RV3_INVALID);
    if(p->count==p->cap) return bad(p,RV3_CAPACITY);
    id=p->count++;
    p->t[id].start=p->p; p->t[id].parent=parent;
    p->t[id].key_start=ks; p->t[id].key_end=ke;
    c=p->s[p->p];
    if(c=='{' || c=='[') {
        if(depth>=p->limit) return bad(p,RV3_DEPTH);
        object=c=='{'; close=object?'}':']';
        p->t[id].kind=object?RV3_OBJECT:RV3_ARRAY; ++p->p; ws(p);
        if(p->p<p->n && p->s[p->p]==close) ++p->p;
        else {
            for(;;) {
                ks=ke=RV3_NONE;
                if(object) {
                    ks=p->p; if(!string(p)) return 0; ke=p->p; ws(p);
                    if(p->p==p->n || p->s[p->p++]!=':') return bad(p,RV3_INVALID);
                }
                if(!value(p,id,ks,ke,depth+1)) return 0;
                ws(p); if(p->p==p->n) return bad(p,RV3_INVALID);
                c=p->s[p->p++]; if(c==close) break;
                if(c!=',') return bad(p,RV3_INVALID);
                ws(p);
            }
        }
    } else if(c=='"') { p->t[id].kind=RV3_STRING; if(!string(p)) return 0; }
    else if(c=='-' || digit(c)) { p->t[id].kind=RV3_NUMBER; if(!number(p)) return 0; }
    else if(c=='t') { p->t[id].kind=RV3_BOOL; if(!literal(p,"true")) return 0; }
    else if(c=='f') { p->t[id].kind=RV3_BOOL; if(!literal(p,"false")) return 0; }
    else if(c=='n') { p->t[id].kind=RV3_NULL; if(!literal(p,"null")) return 0; }
    else return bad(p,RV3_INVALID);
    p->t[id].end=p->p; return 1;
}
rv3_result rv3_parse(const unsigned char *s,rv3_size n,rv3_token *t,rv3_size cap,unsigned depth) {
    parser p; rv3_result r;
    r.status=RV3_ARGUMENT; r.count=0; r.error_offset=0;
    /* Fixed recursion ceiling bounds stack use; caller may choose less. */
    if(!s || !t || !depth || depth>128) return r;
    p.s=s; p.n=n; p.p=0; p.count=0; p.cap=cap; p.t=t; p.limit=depth; p.status=RV3_OK;
    if(value(&p,RV3_NONE,RV3_NONE,RV3_NONE,0)) {
        ws(&p); if(p.p!=n) bad(&p,RV3_INVALID);
    }
    r.status=p.status; r.error_offset=p.p;
    if(p.status==RV3_OK) r.count=p.count;
    return r;
}
