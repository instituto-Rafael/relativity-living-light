#!/usr/bin/env python3
"""RLL: Genesis 1 three-language compression RATIO, fixed-12-bit LZW.

Stdlib-only, offline checks by default. Upstream fetch is MANUAL and pinned.
Corpus compression is not a statement about truth, semantics or cosmology.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import unicodedata
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "data/contracts/rll_genesis_lzw12_ratio_v1.json"
LANGUAGES = ("he", "arc", "grc")
VARIANTS = ("vocalized", "without_diacritics")


def load_contract(path=CONTRACT):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def pack12(codes):
    acc = 0
    bits = 0
    out = bytearray()
    for code in codes:
        if not 0 <= code < 4096:
            raise ValueError("CODE_OUTSIDE_12_BITS")
        acc = (acc << 12) | code
        bits += 12
        while bits >= 8:
            bits -= 8
            out.append((acc >> bits) & 255)
            acc &= (1 << bits) - 1
    if bits:
        out.append((acc << (8 - bits)) & 255)
    return bytes(out)


def unpack12(packed, count):
    if count < 0 or len(packed) != (12 * count + 7) // 8:
        raise ValueError("LZW_PACKED_SIZE_MISMATCH")
    acc, bits, codes = 0, 0, []
    for byte in packed:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 12 and len(codes) < count:
            bits -= 12
            codes.append((acc >> bits) & 4095)
            acc &= (1 << bits) - 1
    if len(codes) != count or acc:
        raise ValueError("NONZERO_PADDING_OR_TRUNCATION")
    return codes


def encode12(data: bytes):
    if not data:
        raise ValueError("TOKEN_VAZIO_EMPTY_INPUT")
    table = {bytes((i,)): i for i in range(256)}
    next_code = 256
    word = b""
    codes = []
    for byte in data:
        candidate = word + bytes((byte,))
        if candidate in table:
            word = candidate
        else:
            if word:
                codes.append(table[word])
            if next_code >= 4096:
                raise ValueError("DICTIONARY_OVERFLOW_NO_RESET_POLICY")
            table[candidate] = next_code
            next_code += 1
            word = bytes((byte,))
    if word:
        codes.append(table[word])
    return pack12(codes), len(codes)


def decode12(packed, count):
    codes = unpack12(packed, count)
    reverse = {i: bytes((i,)) for i in range(256)}
    next_code = 256
    prior = b""
    decoded = bytearray()
    for code in codes:
        if code in reverse:
            item = reverse[code]
        elif code == next_code and prior:
            item = prior + prior[:1]
        else:
            raise ValueError("INVALID_LZW_CODE")
        decoded.extend(item)
        if prior:
            reverse[next_code] = prior + item[:1]
            next_code += 1
        prior = item
    return bytes(decoded)


def measure(data: bytes):
    packed, codes = encode12(data)
    if decode12(packed, codes) != data:
        raise ValueError("LOSSLESS_ROUNDTRIP_FAILED")
    return {
        "raw_bytes": len(data), "packed_bytes": len(packed),
        "codewords": codes,
        "compression_ratio": len(data) / len(packed),
        "compressed_bits_per_original_byte": 8 * len(packed) / len(data),
        "roundtrip": True,
    }


def normalize_passage(verses):
    if len(verses) != 31 or not all(isinstance(x, str) and x.strip() for x in verses):
        raise ValueError("GENESIS_VERSES_31_REQUIRED")
    return unicodedata.normalize("NFC", "\n".join(verses) + "\n")


def remove_marks(text):
    return unicodedata.normalize(
        "NFC",
        "".join(c for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"),
    )


def extract_verses(language, raw: bytes):
    content = raw.decode("utf-8-sig")
    if language == "he":
        parsed = json.loads(content)["verses"]
        if len(parsed) != 31 or any(v["n"] != i + 1 for i, v in enumerate(parsed)):
            raise ValueError("HEBREW_VERSE_NUMBERS_INVALID")
        return [v["he"].strip() for v in parsed]
    if language == "arc":
        in_chapter = False
        verses = []
        for line in content.replace("\r", "").split("\n"):
            item = line.strip()
            if item == "Chapter 1":
                in_chapter = True
                continue
            if item == "Chapter 2":
                break
            if in_chapter and item:
                verses.append(" ".join(html.unescape(
                    re.sub(r"</?b>", "", item, flags=re.I)
                ).split()))
        if len(verses) != 31:
            raise ValueError("ARAMAIC_VERSE_COUNT_INVALID")
        return verses
    if language == "grc":
        verses = {}
        for line in content.splitlines():
            found = re.match(r"^1\.1\.(\d{1,2})\s+(.+)$", line)
            if found:
                index = int(found.group(1))
                if index in verses:
                    raise ValueError("GREEK_DUPLICATE_VERSE")
                verses[index] = found.group(2).strip()
        if set(verses) != set(range(1, 32)):
            raise ValueError("GREEK_VERSE_ALIGNMENT_INVALID")
        return [verses[i] for i in range(1, 32)]
    raise ValueError("UNREGISTERED_LANGUAGE")


def _row(raw, packed, words):
    return {"raw_bytes": raw, "packed_bytes": packed, "codewords": words}


def audit(contract):
    if contract.get("schema") != "rll.genesis1_three_language_compression_ratio.lzw12.v1":
        raise ValueError("WRONG_CONTRACT_SCHEMA")
    if contract.get("verse_count") != 31:
        raise ValueError("VERSE_COUNT_NOT_31")
    for flag in ("claim_allowed", "physical_cosmology_claim_allowed",
                 "semantic_information_invariance_claim_allowed"):
        if contract.get(flag) is not False:
            raise ValueError("CLAIM_GATE_BROKEN:" + flag)
    if contract.get("compression_ratio_not_savings_percentage") is not True:
        raise ValueError("METRIC_CONFUSION_RATIO_VS_SAVINGS")
    if set(contract["sources"]) != set(LANGUAGES) or set(contract["measurements"]) != set(LANGUAGES):
        raise ValueError("LANGUAGE_SET_MISMATCH")
    output = {}
    for language in LANGUAGES:
        src = contract["sources"][language]
        if len(src["commit"]) != 40 or len(src["git_blob_sha1"]) != 40:
            raise ValueError("SOURCE_REVISION_OR_BLOB_UNPINNED")
        if not re.fullmatch(r"[a-f0-9]{40}", src["commit"] + ""):
            raise ValueError("MALFORMED_COMMIT")
        if not re.fullmatch(r"[a-f0-9]{40}", src["git_blob_sha1"]):
            raise ValueError("MALFORMED_BLOB")
        if set(contract["measurements"][language]) != set(VARIANTS):
            raise ValueError("UNREGISTERED_VARIANT")
        output[language] = {}
        for variant in VARIANTS:
            m = contract["measurements"][language][variant]
            raw, packed, codes = (m[k] for k in ("raw_bytes", "packed_bytes", "codewords"))
            if not all(type(x) is int and x > 0 for x in (raw, packed, codes)):
                raise ValueError("INVALID_BYTES_OR_CODEWORDS")
            if packed != (12 * codes + 7) // 8:
                raise ValueError("PACKED_12BIT_LENGTH_INVALID")
            if raw < packed:
                raise ValueError("UNEXPECTED_BENCHMARK_EXPANSION")
            output[language][variant] = {
                **_row(raw, packed, codes),
                "compression_ratio": raw / packed,
                "compressed_bits_per_original_byte": 8 * packed / raw,
            }
    return output


def pinned_url(source):
    return ("https://raw.githubusercontent.com/" + source["repository"] + "/" +
            source["commit"] + "/" + source["path"])


def verify_upstream(contract):
    output = {}
    for language in LANGUAGES:
        source = contract["sources"][language]
        req = Request(pinned_url(source), headers={"User-Agent": "RLL-Ratio-Audit/1.0"})
        with urlopen(req, timeout=40) as response:
            raw = response.read()
        if git_blob_sha1(raw) != source["git_blob_sha1"]:
            raise ValueError("PINNED_GIT_BLOB_CHANGED:" + language)
        text = normalize_passage(extract_verses(language, raw))
        output[language] = {}
        for variant in VARIANTS:
            normalized = text if variant == "vocalized" else remove_marks(text)
            m = measure(normalized.encode("utf-8"))
            declared = contract["measurements"][language][variant]
            if any(m[key] != declared[key] for key in
                   ("raw_bytes", "packed_bytes", "codewords")):
                raise ValueError("UPSTREAM_MEASUREMENT_MISMATCH:" + language + ":" + variant)
            output[language][variant] = {
                **m, "passage_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
            }
    return output


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--contract", type=Path, default=CONTRACT)
    args.add_argument("--output", type=Path)
    args.add_argument("--verify-upstream", action="store_true")
    args.add_argument("--require-pass", action="store_true")
    parsed = args.parse_args()
    data = load_contract(parsed.contract)
    rows = audit(data)
    upstream = verify_upstream(data) if parsed.verify_upstream else None
    receipt = {
        "schema": "rll.genesis1_lzw12_ratio_receipt.v1",
        "state": "PASS_PINNED_CORPUS_REMEASURE" if upstream else "PASS_SCOPED_OFFLINE_RATIO_CONTRACT",
        "compression_ratio_definition": "original_bytes/compressed_bytes",
        "verified_upstream_fetch": bool(upstream),
        "offline_source_content_fetched": False,
        "rows": upstream if upstream is not None else rows,
        "claim_allowed": False, "semantic_equivalence_proven": False,
        "cosmology_model_validation": "NOT_RUN",
    }
    result = json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if parsed.output:
        parsed.output.parent.mkdir(parents=True, exist_ok=True)
        parsed.output.write_text(result, encoding="utf-8")
    print(result)
    if parsed.require_pass and not receipt["state"].startswith("PASS"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
