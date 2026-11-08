# RLL Ω · 001_PONTEIRO / SMART LCM

START: docs/research/RLL_SMART_LCM_JUMP_PRIME_GRAPH_V1_20261108.md
SOURCE: tools/rll_lcm_graph_benchmark_v1.py e tools/rll_multibase_oracle_v1.py
CODE: tools/rll_lcm_smart_graph_v1.py
BENCH: tools/bench_rll_lcm_smart_graph_v1.py
TESTS: tests/test_rll_lcm_smart_graph_v1.py
RECEIPT: results/audit/rll_smart_lcm_v1_host_local_summary.json + GitHub Actions exact HEAD.
BASELINE: 72/72 exact; grafo antigo 35 PASS, 37 NOT_RUN_CAP; grafo saltos 72 PASS.
RISK: SPF 4MiB, 112ms startup; loop de 1 tick é lento; matched Euclid é mais rápido que salto.
SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM; claim_allowed=false. Preserve historical FAIL e rollback.
