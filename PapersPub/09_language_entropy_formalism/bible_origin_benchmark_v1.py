#!/usr/bin/env python3
"""Bible origin-language entropy/compression benchmark V1.

Input: JSONL rows with ref, book, language, text, source_id.
Scope: computational structure only. No semantic/thermodynamic/quantum claim.
"""

from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import json
import lzma
import math
import random
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def entropy_symbols(seq) -> float:
    n = len(seq)
    if not n:
        return 0.0
    counts = Counter(seq)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def conditional_entropy_1(seq) -> float:
    if len(seq) < 2:
        return 0.0
    prev = Counter(seq[:-1])
    pairs = Counter(zip(seq[:-1], seq[1:]))
    n = len(seq) - 1
    h = 0.0
    for (a, _b), c in pairs.items():
        p_ab = c / n
        p_b_given_a = c / prev[a]
        h -= p_ab * math.log2(p_b_given_a)
    return h


def redundancy(h0: float, alphabet: int):
    if alphabet <= 1:
        return 0.0
    return 1.0 - h0 / math.log2(alphabet)


def compressors(raw: bytes) -> dict:
    encoded = {
        "gzip_9": gzip.compress(raw, compresslevel=9, mtime=0),
        "bz2_9": bz2.compress(raw, compresslevel=9),
        "lzma_9": lzma.compress(raw, preset=9),
    }
    decoded = {
        "gzip_9": gzip.decompress(encoded["gzip_9"]),
        "bz2_9": bz2.decompress(encoded["bz2_9"]),
        "lzma_9": lzma.decompress(encoded["lzma_9"]),
    }
    return {
        k: {
            "bytes": len(v),
            "ratio_vs_raw": (len(v) / len(raw)) if raw else 0.0,
            "reconstruction_equal": decoded[k] == raw,
            "sha256": sha256(v),
        }
        for k, v in encoded.items()
    }


def analyze_text(text: str) -> dict:
    nfc = unicodedata.normalize("NFC", text)
    raw = nfc.encode("utf-8")
    chars = list(nfc)
    h_char = entropy_symbols(chars)
    h_cond = conditional_entropy_1(chars)
    c1 = 1.0 - (h_cond / h_char) if h_char > 0 else 0.0
    return {
        "unicode_normalization": "NFC",
        "codepoints": len(chars),
        "utf8_bytes": len(raw),
        "alphabet_codepoints": len(set(chars)),
        "h0_char_bits_per_symbol": h_char,
        "h1_cond_char_bits_per_symbol": h_cond,
        "c1_local_predictability": c1,
        "i1_local_incoherence": 1.0 - c1,
        "redundancy_alphabet": redundancy(h_char, len(set(chars))),
        "h0_byte_bits_per_byte": entropy_symbols(raw),
        "raw_sha256": sha256(raw),
        "compression": compressors(raw),
    }


def null_order_gain(records, permutations: int, seed: int, codec: str) -> dict:
    texts = [r["text"] for r in records]
    observed_raw = "\n".join(texts).encode("utf-8")
    observed = compressors(observed_raw)[codec]["bytes"]
    rng = random.Random(seed)
    null = []
    for _ in range(permutations):
        idx = list(range(len(texts)))
        rng.shuffle(idx)
        raw = "\n".join(texts[i] for i in idx).encode("utf-8")
        null.append(compressors(raw)[codec]["bytes"])
    med = statistics.median(null) if null else observed
    gain = (med - observed) / med if med else 0.0
    wins = sum(observed < x for x in null)
    return {
        "metric_state": "CANDIDATE_PROJECT_METRIC",
        "codec": codec,
        "permutations": permutations,
        "seed": seed,
        "observed_bytes": observed,
        "null_min": min(null) if null else observed,
        "null_median": med,
        "null_max": max(null) if null else observed,
        "observed_beats_null_count": wins,
        "observed_beats_null_fraction": wins / len(null) if null else 0.0,
        "centripia_candidate_order_gain": gain,
    }


def parse_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            missing = [k for k in ("ref", "book", "language", "text", "source_id") if k not in obj]
            if missing:
                raise ValueError(f"line {lineno}: missing {missing}")
            obj = dict(obj)
            obj["text"] = unicodedata.normalize("NFC", str(obj["text"]).strip())
            rows.append(obj)
    return rows


def shared_reference_seed(rows):
    by_lang = defaultdict(dict)
    for r in rows:
        by_lang[r["language"]][r["ref"]] = r["text"]
    langs = sorted(by_lang)
    if len(langs) < 2:
        return {"status": "NOT_APPLICABLE_LT2_LANGUAGES"}
    refs = sorted(set.intersection(*(set(by_lang[l]) for l in langs)))
    if not refs:
        return {"status": "NOT_APPLICABLE_NO_SHARED_REFS"}
    verbose = [
        {"ref": ref, "language": lang, "text": by_lang[lang][ref]}
        for ref in refs for lang in langs
    ]
    seed = {
        "schema": "rll.shared_ref_seed.v1",
        "refs": refs,
        "languages": langs,
        "texts": {lang: [by_lang[lang][r] for r in refs] for lang in langs},
    }
    vb = json.dumps(verbose, ensure_ascii=False, separators=(",", ":")).encode()
    sb = json.dumps(seed, ensure_ascii=False, separators=(",", ":")).encode()
    reconstructed = [
        {"ref": ref, "language": lang, "text": seed["texts"][lang][i]}
        for i, ref in enumerate(seed["refs"]) for lang in seed["languages"]
    ]
    rb = json.dumps(reconstructed, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "status": "ANALYZED",
        "languages": langs,
        "shared_refs": len(refs),
        "verbose_bytes": len(vb),
        "seed_bytes": len(sb),
        "delta_bytes": len(vb) - len(sb),
        "delta_pct_vs_verbose": ((len(vb) - len(sb)) * 100 / len(vb)) if vb else 0.0,
        "exact_reconstruction": vb == rb,
        "verbose_sha256": sha256(vb),
        "reconstructed_sha256": sha256(rb),
        "seed_sha256": sha256(sb),
        "seed_compression": compressors(sb),
    }


def selftest():
    rows = [
        {"ref": "A.1.1", "book": "A", "language": "x", "text": "abba abba", "source_id": "s"},
        {"ref": "A.1.2", "book": "A", "language": "x", "text": "abba baba", "source_id": "s"},
        {"ref": "A.1.1", "book": "A", "language": "y", "text": "alpha alpha", "source_id": "t"},
        {"ref": "A.1.2", "book": "A", "language": "y", "text": "alpha beta", "source_id": "t"},
    ]
    a = analyze_text("\n".join(r["text"] for r in rows))
    sr = shared_reference_seed(rows)
    assert all(v["reconstruction_equal"] for v in a["compression"].values())
    assert sr["exact_reconstruction"] is True
    out = {
        "status": "PASS_SELFTEST",
        "raw_sha256": a["raw_sha256"],
        "shared_reference_exact": sr["exact_reconstruction"],
    }
    print(json.dumps(out, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--permutations", type=int, default=32)
    ap.add_argument("--seed", type=int, default=144000)
    ap.add_argument("--codec", choices=["gzip_9", "bz2_9", "lzma_9"], default="lzma_9")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return 0
    if not args.input:
        ap.error("--input is required unless --selftest is used")
    if args.permutations < 1:
        ap.error("--permutations must be >= 1")

    rows = parse_jsonl(args.input)
    if not rows:
        raise SystemExit("empty corpus")

    groups = defaultdict(list)
    for r in rows:
        groups[(r["language"], r["book"])].append(r)

    group_results = {}
    for (lang, book), rs in sorted(groups.items()):
        rs = sorted(rs, key=lambda x: x["ref"])
        text = "\n".join(r["text"] for r in rs)
        group_results[f"{lang}:{book}"] = {
            "records": len(rs),
            "source_ids": sorted(set(r["source_id"] for r in rs)),
            "metrics": analyze_text(text),
            "order_null": null_order_gain(rs, args.permutations, args.seed, args.codec),
        }

    result = {
        "schema": "rll.bible_origin_entropy_result.v1",
        "status": "ANALYSIS_RUN_COMPUTATIONAL_SCOPE",
        "claim_allowed": False,
        "input": str(args.input),
        "records": len(rows),
        "languages": sorted(set(r["language"] for r in rows)),
        "books": sorted(set(r["book"] for r in rows)),
        "parameters": {
            "unicode": "NFC",
            "permutations": args.permutations,
            "seed": args.seed,
            "null_codec": args.codec,
        },
        "groups": group_results,
        "shared_reference_seed": shared_reference_seed(rows),
        "boundaries": [
            "C1 is local symbol predictability, not semantic coherence",
            "centripia_candidate_order_gain is project-defined, not thermodynamic syntropy",
            "codec compression is separate from ZIPRAF logical address density",
            "text metrics do not establish phonetic, neural, physical, or theological claims",
        ],
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
