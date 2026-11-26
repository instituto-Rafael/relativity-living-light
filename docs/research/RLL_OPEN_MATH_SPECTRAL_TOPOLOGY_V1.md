# RLL Ω — Pesquisa matemática: espectro de primos e homologia finita V1

**Estado:** EXPERIMENTO_FINITO / NÃO TEORIA NOVA. `claim_allowed=false`, `publication_effect=NONE`.

**Fonte e produtor:** programa de sistemas modulares M=54.600 no repositório de pesquisa `rafaelmeloreisnovo/papers`, e Programa Geométrico Ω7. Este RLL executa apenas provas computacionais de invariantes finitos e uma exploração de nulos estatísticos. Não converte esses métodos em soluções para Riemann, Navier–Stokes, Yang–Mills ou outros problemas abertos.

## Pesquisa A — resíduo de primos: hipótese e falsificador

- **Universo amostral:** inteiros `2..N` coprimos com 54.600, com `N=10000` por padrão; primalidade por crivo exato na faixa.
- **Nulo condicionado H0:** dada a contagem de primos observada em cada classe invertível mod 70, seus rótulos são permutáveis entre os candidatos daquela classe. A projeção mod 350 deriva dos *mesmos candidatos* e conserva compatibilidade CRT.
- **Alternativa exploratória H1:** a contagem fina mod 350 produz potência espectral além daquela sob esse nulo **específico**. É proibido extrapolar a uma teoria assintótica dos primos.
- **Estatística fixa:** máximo da potência de Fourier *aditiva* sobre as frequências `1..16` em `Z/350Z`, normalizado pelo total esperado de primos. Não é transformada por caracteres de Dirichlet.
- **Controle de múltiplas frequências:** a permutação reavalia o máximo entre todas as 16 frequências, não cada uma isoladamente.
- **Distribuição nula:** `127` amostras determinísticas pelo gerador Python `Random(seed=20261121)`, sem reposição por grupo, preservando marginais mod 70. Estimador exploratório `p=(1+excedências)/(1+127)`; resolução mínima `1/128`.
- **Falsificadores:** estatística compatível com nulo; desaparecimento sob controles de condutor/corridas de primos; ausência de reprodução fora da amostra.
- **Lacuna:** permutação não preserva todos os caracteres nem a dependência aritmética de primos; sem *holdout* ou poder estatístico, `significance_claim=BLOCKED`.

## Pesquisa B — topo de triângulos: lema computacional de homologia

- **Objetos:** superfície da esfera via quatro faces do tetraedro; toro por grade `n×n` com identificações periódicas e duas faces triangulares por célula (`3<=n<=8`).
- **Operador:** matrizes de bordo `∂1`, `∂2` sobre `F2`, implementadas por bitsets; verifica `∂1∂2=0` sem tolerância numérica.
- **Invariantes:** números de Betti `b0=V-rank(∂1)`, `b1=E-rank(∂1)-rank(∂2)`, `b2=F-rank(∂2)`; Euler `χ=V-E+F=b0-b1+b2`.
- **Controles positivos:** esfera `(b0,b1,b2)=(1,0,1)`, `χ=2`; toro `(1,2,1)`, `χ=0`.
- **Controle negativo:** remover uma única face do toro produz superfície perfurada `(1,2,0)`, `χ=-1`.
- **Falsificadores:** qualquer falha de composição de bordo, fórmula Euler, erro de fecho ou divergência de ranks exatos em `n=3,4,5`.
- **Limite:** teoremas de homologia dos modelos são clássicos; este código verifica exemplos finitos, não prova a generalidade da classificação de superfícies nem a singularidade do formalismo Ω7.

## Contratos, execução e receipts

`tools/math/open_math_spectral_topology_v1.py`, `tests/test_open_math_spectral_topology_v1.py`, `.github/workflows/omega-math-explorer.yml`. Python 3.11 stdlib; execução offline e sintética. Output: `artifacts/omega-math-explorer/open_math_v1/{report.json,receipt.md}`, com hash real dos bytes e do produtor; diretório imutável por execução.

A prova de CI só existe após confirmação de `run_id`/HEAD. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. `TOKEN_VAZIO` não equivale a zero. Nenhuma modificação de `main`, rulesets, ACL ou publicação científica é autorizada por este programa.

**Próximo gate:** controles de condutor, modelos de corridas de primos, *holdout*, comparação de fórmulas conhecidas e replicação independente; conexão com problemas abertos continua conjectural.
