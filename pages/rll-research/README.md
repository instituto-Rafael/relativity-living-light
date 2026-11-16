# RLL Research Fragments Jekyll source

This isolated Jekyll source is built by the academic-relation workflow into a downloadable preview artifact.

The workflow does not deploy this directory to GitHub Pages. It uses read-only repository permissions, stores preview and intake receipts as workflow artifacts, and leaves claim promotion behind human review.

`_data/research_graph.json` is generated during the build from the canonical relation graph, package, curated bibliography, source-file digests, and (when requested) one arXiv intake candidate. It is not committed as a second source of truth.
