---
layout: default
title: Research fragments
---

{% assign graph = site.data.research_graph %}

<p class="boundary"><strong>Claim gate:</strong> this page displays research candidates and provenance only. The package state is <code>{{ graph.state | escape }}</code>; <code>claim_allowed={{ graph.claim_allowed }}</code>.</p>

## Build receipt

- Repository revision: <code>{{ graph.receipt.revision | escape }}</code>
- Workflow run: <code>{{ graph.receipt.run_id | escape }}</code>
- Source digests: relation graph <code>{{ graph.receipt.source_sha256.relation_graph | escape }}</code>; package <code>{{ graph.receipt.source_sha256.package | escape }}</code>; bibliography <code>{{ graph.receipt.source_sha256.bibliography | escape }}</code>.
- Raw snapshots for the curated bibliography are not stored in this repository; their source digest is <code>{{ graph.bibliography_source_digest | escape }}</code>.

## Bibliographic anchors

{% for paper in graph.bibliography %}
<article class="card">
  <h3><a href="{{ paper.arxiv_url | escape }}">{{ paper.title | escape }}</a></h3>
  <p>{{ paper.authors | join: ", " | escape }} · {{ paper.arxiv_version | escape }} · {{ paper.journal_reference | escape }}</p>
  <p>arXiv: <a href="{{ paper.arxiv_url | escape }}">{{ paper.work_id | escape }}</a> · arXiv DOI: <a href="https://doi.org/{{ paper.arxiv_doi | escape }}">{{ paper.arxiv_doi | escape }}</a>{% if paper.related_doi %} · journal DOI: <a href="https://doi.org/{{ paper.related_doi | escape }}">{{ paper.related_doi | escape }}</a>{% endif %}</p>
  <p>Role: <code>{{ paper.relation_role | escape }}</code>. Metadata state: <code>{{ paper.metadata_state | escape }}</code>. This citation provides context, not validation of RLL.</p>
</article>
{% endfor %}

## Current relation graph

<p>Status: <code>{{ graph.status | escape }}</code>. {{ graph.boundary | escape }}</p>

### Nodes

<ul>
{% for node in graph.nodes %}
  <li><code>{{ node.id | escape }}</code> — {{ node.kind | escape }}</li>
{% endfor %}
</ul>

### Candidate edges

<table>
  <thead><tr><th>From</th><th>Relation</th><th>To</th><th>Bibliographic anchors</th><th>Review state</th></tr></thead>
  <tbody>
  {% for edge in graph.edges %}
    <tr>
      <td><code>{{ edge.from | escape }}</code></td>
      <td><code>{{ edge.edge_type | escape }}</code></td>
      <td><code>{{ edge.to | escape }}</code></td>
      <td>{% for work_id in edge.evidence_work_ids %}<span>{{ work_id | escape }}{% unless forloop.last %}, {% endunless %}</span>{% else %}TOKEN_VAZIO_EDGE_CITATION{% endfor %}</td>
      <td><code>{{ edge.review_state | escape }}</code></td>
    </tr>
  {% endfor %}
  </tbody>
</table>

{% assign incoming = graph.candidate_intake %}
{% if incoming %}
## New arXiv intake candidate

<article class="card">
  <h3><a href="{{ incoming.source_locator | escape }}">{{ incoming.title | escape }}</a></h3>
  <p>{{ incoming.authors | join: ", " | escape }}</p>
  <p>Source response SHA-256: <code>{{ incoming.source_sha256 | escape }}</code>. Retrieved at <code>{{ incoming.retrieved_at | escape }}</code>.</p>
  <p>Metadata state: <code>{{ incoming.metadata_evidence_state | escape }}</code>. Claim gate: <code>claim_allowed={{ incoming.claim_allowed }}</code>.</p>
  <p>{{ incoming.abstract | escape | newline_to_br }}</p>
  {% if incoming.candidate_relations.size > 0 %}
  <h4>Human-declared relation candidates</h4>
  <ul>{% for edge in incoming.candidate_relations %}<li><code>{{ edge.from | escape }}</code> → <code>{{ edge.to | escape }}</code>: {{ edge.relation_note | escape }} <strong>{{ edge.review_state | escape }}</strong></li>{% endfor %}</ul>
  {% else %}
  <p>No relation edge was asserted. Add a target and short note in a later manual review to create a candidate edge.</p>
  {% endif %}
</article>
{% endif %}

## Boundary

Researcher names from the arXiv record are metadata strings. The page does not merge people by name, infer affiliations, send messages, or promote an edge to evidence. Relation candidates remain pending until a source-level argument, independent test, baseline, and contradiction check are recorded.
