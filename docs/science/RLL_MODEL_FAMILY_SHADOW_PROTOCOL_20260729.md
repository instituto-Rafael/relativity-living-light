# RLL — Protocolo de famílias de modelos sem adaptação numérica

**Estado:** `EXPERIMENTAL_SHADOW`  
**Data:** 2026-07-29  
**Claim:** `claim_allowed=false`  
**Regra central:** comparar estruturas; não ajustar a régua depois de olhar o placar.

## 1. Intenção

O objetivo não é fazer o RLL “lutar” contra outros modelos cosmológicos.

O objetivo é construir um torneio justo:

```text
dados imutáveis
→ covariância imutável
→ fórmulas predeclaradas
→ bounds predeclarados
→ mesma função objetivo
→ mesma semente
→ comparação
→ análise de resíduos e identificabilidade
```

A execução paralela é deliberadamente separada do artefato canônico:

```text
results/structure_d/joint_real_likelihood.*   = preservado
results/structure_d/model_family_shadow.*     = novo benchmark paralelo
```

Nenhum resultado deste benchmark promove, rebaixa ou substitui os resultados canônicos.

---

## 2. Achados estruturais que motivaram a rota paralela

### 2.1 Fechamento e geometria

O pipeline canônico atual ajusta `Om` e `OL` independentemente nos modelos de fundo. Isso permite:

\[
\Omega_m+\Omega_\Lambda+\Omega_r\neq1.
\]

Entretanto, a distância transversal é calculada como distância comóvel plana. Assim, a liberdade numérica pode representar curvatura implícita em \(H(z)\), enquanto a geometria usada em BAO continua plana.

A correção usada no benchmark shadow é:

- modelos planos: \(\Omega_{de,0}=1-\Omega_{m,0}-\Omega_{r,0}-\sum\Omega_{extra,0}\);
- modelo curvo: \(\Omega_{de,0}=1-\Omega_{m,0}-\Omega_{r,0}-\Omega_{k,0}\);
- quando \(\Omega_k\neq0\), a distância transversal usa explicitamente \(S_k(\chi)\).

Portanto:

\[
\boxed{\text{curvatura no fundo}\Rightarrow\text{curvatura na distância}}
\]

### 2.2 CMB comprimido

O pipeline canônico calcula a escala acústica usando o `r_d` aproximado. Porém, \(\ell_A\) requer o horizonte sonoro na recombinação, \(r_s(z_*)\), e não simplesmente o horizonte na época de arrasto bariônico.

Até existir backend explícito para \(r_s(z_*)\), o benchmark registra:

```text
CMB_shift = TOKEN_VAZIO_RS_STAR_BACKEND
```

### 2.3 Crescimento

A aproximação:

\[
f\sigma_8\propto \Omega_m(z)^{0.55}
\]

não constitui backend de perturbações igualmente válido para todas as famílias, especialmente fluidos não padrão, setores interagentes ou componentes com dinâmica própria.

Até existir CLASS/CAMB ou equação de crescimento específica por modelo:

```text
fsigma8 = TOKEN_VAZIO_MODEL_SPECIFIC_GROWTH
```

### 2.4 Contagem observacional

Quando a covariância CMB completa contém três observáveis \((R,\ell_A,\omega_b)\), `N` precisa contar três termos, não dois. O benchmark shadow evita essa ambiguidade porque usa somente:

```text
H(z) + DESI DR2 BAO
```

Logo:

\[
N=N_{H(z)}+N_{BAO}.
\]

---

## 3. Dez modelos fundamentais

| ID | Família | Núcleo físico/matemático |
|---|---|---|
| `FLCDM` | baseline plano | constante cosmológica com fechamento explícito |
| `oLCDM` | geometria | LCDM com \(\Omega_k\) e distância curva coerente |
| `wCDM` | EoS constante | \(w=\mathrm{constante}\) |
| `CPL` | EoS dinâmica | \(w(a)=w_0+w_a(1-a)\) |
| `JBP` | EoS dinâmica | \(w(z)=w_0+w_a z/(1+z)^2\) |
| `BA` | EoS dinâmica regular | \(w(z)=w_0+w_a z(1+z)/(1+z^2)\) |
| `FSLL1` | EoS dinâmica regular | \(w(z)=w_0+w_a z/(1+z^2)\) |
| `PEDE` | emergência tardia | densidade escura emerge fenomenologicamente em baixo redshift |
| `GCG` | fluido efetivo | família generalized Chaplygin gas usada como setor DE separado |
| `RLL` | transição logística | setor RLL matéria-like ↔ constante-like com fechamento plano |

As famílias CPL, JBP, BA e FSLL1 não são tratadas como quatro “verdades físicas”. Elas são quatro coordenatizações adversariais para testar quanto uma conclusão depende da parametrização escolhida.

Referências primárias registradas no contrato:

- Chevallier & Polarski (2001), DOI `10.1142/S0218271801000822`;
- Linder (2003), DOI `10.1103/PhysRevLett.90.091301`;
- Jassal, Bagla & Padmanabhan (2005), DOI `10.1111/j.1745-3933.2005.08577.x`;
- Barboza & Alcaniz (2008), DOI `10.1016/j.physletb.2008.08.012`;
- Li & Shafieloo, arXiv `1906.08275`;
- Feng, Shen, Li & Li, arXiv `1206.0063`;
- generalized Chaplygin gas, arXiv `astro-ph/0304325`.

---

## 4. Cinco composições permitidas

O benchmark não executa todas as permutações combinatórias.

Ele permite apenas composições ancoradas no RLL:

```text
RLL + wCDM
RLL + CPL
RLL + JBP
RLL + BA
RLL + PEDE
```

A forma geral é:

\[
E^2(z)=
\Omega_m(1+z)^3
+\Omega_r(1+z)^4
+\Omega_{de,0}g_{de}(z)
+\Omega_{s0}g_{RLL}(z),
\]

com:

\[
\Omega_{de,0}=1-\Omega_m-\Omega_r-\Omega_{s0}.
\]

Isso impede que a soma das densidades seja ajustada livremente para absorver resíduos.

### Propriedade de aninhamento

Cada composição precisa satisfazer:

\[
\Omega_{s0}=0
\Rightarrow
\text{modelo companheiro recuperado exatamente}.
\]

O RLL puro precisa satisfazer:

\[
\Omega_{s0}=0
\Rightarrow
\mathrm{FLCDM}.
\]

Esses invariantes estão cobertos por testes automatizados.

---

## 5. Permutações bloqueadas

As seguintes classes não entram automaticamente:

### Duas parametrizações do mesmo setor

```text
CPL + JBP
CPL + BA
JBP + FSLL1
```

Elas descrevem o mesmo setor de energia escura com funções concorrentes. Somá-las sem dois fluidos fisicamente definidos tende a produzir redundância, degenerescência e parâmetros não identificáveis.

### RLL + EDE

Permanece:

```text
TOKEN_VAZIO_EARLY_TIME_BACKEND
```

O setor RLL se torna matéria-like em uma região de redshift. Misturá-lo com energia escura primordial sem CMB e perturbações completas pode tornar os setores indistinguíveis.

### RLL + GCG

Permanece:

```text
TOKEN_VAZIO_DENSITY_SECTOR_DEGENERACY
```

Ambos podem interpolar comportamentos efetivos distintos ao longo do redshift. A composição só deve ser liberada depois de Fisher, posterior e análise de correlação.

---

## 6. Regra antiadaptação

É proibido depois de observar os resultados:

- alterar dados para um modelo;
- alterar barras de erro para um modelo;
- trocar covariância;
- mudar `bounds` apenas no modelo que falhou;
- remover parâmetros de `k`;
- mudar `N`;
- trocar semente até aparecer resultado desejado;
- selecionar somente a parametrização favorável;
- excluir um ponto porque ele prejudicou um modelo sem ablação predeclarada.

O contrato congela:

```text
mesmos dados
mesma covariância
mesma função objetivo
mesma semente por rodada
bounds anteriores à execução
k = quantidade real de parâmetros livres
```

A robustez exige todas as sementes predeclaradas:

```text
11, 23, 37, 53, 71
```

Uma execução isolada pode gerar diagnóstico, mas não ranking promovível.

---

## 7. Dados usados no benchmark

Incluídos:

```text
data/real/Hz_data_real.csv
data/real/cosmology/desi_dr2_bao_primary_points.csv
data/real/desi_dr2_bao_covariance.csv
```

Fallback de covariância:

```text
data/real/cosmology/desi_dr2_bao_covariance_summary.csv
```

Excluídos até implementação correta:

```text
CMB compressed → TOKEN_VAZIO_RS_STAR_BACKEND
fσ8           → TOKEN_VAZIO_MODEL_SPECIFIC_GROWTH
Pantheon+     → TOKEN_VAZIO_MATERIALIZATION_OR_LIKELIHOOD
```

A exclusão não significa que esses dados sejam ruins. Significa que um torneio amplo não deve reutilizar um backend aproximado como se fosse igualmente correto para todos os modelos.

---

## 8. Execução

Todos os modelos:

```bash
python -m data.pipelines.structure_d.model_family_shadow
```

Somente os dez modelos fundamentais:

```bash
RLL_MODEL_FAMILY_MODE=core \
python -m data.pipelines.structure_d.model_family_shadow
```

Somente composições:

```bash
RLL_MODEL_FAMILY_MODE=compositions \
python -m data.pipelines.structure_d.model_family_shadow
```

Configuração explícita:

```bash
RLL_MODEL_FAMILY_SEED=11 \
RLL_MODEL_FAMILY_MAXITER=120 \
RLL_MODEL_FAMILY_TOL=1e-6 \
python -m data.pipelines.structure_d.model_family_shadow
```

Saídas:

```text
results/structure_d/model_family_shadow.json
results/structure_d/model_family_shadow.csv
```

Cada saída registra:

- hash SHA-256 das entradas;
- commit SHA;
- dados e covariância usados;
- seed, tolerância e iterações;
- `N`, `k`, `dof`;
- decomposição de \(\chi^2\);
- AIC, AICc e BIC;
- parâmetros ajustados;
- `claim_allowed=false`.

---

## 9. O que significa “dar certo”

Não significa obter o menor \(\chi^2\) em uma rodada.

Um modelo “dá certo” somente quando sobrevive simultaneamente a:

\[
\boxed{
\text{coerência matemática}
\cap
\text{fechamento físico}
\cap
\text{estabilidade multi-seed}
\cap
\text{parâmetros identificáveis}
\cap
\text{resíduos sem estrutura}
\cap
\text{dados independentes}
}
\]

Uma composição que reduz \(\chi^2\) mas produz correlações quase unitárias entre parâmetros deve permanecer:

```text
TOKEN_VAZIO_IDENTIFIABILITY
```

O próximo gate quantitativo é:

```text
multi-seed
→ Fisher/posterior
→ matriz de correlação
→ profile likelihood
→ ablação por dataset
→ posterior predictive checks
```

---

## 10. Síntese

A arquitetura deixa de perguntar:

> “Como fazer o RLL vencer?”

E passa a perguntar:

> “Qual estrutura explica os mesmos dados com geometria, fechamento, parâmetros e incertezas coerentes — e continua estável quando mudamos a parametrização sem mudar os números?”

```text
F_ok   = 10 modelos + 5 composições + fechamento + distância curva + antiadaptação.
F_gap  = execução remota completa, multi-seed, Pantheon+, r_s(z*) e crescimento específico.
F_next = rodar o shadow benchmark e auditar identificabilidade antes de qualquer claim.
```
