# RLL Ω — MMC: ciclos modulares × Euclides × complementação

**Estado:** experimento matemático reproduzível, Python 3 stdlib, sem rede/segredos. Não testa cosmologia, órbita ou ARMv7 físico. claim_allowed=false.

## Hipóteses

**H1:** grafo explícito de resíduos modulares encontra o MMC mais rapidamente que Euclides para o mesmo corpus de inteiros. **H2:** empréstimo por complemento acelera a etapa MDC.

**Teorema independente da medição:** para inteiros positivos n_i, S(t)=(t mod n_1,...,t mod n_k) retorna ao vetor zero no menor instante positivo t=mmc(n_1,...,n_k). Em símbolos geométricos, cada fase é 2π(t mod n)/n; π e raízes irracionais para raios não reduzem o número de passos inteiros.

## Valores de referência

- mmc(7,10,14) = 70.
- mmc(7,35,50,70) = 350.
- 7×70 = (7+3)×70−3×70 = 490.

## Resultados locais medidos (Linux x86-64, Python 3.13.5)

- **72/72** casos exatos para Euclides e complemento, comparados com math.lcm.
- Grafo exato para **35/35** casos que retornaram dentro de 5.000 passos; **37 NOT_RUN_CAP**, nunca tratados como FAIL ou PASS.
- **13/13** testes adversariais unittest PASS local.
- Complemento repetido ingênuo no MDC(1.000.004,1.000.003) atingiu teto de 5.000 passos, apesar da identidade algébrica ser correta.

### Tempo comparável sobre os mesmos 15 casos pequenos

| Método | Mediana por chamada |
|---|---:|
| math.lcm nativo CPython (C) | 116 ns |
| Euclides Python | 1.123 ns |
| Complemento uma vez + Euclides Python | 1.283 ns |
| Grafo de resíduos Python | 48.195 ns |

O grafo puro foi cerca de 42,9× mais lento que Euclides Python nessa implementação e amostra. A medição não refuta **todas** as estratégias possíveis de grafos, CRT/fatoração, nem permite comparar hardware físico. A implementação C de math.lcm é registrada separadamente.

### Reprodutibilidade

- Casos: 6 exemplos, 7 fatores comuns, 5 grupos de primos, 5 potências, 7 sinais/zero e 42 casos pseudoaleatórios (seed 20261108); total 72.
- Benchmark: time.perf_counter_ns; 11 amostras×250 chamadas por caso para métodos rápidos; 7 amostras×15 chamadas para grafo de 15 casos pequenos. Valores sujeitos a ruído térmico/escalonamento.
- Código: tools/rll_lcm_graph_benchmark_v1.py
- Testes: tests/test_rll_lcm_graph_benchmark_v1.py
- Resultado do host: results/audit/rll_lcm_graph_benchmark_v1_hosted_summary.json.
- Antecedentes: tools/rll_multibase_oracle_v1.py, docs/science/RLL_COMPENSATION_MULTIBASE_ANGULAR_V1.md, data/contracts/rll_multibase_complement_falsification.v1.json.

Na raiz RLL:

    python3 -m unittest discover -s tests -p test_rll_lcm_graph_benchmark_v1.py -v
    python3 tools/rll_lcm_graph_benchmark_v1.py --no-timing --output /tmp/mmc_sanity.json
    python3 tools/rll_lcm_graph_benchmark_v1.py --output /tmp/mmc_timed.json

A PR no GitHub aciona os workflows existentes, particularmente .github/workflows/python-tests.yml. Nenhum workflow, threshold, código de cosmologia ou proteção é alterado. CI só é PASS quando GitHub confirmar o HEAD, não porque houve teste local.

SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM. A prova de correção é da aritmética clássica; os tempos são observações do host. claim_allowed=false para extrapolações físicas. Reversível fechando a PR DRAFT sem merge.
