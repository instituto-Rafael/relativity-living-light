# MaisDoIt — Horto Relacional de Projeto — V5

**Data:** 2026-09-05  
**Estado:** `APPEND_ONLY / CLAIM_ALLOWED_FALSE / COMPLETE_NO`  
**Escopo:** elevar o N55 de sessão/chat para `PROJECT_FIELD`.

## 1. Mudança de escala

A unidade de trabalho deixa de ser apenas o turno ou a conversa isolada. O campo passa a ser o projeto inteiro:

```text
TURN → CHAT → CONVERSATION_OBJECTS → PROJECT → PROJECT_SOURCES
→ CONNECTED_SOURCES → WEB_PRIOR_ART → EVIDENCE/CUSTODY → HORTO_RELATIONAL_FIELD
```

A documentação oficial da OpenAI observada em 2026-09-05 sustenta que Projects reúnem chats, arquivos, instruções e contexto relacionado; Projects possuem comportamento de memória; chats do mesmo projeto podem ser usados como referência conforme configurações; em Plus/Pro, chats e arquivos do projeto podem ser priorizados ao responder dentro dele.

Isso sustenta tratar o `ChatGPT Project` como um contêiner contextual relacional. Não sustenta afirmar que todos os chats do projeto foram carregados integralmente em cada invocação.

```text
PROJECT_CONTEXT_AVAILABLE != EXHAUSTIVE_PROJECT_CONTENT
PROJECT_MEMORY_REFERENCE != EXHAUSTIVE_TRANSCRIPT_READ
```

A configuração exata de memória do projeto permanece `TOKEN_VAZIO_PROVIDER_SETTING` enquanto não for lida diretamente.

## 2. O “horto em flor” como interface formal

A metáfora é preservada, mas tipada:

| Horto | Objeto técnico |
|---|---|
| solo | arquivos, índices, instruções e fontes |
| raízes | autoridade, provenance, lineage, contratos, memória longitudinal |
| caules | chats/conversas |
| ramos | turns, ocorrências, fórmulas, claims, decisões e artefatos |
| polinização | relações transversais entre chats/fontes |
| flores | knowledge objects com estado de evidência declarado |
| sementes | F_next, hipóteses candidatas e TOKEN_VAZIO com next_probe |
| compostagem | resultados negativos, falhas, contradições e superseded |

`METAPHOR_IS_NOT_MECHANISM=true`.

## 3. Grafo multiplex do projeto

```text
H_P = (V,E,H3,T,S,A,Pv)
```

onde `V` contém PROJECT, CHAT, TURN, OCCURRENCE, FILE, SOURCE, INDEX, MEMORY_NODE, REPO, BRANCH, COMMIT, PR, WORKFLOW, ARTIFACT, CLAIM, FORMULA, HYPOTHESIS, EVIDENCE, FALSIFIER, GAP, TOKEN_VAZIO, RECEIPT e KNOWLEDGE_OBJECT.

`E` usa o vocabulário relacional N55-V4 `R01..R120`. `H3` contém hyperedges de terceira ordem ou superiores quando a relação binária perde contexto. `T` preserva tempo/lineage/supersession; `S` guarda estado epistemológico; `A` guarda autoridade/provider boundary; `Pv` guarda provenance/custody.

Cada conversa vira:

```text
C_i=(turns,occurrences,objects,sources,formulas,hypotheses,controls,
     decisions,artifacts,gaps,relations,lineage,coverage_vector)
```

Pertencer ao mesmo projeto não é evidência de relação:

```text
SAME_PROJECT != SAME_TOPIC != SAME_OBJECT != SAME_CLAIM
```

## 4. Relações cross-chat

Para cada par `(C_i,C_j)`, procurar somente relações demonstráveis:

- knowledge objects compartilhados;
- fórmulas iguais, equivalentes ou contraditórias;
- hipótese em um chat e teste em outro;
- F_gap fechado posteriormente;
- F_next herdado de conversa anterior;
- PRECEDES/SUCCEEDS/SUPERSEDES/CONTRADICTS;
- arquivo, repositório ou fonte comum;
- mudança metodológica;
- mudança de estado epistemológico;
- receipt/artefato criado em outro chat;
- analogia sem identidade;
- TOKEN_VAZIO transversal ainda aberto.

Uma aresta cross-chat exige:

```text
{relation_type, source_chat_i, source_chat_j,
 source_pointer_i, source_pointer_j, object_ids,
 confidence_state, evidence_state, falsifier_or_next_probe}
```

Sem ponte demonstrável: `TOKEN_VAZIO_RELATION`.

## 5. Hyperedges de terceira ordem

A V5 formaliza relações que não cabem honestamente em um par:

```text
H3(CHAT_i, FILE_j, PR_k)
```

pode representar uma hipótese que nasce em um chat, é formalizada em um arquivo e é implementada/testada em um PR.

```text
H3(CHAT_i, CHAT_j, EVID_k)
```

pode representar proposta, contradição e evidência que resolve — ou mantém — o paradoxo.

Cada hyperedge recebe NIBIGUIRI de segunda ordem: qual elemento a desmonta, qual conversa contradiz, qual fonte reduz novidade, qual representação cria falso positivo, qual provider boundary impede reconstrução e qual F_gap sobrevive.

## 6. Operador de contexto

A V5 usa apenas como abstração de engenharia:

```text
Γ_P(q,t)=SELECT_AVAILABLE(
  project_instructions,
  project_chats,
  project_files,
  project_memory_if_enabled,
  connected_sources,
  web_when_required,
  current_turn
  | q,t,provider_policy)
```

Isso **não** é uma afirmação sobre o algoritmo interno do ChatGPT. Serve para registrar o que foi observado e o que não foi recuperado.

```text
context_observed = {chat atual, refs de projeto disponíveis, arquivos lidos,
                    conectores consultados, web consultada, memória material}
context_not_observed = {chats não recuperados, arquivos inacessíveis,
                        ranking/estado interno do provider}
claim_boundary = AVAILABLE_CONTEXT_ONLY
```

## 7. Cobertura deixa de ser escalar

```text
C_HORTO=(
 C_turn,C_chat,C_cross_chat,C_object,C_relation,C_hyperedge,
 C_transform,C_falsifier,C_provenance,C_context,C_temporal,
 C_opposition,C_anomaly,C_reconstruction,C_project_file,
 C_instruction,C_memory_available,C_connector,C_repo,
 C_web_prior_art,C_receipt,C_gap_closure)
```

São **22 dimensões**. Nenhuma dimensão obrigatória em TOKEN_VAZIO pode ser escondida por uma média alta em outras dimensões.

## 8. Navegação MaisDoIt

```text
ATLAS:X = localizar nós/rotas e escolher caminho
NOVO:X  = NOVOexport/JSON primeiro quando for autoridade bruta
L:X     = evolução longitudinal
O:X     = eixos ortogonais
T:X     = pontes transversais/cross-chat
REL:X   = relações e hyperedges
SCALE:X = META→projeto→chat→turn→objeto→token/yocto
EVID:X  = evidência/prova/gates/falsificadores/receipts
GAP:X   = TOKEN_VAZIO e closure gates
LEARN:X = delta append-only, supersession e antirregressão
```

Esses operadores são projeções do mesmo horto, não dez bancos independentes.

## 9. Antirregressão do Project Field

```text
PROJECT_MEMORY_REFERENCE != EXHAUSTIVE_TRANSCRIPT_READ
PROJECT_FILE_PRESENT != FILE_CONTENT_OBSERVED
SAME_PROJECT != SEMANTIC_RELATION
CROSS_CHAT_SIMILARITY != CAUSALITY
MEMORY != CANONICAL_AUTHORITY
WEB != PRIVATE_SOURCE
CONNECTOR_SEARCH != FULL_PROVIDER_CORPUS
CURRENT_CONTEXT != ENTIRE_ACCOUNT
PROJECT_CONTEXT != CROSS_PROJECT_CONTEXT sem suporte explícito do provider/configuração
WRITE_OR_MERGE != SCIENTIFIC_PROOF
```

## 10. R3

### F_ok

- escala ampliada para `PROJECT_FIELD`;
- horto mapeado para grafo multiplex;
- chats, arquivos, instruções, memória disponível, conectores, web e repositórios separados por classe;
- arestas cross-chat e hyperedges de terceira ordem formalizados;
- vetor de cobertura de 22 dimensões;
- limites do produto preservados.

### F_gap

- inventário atômico de **todas** as conversas do MaisDoIt ainda não materializado;
- `PROJECT_MEMORY_MODE=TOKEN_VAZIO_PROVIDER_SETTING`;
- matriz `chat×chat×object×relation×source_pointer` ainda não completa;
- chats não recuperados pelo contexto/provider permanecem `TOKEN_VAZIO_PROVIDER_CONTEXT`.

### F_next

```text
PROJECT_INVENTORY
→ enumerate_available_chats
→ atomic_extraction_per_chat
→ bind_files_and_sources
→ L/O/T/C/P
→ cross_chat_relations
→ third_order_hyperedges
→ NIBIGUIRI-2
→ evidence/falsifier
→ receipt/index/memory
→ recalculate C_HORTO
```

O próximo ganho não vem de “mais itens” isolados; vem principalmente de **arestas e hyperedges verificadas entre partes do horto que já existem**.
