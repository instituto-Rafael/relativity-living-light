# ∆∅ → ΩΠμ — Formalização, anterioridade e limite de claim — V1

**Data:** 2026-10-04  
**Status:** RESEARCH_NOTE / PRIOR_ART_SCREEN_V1 / CLAIM_ALLOWED=false  
**Autor da gramática em avaliação:** Rafael Melo Reis  
**Regra:** SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM  
**Regra:** TOKEN_VAZIO ≠ 0 ≠ null ≠ "" ≠ false

## 1. Escopo

Este documento registra a gramática simbólico-operacional desenvolvida nesta sessão e a compara, de modo não exaustivo, com literatura localizada via alphaXiv. Ele **não** declara patenteabilidade, novidade jurídica, validade física ou prioridade absoluta. O que a triagem permite dizer é mais restrito: componentes isolados possuem anterioridade clara; a combinação específica abaixo permanece uma hipótese de composição autoral que exige busca de anterioridade mais ampla.

## 2. Gramática registrada

A cadeia de origem operacional é:

```text
∆∅ → ∅ → 0 → 1 → 2 → 3
```

Interpretação de trabalho:
- ∆∅: mudança detectável aplicada a um estado ainda não contabilizado;
- ∅: ausência/pré-condição ainda não convertida em zero operacional;
- 0: vazio contabilizado;
- 1: unidade operacional;
- 2: relação/oposição;
- 3: fechamento operacional.

A forma simbólica mantém distinção entre representação e redução:

```text
0001123 ≠ 123
red(0001123) = 123
```

Uma construção interna usada na gramática é:

```text
3 = 2 + 1_μ
3k = k(2 + 1_μ), k ∈ {1,2,3}
```

A família geométrica registrada é:

```text
r_n = r_0 (√3/2)^n
```

ou, com índice genérico:

```text
r_n = r_0 (√3/2)^{f(n)}
```

A escala/projeção é representada por:

```text
Ω →[Π] Π(Ω) →[Π_μ] μ
```

com:
- Ω: universo lógico total considerado;
- Π: família de operadores de projeção/permutação;
- μ: granularidade mínima da operação corrente.

A unidade recursiva é:

```text
U_k = (source, state, relations, evidence, gaps, routes, children)
U_k → {U_{k-1}^{(1)}, …, U_{k-1}^{(m)}} até U_0 = μ
```

Para projeções multidisciplinares:

```text
Π_{A→C} = Π_{B→C} ∘ Π_{A→B}
```

somente quando ambas as transformações estão definidas.

A dinâmica incremental é:

```text
S_{t+1} = S_t ⊕ ∆_t
```

e, com `S_0 = ∅`:

```text
S_n = ∅ ⊕ ⨁_{k=0}^{n-1} ∆_k
```

## 3. Proveniência como restrição de transformação

Uma projeção não apaga sua origem. Modelamos:

```text
Π(x) = (y, ρ)
```

onde `ρ` é a proveniência da transformação. Portanto a existência de `y` não promove automaticamente `x` ou `y` a evidência ou claim factual.

Invariantes:

```text
SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM
TOKEN_VAZIO ≠ 0/null/empty/false
IMPLEMENTED_UNTESTED ≠ PASS
```

TOKEN_VAZIO é usado como estado tipado quando uma origem, autoridade, evidência, alvo ou relação esperada ainda não está resolvida.

## 4. Objeto formal compacto

```text
R_{∆∅}^{ΩΠμ} = <∅, 0, 1, 2, 3, ∆, Π, Ω, μ, R, E, V, ρ>
```

onde:
- R = relações;
- E = evidência;
- V = TOKEN_VAZIO;
- ρ = proveniência.

Dinâmica:

```text
R_{t+1} = R_t ⊕ ∆_μ
```

sob projeções recursivas de Ω até μ.

## 5. Triagem de anterioridade via alphaXiv

### 5.1 Proveniência e factualidade — anterioridade forte

**Fabio Vitali; Valentina Pasqual. _Provenance-Enhanced Statements in Knowledge Graphs_. arXiv:2606.15246 (2026).**

O trabalho distingue a verdade de uma atribuição da verdade do conteúdo atribuído, modela declarações com proveniência e discute compromisso factual/epistêmico. Também revisa RDF reification, named graphs, RDF-star, nanopublicações e micropublicações. Portanto, a separação conceitual entre fonte, afirmação, proveniência e factualidade **não é novidade isolada**.

Referência: https://arxiv.org/abs/2606.15246

### 5.2 Memória em camadas, fontes remotas e proveniência — anterioridade forte

**Pengyuan Zhu; Ming Wu. _Agent Zero Memory: Provenance-Aware Long-Term Memory for LLM Agents_. arXiv:2608.29606 (2026).**

O trabalho mantém três memórias em paralelo (timeline de eventos, grafo entidade-evento e memória documental hierárquica), conserva fontes brutas, associa itens derivados a origem/timestamp/evidence pointer e usa roteamento de fontes. Mostra construção incremental sobre conversas, arquivos e conectores. Portanto, memória remota em camadas, proveniência por item e contexto reconstruível **não são novidade isolada**.

Referência: https://arxiv.org/abs/2608.29606

### 5.3 Event sourcing, append-only, projeção e replay — anterioridade forte

**Elzo Brito dos Santos Filho. _ESAA: Event Sourcing for Autonomous Agents in LLM-Based Software Engineering_. arXiv:2602.23193 (2026).**

O trabalho usa log append-only, estado materializado por projeção, replay determinístico, hashing e separação entre intenção probabilística do agente e execução determinística do orquestrador. Portanto, a ideia geral de `estado atual = projeção de deltas/eventos` e replay auditável **não é novidade isolada**.

Referência: https://arxiv.org/abs/2602.23193

## 6. O que permanece candidato a composição autoral

Nesta triagem de três trabalhos, **não foi encontrada uma correspondência exata** para a gramática completa abaixo:

```text
∆∅ → ∅^n0^n → 0001123 → 123 → 369 → Π → ΩΠ → Πμ → ∆_μ → TOKEN_VAZIO/EVIDENCE
```

Nem foi encontrada, nesses três trabalhos, a combinação explícita de:
1. vazio tipado como estado operacional não colapsável em zero/null/empty/false;
2. recursão da mesma gramática entre escalas de corpus/domínio até μ;
3. operadores de projeção multidisciplinar com preservação obrigatória de proveniência;
4. ligação da gramática simbólica com um motor incremental auditável.

Isso é apenas **ausência de correspondência na amostra consultada**, não prova de novidade universal.

## 7. Classificação epistemológica

| Elemento | Estado |
|---|---|
| Event sourcing / append-only / replay | KNOWN_PRIOR_ART |
| Knowledge graph + provenance | KNOWN_PRIOR_ART |
| Layered long-term memory + source routing | KNOWN_PRIOR_ART |
| SOURCE/EVIDENCE/CLAIM separation generally | KNOWN_PRIOR_ART |
| Exact ∆∅ → ΩΠμ grammar | CANDIDATE_AUTHORIAL_COMPOSITION / NEEDS_BROADER_SEARCH |
| TOKEN_VAZIO exact operational semantics | CANDIDATE_AUTHORIAL_COMPOSITION / NEEDS_BROADER_SEARCH |
| Recursive cross-disciplinary projection grammar | CANDIDATE_AUTHORIAL_COMPOSITION / NEEDS_BROADER_SEARCH |

## 8. Claim gate

`claim_allowed=false`.

Nenhuma das seguintes frases está autorizada por este documento:
- “é uma nova lei da física”;
- “não existe nada semelhante na literatura”;
- “é patenteável”;
- “é matematicamente provado como teoria universal”.

O que está autorizado:
- existe uma gramática definida e codificável;
- seus componentes conhecidos foram separados de sua composição específica;
- a implementação pode ser testada como protocolo computacional;
- uma busca de anterioridade mais ampla pode continuar sobre o objeto formalizado.

## 9. Próximos testes

1. validar leis de composição de Π;
2. definir condições de identidade/equivalência entre projeções;
3. testar idempotência de ∆_μ;
4. definir quando TOKEN_VAZIO abre, atualiza e fecha;
5. testar replay e reconstrução;
6. construir matriz de anterioridade ampliada;
7. separar claramente hipótese física, matemática, computacional e simbólica.

R3 = `<F_ok: gramática formalizada + anterioridade inicial separada; F_gap: busca não exaustiva e sem prova de novidade jurídica/física; F_next: testes formais + prior-art ampliado + evidência reprodutível>`.
