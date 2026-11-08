#!/usr/bin/env python3
"""Same Portuguese semantic windows in UTF-8, Braille Unicode and packed 6-dot.
Source-text compression only. Not a full Portuguese Braille editorial transcriber.
Requires Python 3 + zstd v1.5.7 on PATH; no binaries/program compilation measured.
"""
from __future__ import annotations
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TXT = ROOT / "texto_portugues.txt"
LETTERS = dict(zip(
    "abcdefghijklmnopqrstuvwxyz",
    "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵"))
LETTERS.update({
    "á":"⠷","à":"⠫","â":"⠡","ã":"⠜","é":"⠿","ê":"⠣",
    "í":"⠌","ó":"⠬","ô":"⠹","õ":"⠪","ú":"⠾","ç":"⠯",
    " ":"⠀",",":"⠂",";":"⠆",":":"⠒",".":"⠄","?":"⠢",
    "!":"⠖","-":"⠤",
})
NUMS = dict(zip("1234567890", "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚"))
REVERSE = {v:k for k,v in LETTERS.items()}
REVERSE_NUMS = {v:k for k,v in NUMS.items()}
CAP, NUM = "⠨", "⠼"
assert len(REVERSE) == len(LETTERS)

def braille(s: str) -> str:
    out, numeric = [], False
    for ch in s:
        if ch in NUMS:
            if not numeric:
                out.append(NUM)
            numeric = True
            out.append(NUMS[ch])
            continue
        numeric = False
        if ch.lower() != ch and ch.lower() in LETTERS:
            out += [CAP, LETTERS[ch.lower()]]
        elif ch in LETTERS:
            out.append(LETTERS[ch])
        else:
            raise ValueError("Unmapped Portuguese symbol " + repr(ch))
    return "".join(out)

def decode_braille(s: str) -> str:
    out, cap, numeric = [], False, False
    for ch in s:
        if ch == CAP:
            if cap: raise ValueError("double uppercase marker")
            cap, numeric = True, False
            continue
        if ch == NUM:
            if numeric: raise ValueError("double numeric marker")
            numeric = True
            continue
        if numeric and ch in REVERSE_NUMS:
            out.append(REVERSE_NUMS[ch])
            continue
        numeric = False
        if ch not in REVERSE: raise ValueError("unknown cell")
        value = REVERSE[ch]
        if cap:
            if not value.isalpha(): raise ValueError("non-letter capitalization")
            value = value.upper()
            cap = False
        out.append(value)
    if cap or numeric: raise ValueError("dangling marker")
    return "".join(out)

def packed6(s: str) -> bytes:
    codes = [ord(c) - 0x2800 for c in s]
    if any(v < 0 or v >= 64 for v in codes): raise ValueError("six-dot only")
    out = bytearray(len(codes).to_bytes(4, "big"))
    acc = bits = 0
    for code in codes:
        acc = (acc << 6) | code
        bits += 6
        while bits >= 8:
            bits -= 8
            out.append((acc >> bits) & 255)
            acc &= (1 << bits) - 1
    if bits: out.append((acc << (8 - bits)) & 255)
    return bytes(out)

def unpack6(blob: bytes) -> str:
    n = int.from_bytes(blob[:4], "big")
    if len(blob) - 4 != (6*n + 7)//8: raise ValueError("bad length")
    cells, acc, bits = [], 0, 0
    for byte in blob[4:]:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 6 and len(cells) < n:
            bits -= 6
            cells.append(chr(0x2800 + ((acc >> bits) & 63)))
            acc &= (1 << bits) - 1
    return "".join(cells)

def compress(payload: bytes) -> bytes:
    c = subprocess.run(["zstd", "-q", "-19", "--long=10", "-c"],
                       input=payload, capture_output=True, check=True).stdout
    decoded = subprocess.run(["zstd", "-q", "-d", "-c"],
                             input=c, capture_output=True, check=True).stdout
    assert decoded == payload
    return c

def measure(text: str):
    for index, start in enumerate(range(0, len(text), 256), 1):
        s = text[start:start+256]
        b = braille(s)
        assert decode_braille(b) == s
        pt, uni, pack = s.encode("utf-8"), b.encode("utf-8"), packed6(b)
        assert unpack6(pack) == b
        result = []
        for value in (pt, uni, pack):
            result.extend((len(value), len(compress(value))))
        yield [index,start,len(s),len(b),*result]

def main():
    source = TXT.read_bytes()
    text = source.decode("utf-8")
    assert len(text) == 1256
    assert hashlib.sha256(source).hexdigest() == (
        "ce345d79784d938039382b5d98cc89fa867e137a1a22f46e7a2a7f80623effd2")
    expected = list(csv.reader((ROOT/"janelas_256.csv").open(encoding="utf-8")))[1:]
    actual = list(measure(text))
    assert [[str(v) for v in row] for row in actual] == expected, "measurements drift"
    for row in actual: print(",".join(str(x) for x in row))
    print("PASS_SCOPED 5 semantic windows, roundtrip and fixed-zstd-window comparisons")

if __name__ == "__main__":
    main()
