#include "../../native/reconstruction_v3/rv3.h"
int main(void) {
    rv3_token t[8]; rv3_result r;
    r=rv3_parse((const unsigned char *)"[1,2]",5,t,2,8);
    if(r.status!=RV3_CAPACITY || r.count!=0) return 1;
    r=rv3_parse((const unsigned char *)"[[0]]",5,t,8,1);
    if(r.status!=RV3_DEPTH || r.count!=0) return 2;
    r=rv3_parse((const unsigned char *)"[[0]]",5,t,8,2);
    if(r.status!=RV3_OK || r.count!=3 || t[2].parent!=1) return 3;
    r=rv3_parse((const unsigned char *)"null",4,t,8,129);
    if(r.status!=RV3_ARGUMENT || r.count!=0) return 4;
    r=rv3_parse((const unsigned char *)"null",4,t,0,8);
    if(r.status!=RV3_CAPACITY || r.count!=0) return 5;
    r=rv3_parse((const unsigned char *)"{} garbage",10,t,8,8);
    if(r.status!=RV3_INVALID || r.count!=0) return 6;
    return 0;
}
