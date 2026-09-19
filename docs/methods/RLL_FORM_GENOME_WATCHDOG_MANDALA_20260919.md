# RLL — Genoma de Formas + Watchdog Cruzado + Mandala Auditável V1

**Date:** 2026-09-19  
**State:** `METHOD_CONTRACT / IMPLEMENTED_BOUNDED_COMPOSITION`  
**claim_allowed:** false

## 0. Origem e fronteira

Esta camada nasce de três fontes internas preservadas:

1. sessão corrente RLL de retroalimentação/permutação;
2. export RAFAELIA com estados Yin/Yang/∅, trigramas, Bagua, geometria Tao e mandala;
3. contratos anteriores MHEL-Ω/Bagua que já separam metáfora, matemática, implementação e claim.

### Correção biológica da analogia

A analogia "mRNA reconstrói a outra parte do DNA" não é usada literalmente.

Em biologia comum:
- DNA serve de molde para RNA na transcrição;
- mRNA normalmente leva informação para tradução em proteína;
- síntese de uma fita complementar de DNA usa DNA como molde;
- RNA pode servir de molde para DNA em casos especiais de transcrição reversa.

Aqui usamos apenas uma **analogia computacional declarada**:

```text
SOURCE_SHAPE_GENOME
-> TRANSCRIBED_FORM_FRAGMENT
-> RECOMBINATION
-> PHENOTYPE_OF_FORM
-> TEST
-> RECEIPT
```

## 1. Unidade mínima: gene de forma

Cada fragmento é:

```text
FORM_GENE = <
  id,
  source_ref,
  primitive,
  state,
  geometry,
  operators,
  invariants,
  constraints,
  risk_tags,
  falsifiers,
  provenance,
  claim_gate
>
```

Primitivas iniciais:

```text
POINT
AXIS
PAIR
ARC
CIRCLE
TRIAD
TRIGRAM
OCTAGON
RING
PETAL
MANDALA
TOKEN_VAZIO
```

Operadores:

```text
COMPLEMENT
ROTATE
REFLECT
PAIR_ANTIPODE
SPLIT3
SCALE
STACK
RADIALIZE
RECOMBINE
COMPRESS
EXPAND
ROOT_RETURN
```

## 2. Semente Yin/Yang/TOKEN_VAZIO

Fonte recuperada:

```text
E in {YIN=0, YANG=1, TOKEN_VAZIO}
TOKEN_VAZIO != 0
```

Complemento:

```text
C(0)=1
C(1)=0
C(TOKEN_VAZIO)=TOKEN_VAZIO
```

O vazio não é forçado para um polo.

## 3. Três posições -> oito estados

Para bits conhecidos:

```text
B8 = {0,1}^3
|B8| = 2^3 = 8
```

Com estado epistêmico:

```text
E3 = {0,1,TOKEN_VAZIO}^3
|E3| = 3^3 = 27
```

Esses 27 estados não são 27 trigramas históricos. São estados computacionais de conhecimento.

## 4. Octógono / Bagua computacional

A geometria computacional mínima usa:

```text
Q_axial = {N,S,E,W}
Q_diag  = {NE,NW,SE,SW}
Q8 = Q_axial union Q_diag
```

Quatro pares antipodais:

```text
(N,S)
(E,W)
(NE,SW)
(NW,SE)
```

O centro é uma posição adicional:

```text
Q9 = Q8 union {O}
```

A ordem histórica dos trigramas ao redor do octógono permanece configurável:

```text
TRIGRAM_OCTAGON_ORDER = TOKEN_VAZIO_HISTORICAL_ORDER
```

até uma fonte explícita ser vinculada.

## 5. Grupos de transformação

Para oito posições:

```text
C8 = 8 rotations
D8 = 8 rotations + 8 reflections
|D8| = 16
```

A implementação usa isso como ferramenta matemática moderna, não como atribuição histórica automática.

## 6. Tao formal recuperado

Modelo geométrico idealizado:

```text
Y union G = D
int(Y) intersect int(G) = empty
mu(Y)+mu(G)=mu(D)
ideal symmetric case: mu(Y)=mu(G)=mu(D)/2
R_pi(Y)=G
R_pi(G)=Y
```

Isto é uma formalização autoral/geométrica recuperada do corpus.

## 7. Do octógono à mandala

A mandala é tratada como **fenótipo composto de forma**, não como prova cosmológica.

Pipeline:

```text
CENTER
-> 4 AXIAL PAIRS
-> 8 VERTICES
-> TRIGRAM ASSIGNMENT
-> optional C8/D8 transform
-> RINGS
-> radial repetition
-> optional petals/keys
-> MANDALA_FORM
```

A imagem "Mandala RAFAELIA - 42 (Resposta Universal)" é preservada como fonte visual com oito setores e rótulo "42 Chaves". O número 42 não recebe nesta camada uma semântica nova sem um mapa explícito de chave->função.

## 8. Vetor autoral opcional

Fonte anterior registra:

```text
T_RAF = [4,8,3,5,2,4,8,6]
```

Estado:

```text
OPERATOR_AUTHORIAL_UNVALIDATED
```

Pode ser usado como seletor/agenda de composição, nunca como lei.

## 9. Watchdog cruzado de três níveis

### Processo P

Emite um receipt lógico:

```text
T_n = <
 seq,
 input_hash,
 state_hash,
 output_hash,
 invariant_vector,
 claim_gate
>
```

### Watchdog A

Observa:
- monotonicidade de `seq`;
- hash do estado;
- invariantes;
- última receipt de B;
- última receipt do meta-watchdog M.

### Watchdog B

Repete a validação **independentemente**, com a mesma especificação, mas cadeia de receipt separada.

### Meta-watchdog M

Compara A e B:

```text
A=PASS, B=PASS -> CONSENSUS_PASS
A=FAIL, B=FAIL -> CONSENSUS_FAIL
A!=B -> DIVERGENCE_FAIL_CLOSED
A silence -> WATCHDOG_A_SILENT
B silence -> WATCHDOG_B_SILENT
```

### Watchdog do watchdog

Para evitar auto-certificação circular:

```text
M_n is checked by A_(n+1) and B_(n+1)
```

Assim, M nunca valida a si próprio no mesmo tick.

```text
SELF_CERTIFICATION = FORBIDDEN
DELAYED_RECIPROCAL_CHECK = REQUIRED
```

## 10. Redundância e risco comum

Dois watchdogs idênticos podem compartilhar o mesmo erro.

Portanto o receipt registra:

```text
implementation_id
spec_version
input_digest
decision_digest
```

e o sistema distingue:

```text
DUAL_AGREEMENT
from
INDEPENDENCE_EVIDENCE
```

Concordância entre A e B reduz divergência observável; não prova independência.

## 11. Estados do watchdog

```text
PASS
FAIL
DIVERGENCE
STALE
SILENT
REPLAY
HASH_MISMATCH
INVARIANT_BREACH
TOKEN_VAZIO
COMMON_MODE_UNRESOLVED
```

Qualquer divergência relevante é fail-closed para promoção.

## 12. Espaço de composição

Para n genes escolhendo r:

```text
combinations = C(n,r)
ordered permutations = P(n,r)
```

O algoritmo escolhe:

```text
if total_space <= exhaustive_cap:
    enumerate exactly
else:
    deterministic stratified random sample
```

Nunca executa "infinito".

## 13. Crossover / recombinação

Dois genes podem compor somente se:

```text
layer_compatible
AND unit_compatible
AND geometry_compatible
AND no_exclusive_claim_boundary
```

Resultado:

```text
CHILD = RECOMBINE(parent_A,parent_B,operator)
```

O child herda:
- source refs;
- invariants;
- risk tags;
- unresolved gaps;
- parent hashes.

## 14. Auditoria de possibilidade

Cada possibilidade recebe:

```text
POSSIBILITY = <
  genome_hash,
  parent_ids,
  operator_chain,
  geometry_state,
  predicted_outputs,
  failure_modes,
  watchdog_state,
  evidence_state,
  claim_allowed
>
```

Estados:

```text
GENERATED
STRUCTURALLY_VALID
STRUCTURALLY_INVALID
TEST_READY
TESTED_PASS
TESTED_FAIL
DIVERGENT_WATCHDOGS
TOKEN_VAZIO
BLOCKED_CLAIM
```

## 15. FMEA mínima

Para cada possibilidade:

```text
risk = severity * occurrence * detectability
```

Isto é prioridade operacional, não probabilidade física.

Mitigações:
- redundância;
- watchdog cruzado;
- checksum/hash;
- replay protection;
- deterministic seed;
- bounded search;
- provenance;
- fail-closed claim gate;
- rollback by parent hash.

## 16. Varredura recorrente

Integra com a régua anterior:

```text
FORWARD
-> COMPOSE
-> WATCH
-> REVERSE
-> CROSS_CHECK
-> COMPRESS
-> NEW_REPRESENTATION
-> RESWEEP
```

Terminal:

```text
SATURATED_UNDER_CURRENT_RULER
!=
COMPLETE
```

## 17. R3

**F_ok:** Tao/Yin-Yang, 3 bits->8 estados, eixos octogonais, C8/D8, mandala visual, gene de forma e watchdog cruzado estão separados por camada e implementáveis.  
**F_gap:** ordem histórica exata dos trigramas no octógono e semântica das 42 chaves permanecem TOKEN_VAZIO; independência real entre watchdogs exige implementações diversas ou validação externa.  
**F_next:** executar fixtures determinísticos, enumerar 8 trigramas/64 pares pequenos exaustivamente, usar amostragem limitada acima do cap, e promover somente receipts que passem A/B/M sem divergência.


## 18. Genes de forma recuperados por nova passada

O export também preserva uma decomposição por cardinalidade/processo que agora é carregada como genes independentes:

```text
GF-001  1 -> origem/ponto
GF-002  2 -> Yin/Yang
GF-003  3 -> três linhas / tríade / terços
GF-004  4 -> eixos cardinais
GF-005  5 -> cinco fases como processo organizacional
GF-006  6 -> seis linhas
GF-008  8 -> octógono / oito estados
GF-042 42 -> rótulo visual “42 Chaves”; semântica permanece TOKEN_VAZIO
```

A sequência de decomposição computacional:

```text
1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 8 -> 42?
```

não afirma uma genealogia histórica ou física. O `42` final é uma âncora visual ainda sem mapa formal de 42 genes/chaves.

O vetor autoral anterior:

```text
[4,8,3,5,2,4,8,6]
```

permanece separadamente como `OPERATOR_AUTHORIAL_UNVALIDATED`.

## 19. FMEA operacional calculável

O watchdog passa a carregar um registro de riscos.

```text
RPN = severity * occurrence * detectability
```

As três escalas são ordinais e declaradas. O RPN serve apenas para **priorização operacional**.

Não é:

```text
RPN != physical probability
RPN != clinical risk
RPN != scientific truth score
```

Riscos iniciais:
- common-mode entre watchdogs;
- silêncio/stale;
- replay;
- perda de proveniência;
- explosão combinatória;
- promoção semântica indevida.

O limiar inicial de mitigação é configurável e pode ser alterado por receipt; não é uma constante universal.
