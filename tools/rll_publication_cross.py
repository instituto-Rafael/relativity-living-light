"""Match incoming publication metadata against the current producer's tracked model paths."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.rll_age_gate import H0, MATTER
from tools.rll_literature import require_unpromoted, write_json_atomic

FEEDS = ("https://www.nature.com/nature.rss", "https://rss.arxiv.org/rss/astro-ph.CO",
         "https://rss.arxiv.org/rss/gr-qc", "https://rss.arxiv.org/rss/astro-ph.SR")
GROUPS = {
    "gravitational": ("gravitational", "gravity", "gravitation"),
    "hubble": ("hubble", "h0", "cosmology"),
    "stellar": ("stellar", "solar", "star", "sun"),
    "plasma": ("plasma", "magnetohydrodynamic"),
    "supernova": ("supernova", "supernovae", "pantheon"),
    "chronology": ("chronology", "chronometers", "ages"),
}
MEASURE = re.compile(r'\bH[_ ]?0\s*=\s*(\d+(?:\.\d+)?)\s*(?:±|\+-|\+/-|\\pm)\s*(\d+(?:\.\d+)?)\s*km/s/Mpc\b', re.I)


def words(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def tags(text):
    tokens = words(text)
    return sorted(k for k, aliases in GROUPS.items() if tokens.intersection(aliases))


def observation(title, summary):
    text = html.unescape(re.sub(r'<[^>]+>', ' ', summary))
    quantities = sorted(set((float(m[1]), float(m[2])) for m in MEASURE.finditer(text)
                            if float(m[2]) > 0 and math.isfinite(float(m[1])) and math.isfinite(float(m[2]))))
    powers = re.findall(r"H\(z\)\s*=\s*H[_ ]?0\s*[*·]?\s*\(1\s*\+\s*z\)\s*\^\s*\{?(-?\d+(?:\.\d+)?)\}?(?![\w.+*/^-])(?=\s*(?:$|[,;]))", text)
    return {"h_power_exponents": [float(n) for n in powers if abs(float(n)) <= 10], "title": title, "topics": tags(title + ' ' + text), "h0_mentions": quantities,
            "source_text_sha256": hashlib.sha256(summary.encode()).hexdigest()}


def evaluate(record, paths):
    topics = set(record["topics"])
    matches = [(len(topics.intersection(t)), path) for path, t in paths if topics.intersection(t)]
    record["candidate_model_paths"] = [p for _, p in sorted(matches, key=lambda v: (-v[0], v[1]))[:8]]
    record["tests"] = [{"observable": "H0", "unit": "km/s/Mpc", "reported": v, "reported_error": e,
                        "nominal_model": H0, "residual_in_reported_errors": (v-H0)/e,
                        "model_source": "tools/rll_age_gate.py:H0", "status": "conditional_numeric_screen"}
                       for v,e in record["h0_mentions"]]
    for power in record.get("h_power_exponents", []):
        grid = []
        for z in (0, 0.5, 1, 2):
            matter_scale = (1+z)**3
            transition = 1 / (1 + math.exp((z-1)/0.3))
            nominal = H0 * math.sqrt(MATTER*matter_scale + 1-MATTER-0.02
                                     + 0.02*(transition+(1-transition)*matter_scale))
            grid.append({"z": z, "paper_H": H0*(1+z)**power, "nominal_RLL_H": nominal})
        record["tests"].append({"status": "formula_grid_comparison", "unit": "km/s/Mpc",
                                "assumption": "common H0; flat nominal RLL without radiation",
                                "paper_exponent": power, "grid": grid})
    record["status"] = "screened" if record["tests"] else "missing_executable_binding_or_measurement"
    record["claim_allowed"] = False


def fetch(url):
    with urllib.request.urlopen(url, timeout=35) as response:
        return response.read(8_000_000)


def record_bytes(record):
    return json.dumps(record, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def replace_record(key, candidate, records, history, bindings, model_commit):
    """Archive the complete previous row before a semantic change, not just its hash."""
    if key in records:
        previous = record_bytes(records[key])
        if previous == record_bytes(candidate):
            bindings[key] = model_commit
            return
        history.setdefault(key, []).append({
            "record_sha256": hashlib.sha256(previous).hexdigest(),
            "record": json.loads(previous),
            "model_commit": bindings.get(key),
        })
    records[key] = candidate
    bindings[key] = model_commit


def ingest(data, feed, records, history, bindings, models, model_commit):
    for item in ET.fromstring(data).iter():
        if item.tag.split('}')[-1] != 'item':
            continue
        fields = {n.tag.split('}')[-1]: ''.join(n.itertext()).strip() for n in item}
        key = fields.get('link')
        if key and fields.get('title'):
            candidate = dict(observation(fields['title'], fields.get('description', '')), feed=feed)
            evaluate(candidate, models)
            replace_record(key, candidate, records, history, bindings, model_commit)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--offline", action="store_true", help="Replay only pinned local inputs.")
    args = parser.parse_args()
    target = args.output or args.catalog
    if args.offline and (not args.output or target.resolve() == args.catalog.resolve()):
        parser.error("--offline requires a distinct --output")
    seed_path = Path("data/chronology/publication_seed.json")
    if target.resolve() == seed_path.resolve():
        parser.error("output must not replace the source seed")
    source_bytes = args.catalog.read_bytes()
    seed_bytes = seed_path.read_bytes()
    catalog = json.loads(source_bytes)
    seed = json.loads(seed_bytes)
    require_unpromoted(catalog)
    require_unpromoted(seed)
    records = catalog.setdefault("publication_crosses", {})
    history = catalog.setdefault("publication_cross_history", {})
    bindings = dict.fromkeys(records, catalog.get("cross_model_commit"))
    for url, row in seed.items():
        records.setdefault(url, row)
    paths = subprocess.check_output(["git","ls-files","src","data/pipelines","tools"],text=True).splitlines()
    models = [(p, tags(p)) for p in paths if p.endswith(('.py','.c','.h'))]
    model_commit = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    failures = []
    for feed in (() if args.offline else FEEDS):
        try:
            ingest(fetch(feed), feed, records, history, bindings, models, model_commit)
        except (OSError, ET.ParseError) as err:
            failures.append(feed)
            print(f"feed unavailable: {feed} ({type(err).__name__})", file=sys.stderr)
    if not args.offline and len(failures) == len(FEEDS):
        raise RuntimeError("all publication feeds unavailable")
    for key, record in list(records.items()):
        candidate = json.loads(record_bytes(record))
        evaluate(candidate, models)
        replace_record(key, candidate, records, history, bindings, model_commit)
    catalog["cross_model_commit"] = model_commit
    catalog["unavailable_feeds"] = None if args.offline else failures
    catalog["feed_status"] = "NOT_RUN_OFFLINE" if args.offline else ("PARTIAL" if failures else "FETCHED")
    catalog["claim_allowed"] = False
    catalog["catalog_input_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    catalog["publication_seed_sha256"] = hashlib.sha256(seed_bytes).hexdigest()
    write_json_atomic(target, catalog)


if __name__ == '__main__':
    main()
