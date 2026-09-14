from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

TOKEN_VAZIO = "TOKEN_VAZIO"
SCHEMA_VERSION = "rll.orcid_vector.v1"
VECTOR_MODEL = "rll-hash32-v1"
VECTOR_DIMENSIONS = 32
DEFAULT_DB = Path("artifacts/orcid_rll/orcid_rll.sqlite3")
ORCID_API = "https://pub.orcid.org/v3.0"
CROSSREF_API = "https://api.crossref.org/works"
DATACITE_API = "https://api.datacite.org/dois"
OPENALEX_API = "https://api.openalex.org/works"
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
TOKENS = re.compile(r"[a-z0-9]+", re.I)

KEYWORDS: dict[str, tuple[str, ...]] = {
    "mathematics": ("algebra", "analysis", "calculus", "equation", "geometry", "mathematics", "matrix", "probability", "statistics", "tensor", "topology", "matematica", "matriz"),
    "physics": ("cosmology", "energy", "field theory", "gravity", "particle", "physics", "relativity", "spacetime", "wave", "cosmologia", "fisica", "gravidade", "relatividade"),
    "physics.classical": ("classical mechanics", "fluid dynamics", "hamiltonian", "lagrangian", "mechanics", "newtonian", "optics", "thermodynamics", "mecanica classica", "termodinamica"),
    "physics.quantum": ("entanglement", "hilbert", "quantum", "qubit", "schrodinger", "spin", "superposition", "emaranhamento", "quantico", "quantica"),
    "chemistry": ("catalysis", "chemical", "chemistry", "compound", "electrochemistry", "molecule", "polymer", "reaction", "quimica", "molecula", "reacao"),
    "biology": ("bioinformatics", "biological", "biology", "cell", "ecology", "evolution", "gene", "genome", "microbiology", "protein", "biologia", "celula", "evolucao"),
    "physiology": ("cardiac", "cardiovascular", "endocrine", "exercise physiology", "metabolism", "muscle", "neural", "neuroscience", "physiology", "respiratory", "fisiologia", "metabolismo", "musculo"),
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def normalize(value: str | None) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(c for c in value if not unicodedata.combining(c)).casefold()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).strip().lower()
    return value or None


def canonicalize_orcid(value: str) -> str:
    value = re.sub(r"^https?://orcid\.org/", "", value.strip(), flags=re.I).upper()
    if not ORCID_RE.fullmatch(value):
        raise ValueError(f"ORCID iD malformado: {value!r}")
    digits = value.replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    check = (12 - total % 11) % 11
    expected = "X" if check == 10 else str(check)
    if digits[-1] != expected:
        raise ValueError(f"Checksum ORCID inválido: {value}")
    return value


def classify_disciplines(text: str) -> tuple[list[str], dict[str, float]]:
    clean = normalize(text)
    scores: dict[str, float] = {}
    for label, words in KEYWORDS.items():
        hits = sum(1 for word in words if normalize(word) in clean)
        if hits:
            scores[label] = round(min(1.0, hits / 3), 6)
    if any(k.startswith("physics.") for k in scores):
        scores["physics"] = max(scores.get("physics", 0.0), 0.5)
    labels = sorted(scores) or ["unclassified"]
    return labels, scores


def hash_embedding(text: str, dimensions: int = VECTOR_DIMENSIONS) -> list[float]:
    vector = [0.0] * dimensions
    for token in TOKENS.findall(normalize(text)):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[index] += sign * (1.0 + math.log1p(len(token)))
    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm for v in vector] if norm else vector


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _value(node: Any) -> str | None:
    if isinstance(node, str):
        return node
    if isinstance(node, Mapping) and isinstance(node.get("value"), str):
        return node["value"]
    return None


def _year(node: Any) -> int | None:
    if isinstance(node, Mapping):
        node = node.get("year")
    node = _value(node) or node
    try:
        return int(node) if node is not None else None
    except (TypeError, ValueError):
        return None


def iter_orcid_works(record: Mapping[str, Any]) -> Iterator[Mapping[str, Any]]:
    activities = record.get("activities-summary") or record.get("activities_summary") or {}
    candidates = [activities.get("works") if isinstance(activities, Mapping) else None, record.get("works"), record if "group" in record else None]
    for works in candidates:
        if not isinstance(works, Mapping):
            continue
        for group in works.get("group") or []:
            if not isinstance(group, Mapping):
                continue
            for item in group.get("work-summary") or group.get("work_summary") or []:
                if isinstance(item, Mapping):
                    yield item


def parse_orcid_summary(item: Mapping[str, Any], owner: str) -> dict[str, Any]:
    ids = item.get("external-ids") or item.get("external_ids") or {}
    external: dict[str, str] = {}
    for entry in (ids.get("external-id") or ids.get("external_id") or []) if isinstance(ids, Mapping) else []:
        if not isinstance(entry, Mapping):
            continue
        kind = entry.get("external-id-type") or entry.get("external_id_type")
        value = entry.get("external-id-value") or entry.get("external_id_value")
        if isinstance(kind, str) and isinstance(value, str):
            external[kind.casefold()] = value
    title_node = item.get("title") or {}
    title = _value(title_node.get("title")) if isinstance(title_node, Mapping) else None
    doi = normalize_doi(external.get("doi"))
    put = item.get("put-code") or item.get("put_code")
    logical = f"doi:{doi}" if doi else f"orcid:{owner}:put:{put}"
    journal = _value(item.get("journal-title") or item.get("journal_title"))
    url = _value(item.get("url"))
    return {
        "logical_id": logical,
        "owner_orcid": owner,
        "title": title or TOKEN_VAZIO,
        "abstract": None,
        "doi": doi,
        "publication_year": _year(item.get("publication-date") or item.get("publication_date")),
        "work_type": item.get("type") if isinstance(item.get("type"), str) else None,
        "journal": journal,
        "url": url,
        "metadata_state": "ORCID_INGESTED" if title else TOKEN_VAZIO,
        "claim_allowed": False,
    }


def parse_crossref(payload: Mapping[str, Any]) -> dict[str, Any]:
    message = payload.get("message") if isinstance(payload.get("message"), Mapping) else payload
    titles = message.get("title") or []
    title = titles[0] if isinstance(titles, list) and titles else titles if isinstance(titles, str) else None
    date = message.get("published") or message.get("published-print") or message.get("issued") or {}
    parts = date.get("date-parts") if isinstance(date, Mapping) else None
    year = parts[0][0] if isinstance(parts, list) and parts and parts[0] else None
    authors = []
    for author in message.get("author") or []:
        if not isinstance(author, Mapping):
            continue
        raw_orcid = author.get("ORCID") or author.get("orcid")
        try:
            oid = canonicalize_orcid(raw_orcid) if isinstance(raw_orcid, str) else None
        except ValueError:
            oid = None
        authors.append({"given": author.get("given"), "family": author.get("family"), "orcid": oid})
    containers = message.get("container-title") or []
    return {
        "provider_record_id": normalize_doi(message.get("DOI")) or sha(canonical_json(message)),
        "title": title,
        "abstract": message.get("abstract"),
        "doi": normalize_doi(message.get("DOI")),
        "publication_year": int(year) if year else None,
        "work_type": message.get("type"),
        "journal": containers[0] if isinstance(containers, list) and containers else None,
        "url": message.get("URL"),
        "authors": authors,
        "is_retracted": False,
    }


def parse_datacite(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
    attributes = data.get("attributes") if isinstance(data.get("attributes"), Mapping) else data
    titles = attributes.get("titles") or []
    title = titles[0].get("title") if titles and isinstance(titles[0], Mapping) else None
    descriptions = attributes.get("descriptions") or []
    abstract = next((item.get("description") for item in descriptions if isinstance(item, Mapping) and item.get("descriptionType") == "Abstract"), None)
    creators = []
    for creator in attributes.get("creators") or []:
        if not isinstance(creator, Mapping):
            continue
        oid = None
        for identifier in creator.get("nameIdentifiers") or []:
            if not isinstance(identifier, Mapping):
                continue
            if str(identifier.get("nameIdentifierScheme") or "").casefold() == "orcid":
                raw = identifier.get("nameIdentifier")
                try:
                    oid = canonicalize_orcid(raw) if isinstance(raw, str) else None
                except ValueError:
                    oid = None
        creators.append({"name": creator.get("name"), "orcid": oid})
    types = attributes.get("types") or {}
    return {
        "provider_record_id": str(data.get("id") or attributes.get("doi") or sha(canonical_json(payload))),
        "title": title,
        "abstract": abstract,
        "doi": normalize_doi(attributes.get("doi")),
        "publication_year": attributes.get("publicationYear"),
        "work_type": types.get("resourceTypeGeneral") if isinstance(types, Mapping) else None,
        "journal": attributes.get("publisher"),
        "url": attributes.get("url"),
        "authors": creators,
        "is_retracted": False,
    }


def _openalex_abstract(index: Any) -> str | None:
    if not isinstance(index, Mapping):
        return None
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        if isinstance(word, str) and isinstance(positions, list):
            words.extend((int(pos), word) for pos in positions)
    return " ".join(word for _, word in sorted(words)) or None


def parse_openalex(payload: Mapping[str, Any]) -> dict[str, Any]:
    doi = normalize_doi((payload.get("ids") or {}).get("doi") if isinstance(payload.get("ids"), Mapping) else payload.get("doi"))
    authors = []
    for authorship in payload.get("authorships") or []:
        author = authorship.get("author") if isinstance(authorship, Mapping) else None
        raw = author.get("orcid") if isinstance(author, Mapping) else None
        try:
            oid = canonicalize_orcid(raw) if isinstance(raw, str) else None
        except ValueError:
            oid = None
        authors.append({"name": author.get("display_name") if isinstance(author, Mapping) else None, "orcid": oid})
    location = payload.get("primary_location") or {}
    source = location.get("source") if isinstance(location, Mapping) else None
    return {
        "provider_record_id": str(payload.get("id") or doi or sha(canonical_json(payload))),
        "title": payload.get("display_name") or payload.get("title"),
        "abstract": _openalex_abstract(payload.get("abstract_inverted_index")),
        "doi": doi,
        "publication_year": payload.get("publication_year"),
        "work_type": payload.get("type"),
        "journal": source.get("display_name") if isinstance(source, Mapping) else None,
        "url": location.get("landing_page_url") if isinstance(location, Mapping) else None,
        "authors": authors,
        "is_retracted": bool(payload.get("is_retracted")),
    }


@dataclass(frozen=True)
class ValidationResult:
    state: str
    score: float
    details: dict[str, Any]


def validate_metadata(base: Mapping[str, Any], enriched: Mapping[str, Any], owner: str) -> ValidationResult:
    base_doi, new_doi = normalize_doi(base.get("doi")), normalize_doi(enriched.get("doi"))
    doi_exact = bool(base_doi and new_doi and base_doi == new_doi)
    title_score = SequenceMatcher(a=normalize(str(base.get("title") or "")), b=normalize(str(enriched.get("title") or ""))).ratio()
    by, ny = base.get("publication_year"), enriched.get("publication_year")
    year_exact = bool(by and ny and int(by) == int(ny))
    owner_match = owner in {a.get("orcid") for a in enriched.get("authors") or [] if isinstance(a, Mapping)}
    score = round(min(1.0, (0.45 if doi_exact else 0) + 0.30 * title_score + (0.10 if year_exact else 0) + (0.15 if owner_match else 0)), 6)
    conflicts = []
    if base_doi and new_doi and base_doi != new_doi:
        conflicts.append("DOI_MISMATCH")
    if base.get("title") not in (None, "", TOKEN_VAZIO) and enriched.get("title") and title_score < 0.55:
        conflicts.append("TITLE_MISMATCH")
    if by and ny and abs(int(by) - int(ny)) > 1:
        conflicts.append("YEAR_MISMATCH")
    if enriched.get("is_retracted"):
        state = "FLAGGED_RETRACTION"
    elif conflicts:
        state = "METADATA_CONFLICT"
    elif score >= 0.78:
        state = "VERIFIED_METADATA"
    elif score > 0:
        state = "PARTIAL_METADATA"
    else:
        state = TOKEN_VAZIO
    return ValidationResult(state, score, {"doi_exact": doi_exact, "title_similarity": round(title_score, 6), "year_exact": year_exact, "owner_orcid_match": owner_match, "is_retracted": bool(enriched.get("is_retracted")), "conflicts": conflicts})
