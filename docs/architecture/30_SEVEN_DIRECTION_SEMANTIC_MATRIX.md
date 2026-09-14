# RAFAELIA Semantic Matrix 7D — Tokenização Além da Superfície

> Status: arquitetura operacional v1.
> Escopo: transformar texto, arquivos e eventos em unidades semântico-estruturais governadas.
> Regra: este documento descreve uma camada RAFAELIA acima da tokenização lexical; não afirma que tokenizadores de LLM exponham internamente estes campos.

## 1. Problema

Tokenizar caracteres, bytes ou subpalavras é necessário para computação, mas não basta para uma arquitetura que precisa:

- abrir variáveis omitidas;
- distinguir relações alinhadas de forças contrárias;
- percorrer causa e consequência nos dois sentidos;
- registrar evidência e incerteza;
- tratar lacunas sem inventar conteúdo;
- controlar finalidade, retenção e autorização;
- converter análise em ação auditável.

A unidade de trabalho deixa de ser apenas um token lexical e passa a ser uma `SemanticTokenUnit`.

```text
span bruto
→ tokens lexicais
→ sete leituras especializadas
→ matriz de relações
→ síntese governada
→ ação ou TOKEN_VAZIO
```

## 2. Duas paridades relacionais

A matriz usa duas paridades complementares.

### Paridade A — convergente

Procura elementos que compartilham direção, função, simetria, dependência ou invariante.

```text
isogonia
analogia controlada
dependência
compatibilidade
conservação
```

### Paridade B — divergente

Procura resistência, oposição, contradição, limite e modo de falha.

```text
antagonismo
restrição
contradição
perda
risco
falha
```

A primeira paridade evita perder relações úteis. A segunda impede que semelhança seja confundida com verdade.

```text
Síntese = convergência governada por divergência
```

## 3. As sete direções

A análise ocorre em sete núcleos especializados. Nenhum núcleo decide sozinho.

| Direção | Núcleo | Pergunta principal |
|---|---|---|
| D1 | Estrutura lexical | O que foi literalmente escrito e onde há ambiguidade? |
| D2 | Entidade e domínio | Quais objetos, grandezas, unidades e variáveis pertencem ao problema? |
| D3 | Relação isogônica | O que se alinha, depende, conserva ou compartilha estrutura? |
| D4 | Antagonismo e restrição | O que resiste, limita, contradiz ou pode falhar? |
| D5 | Causalidade e tempo | O que causa o quê, para frente e para trás? |
| D6 | Evidência e lacuna | O que foi observado, inferido, omitido ou ainda precisa ser medido? |
| D7 | Operação e governança | O que pode ser feito, sob qual permissão, sandbox e auditoria? |

### D1 — Estrutura lexical

Preserva texto original, normalização, posição, papéis sintáticos, ambiguidades e variantes linguísticas. D1 não atribui verdade; evita que a camada superior apague o que realmente foi escrito.

### D2 — Entidade e domínio

Expande o vocabulário superficial em variáveis de domínio. Uma frase sobre polia e rampa deve abrir, quando aplicável:

```text
massa
gravidade
ângulo
atrito estático e cinético
peso e elasticidade do cabo
raio e inércia da polia
deformação
condições de contorno
incerteza de medição
```

D2 não presume valores. Variável necessária sem valor entra em D6 como lacuna.

### D3 — Relação isogônica

Mapeia dependências, alinhamentos, invariantes, simetrias, relações funcionais e analogias explicitamente marcadas. Analogia nunca recebe automaticamente o estado de evidência.

### D4 — Antagonismo e restrição

Mapeia forças contrárias, perdas, limites físicos ou lógicos, incompatibilidades, contradições, modos de falha e riscos de segurança. D4 pergunta: “o que faria esta interpretação perder?”

### D5 — Causalidade e tempo

Executa quatro travessias:

```text
direta: origem → efeito
inversa: efeito → origem possível
derivada: estado → taxa de mudança
antiderivada: taxa/efeito → trajetória ou condição anterior
```

Também registra escopo temporal e separa correlação de causalidade.

### D6 — Evidência e lacuna

Classifica cada afirmação como não observada, declarada, parcial, validada ou contradita.

Quando uma variável, fonte, licença, protocolo ou evidência está ausente:

```text
TOKEN_VAZIO = lacuna registrada + risco + próxima busca
```

TOKEN_VAZIO não é preenchimento automático. É um bloqueio produtivo contra invenção.

### D7 — Operação e governança

Define ação pretendida, alvo de runtime, `allow`, `sandbox_only`, `blocked` ou `human_review`, necessidade de auditoria, privacidade, elegibilidade para treinamento, retenção, finalidade e proprietário.

Entrada sem política explícita não recebe permissão por silêncio.

## 4. Árvore de núcleos especializados

```text
                    ORQUESTRADOR 7D
                          │
          ┌───────────────┴───────────────┐
          │                               │
   PARIDADE CONVERGENTE           PARIDADE DIVERGENTE
          │                               │
   D1 ─ D2 ─ D3                    D4 ─ D5 ─ D6
          └───────────────┬───────────────┘
                          │
                         D7
                  governança e ação
                          │
               síntese / bloqueio / teste
```

D7 não vence semanticamente os outros núcleos. Ele decide apenas se a saída pode avançar para execução, sandbox, revisão humana ou bloqueio.

## 5. Matriz de estado

Cada unidade pode ser vista como um vetor:

\[
v_i = (L_i, E_i, R_i, A_i, C_i, G_i, O_i)
\]

onde:

- \(L\) = fidelidade lexical;
- \(E\) = cobertura de entidades e variáveis;
- \(R\) = relações convergentes;
- \(A\) = antagonismos e restrições;
- \(C\) = causalidade e temporalidade;
- \(G\) = evidência, incerteza e gaps;
- \(O\) = prontidão operacional/governança.

A unidade não recebe uma média simples. Um zero de governança ou evidência pode bloquear execução mesmo com alta riqueza semântica.

```text
ExecutionReady =
SemanticCoverage
× EvidenceGate
× GovernanceGate
× SafetyGate
```

## 6. Empilhamento multidimensional

A análise não deve crescer por repetição de resumos. Deve crescer por empilhamento preservando referências.

```text
nível 0: spans e tokens
nível 1: SemanticTokenUnit
nível 2: relações entre unidades
nível 3: comunidades de conceitos
nível 4: invariantes e antagonismos
nível 5: hipóteses e falsificadores
nível 6: decisões governadas
nível 7: execução, log e retroalimentação
```

Cada nível aponta para os anteriores por IDs. Compressão sem referência vira perda de custódia.

## 7. Sustentabilidade operacional

```text
capturar
→ classificar
→ analisar em 7D
→ registrar TOKEN_VAZIO
→ pesar relações
→ aplicar governança
→ validar schema
→ testar em CI
→ executar em sandbox
→ registrar resultado
→ atualizar ledger
```

Regras:

1. Não criar um novo nome quando um conceito canônico já existe.
2. Não transformar metáfora em evidência.
3. Não executar lacuna.
4. Não vetorizar dado privado sem política de uso.
5. Não duplicar artefato sem `parent`, `supersedes` ou hash.
6. Não publicar estado sem fixture e validação.
7. Não ampliar volume antes de ampliar coerência.

## 8. Contratos implementados

```text
schemas/semantic_token_unit.schema.json
schemas/formal_treatment_record.schema.json
schemas/examples/semantic_token_unit.pulley_ramp.example.json
schemas/examples/formal_treatment_record.token_vazio.example.json
scripts/validate_semantic_governance_schemas.py
tests/test_semantic_governance_schemas.py
```

O Tail Protocol recebe campos opcionais de política:

```text
privacy=public|private|sensitive|unknown
train=no|yes_explicit|unknown
ret=ephemeral|session|workspace|archive|unknown
purpose=inference|audit|evaluation|indexing|training_explicit|unknown
owner=user|organization|public|unknown
```

## 9. Limites

- A matriz 7D é uma arquitetura de análise RAFAELIA, não uma descrição comprovada dos mecanismos internos de qualquer fornecedor de IA.
- Relações semânticas são hipóteses até receberem evidência adequada.
- O schema valida estrutura; não valida automaticamente verdade científica.
- Um campo `train=no` expressa política do artefato, mas sua eficácia externa depende de contrato, plataforma e mecanismos verificáveis.
- Metáforas expandem o espaço de perguntas; testes decidem.

## 10. Invariante

```text
Cada entrada deve ser lida em múltiplas direções,
mas só pode avançar segundo sua natureza,
sua evidência e sua política de uso.
```

## Retroalimentação

- F_ok: transforma a tese de tokenização semântica em contrato 7D validável.
- F_gap: falta ligar o ledger do Drive ao ledger do GitHub por IDs estáveis.
- F_next: popular o Drive, eliminar a raiz duplicada e executar a CI da branch.
