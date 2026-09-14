# RLL — Calibração Teoria ≈ Prática em ΩΠ∞

**Status:** experimental shadow  
**Claim policy:** `claim_allowed=false`  
**Publication effect:** `NONE`

## 1. Intenção

A pesquisa não precisa escolher entre dois extremos:

```text
ideia sem disciplina
ou
ideia bloqueada até validação absoluta
```

A camada de calibração mantém uma relação de trabalho:

\[
\text{teoria}\;\approx\;\text{prática}
\]

O símbolo `≈` não significa confirmação. Ele indica que existe uma operação contínua de aproximação, comparação, correção e nova execução.

A pergunta operacional deixa de ser apenas:

> A teoria está comprovada?

E passa também a incluir:

> Qual é o menor delta ainda aberto entre esta construção teórica e um teste prático discriminante?

## 2. Três ordens independentes

A arquitetura passa a possuir três ordens que não podem ser confundidas:

1. **Promoção científica:** quanto a evidência permite afirmar.
2. **Explorabilidade P0–P5:** quão próxima a possibilidade está de uma execução útil.
3. **Calibração C0–C5:** quão completa está a ligação teoria → configuração → observação → residual → decisão → recibo.

Assim:

```text
alta explorabilidade != alta confirmação
boa calibração != teoria fundamental
resultado negativo != conhecimento perdido
implementação pronta != validação observacional
```

## 3. Operadores simbólicos

A notação fornecida foi preservada como linguagem metodológica:

| Símbolo | Função operacional |
|---|---|
| `[≈]` | operador de aproximação em trabalho |
| `Δ` | residual explícito entre esperado e observado |
| `±` | direção do residual, nunca nota moral ou probabilidade |
| `§` | fronteira de escopo e autoridade |
| `✓` | verificação ligada a recibo concreto |
| `¶` | proveniência, narrativa e cadeia de transformação |
| `Ω` | retorno iterativo pelo ciclo de calibração |
| `Π` | composição das dimensões declaradas sem média opaca |
| `∞` | possibilidade aberta de evolução, não execução infinita nem verdade universal |

A expressão pode ser lida como:

\[
[\approx]\;\Delta[(\pm;\approx)]\;[===[(\S\;\checkmark\;\P)]]
\]

ou, operacionalmente:

\[
\boxed{
\text{aproximar}
\rightarrow
\text{medir residual e direção}
\rightarrow
\text{preservar escopo, verificação e proveniência}
\rightarrow
\text{recalibrar}
}
\]

Esses símbolos não definem uma nova constante física, partícula, campo ou lei cosmológica.

## 4. Invariante ΩΠ∞ dos dados

A invariante de conhecimento é:

\[
K_n=
\left\langle
\text{fonte},
\text{transformação},
\text{escopo},
\Delta,
\text{decisão},
\text{recibo}
\right\rangle_n
\]

A evolução ocorre por:

\[
K_{n+1}=\Omega(K_n, E_{n+1})
\]

onde `E` representa nova evidência, correção, refutação ou lacuna identificada.

A composição é:

\[
\Pi K=
K_{\mathrm{modelo}}
\otimes
K_{\mathrm{código}}
\otimes
K_{\mathrm{observável}}
\otimes
K_{\mathrm{configuração}}
\otimes
K_{\mathrm{recibo}}
\otimes
K_{\mathrm{falsificador}}.
\]

Nenhum termo obrigatório ausente é substituído por zero ou por uma média. Quando uma ligação não existe:

\[
K_d=\mathrm{TOKEN\_VAZIO}.
\]

O infinito é potencial:

\[
K_0\rightarrow K_1\rightarrow K_2\rightarrow\cdots
\]

Cada execução permanece finita e auditável.

## 5. Vetor de calibração

Cada possibilidade recebe seis deltas obrigatórios:

\[
\Delta_i=
\left\langle
\Delta_{TM},
\Delta_{EC},
\Delta_{OM},
\Delta_{PC},
\Delta_{PR},
\Delta_{FD}
\right\rangle
\]

| Delta | Relação |
|---|---|
| `Δ_TM` | escopo teórico → modelo específico |
| `Δ_EC` | equação/algoritmo → código |
| `Δ_OM` | observável → medição |
| `Δ_PC` | parâmetro → configuração congelada |
| `Δ_PR` | previsão → recibo |
| `Δ_FD` | falsificador → decisão |

Cada eixo recebe apenas um estado:

```text
EVIDENCED
PARTIAL
TOKEN_VAZIO
```

`PARTIAL` precisa declarar o que existe e o que falta. `TOKEN_VAZIO` precisa declarar razão, próxima ação e critério de saída.

## 6. Estados da relação

### `APPROX_WORKING`

Há ligação teoria–prática, mas algum delta obrigatório continua aberto.

### `APPROX_BOUNDED`

Uma comparação pré-registrada gerou recibo dentro da tolerância e do escopo declarados.

Isso significa somente:

> o modelo reproduziu este alvo, nesta configuração e nesta tolerância.

### `NOT_EQUAL_OBSERVED`

O residual atravessou um falsificador ou limite pré-registrado.

Esse estado é conhecimento válido e não pode ser renomeado como sucesso.

### `TOKEN_VAZIO_UNDEFINED`

A comparação ainda não pode ser calculada honestamente porque falta modelo, observável, configuração ou recibo obrigatório.

## 7. Maturidade de calibração

| Nível | Estado | Critério |
|---|---|---|
| C5 | `INDEPENDENTLY_REPRODUCED` | execução independente reproduz a relação delimitada |
| C4 | `ROBUST_REPEATED` | repetições pré-registradas demonstram estabilidade |
| C3 | `RECEIPTED_COMPARISON` | execução comparativa gera residual e decisão auditáveis |
| C2 | `EXECUTABLE_SHADOW` | teoria e código estão ligados numa rota não publicante |
| C1 | `LINKED` | fontes, família e caminho de implementação estão relacionados |
| C0 | `TOKEN_VAZIO_UNCALIBRATED` | ainda falta selecionar identidade ou comparação mínima |

A escala C não substitui P0–P5 nem S0–S9.

## 8. Portfólio inicial

### RLL de fundo

```text
P5_NEAR_OPERATIONAL
C2_EXECUTABLE_SHADOW
APPROX_WORKING
```

Equação e código estão ligados. O delta dominante está entre previsão e recibo robusto multi-seed.

### Setor escuro interagente

```text
P4_FORMALIZABLE_NEAR
C1_LINKED
TOKEN_VAZIO_UNDEFINED
```

O delta principal é selecionar um termo covariante `Q_mu` e materializar fundo mais perturbações.

### Reconstrução não paramétrica

```text
P4_FORMALIZABLE_NEAR
C1_LINKED
TOKEN_VAZIO_UNDEFINED
```

O observável existe, mas kernel, regularização, política de hiperparâmetros e cobertura ainda precisam ser congelados.

### Gravidade forte/plasma → cosmologia

```text
P2_BRIDGE_CANDIDATE
C1_LINKED
TOKEN_VAZIO_UNDEFINED
```

Mecanismos locais possuem implementação e literatura, mas falta operador de ponte e assinatura cosmológica independente da fonte.

### Extensões genéricas de Einstein

```text
P1_SPECULATIVE_SEED
C0_TOKEN_VAZIO_UNCALIBRATED
TOKEN_VAZIO_UNDEFINED
```

A família é ampla demais. Primeiro precisa ser escolhida uma ação ou família de equações específica.

## 9. Ciclo executável

```text
teoria
→ mapeamento operacional
→ shadow executável
→ observação prática
→ residual assinado
→ decisão do falsificador
→ recibo
→ próxima ponte
→ nova iteração Ω
```

A calibração nunca termina por beleza textual. Ela somente muda de estado quando um artefato novo modifica um delta verificável.

## 10. Regra final

\[
\boxed{
\text{conhecimento}
=
\text{dados preservados}
+
\text{relações explícitas}
+
\text{contradições}
+
\text{lacunas}
+
\text{execuções}
+
\text{recibos}
}
\]

O objetivo não é forçar teoria e prática a parecerem iguais. O objetivo é tornar observável, reproduzível e corrigível cada passo que as aproxima ou as afasta.
