"""Match incoming publication metadata against the current producer's tracked model paths."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
from tools.rll_age_gate import MATTER
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

from tools.rll_age_gate import H0

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


def ingest(data, feed, records):
    for item in ET.fromstring(data).iter():
        if item.tag.split('}')[-1] != 'item':
            continue
        fields = {n.tag.split('}')[-1]: ''.join(n.itertext()).strip() for n in item}
        key = fields.get('link')
        if key and fields.get('title'):
            records[key] = dict(observation(fields['title'], fields.get('description', '')), feed=feed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--offline", action="store_true", help="Replay only pinned local inputs.")
    args = parser.parse_args()
    target = args.output or args.catalog
    if args.offline and (not args.output or target.resolve() == args.catalog.resolve()):
        parser.error("--offline requires a distinct --output")
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    records = catalog.setdefault("publication_crosses", {})
    seed = json.loads(Path("data/chronology/publication_seed.json").read_text())
    for url, row in seed.items():
        records.setdefault(url, row)
    failures = []
    for feed in (() if args.offline else FEEDS):
        try:
            ingest(fetch(feed), feed, records)
        except (OSError, ET.ParseError) as err:
            failures.append(feed)
            print(f"feed unavailable: {feed} ({type(err).__name__})", file=sys.stderr)
    if not args.offline and len(failures) == len(FEEDS):
        raise RuntimeError("all publication feeds unavailable")
    paths = subprocess.check_output(["git","ls-files","src","data/pipelines","tools"],text=True).splitlines()
    models = [(p, tags(p)) for p in paths if p.endswith(('.py','.c','.h'))]
    for record in records.values():
        evaluate(record, models)
    catalog["cross_model_commit"] = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    catalog["unavailable_feeds"] = None if args.offline else failures
    catalog["feed_status"] = "NOT_RUN_OFFLINE" if args.offline else ("PARTIAL" if failures else "FETCHED")
    catalog["claim_allowed"] = False
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(target)


if __name__ == '__main__':
    main()
