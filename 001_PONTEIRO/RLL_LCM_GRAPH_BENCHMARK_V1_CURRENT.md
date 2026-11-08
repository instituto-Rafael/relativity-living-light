# 001_PONTEIRO — RLL MMC grafo modular / Euclides

SOURCE: docs/research/RLL_LCM_GRAPH_EUCLID_BENCHMARK_V1.md
ALGORITMOS: tools/rll_lcm_graph_benchmark_v1.py
TESTES: tests/test_rll_lcm_graph_benchmark_v1.py
RECEIPT LOCAL: results/audit/rll_lcm_graph_benchmark_v1_hosted_summary.json

Controle: mmc(7,10,14)=70 e mmc(7,35,50,70)=350.
72/72 Euclides e complemento exatos; grafo 35 PASS_SCOPED/37 NOT_RUN_CAP por limite 5000; 13 unittest PASS local.
Hipótese de velocidade do grafo explícito NÃO APOIADA pelo benchmark, ~42,9× mais lento no mesmo subconjunto.
Sem modificação de workflow ou ciência RLL. claim_allowed=false, DRAFT/HOLD.
