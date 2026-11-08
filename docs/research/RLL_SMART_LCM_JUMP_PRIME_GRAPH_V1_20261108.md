# RLL — MMC por saltos e grafo de fatores primos · 2026-11-08

**Estado:** DRAFT/HOLD · matemática clássica; sem alegação de nova física, velocidade universal ou teorema original. Rota: 001_PONTEIRO/RLL_SMART_LCM_GRAPH_V1_CURRENT.md.

## SOURCE e anterioridade

Produtor: RLL. Referências imutadas em main: tools/rll_lcm_graph_benchmark_v1.py (72 casos anteriores, Euclides e grafo ingênuo), tools/rll_multibase_oracle_v1.py, docs/science/RLL_COMPENSATION_MULTIBASE_ANGULAR_V1.md. MB7-16 é hipótese testável anterior. Contrato: SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM.

## O quarto método

A projeção angular de n ciclos produz a fase 2π(t mod n)/n. Ao adicionar um novo ciclo n quando a condição anterior já tem período M, a próxima coincidência positiva satisfaz M*k ≡ 0 (mod n). O menor k é n/gcd(M,n); portanto M'=M*k. Isso cria uma aresta diretamente para o próximo evento, sem percorrer cada batida.

Exemplo (7,10,14): M=1 -> 7 -> 70 -> 70, ou MMC=70. Exemplo (7,35,50,70): M=1 -> 7 -> 35 -> 350 -> 350. Essa técnica usa o MDC de Euclides; é uma **representação de grafo de eventos**, não um algoritmo independente ou original.

A segunda opção é o semirreticulado de fatores primos: v_p(MMC)=max_i v_p(n_i). Dois produtores exatos de fatores: divisão experimental e tabela SPF (fator primo mínimo) reaproveitável.

## O que o teste local mostrou — 72 entradas idênticas

Local Linux x86-64, Python 3.13.5, mediana de lotes repetidos em nanosegundos/chamada, sem inferir desempenho em ARM ou outras CPUs.

| Método | Mediana sobre mesmos 72 casos |
|---|---:|
| Python math.lcm nativo | 154 ns |
| Euclides com math.gcd nativo | 328 ns |
| Grafo de salto com math.gcd nativo | 1008 ns |
| Euclides com gcd implementado em Python | 1229 ns |
| Grafo de salto com gcd implementado em Python | 1447 ns |
| Complemento de Euclides Python | 1399 ns |
| Fatores com SPF pré-calculado, quente | 3454 ns |
| Divisão de fatores sem SPF | 5175 ns |

**A comparação justa exige usar o mesmo backend de MDC.** O grafo de saltos não venceu Euclides. Em 17 casos pequenos, grafo sequencial = 38168 ns/chamada; salto = 979 ns (aproximadamente 39x melhor que percorrer estados), mas Euclides com MDC nativo = 334 ns e math.lcm = 109 ns.

- Cinco métodos, com controles adicionais de backend, retornaram o MMC exato para 72/72 casos.
- O grafo ingênuo anterior finalizou apenas 35/72 sob limite de 5000; os outros 37 têm estado NOT_RUN_CAP, não erro matemático.
- Grafo inteligente visitou 229 arestas de eventos somadas nos 72 casos, eliminando cap.
- SPF: tabela uint32 de 4.000.136 bytes (aprox. 3,81 MiB) e 112 ms para pré-calcular; esse custo **não** entra nos tempos quentes. Nesta carga, como o SPF já é mais lento que Euclides no estado quente, não há ponto de amortização medido.
- Local: 14/14 testes unittest, 350 tuplas aleatórias com semente fixa, 3721 pares exaustivos, primos, sinais, zero conhecido distinto de TOKEN_VAZIO e grandes semiprimos.
- O teste local isolado usou espelho de referência do Euclides RLL; essa cópia não é enviada no PR. A CI fará o teste contra o arquivo real no repositório, não se deve chamar os dois artefatos de byte-idênticos.

## Reproduzir e falsificar

Na raiz do repositório:
- python3 -m unittest discover -s tests -p test_rll_lcm_smart_graph_v1.py -v
- python3 tools/bench_rll_lcm_smart_graph_v1.py --quick --output artifacts/python-tests/rll_smart_lcm_ci.json --csv artifacts/python-tests/rll_smart_lcm_ci_cases.csv

A etapa escopada no workflow python-tests.yml executa antes do pytest geral. O restante dos gates permanece intacto. A suíte global poderá falhar de forma independente; jamais promover por causa de um PASS escopado.

H1 exatidão de saltos: passível de refutação por qualquer par incorreto, verificação limitada aos testes. H2 vantagem de desempenho contra Euclides com backend idêntico: não apoiada localmente. H3 ganho SPF após amortização: não apoiado neste corpus. H4 uso físico das fases: TOKEN_VAZIO e exige grandezas, unidades, modelo e observáveis.

Rollback: fechar PR ou reverter arquivos aditivos + passo isolado do CI. Sem mudança em física, likelihood, covariância ou parâmetros RLL.
