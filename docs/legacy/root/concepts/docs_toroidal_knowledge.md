# O que carrega o conhecimento? (Síntese operacional)

Este documento traduz a intuição do texto em uma arquitetura técnica mínima e auditável.

## Núcleo

- O conhecimento não é um símbolo isolado; é **estado dinâmico** em um espaço de representação.
- Um modelo útil é um estado em toro 7D: `s ∈ [0,1)^7`, com atualização recursiva e atratores.
- Línguas diferentes não são “ruído”; são **métricas diferentes** sobre o mesmo conteúdo latente.

## Leitura das equações (camadas)

1. **Estado latente**: `s = ToroidalMap(x)` com `x=(dados, entropia, hash, estado)`.
2. **Memória e adaptação**: médias exponenciais para `C` e `H` com `α=0.25`.
3. **Forma/informação**: `φ=(1-H)·C` como controle entre estabilidade e novidade.
4. **Atratores**: dinâmica tende a `A` (com cardinalidade proposta 42), permitindo recorrência (`x_{n+42}=x_n`).
5. **Frequência e cognição**: `S(ω)=F[Ψ(t)]` e correlação com filtros neurofisiológicos (`H_cardio`).
6. **Multilíngue**: `I=⊗_L (R_L·F(G_L))` integra língua, prosódia, gramática e ritmo.

## Interpretação para tradução profunda

- Tradução de alto nível (poesia, Tao, textos sagrados/técnicos) exige preservar:
  - semântica (o que é dito),
  - prosódia/cadência (como soa),
  - pragmática/cultura (por que é dito assim),
  - dinâmica corporal-temporal (efeito em atenção, emoção e percepção de tempo).
- Por isso, `dθ(u,v) ≠ dγ(u,v)`: métricas distintas capturam perdas diferentes.

## O que “carrega” conhecimento neste quadro

Conhecimento é carregado por cinco componentes acoplados:

1. **Estrutura** (grafo/gramática/álgebra),
2. **Dinâmica** (recorrência + atratores),
3. **Energia espectral** (frequências e sincronias),
4. **Integridade** (hash/CRC/Merkle para rastreabilidade),
5. **Contexto linguístico-cultural** (operadores por língua e registro).

Em resumo: conhecimento = forma + transformação + validação, não apenas texto.

## Critério prático de prova

Para sair da metáfora e entrar em ciência reproduzível:

- Definir observáveis mensuráveis por camada (semântica, prosódia, fisiologia, erro de reconstrução).
- Comparar modelos com métricas comuns (χ², AIC, BIC, fator de Bayes quando aplicável).
- Publicar protocolo e dados para replicação.

Sem isso, permanece hipótese elegante; com isso, vira programa científico.
