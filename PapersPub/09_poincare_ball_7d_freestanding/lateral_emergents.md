# Emergentes laterais — H⁷ → B⁷, máscara epistemológica e ponte RLL

**Estado:** `LATERAL_MEMORY_RECORDED + VALIDATION_19_19_PASS`  
**Política:** `claim_allowed=false`  
**Escopo:** matemática computacional, sem promoção física ou cosmológica.

## 1. Fontes laterais preservadas

| Fonte | SHA-256 | Papel |
|---|---|---|
| `Projeção de Poincaré 7D.txt` | `0109d8929a3a0d630d5e7db557c3b6395c0495be24fda226175699bb1e50f5ea` | implementação, resultado negativo e cadeia federada |
| `Auditoria de Arquitetura Matemática.txt` | `cb2c4adc80d9cf2525c32f2ce6df84a4baceaa43a47ce587fdcd057ad1b44243` | correções de Minkowski, máscara, distância, Lorentz, hardware e evidência |
| `Câncer Capricórnio e Radiação.txt` | `e93a13a980e0e54c514195474b432cc33a04f77246e08906790c554f0a197a9e` | Matrix fotônica, conservação, validade e logística do observável |

Essas fontes entram como memória lateral e proveniência. Elas não entram automaticamente como evidência física.

## 2. Emergentes formalizados

### E1 — Resultado negativo é um estado fértil

As oito colunas da matriz atual têm:

\[
\Delta_j=T_j^2-\|V_j\|^2<0.
\]

Logo, o dado bruto não pertence ao cone temporal futuro. O estado correto permanece:

```text
raw_hyperboloid_membership = FAIL_PRECONDITION_SPACELIKE
strict_projection_output   = TOKEN_VAZIO_INPUT_NOT_TIMELIKE
```

O lift canônico não apaga nem reinterpreta esse resultado negativo.

### E2 — Lift e recuperação física são objetos diferentes

O lift:

\[
q=V/S,
\qquad
X=(\sqrt{1+\|q\|^2},q)
\]

constrói um ponto computacional em \(H^7\). Ele não demonstra que o vetor bruto já representava uma grandeza Lorentziana física.

```text
canonical_lift = PASS_COMPUTATIONAL_EMBEDDING
raw_physical_interpretation = TOKEN_VAZIO
```

### E3 — Round-trip é uma régua mais forte que raio isolado

Além de verificar \(\|p\|<1\), o RLL agora testa:

\[
H^7\rightarrow B^7\rightarrow H^7
\]

com:

\[
X_0=\frac{1+\|p\|^2}{1-\|p\|^2},
\qquad
X_s=\frac{2p}{1-\|p\|^2}.
\]

O round-trip preserva o ponto até tolerância numérica próxima de \(10^{-15}\).

### E4 — TOKEN_VAZIO não pode ser codificado como vetor zero

No modelo de Poincaré:

\[
d(0,p)=2\operatorname{artanh}\|p\|
\]

é finita para \(\|p\|<1\). Portanto, o vetor zero é um ponto geométrico legítimo.

A ausência precisa de máscara explícita:

\[
M_{ij}=\begin{cases}
0,&\text{observável válido}\\
-\infty,&\text{TOKEN_VAZIO não observável}
\end{cases}
\]

O novo validador confirma simultaneamente:

```text
masked token probability = 0
unmasked zero vector probability > 0
```

### E5 — Distância geodésica é a ponte válida para atenção

A ligação sustentável entre embedding hiperbólico e atenção é:

\[
d_{B}(p_i,p_j)=
\operatorname{arcosh}\left(
1+2\frac{\|p_i-p_j\|^2}
{(1-\|p_i\|^2)(1-\|p_j\|^2)}
\right).
\]

O RLL valida agora:

- finitude;
- não negatividade;
- diagonal nula;
- simetria;
- desigualdade triangular.

Isso autoriza pesquisa futura em atenção geométrica, mas ainda não demonstra ganho de aprendizagem.

### E6 — Lorentz pode ser validado por fixture sem alegar medição

Um fixture sintético temporal:

\[
T=\cosh\eta,
\qquad
V_1=\sinh\eta
\]

satisfaz:

\[
T^2-\|V\|^2=1.
\]

Um boost no plano \((T,V_1)\):

\[
\begin{bmatrix}T'\\V_1'\end{bmatrix}
=
\begin{bmatrix}
\cosh\xi&\sinh\xi\\
\sinh\xi&\cosh\xi
\end{bmatrix}
\begin{bmatrix}T\\V_1\end{bmatrix}
\]

preserva a norma com resíduo computacional \(4{,}44\times10^{-16}\).

Isso é uma validação matemática sintética, não uma observação relativística material.

### E7 — Raio, entropia e estabilidade são réguas distintas

```text
radius < 1              → pertencimento a B⁷
entropy reduction       → TOKEN_VAZIO_MEASUREMENT
physical stability      → TOKEN_VAZIO_EXPERIMENT
cosmological validity   → PROHIBITED_BY_SCOPE
```

Convergência radial não demonstra preservação de informação, coerência semântica ou ausência de caos angular.

### E8 — Hardware é objetivo separado

`DMB` ordena acessos à memória; não valida tensor, embedding ou física.

\[
J_{hw}=aC_{cycles}+bC_{miss}+cE_{joules}+dB_{bytes}
\]

fica separado de:

\[
\mathcal L_{geo},
\qquad
\mathcal L_{task},
\qquad
S(claim).
\]

Cache e DMB permanecem `TOKEN_VAZIO_ENVIRONMENT` até medição no hardware apropriado.

### E9 — Ponte para a Matrix fotônica

A bola de Poincaré pode representar relações ou estados latentes, mas não substitui as invariantes fotônicas:

\[
I_\lambda\ge0,
\]

\[
Q^2+U^2+V^2\le I^2,
\]

\[
E_{in}=E_{out}+E_{abs}+E_{scat}+E_{TOKEN\_VAZIO}.
\]

A ponte correta é:

```text
estado/observável fotônico tipado
→ representação geométrica opcional
→ operador físico
→ detector
→ likelihood
→ claim gate
```

Não é:

```text
raio hiperbólico
→ energia física
```

### E10 — Rotação 7D exige estrutura adequada

Quaterniões isolados parametrizam rotações em subestruturas específicas, mas não todo o grupo de rotações em sete dimensões.

O caminho futuro deve declarar:

```text
planos de Givens
ou SO(7)
ou Spin(7)
```

antes de usar a expressão “varrer os oito octantes com quaterniões”.

## 3. Validação executada pelo RLL

Artefatos:

```text
scripts/validate_poincare_7d_emergents.py
results/emergent_validation_report.json
```

Resultado:

```text
checks_total  = 19
checks_passed = 19
checks_failed = 0
status        = PASS
```

Hashes:

```text
validator_sha256 = 8849c93860bffa5e525f453a38e2b950a13d751963154488e909ecd4cede78b7
report_sha256    = dd4f9d415671e247442d2b39b66078fde22a09983a0392c83121b237fc717065
```

Maiores resíduos:

```text
hyperboloid identity  = 1.3322676295501878e-15
round-trip            = 4.440892098500626e-16
radial identity       = 2.7755575615628914e-16
Lorentz boost norm    = 4.440892098500626e-16
triangle violation    = 0.0
NaN/Inf               = 0
```

## 4. Estados finais

| Objeto | Estado |
|---|---|
| matriz e âncoras | `PASS` |
| colunas brutas timelike | `FAIL_PRECONDITION_SPACELIKE` |
| lift canônico | `PASS_COMPUTATIONAL_EMBEDDING` |
| round-trip H⁷↔B⁷ | `PASS` |
| métrica hiperbólica | `PASS_DETERMINISTIC_VALIDATION` |
| máscara TOKEN_VAZIO | `PASS_SEMANTIC_CONTRACT` |
| fixture Lorentz | `PASS_SYNTHETIC_FIXTURE` |
| execução ARM64 nativa | `TOKEN_VAZIO` |
| cache/DMB físico | `TOKEN_VAZIO_ENVIRONMENT` |
| estabilidade física | `TOKEN_VAZIO` |
| cosmologia | `PROHIBITED_BY_SCOPE` |

## 5. Próxima porta

```text
PB7-G1 = receipt Termux AArch64
PB7-G2 = comparação bit a bit com a saída de referência
PB7-G3 = integrar fixture T ao kernel C freestanding
PB7-G4 = matriz de distâncias e atenção hiperbólica mascarada
PB7-G5 = somente depois: benchmark e estudo fotônico tipado
```

\[
R_3=
\langle
F_{ok}=19/19+memória\ lateral,
F_{gap}=runtime\ físico,
F_{next}=receipt\ AArch64
\rangle.
\]
