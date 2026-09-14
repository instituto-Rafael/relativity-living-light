# 24 — Ponte Formal de Física e Evidência: RLL ↔ RafPolimata

**Status:** `METHOD_DEFINED`  
**Função:** conectar a formalidade matemática do Orquestrador Científico do RafPolimata aos dados, likelihoods, simulações e falsificadores do RLL.  
**Regra:** este documento não converte semântica, topologia ou coincidência numérica em verdade física; ele define as provas necessárias para que um claim físico possa avançar.

---

## 1. Separação de responsabilidades

| Camada | Responsabilidade | Repositório canônico |
|---|---|---|
| Equações, unidades e gates | registro formal, consistência dimensional, estatística, NTP | `RafPolimata` |
| Cosmologia e observáveis | `H(z)`, distâncias, espectros, dados reais, likelihood | `relativity-living-light` |
| Runtime e benchmark | execução C/ASM, erro numérico, hash e desempenho | `ChipQuantum` |
| Controle/agente | ingestão, decisão, explicabilidade e segurança | `llamaRafaelia` |
| Dispositivo | telemetria, clock, energia e isolamento Android | `Vectras-VM-Android` |

O RLL só deve importar uma equação externa por identificador estável e registrar:

```text
{equation_id, version, domain, assumptions, units, implementation_ref,
 dataset_ref, uncertainty, run_id, artifact_hash, verdict}
```

---

## 2. Estados de claim compatíveis

| Estado RLL | Estado do orquestrador | Interpretação |
|---|---|---|
| `PARABOLA_DIDATICA` | `METAPHOR` | didática, sem claim físico |
| `METAFORA` | `METAPHOR` | relação semântica/analógica |
| `HIPOTESE` | `FORMALIZED` | modelo matemático definido |
| `METHOD_DEFINED` | `METHOD_DEFINED` | método e falsificador definidos |
| `SIMULATED` | `SIMULATED` | resultado numérico reproduzível |
| `EVIDENCE_LINKED` | `EVIDENCE_LINKED` | dado real e incerteza ligados |
| `REPLICATED` | `REPLICATED` | repetição independente |
| `CLAIM_ALLOWED` | `CLAIM_ALLOWED` | alegação limitada ao domínio |
| `TOKEN_VAZIO` | `TOKEN_VAZIO` | ausência reconhecida |
| `CONTRADICTION` | `CONTRADICTION` | hipótese contrariada |

A promoção direta `METAFORA → CLAIM_ALLOWED` permanece proibida.

---

## 3. Prova de ação física

Uma ação física alegada deve satisfazer conservação e mensuração:

```math
\Delta E_{sistema}=Q-W+\sum_j E_{in,j}-\sum_k E_{out,k},
```

```math
\frac{d\mathbf p}{dt}=\sum\mathbf F,\qquad
\frac{d\mathbf L}{dt}=\sum\boldsymbol\tau,
```

```math
\frac{dQ_{eletrica}}{dt}=I,
```

com resíduos normalizados:

```math
r_E=\frac{|\Delta E_{medida}-\Delta E_{modelo}|}{u_E},
```

```math
r_p=\sqrt{(\mathbf p_{medida}-\mathbf p_{modelo})^T
\Sigma_p^{-1}(\mathbf p_{medida}-\mathbf p_{modelo})}.
```

`CLAIM_ALLOWED` exige resíduos compatíveis com o orçamento de incerteza e ausência de ganho energético não contabilizado.

---

## 4. Mecânica quântica: adaptador obrigatório

O uso de vocabulário quântico no RLL deve apontar para um adaptador com:

1. espaço de Hilbert `\mathcal H`;
2. estado normalizado `|\psi\rangle`;
3. Hamiltoniano auto-adjunto `\hat H`;
4. observável `\hat A`;
5. regra de medida;
6. protocolo experimental ou simulador quântico identificado;
7. baseline clássico equivalente.

Equações mínimas:

```math
i\hbar\partial_t|\psi\rangle=\hat H|\psi\rangle,
```

```math
P(a)=|\langle a|\psi\rangle|^2,
```

```math
\Delta A\,\Delta B\ge\frac12|\langle[\hat A,\hat B]\rangle|.
```

Sem esses campos, o claim fica em `METAFORA`, `HIPOTESE` ou `SIMULATED_CLASSICALLY`, nunca como efeito quântico demonstrado.

---

## 5. Física clássica, relatividade e cosmologia

A camada clássica deve declarar qual aproximação usa:

- Newtoniana: `v/c ≪ 1`, campo fraco;
- relatividade especial: métrica plana;
- relatividade geral: métrica, conexão, tensor de curvatura e tensor energia-momento;
- cosmologia FLRW: homogeneidade/isotropia e parâmetros do modelo.

Para o RLL cosmológico, a cadeia mínima é:

```math
E_{RLL}(z;\theta)=\frac{H(z;\theta)}{H_0},
```

```math
d_L(z)=(1+z)\frac{c}{H_0}\int_0^z\frac{dz'}{E_{RLL}(z';\theta)},
```

```math
\mu(z)=5\log_{10}\left(\frac{d_L(z)}{\mathrm{Mpc}}\right)+25.
```

O teste deve comparar RLL, ΛCDM e modelos competidores com a mesma seleção de dados, covariância, priors e tratamento de nuisance parameters.

---

## 6. Estatística e confiabilidade

Para vetor de resíduos `r=y-f(\theta)`:

```math
\chi^2=r^T\Sigma^{-1}r.
```

O relatório deve incluir, no mínimo:

- `N`, número de parâmetros e graus de liberdade;
- matriz de covariância ou justificativa da aproximação diagonal;
- log-likelihood máxima;
- AIC, AICc e BIC;
- posterior/intervalos de credibilidade quando Bayesiano;
- análise de sensibilidade a priors;
- testes de convergência;
- posterior predictive checks;
- validação em dados não usados no ajuste.

Nenhum valor com muitas casas decimais deve ser exibido além da resolução sustentada pela incerteza.

---

## 7. Grafos de evidência e fragmentos semânticos

Os fragmentos de conversa, textos e símbolos entram como nós de proveniência, não como medições físicas:

```math
G=(V,E),\qquad L=D-A.
```

Cada nó deve carregar `claim_state`; cada aresta deve ter tipo explícito. Relações semânticas podem sugerir hipóteses, mas não substituir likelihood ou experimento.

Tipos de aresta recomendados:

- `DERIVED_FROM`
- `OBSERVED_IN`
- `IMPLEMENTED_BY`
- `TESTED_BY`
- `FALSIFIED_BY`
- `REPLICATED_BY`
- `SEMANTICALLY_RELATED`

`SEMANTICALLY_RELATED` não pode alimentar diretamente `CAUSES`.

---

## 8. Poincaré, atratores e estabilidade

Qualquer claim sobre atratores físicos deve fornecer:

- equações diferenciais ou mapa discreto;
- espaço de estados;
- seção de Poincaré;
- condições iniciais;
- análise de bifurcação;
- expoentes de Lyapunov;
- robustez a ruído e resolução.

```math
x_{n+1}=P(x_n),\qquad P^k(x^*)=x^*.
```

Os 42 atratores do ecossistema permanecem **estrutura arquitetural** até existir essa prova dinâmica para um sistema físico específico.

---

## 9. Tempo, NTP e cadeia de custódia

Todo resultado computacional deve registrar:

```text
utc_timestamp, monotonic_start, monotonic_end, ntp_offset,
ntp_delay, jitter, dispersion, host, architecture, compiler,
flags, seed, dataset_hash, code_commit, artifact_hash
```

Para NTP:

```math
\theta=\frac12[(T_2-T_1)+(T_3-T_4)],
```

```math
\delta=(T_4-T_1)-(T_3-T_2),
```

```math
\lambda=\epsilon+\frac\delta2.
```

UTC ordena artefatos; relógio monotônico mede duração. NTS deve ser usado quando disponível para autenticação do tempo.

---

## 10. Manifesto de experimento

Cada execução deverá produzir JSON equivalente a:

```json
{
  "claim_id": "RLL-CLAIM-0001",
  "equation_ids": ["E30", "E31", "E32"],
  "claim_state_before": "METHOD_DEFINED",
  "dataset": {
    "id": "dataset-id",
    "sha256": "TOKEN_VAZIO",
    "license": "TOKEN_VAZIO"
  },
  "runtime": {
    "commit": "TOKEN_VAZIO",
    "seed": 42,
    "clock": "MONOTONIC",
    "utc_source": "NTP"
  },
  "uncertainty": {
    "method": "GUM_or_posterior",
    "value": "TOKEN_VAZIO"
  },
  "verdict": "TOKEN_VAZIO"
}
```

---

## 11. Matriz de testes do projeto motor/energia

Apesar de o RLL ser principalmente cosmológico, o mesmo contrato pode receber resultados externos do projeto motor híbrido:

| Fator | Níveis mínimos | Resposta |
|---|---|---|
| ligação elétrica | Y, Δ, baseline fixa | energia, torque, ripple |
| velocidade | baixa, média, alta | eficiência e temperatura |
| carga | 25%, 50%, 75%, 100% | perdas e estabilidade |
| temperatura do combustível | faixa segura definida | BSFC e emissões |
| fração energética H₂ | 0 e níveis controlados | eficiência e pressão |
| origem de energia do H₂ | externa, regenerativa, alternador | ganho líquido |
| controlador | determinístico, MPC, IA protegida | custo e segurança |

O ganho é aceito apenas por balanço `tank-to-wheel` e intervalo de confiança.

---

## 12. Gates RLL

1. `RLL-F01`: equação registrada no RafPolimata.
2. `RLL-F02`: unidade e domínio declarados.
3. `RLL-F03`: dataset real e hash.
4. `RLL-F04`: incerteza e covariância.
5. `RLL-F05`: baseline congelado.
6. `RLL-F06`: hipótese nula e falsificador.
7. `RLL-F07`: relógio e proveniência.
8. `RLL-F08`: execução reproduzível.
9. `RLL-F09`: comparação de modelos.
10. `RLL-F10`: claim limitado ao resultado.

---

## 13. Resultado esperado

A ponte não promete unificação automática. Ela permite que uma relação simbólica atravesse etapas verificáveis:

```math
\text{símbolo}\to\text{definição}\to\text{equação}\to\text{código}
\to\text{dado}\to\text{incerteza}\to\text{falsificador}\to\text{claim limitado}.
```

Esse é o vetor de sustentação: não a quantidade de fórmulas, mas a continuidade auditável entre significado, matemática, execução e realidade observada.
