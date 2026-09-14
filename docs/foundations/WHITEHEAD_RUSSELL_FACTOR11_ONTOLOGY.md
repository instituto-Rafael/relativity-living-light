# Whitehead–Russell × Ontologia Discreta × Fator 11

> **Estado:** fundação lógico-computacional auditável  
> **Escopo físico:** `TOKEN_VAZIO`  
> **Claim global:** `claim_allowed=false`

## 1. Objetivo

Este documento separa, por tipos, quatro objetos que não devem ser colapsados:

1. classe vazia tipada;
2. cardinalidade zero;
3. classe unitária/cardinalidade um;
4. palavra discreta `11`, decimal onze e duas ocorrências unitárias.

A finalidade é preservar a intuição autoral sem transformar analogia ontológica em prova cosmológica.

## 2. Fronteira histórica e formal

A comparação com Alfred North Whitehead e Bertrand Russell é fundacional, não uma alegação de equivalência integral com *Principia Mathematica*. O presente módulo adota apenas a disciplina de tipos:

\[
\text{objeto lógico}\neq\text{cardinal}\neq\text{inscrição}\neq\text{observável físico}.
\]

Uma classe vazia de tipo \(\tau\) é representada por:

\[
\varnothing_\tau=(\tau,\emptyset).
\]

Duas classes vazias de tipos distintos podem ter a mesma cardinalidade:

\[
\#\varnothing_\tau=\#\varnothing_\sigma=0,
\]

sem serem o mesmo objeto tipado:

\[
\varnothing_\tau\neq\varnothing_\sigma\quad(\tau\neq\sigma).
\]

## 3. O símbolo `11` exige três tipos

### 3.1 Palavra discreta

\[
11_{\mathrm{word}}=(1,1),\qquad |11_{\mathrm{word}}|=2.
\]

Ela preserva ordem e multiplicidade.

### 3.2 Cardinalidade da união disjunta

Para dois singletons marcados:

\[
U=\{u\},\qquad V=\{v\},
\]

\[
\#(U\sqcup V)=2.
\]

### 3.3 Número decimal

\[
11_{\mathbb N}=10+1.
\]

Logo:

\[
11_{\mathrm{word}}\neq 2_{\mathbb N}\neq 11_{\mathbb N}
\]

como objetos tipados, embora a mesma grafia possa participar de conversões explícitas.

## 4. Valor racional e proveniência do fator 11

Defina o espaço de apresentações:

\[
\mathcal P=\{(p,q)\in\mathbb Z^2:q\neq0\}.
\]

O mapa de valor é:

\[
\pi(p,q)=\frac pq\in\mathbb Q.
\]

Para:

\[
(77,33)=11(7,3),
\]

temos:

\[
\pi(77,33)=\pi(7,3)=\frac73.
\]

O valor reduzido e a proveniência devem ser armazenados separadamente:

```json
{
  "presentation": [77, 33],
  "reduced_pair": [7, 3],
  "rational_value": "7/3",
  "common_scale": 11
}
```

A redução não é perda quando o contrato exige apenas o racional. Ela é perda de proveniência quando a escala de apresentação fazia parte do objeto documental.

## 5. Critério de gauge representacional

Para um observável \(O\), o fator comum é gauge somente se:

\[
O(77,33)=O(7,3).
\]

Para o observável racional:

\[
O_{\mathbb Q}(p,q)=\frac pq,
\]

a invariância é exata.

Se for proposto um observável sensível à escala:

\[
O_{11}(77,33)\neq O_{11}(7,3),
\]

isso produz apenas uma **hipótese candidata**. Não produz evidência física.

## 6. Ponte para RLL: estado atual

O espaço de parâmetros cosmológicos pode ser representado por:

\[
\Theta_{RLL}=\{H_0,\Omega_m,\Omega_{s0},z_t,w_t,\ldots\}.
\]

A ponte desejada teria a forma:

\[
\mathcal M:\mathsf{DiscreteRepresentation}\longrightarrow\Theta_{RLL}.
\]

No estado atual, não há derivação tipada, unidade física ou observável independente que defina:

\[
\mathcal M(11_{\mathrm{word}}),
\qquad
\mathcal M(\text{common\_scale}=11),
\qquad\text{ou}\qquad
11\mapsto\Omega_{s0}.
\]

Portanto:

\[
\boxed{\mathcal M_{11}=\texttt{TOKEN\_VAZIO}}
\]

## 7. Claims permitidos

- `[E] PASS_EXACT`: \(77/33=7/3\).
- `[E] PASS_EXACT`: \(\gcd(77,33)=11\).
- `[E] PASS_EXACT`: a palavra `11` contém duas ocorrências de `1`.
- `[C] CONVENTION`: classes vazias são marcadas por tipo no módulo operacional.
- `[V] TOKEN_VAZIO`: ligação física entre o fator 11 e parâmetros RLL.

## 8. Claims bloqueados

- “Whitehead e Russell provaram o RLL.”
- “DESI mediu o fator 11.”
- “Cancelar 11 destrói necessariamente uma quantidade física.”
- “\(\Omega_{s0}=0\) decorre da redução de frações.”
- “Uma diferença de representação gera corrente de Noether.”

## 9. Contrato de promoção científica

O estado só pode sair de `TOKEN_VAZIO` quando existirem simultaneamente:

1. domínio e contradomínio tipados do morfismo;
2. equação dimensionalmente consistente;
3. previsão \(\Delta O_{11}(z)\) registrada antes do ajuste;
4. null model e falsificador quantitativo;
5. dados reais, covariância e proveniência;
6. inferência com diagnóstico de fronteira/identificabilidade;
7. implementação independente;
8. artefatos, ambiente e hashes reproduzíveis.

## 10. Implementação

```text
src/rll/discrete_ontology.py
tests/test_discrete_ontology.py
schemas/discrete_ontology_claim.schema.json
data/epistemic_void/factor11_discrete_ontology.json
tools/validate_discrete_ontology_claim.py
```

Execução:

```bash
python -m pytest -q tests/test_discrete_ontology.py
python tools/validate_discrete_ontology_claim.py --write-report
```

## R3

```text
F_ok   = distinção de tipos + invariantes exatos + proveniência do fator 11
F_gap  = morfismo físico M_11, unidades, previsão e dado independente
F_next = preregistrar O_11 ou manter o fator 11 como metadado/gauge
```
