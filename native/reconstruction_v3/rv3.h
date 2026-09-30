#ifndef RV3_H
#define RV3_H
/* Caller owns immutable source and token storage. No libc, heap or I/O. */
typedef __SIZE_TYPE__ rv3_size;
#define RV3_NONE ((rv3_size)-1)
enum rv3_kind { RV3_OBJECT=1, RV3_ARRAY, RV3_STRING, RV3_NUMBER, RV3_BOOL, RV3_NULL };
enum rv3_status { RV3_OK=0, RV3_INVALID, RV3_CAPACITY, RV3_DEPTH, RV3_ARGUMENT };
typedef struct {
    rv3_size start, end, parent, key_start, key_end;
    unsigned kind;
} rv3_token;
typedef struct { unsigned status; rv3_size count, error_offset; } rv3_result;
/* Output valid only on RV3_OK; other statuses return count=0.
 * Strings include quotes; key offsets include quotes or are RV3_NONE.
 * Depth counts containers, including root. Duplicate keys are preserved.
 * UTF-8 and Unicode escapes validated; no Unicode normalization performed.
 * Bounded full-document API: chunk streaming is a separate future adapter.
 */
rv3_result rv3_parse(const unsigned char *, rv3_size, rv3_token *, rv3_size, unsigned);
#endif
