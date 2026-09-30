#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, re, unicodedata, urllib.request, zipfile
from pathlib import Path

BOOK_ORDER = [
"GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI","1CH","2CH",
"EZR","NEH","EST","JOB","PSA","PRO","ECC","SNG","ISA","JER","LAM","EZK","DAN","HOS",
"JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP","HAG","ZEC","MAL","MAT","MRK","LUK",
"JHN","ACT","ROM","1CO","2CO","GAL","EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT",
"PHM","HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV"
]
NOTE_BLOCKS = [("f","f*"),("x","x*"),("fig","fig*")]

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def clean_inline(s: str) -> str:
    for start,end in NOTE_BLOCKS:
        s = re.sub(rf"\\{start}\b.*?\\{end}\b", " ", s, flags=re.S)
    s = re.sub(r"\\w\s+([^|\\]+)(?:\|[^\\]*)?\\w\*", r"\1", s)
    s = re.sub(r"\\\+?[\w\d-]+\*?", " ", s)
    s = re.sub(r"\|[^\s]+", " ", s)
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()

def parse_usfm(text: str, expected_book: str) -> list[dict]:
    text = text.replace("\r\n","\n").replace("\r","\n")
    text = re.sub(r"\\f\b.*?\\f\*", " ", text, flags=re.S)
    text = re.sub(r"\\x\b.*?\\x\*", " ", text, flags=re.S)
    chapter = None
    cur = None
    verses = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^\\c\s+(\d+)", line)
        if m:
            chapter = int(m.group(1)); continue
        m = re.match(r"^\\v\s+([0-9]+(?:[-–][0-9]+)?[a-z]?)\s*(.*)$", line)
        if m and chapter is not None:
            if cur:
                cur["text"] = clean_inline(" ".join(cur.pop("_buf")))
                verses.append(cur)
            cur = {"book":expected_book,"chapter":chapter,"verse":m.group(1),"_buf":[m.group(2)]}
            continue
        if cur and not line.startswith("\\id ") and not line.startswith("\\h "):
            cur["_buf"].append(line)
    if cur:
        cur["text"] = clean_inline(" ".join(cur.pop("_buf")))
        verses.append(cur)
    return [v for v in verses if v["text"]]

def detect_book(member_text: str) -> str | None:
    m = re.search(r"(?m)^\\id\s+([1-3]?[A-Z]{2,3})\b", member_text)
    return m.group(1) if m else None

def fetch_zip(url: str, timeout: int=60) -> bytes:
    req=urllib.request.Request(url, headers={"User-Agent":"RLL-Bible10/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data=r.read()
    if not data.startswith(b"PK"):
        raise ValueError("source_not_zip")
    return data

def extract_translation(zip_bytes: bytes, selected: set[str] | None) -> tuple[dict[str,list[dict]],dict]:
    found={}
    member_receipts=[]
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():
            if name.endswith("/") or not re.search(r"\.(?:usfm|sfm|txt)$", name, re.I):
                continue
            raw=z.read(name)
            try:
                text=raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text=raw.decode("utf-8","replace")
            book=detect_book(text)
            if not book or (selected is not None and book not in selected):
                continue
            verses=parse_usfm(text,book)
            if verses:
                found[book]=verses
                member_receipts.append({"member":name,"book":book,"bytes":len(raw),"sha256":sha256_bytes(raw),"verses":len(verses)})
    return found,{"members":member_receipts}

def write_translation(out_root: Path, lang: str, meta: dict, books: dict[str,list[dict]], source_receipt: dict):
    d=out_root/lang
    d.mkdir(parents=True,exist_ok=True)
    (d/"source.json").write_text(json.dumps({
      "schema":"rll.bible10.translation-source.v1",
      "lang":lang, **meta, **source_receipt,
      "claim_allowed":False
    },ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for book,verses in books.items():
        with (d/f"{book}.jsonl").open("w",encoding="utf-8") as f:
            for v in verses:
                rec={"ref":f'{book} {v["chapter"]}:{v["verse"]}',"book":book,"chapter":v["chapter"],"verse":v["verse"],"lang":lang,"text":v["text"]}
                f.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--books",default="JHN,GEN,MAT",help="comma list or ALL")
    ap.add_argument("--cache",type=Path)
    args=ap.parse_args()
    reg=json.loads(args.registry.read_text(encoding="utf-8"))
    selected=None if args.books.upper()=="ALL" else {x.strip().upper() for x in args.books.split(",") if x.strip()}
    if selected is not None:
        bad=selected-set(BOOK_ORDER)
        if bad: raise SystemExit("unknown books: "+",".join(sorted(bad)))
    receipts=[]
    args.out.mkdir(parents=True,exist_ok=True)
    if args.cache: args.cache.mkdir(parents=True,exist_ok=True)
    for src in reg["languages"]:
        if src.get("license")!="Public Domain":
            raise SystemExit(f"refuse_non_public_domain:{src['lang']}")
        eid=src["ebible_id"]
        url=f"https://ebible.org/Scriptures/{eid}_usfm.zip"
        cache=(args.cache/f"{eid}_usfm.zip") if args.cache else None
        if cache and cache.exists():
            zbytes=cache.read_bytes(); origin="cache"
        else:
            zbytes=fetch_zip(url); origin="network"
            if cache: cache.write_bytes(zbytes)
        books,detail=extract_translation(zbytes,selected)
        expected=set(BOOK_ORDER) if selected is None else selected
        missing=sorted(expected-set(books))
        source_receipt={
          "download_url":url,"download_origin":origin,
          "download_sha256":sha256_bytes(zbytes),"download_bytes":len(zbytes),
          "selected_books":"ALL" if selected is None else sorted(selected),
          "missing_selected_books":missing,
          "member_receipts":detail["members"]
        }
        write_translation(args.out,src["lang"],{
          "name":src["name"],"title":src["title"],"ebible_id":eid,
          "license":src["license"],"license_url":src["license_url"]
        },books,source_receipt)
        receipts.append({"lang":src["lang"],**source_receipt})
        if missing:
            raise SystemExit(f"missing_books:{src['lang']}:{','.join(missing)}")
    receipt={"schema":"rll.bible10.ingest.receipt.v1","languages":len(receipts),"records":receipts,"claim_allowed":False}
    (args.out/"INGEST_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","languages":len(receipts),"books":args.books,"claim_allowed":False},sort_keys=True))

if __name__=="__main__":
    main()
