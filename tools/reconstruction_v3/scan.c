/* Hosted transport adapter. The kernel rv3.c stays freestanding. */
#include <stdio.h>
#include "../../native/reconstruction_v3/rv3.h"
#ifndef RV3_BYTES
#define RV3_BYTES (16u*1024u*1024u)
#endif
#ifndef RV3_TOKENS
#define RV3_TOKENS 262144u
#endif
static unsigned char input[RV3_BYTES];
static rv3_token tokens[RV3_TOKENS];
int main(int argc,char **argv) {
    FILE *f; size_t n,i; rv3_result r;
    if(argc!=2) { fputs("usage: rv3-scan source.json\n",stderr); return 2; }
    f=fopen(argv[1],"rb"); if(!f) return 2;
    n=fread(input,1,sizeof input,f);
    if(ferror(f) || fgetc(f)!=EOF) { fclose(f); fputs("INPUT_CAPACITY\n",stderr); return 3; }
    fclose(f); r=rv3_parse(input,n,tokens,RV3_TOKENS,64);
    if(r.status) { fprintf(stderr,"RV3_STATUS=%u OFFSET=%zu\n",r.status,r.error_offset); return 4; }
    for(i=0;i<r.count;i++) {
        rv3_token *t=&tokens[i];
        /* Signed sentinel printed explicitly, independent of word size. */
        printf("%zu\t%u\t%zu\t%zu\t",i,t->kind,t->start,t->end);
        if(t->parent==RV3_NONE) printf("-1\t"); else printf("%zu\t",t->parent);
        if(t->key_start==RV3_NONE) puts("-1\t-1");
        else printf("%zu\t%zu\n",t->key_start,t->key_end);
    }
    return ferror(stdout)?5:0;
}
