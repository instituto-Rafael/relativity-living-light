#include "rll_canonical_region.h"

#define RLL_FNV_OFFSET 14695981039346656037ull
#define RLL_FNV_PRIME 1099511628211ull

#include "../generated/rll_canonical_project_sources.inc"

static rll_u64 rll_fold_bytes(rll_u64 h, const rll_u8 *data, rll_u64 length) {
    rll_u64 i = 0ull;
    if ((data == (const rll_u8 *)0) && (length != 0ull)) {
        return 0ull;
    }
    while (i < length) {
        h ^= (rll_u64)data[i];
        h *= RLL_FNV_PRIME;
        i++;
    }
    return h;
}

static rll_u64 rll_fold_u32(rll_u64 h, rll_u32 value) {
    rll_u32 shift = 0u;
    while (shift < 32u) {
        rll_u8 octet = (rll_u8)((value >> shift) & 0xffu);
        h = rll_fold_bytes(h, &octet, 1ull);
        shift += 8u;
    }
    return h;
}

static rll_u64 rll_fold_u64(rll_u64 h, rll_u64 value) {
    rll_u32 shift = 0u;
    while (shift < 64u) {
        rll_u8 octet = (rll_u8)((value >> shift) & 0xffull);
        h = rll_fold_bytes(h, &octet, 1ull);
        shift += 8u;
    }
    return h;
}

static rll_u64 rll_fold_span(rll_u64 h, rll_canonical_span span) {
    h = rll_fold_u32(h, span.length);
    return rll_fold_bytes(h, span.data, (rll_u64)span.length);
}

static rll_u32 rll_span_equal(rll_canonical_span left, const rll_u8 *right, rll_u64 right_length) {
    rll_u64 i = 0ull;
    rll_u32 diff = 0u;
    if ((rll_u64)left.length != right_length) {
        return 0u;
    }
    if ((right == (const rll_u8 *)0) && (right_length != 0ull)) {
        return 0u;
    }
    while (i < right_length) {
        diff |= (rll_u32)(left.data[i] ^ right[i]);
        i++;
    }
    return (rll_u32)(diff == 0u);
}

static rll_u32 rll_digest_nonzero(const rll_u8 digest[32]) {
    rll_u32 i = 0u;
    rll_u32 joined = 0u;
    while (i < 32u) {
        joined |= (rll_u32)digest[i];
        i++;
    }
    return (rll_u32)(joined != 0u);
}

static rll_u32 rll_digest_equal(const rll_u8 left[32], const rll_u8 right[32]) {
    rll_u32 i = 0u;
    rll_u32 diff = 0u;
    while (i < 32u) {
        diff |= (rll_u32)(left[i] ^ right[i]);
        i++;
    }
    return (rll_u32)(diff == 0u);
}

static void rll_store_u32_le(rll_u8 *out, rll_u32 value) {
    out[0] = (rll_u8)(value & 0xffu);
    out[1] = (rll_u8)((value >> 8u) & 0xffu);
    out[2] = (rll_u8)((value >> 16u) & 0xffu);
    out[3] = (rll_u8)((value >> 24u) & 0xffu);
}

static void rll_store_u64_le(rll_u8 *out, rll_u64 value) {
    rll_u32 i = 0u;
    while (i < 8u) {
        out[i] = (rll_u8)((value >> (i * 8u)) & 0xffull);
        i++;
    }
}

const rll_canonical_receipt *rll_canonical_region_receipt(void) {
    return &rll_canonical_receipt_v1;
}

const rll_canonical_source *rll_canonical_region_source(rll_u32 index) {
    if (index >= rll_canonical_receipt_v1.source_count) {
        return (const rll_canonical_source *)0;
    }
    return &rll_canonical_sources[index];
}

rll_u32 rll_canonical_region_source_count(void) {
    return rll_canonical_receipt_v1.source_count;
}

rll_u32 rll_canonical_region_find_source(const rll_u8 *source_id, rll_u64 length) {
    rll_u32 i = 0u;
    while (i < rll_canonical_receipt_v1.source_count) {
        if (rll_span_equal(rll_canonical_sources[i].source_id, source_id, length) != 0u) {
            return i;
        }
        i++;
    }
    return RLL_CANONICAL_SOURCE_NOT_FOUND;
}

rll_u32 rll_canonical_region_custody_flags(void) {
    return rll_canonical_receipt_v1.custody_flags;
}

rll_u64 rll_canonical_region_fingerprint64(void) {
    static const rll_u8 domain[] = {
        0x52,0x4c,0x4c,0x5f,0x43,0x41,0x4e,0x4f,0x4e,0x49,0x43,0x41,0x4c,0x5f,0x52,0x45,
        0x47,0x49,0x4f,0x4e,0x5f,0x56,0x31
    };
    rll_u64 h = RLL_FNV_OFFSET;
    rll_u32 i = 0u;
    h = rll_fold_bytes(h, domain, (rll_u64)sizeof(domain));
    h = rll_fold_u32(h, rll_canonical_receipt_v1.abi_version);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.source_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.verified_local_hash_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.metadata_only_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.private_pointer_only_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.chunk_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.missing_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.hash_mismatch_count);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.vector_dimensions);
    h = rll_fold_span(h, rll_canonical_receipt_v1.vector_model);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.raw_bodies_committed);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.database_committed);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.claim_allowed);
    h = rll_fold_u32(h, rll_canonical_receipt_v1.custody_flags);
    h = rll_fold_bytes(h, rll_canonical_receipt_v1.receipt_manifest_sha256, 32ull);
    h = rll_fold_bytes(h, rll_canonical_receipt_v1.compiled_manifest_sha256, 32ull);

    while (i < rll_canonical_receipt_v1.source_count) {
        const rll_canonical_source *source = &rll_canonical_sources[i];
        h = rll_fold_span(h, source->source_id);
        h = rll_fold_span(h, source->display_name);
        h = rll_fold_span(h, source->local_filename);
        h = rll_fold_bytes(h, source->content_sha256, 32ull);
        h = rll_fold_u64(h, source->size_bytes);
        h = rll_fold_u32(h, source->line_count);
        h = rll_fold_span(h, source->temporal_state);
        h = rll_fold_u32(h, source->relation);
        h = rll_fold_u32(h, source->visibility);
        h = rll_fold_u32(h, source->ingestion_policy);
        h = rll_fold_span(h, source->summary);
        h = rll_fold_span(h, source->next_gate);
        h = rll_fold_u32(h, source->flags);
        h = rll_fold_u64(h, source->source_id_fnv1a64);
        i++;
    }
    return h;
}

rll_u32 rll_canonical_region_validate(void) {
    rll_u32 errors = RLL_CANONICAL_VALID;
    rll_u32 i = 0u;
    rll_u32 verified = 0u;
    rll_u32 metadata_only = 0u;
    rll_u32 private_pointer = 0u;

    if ((rll_canonical_receipt_v1.abi_version != RLL_CANONICAL_REGION_ABI_V1) ||
        (rll_canonical_receipt_v1.source_count != RLL_CANONICAL_GENERATED_SOURCE_COUNT) ||
        (rll_canonical_receipt_v1.vector_dimensions != 32u) ||
        (rll_canonical_receipt_v1.missing_count != 0u) ||
        (rll_canonical_receipt_v1.hash_mismatch_count != 0u)) {
        errors |= RLL_CANONICAL_ERR_RECEIPT;
    }
    if ((rll_canonical_receipt_v1.claim_allowed != 0u) ||
        (rll_canonical_receipt_v1.raw_bodies_committed != 0u) ||
        (rll_canonical_receipt_v1.database_committed != 0u)) {
        errors |= RLL_CANONICAL_ERR_BOUNDARY;
    }
    if ((rll_digest_nonzero(rll_canonical_receipt_v1.receipt_manifest_sha256) == 0u) ||
        (rll_digest_nonzero(rll_canonical_receipt_v1.compiled_manifest_sha256) == 0u)) {
        errors |= RLL_CANONICAL_ERR_RECEIPT;
    }
    {
        rll_u32 matches = rll_digest_equal(
            rll_canonical_receipt_v1.receipt_manifest_sha256,
            rll_canonical_receipt_v1.compiled_manifest_sha256);
        rll_u32 flags = rll_canonical_receipt_v1.custody_flags;
        if ((flags & RLL_CUSTODY_COMPILED_MANIFEST_HASHED) == 0u) {
            errors |= RLL_CANONICAL_ERR_CUSTODY_DECLARATION;
        }
        if (matches != 0u) {
            if (((flags & RLL_CUSTODY_RECEIPT_DIGEST_MATCH) == 0u) ||
                ((flags & RLL_CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED) != 0u)) {
                errors |= RLL_CANONICAL_ERR_CUSTODY_DECLARATION;
            }
        } else if (((flags & RLL_CUSTODY_RECEIPT_DIGEST_MATCH) != 0u) ||
                   ((flags & RLL_CUSTODY_RECEIPT_DIGEST_DIVERGENCE_DECLARED) == 0u)) {
            errors |= RLL_CANONICAL_ERR_CUSTODY_DECLARATION;
        }
    }

    while (i < rll_canonical_receipt_v1.source_count) {
        const rll_canonical_source *source = &rll_canonical_sources[i];
        rll_u32 j = i + 1u;
        if ((source->source_id.data == (const rll_u8 *)0) || (source->source_id.length == 0u) ||
            (source->display_name.data == (const rll_u8 *)0) || (source->display_name.length == 0u) ||
            (source->summary.data == (const rll_u8 *)0) || (source->summary.length == 0u) ||
            (source->next_gate.data == (const rll_u8 *)0) || (source->next_gate.length == 0u) ||
            (source->temporal_state.data == (const rll_u8 *)0) || (source->temporal_state.length == 0u) ||
            (source->size_bytes == 0ull) || (source->line_count == 0u) ||
            (source->relation < RLL_RELATION_METHODOLOGY) ||
            (source->relation > RLL_RELATION_RLL_DIRECT_AND_BIBLIOGRAPHIC)) {
            errors |= RLL_CANONICAL_ERR_SOURCE_METADATA;
        }
        if (rll_digest_nonzero(source->content_sha256) == 0u) {
            errors |= RLL_CANONICAL_ERR_SOURCE_DIGEST;
        }
        if (rll_fnv1a64(source->source_id.data, (rll_u64)source->source_id.length) != source->source_id_fnv1a64) {
            errors |= RLL_CANONICAL_ERR_SOURCE_ID_HASH;
        }
        if ((source->flags & (RLL_SOURCE_CLAIM_ALLOWED | RLL_SOURCE_RAW_BODY_COMMITTED)) != 0u) {
            errors |= RLL_CANONICAL_ERR_BOUNDARY;
        }

        if (source->ingestion_policy == RLL_POLICY_INGEST) {
            verified++;
            if (((source->flags & RLL_SOURCE_VERIFIED_LOCAL_HASH) == 0u) ||
                (source->visibility != RLL_VISIBILITY_PUBLIC_SAFE_METADATA_AND_LOCAL_BODY) ||
                (source->local_filename.data == (const rll_u8 *)0) ||
                (source->local_filename.length == 0u)) {
                errors |= RLL_CANONICAL_ERR_SOURCE_POLICY;
            }
        } else if (source->ingestion_policy == RLL_POLICY_METADATA_ONLY) {
            metadata_only++;
            if (((source->flags & RLL_SOURCE_METADATA_ONLY) == 0u) ||
                (source->visibility != RLL_VISIBILITY_PUBLIC_SAFE_METADATA_ONLY) ||
                (source->local_filename.data == (const rll_u8 *)0) ||
                (source->local_filename.length == 0u)) {
                errors |= RLL_CANONICAL_ERR_SOURCE_POLICY;
            }
        } else if (source->ingestion_policy == RLL_POLICY_POINTER_ONLY) {
            private_pointer++;
            if (((source->flags & RLL_SOURCE_PRIVATE_POINTER_ONLY) == 0u) ||
                (source->visibility != RLL_VISIBILITY_PRIVATE_POINTER_ONLY) ||
                (source->local_filename.data != (const rll_u8 *)0) ||
                (source->local_filename.length != 0u)) {
                errors |= RLL_CANONICAL_ERR_SOURCE_POLICY;
            }
        } else {
            errors |= RLL_CANONICAL_ERR_SOURCE_POLICY;
        }

        while (j < rll_canonical_receipt_v1.source_count) {
            if (rll_span_equal(source->source_id,
                               rll_canonical_sources[j].source_id.data,
                               (rll_u64)rll_canonical_sources[j].source_id.length) != 0u) {
                errors |= RLL_CANONICAL_ERR_SOURCE_DUPLICATE;
            }
            j++;
        }
        i++;
    }

    if ((verified != rll_canonical_receipt_v1.verified_local_hash_count) ||
        (metadata_only != rll_canonical_receipt_v1.metadata_only_count) ||
        (private_pointer != rll_canonical_receipt_v1.private_pointer_only_count) ||
        ((verified + metadata_only + private_pointer) != rll_canonical_receipt_v1.source_count)) {
        errors |= RLL_CANONICAL_ERR_RECEIPT;
    }
    if (rll_canonical_region_fingerprint64() != rll_canonical_receipt_v1.expected_fingerprint64) {
        errors |= RLL_CANONICAL_ERR_FINGERPRINT;
    }
    return errors;
}

rll_u32 rll_canonical_region_frame(rll_u8 *out, rll_u64 capacity) {
    static const rll_u8 magic[8] = {0x52,0x4c,0x4c,0x43,0x52,0x56,0x31,0x00};
    rll_u32 i = 0u;
    rll_u32 validation;
    if ((out == (rll_u8 *)0) || (capacity < (rll_u64)RLL_CANONICAL_REGION_FRAME_SIZE)) {
        return 0u;
    }
    while (i < 8u) {
        out[i] = magic[i];
        i++;
    }
    validation = rll_canonical_region_validate();
    rll_store_u32_le(out + 8u, rll_canonical_receipt_v1.abi_version);
    rll_store_u32_le(out + 12u, validation);
    rll_store_u32_le(out + 16u, rll_canonical_receipt_v1.source_count);
    rll_store_u32_le(out + 20u, rll_canonical_receipt_v1.verified_local_hash_count);
    rll_store_u32_le(out + 24u, rll_canonical_receipt_v1.metadata_only_count);
    rll_store_u32_le(out + 28u, rll_canonical_receipt_v1.private_pointer_only_count);
    rll_store_u32_le(out + 32u, rll_canonical_receipt_v1.chunk_count);
    rll_store_u32_le(out + 36u, rll_canonical_receipt_v1.vector_dimensions);
    rll_store_u32_le(out + 40u, rll_canonical_receipt_v1.missing_count);
    rll_store_u32_le(out + 44u, rll_canonical_receipt_v1.hash_mismatch_count);
    rll_store_u32_le(out + 48u,
        (rll_canonical_receipt_v1.claim_allowed << 0u) |
        (rll_canonical_receipt_v1.raw_bodies_committed << 1u) |
        (rll_canonical_receipt_v1.database_committed << 2u));
    rll_store_u32_le(out + 52u, rll_canonical_receipt_v1.custody_flags);
    i = 0u;
    while (i < 32u) {
        out[56u + i] = rll_canonical_receipt_v1.receipt_manifest_sha256[i];
        out[88u + i] = rll_canonical_receipt_v1.compiled_manifest_sha256[i];
        i++;
    }
    rll_store_u64_le(out + 120u, rll_canonical_region_fingerprint64());
    return RLL_CANONICAL_REGION_FRAME_SIZE;
}
