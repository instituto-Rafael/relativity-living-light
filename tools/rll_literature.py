"""Discover chronological evidence in Crossref and build a DOI-indexed research notebook."""
import argparse
import datetime
import html
import json
import re
from pathlib import Path
import urllib.parse
import urllib.request

TOPICS = [
    ("globular cluster ages Gaia", ("globular", "age"),
     "Quanto tempo sobra para a formação dos aglomerados em cada cosmologia?",
     "Extrair idade, distância, metalicidade e erros compartilhados."),
    ("cosmic chronometers stellar population covariance", ("chronometer",),
     "A expansão inferida de idades diferenciais reproduz a inclinação prevista pelo RLL?",
     "Extrair H(z), calibração de população estelar e matriz de covariância."),
    ("JWST massive quiescent galaxy stellar ages", ("quiescent",),
     "O tempo disponível permite a história de formação inferida do espectro?",
     "Separar redshift observado, idade estelar e prior cosmológico.")
]


def collect(records, search):
    for query, terms, question, check in TOPICS:
        for item in search(query):
            doi = item.get("DOI", "").strip().lower()
            title = html.unescape(re.sub(r"</?[A-Za-z][^>]*>", "", " ".join(item.get("title", []))))
            if query.startswith("cosmic") and not any(w in title.lower() for w in ("cosmolog", "redshift", "supernova", "stellar population", "hubble", "dark energy", "expansion")):
                continue
            if query.startswith("JWST") and "galax" not in title.lower():
                continue
            if not doi.startswith("10.") or not all(t in title.lower() for t in terms):
                continue
            record = records.setdefault(doi, {"title": title, "source": "https://doi.org/" + doi,
                "year": item.get("published", {}).get("date-parts", [[None]])[0][0],
                "status": "bibliographic_candidate", "claim_allowed": False, "questions": {}})
            abstract = html.unescape(re.sub(r"<[^>]*>", " ", item.get("abstract", "")))
            abstract = " ".join(abstract.split())
            # Keep source-linked quantities, not copies of publisher abstracts.
            quantities = re.findall(r"(?<![\w.])\d+(?:[.]\d+)?\s*(?:Gyr|Myr)\b", abstract)
            if quantities:
                record["reported_time_mentions"] = list(dict.fromkeys(quantities))
                record["interpretation"] = "Conferir no artigo se cada tempo mede idade, duração ou erro."
            record["questions"][query] = {"hypothesis_to_test": question, "evidence_needed": check}
    return records


def crossref(query):
    params = urllib.parse.urlencode({"query.bibliographic": query, "rows": 20,
        "filter": "type:journal-article,from-pub-date:2020-01-01",
        "select": "DOI,title,published,abstract"})
    req = urllib.request.Request("https://api.crossref.org/works?" + params,
                                 headers={"User-Agent": "RLL-Literature/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)["message"]["items"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline", action="store_true", help="Replay a pinned local baseline without network access.")
    args = parser.parse_args()
    if args.offline and not args.baseline:
        parser.error("--offline requires --baseline")
    if args.baseline and args.output.resolve() == args.baseline.resolve():
        parser.error("output must not replace the source baseline")
    baseline = json.loads(args.baseline.read_text(encoding="utf-8")) if args.baseline else {}
    records = baseline.get("records", {})
    before = set(records)
    if not args.offline:
        collect(records, crossref)
    payload = {**baseline, "provider": "Crossref",
               "execution_mode": "OFFLINE_REPLAY" if args.offline else "LIVE_DISCOVERY",
               "queries": [t[0] for t in TOPICS], "added_dois": sorted(set(records) - before),
               "records": records, "claim_allowed": False}
    if not args.offline:
        payload["retrieved_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    temp = args.output.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(args.output)


if __name__ == "__main__":
    main()
