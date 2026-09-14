#ifndef RLL_CANONICAL_REGION_H
#define RLL_CANONICAL_REGION_H

#include "pantheon_freestanding.h"

#ifdef __cplusplus
extern "C" {
#endif

#define RLL_CANONICAL_REGION_ABI_V1 0x00010000u
#define RLL_CANONICAL_REGION_FRAME_SIZE 128u
#define RLL_CANONICAL_SOURCE_NOT_FOUND 0xFFFFFFFFu

typedef struct rll_canonical_span {
    const rll_u8 *data;
    rll_u32 length;
} rll_canonical_span;

typedef enum rll_canonical_relation {
    RLL_RELATION_INVALID = 0,
    RLL_RELATION_METHODOLOGY = 1,
    RLL_RELATION_MATHEMATICAL_CONTEXT = 2,
    RLL_RELATION_FEDERATED_GOVERNANCE = 3,
    RLL_RELATION_RLL_DIRECT_AND_METHODOLOGY = 4,
    RLL_RELATION_COMPUTATIONAL_CONTEXT = 5,
    RLL_RELATION_INDEX_POINTER = 6,
    RLL_RELATION_OUT_OF_SCOPE_PERSONAL = 7,
    RLL_RELATION_SOURCE_INVENTORY = 8,
    RLL_RELATION_OPERATIONAL_EVIDENCE = 9,
    RLL_RELATION_RLL_DIRECT_AND_BIBLIOGRAPHIC = 10
} rll_canonical_relation;

typedef enum rll_canonical_visibility {
    RLL_VISIBILITY_INVALID = 0,
    RLL_VISIBILITY_PUBLIC_SAFE_METADATA_AND_LOCAL_BODY = 1,
    RLL_VISIBILITY_PUBLIC_SAFE_METADATA_ONLY = 2,
    RLL_VISIBILITY_PRIVATE_POINTER_ONLY = 3
} rll_canonical_visibility;

typedef enum rll_canonical_ingestion_policy {
    RLL_POLICY_INVALID = 0,
    RLL_POLICY_INGEST = 1,
    RLL_POLICY_METADATA_ONLY = 2,
    RLL_POLICY_POINTER_ONLY = 3
} rll_canonical_ingestion_policy;

enum rll_canonical_source_flags {
    RLL_SOURCE_VERIFIED_LOCAL_HASH = 1u << 0,
    RLL_SOURCE_METADATA_ONLY = 1u << 1,
    RLL_SOURCE_PRIVATE_POINTER_ONLY = 1u << 2,
    RLL_SOURCE_NOT_EVIDENCE_COSMOLOGY = 1u << 3,
    RLL_SOURCE_NOT_EVIDENCE_PHYSICAL_LAW = 1u << 4,
    RLL_SOURCE_NOT_EVIDENCE_BIOLOGY = 1u << 5,
    RLL_SOURCE_CLAIM_ALLOWED = 1u << 6,
    RLL_SOURCE_RAW_BODY_COMMITTED = 1u << 7
};

enum rll_canonical_custody_flags {
    RLL_CUSTODY_COMPILED_MANIFEST_HASHED = 1u << 0,
    RLL_CUSTODY_RECEIPT_DIGEST_MATCH = 1u << 1,
    RLL_CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED = 1u << 2
};

enum rll_canonical_validation_errors {
    RLL_CANONICAL_VALID = 0u,
    RLL_CANONICAL_ERR_RECEIPT = 1u << 0,
    RLL_CANONICAL_ERR_SOURCE_METADATA = 1u << 1,
    RLL_CANONICAL_ERR_SOURCE_DIGEST = 1u << 2,
    RLL_CANONICAL_ERR_SOURCE_POLICY = 1u << 3,
    RLL_CANONICAL_ERR_SOURCE_DUPLICATE = 1u << 4,
    RLL_CANONICAL_ERR_SOURCE_ID_HASH = 1u << 5,
    RLL_CANONICAL_ERR_FINGERPRINT = 1u << 6,
    RLL_CANONICAL_ERR_BOUNDARY = 1u << 7,
    RLL_CANONICAL_ERR_CUSTODY_DECLARATION = 1u << 8
};

typedef struct rll_canonical_source {
    rll_canonical_span source_id;
    rll_canonical_span display_name;
    rll_canonical_span local_filename;
    rll_u8 content_sha256[32];
    rll_u64 size_bytes;
    rll_u32 line_count;
    rll_canonical_span temporal_state;
    rll_u32 relation;
    rll_u32 visibility;
    rll_u32 ingestion_policy;
    rll_canonical_span summary;
    rll_canonical_span next_gate;
    rll_u32 flags;
    rll_u64 source_id_fnv1a64;
} rll_canonical_source;

typedef struct rll_canonical_receipt {
    rll_u32 abi_version;
    rll_u32 source_count;
    rll_u32 verified_local_hash_count;
    rll_u32 metadata_only_count;
    rll_u32 private_pointer_only_count;
    rll_u32 chunk_count;
    rll_u32 missing_count;
    rll_u32 hash_mismatch_count;
    rll_u32 vector_dimensions;
    rll_canonical_span vector_model;
    rll_u32 raw_bodies_committed;
    rll_u32 database_committed;
    rll_u32 claim_allowed;
    rll_u32 custody_flags;
    rll_u8 receipt_manifest_sha256[32];
    rll_u8 compiled_manifest_sha256[32];
    rll_u64 expected_fingerprint64;
} rll_canonical_receipt;

/* Tabela compilada a partir do manifesto e do receipt versionados no RLL. */
const rll_canonical_receipt *rll_canonical_region_receipt(void);
const rll_canonical_source *rll_canonical_region_source(rll_u32 index);
rll_u32 rll_canonical_region_source_count(void);
rll_u32 rll_canonical_region_find_source(const rll_u8 *source_id, rll_u64 length);

/* Validação fail-closed de estrutura; divergências de custódia são declaradas em flags. */
rll_u32 rll_canonical_region_validate(void);
rll_u32 rll_canonical_region_custody_flags(void);
rll_u64 rll_canonical_region_fingerprint64(void);

/* Frame LE de 128 bytes: estado, contagens, fronteiras, dois SHA-256 e fingerprint. */
rll_u32 rll_canonical_region_frame(rll_u8 *out, rll_u64 capacity);

#ifdef __cplusplus
}
#endif

#endif
