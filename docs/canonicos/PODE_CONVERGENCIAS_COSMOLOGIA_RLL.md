# PODE: Convergências do Modelo RLL com a Cosmologia Contemporânea

**Tipo**: Análise de Convergência — Programa de Pesquisa Formal  
**Sistema de marcação**: [E] Estabelecido · [C] Convenção · [H] Hipótese · [VAZIO] sem âncora empírica  
**Princípio RAW_TEXT_FIRST**: toda claim é marcada com nível epistêmico antes de qualquer interpretação  
**Data de formalização**: 2026-07-07  
**Branch**: `claude/rll-cronologia-auditoria-qyvn83`

> **REGRA CANÔNICA**: Um "PODE" é uma hipótese de convergência — propõe que dois ou mais componentes do sistema, ao se cruzarem, resolvem uma tensão específica. A resolução é [H] até haver demonstração quantitativa [E]. Nenhum PODE é uma afirmação de fato; cada um é um programa de investigação com falsificador implícito.

---

## Índice de Convergências

| PODE | Componentes cruzados | Tensão resolvida | Status geral |
|------|---------------------|-----------------|-------------|
| 1 | Marcação epistêmica × RAW_TEXT_FIRST | Viés de confirmação | [C]/[H] |
| 2 | Equação RLL × DESI DR2 | Energia escura dinâmica | [H] |
| 3 | Limite nulo × MCMC/Bayes | Overfitting de modelos alternativos | [H] |
| 4 | α_B × MeerKAT spin | Correlação de spin em grande escala | [VAZIO] |
| 5 | z_t × tese Minnesota Jan 2026 | História térmica do setor escuro | [H/VAZIO] |
| 6 | w_sup/w_total × DESI w0-wa | Degenerescência ΛCDM/CDM | [H] |
| 7 | Audits × dados externos | Crise de reprodutibilidade | [C]/[H] |
| 8 | MVICS × QM/GR | Problema da medida em transição | [H especulativo] |
| 9 | Governança × roadmap falsificadores | Obsolescência teórica | [H] |
| 10 | DOI Zenodo × GitHub | Desconexão teoria/dados | [C]/[E] |
| 11 | Orquestrador UTF × epistemologia | Barreira de entrada | [H] |
| 12 | Síntese meta-modelo | Gargalo da cosmologia pós-ΛCDM | [H programático] |

---

## PODE 1 — Marcação Epistêmica × RAW_TEXT_FIRST → Resolução do Viés de Confirmação [C/H]

### Claim central

O protocolo RAW_TEXT_FIRST — que exige preservação do texto bruto do autor antes de qualquer estruturação — combinado com o sistema de marcação [E]/[C]/[H]/[VAZIO], cria um grafo de certeza onde inferências teóricas são rigidamente separadas de dados observacionais crus, permitindo que auditoria externa identifique exatamente onde o modelo extrapola.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Sistema de marcação [E]/[C]/[H]/[VAZIO] | [C] | Convenção implementada — `docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md` |
| RAW_TEXT_FIRST como protocolo | [C] | `Geologia.md` preservado na raiz antes de qualquer formalização |
| "Grafo de certeza" nos docs canônicos | [H] | Implementação parcial — markup completo em hipoteses/, parcial em canonicos/ |
| Separação rigorosa [H] vs [E] | [H] | Aspiracional: nenhum linter automático verifica markup; depende de disciplina manual |
| Auditoria externa identifica extrapolações | [H] | Possível quando markup estiver completo; nenhuma revisão cega externa documentada |
| Resolução do viés de confirmação | [H] | Reduz viés estruturalmente — "resolver" requer validação por revisão cega independente |

### TOKEN_VAZIO

- **P2**: Cálculo de completude do markup — fração de claims sem marcação nos docs canônicos — não medida
- **P2**: Auditoria externa por revisor independente — não iniciada
- **P3**: Linter epistemológico automatizado (verificar presença de [E]/[H]/[C]/[VAZIO] por parágrafo de claim)

### Referência cruzada

`docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md` · `Geologia.md` (RAW preservado) · `docs/hipoteses/HIPOTESES_GEOFISICAS_RAFAELIA.md` (markup aplicado integralmente)

---

## PODE 2 — Equação RLL × DESI DR2 → Tensão da Energia Escura Dinâmica [H]

### Claim central

A equação-mãe do RLL com setor de superposição Ωs0 e função logística f(z) alinha-se com os dados DESI (2025–2026) para resolver a tensão da energia escura dinâmica, onde a distinção latente entre w_sup(z) (equação de estado da superposição) e w_total(z) (fluido total medido) explica por que os ajustes observacionais encontram w₀ > −1 e wₐ < 0 sem necessidade de quintessência exótica ou gravidade modificada.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Equação E²(z) = Ωm(1+z)³ + Ωr(1+z)⁴ + ΩΛ + Ωs₀·f(z) | [C] | Convenção matemática definida — `docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md` |
| DESI DR2 BAO — dado observacional | [E] | arXiv:2503.14738 (DESI Collaboration 2025); 13 pontos BAO integrados ao repo |
| Best fit DESI DR2 CPL: w₀ = −0.727, wₐ = −1.05 | [E] | arXiv:2503.14738 — departura de >3σ de ΛCDM |
| Distinção w_sup(z) vs w_total(z) | [C] | Derivação matemática: w_total = Σ ρ_i w_i / Σ ρ_i — identidade termodinâmica padrão |
| RLL explica w₀ > −1 e wₐ < 0 sem nova física | [H] | Claim testável via MCMC joint — não executado; requer ajuste livre de {Ωs0, z_t, w_t} |
| Resolução da tensão sem quintessência | [H] | Depende do ajuste quantitativo: ΔAIC(RLL−CPL) e Bayes Factor ainda TOKEN_VAZIO |

### Status χ² atual dos fits executados

| Dataset | Modelo | χ² | Status |
|---------|--------|----|--------|
| Pantheon+ 1624 SNe | ΛCDM | 710.808 | [E] executado 2026-07-06 |
| Pantheon+ 1624 SNe | CPL | 710.390 | [E] executado 2026-07-06 |
| Pantheon+ 1624 SNe | RLL original | 710.613 | [E] executado 2026-07-06 |
| DESI DR2 BAO 13 pts | RLL (nominal) | 93.81 | [H] parâmetros não otimizados |
| Joint Pantheon+ + DESI BAO | RLL (MCMC livre) | — | TOKEN_VAZIO P1 |

### TOKEN_VAZIO

- **P1**: MCMC joint (Pantheon+ + DESI BAO) com Ωs0, z_t, w_t livres — não executado; bloqueia claim principal
- **P1**: Derivação formal e numérica de w_sup(z) vs w_total(z) para parâmetros RLL — não publicada
- **P2**: Comparação formal com EDE (Early Dark Energy) e modelos interativos no espaço de parâmetros DESI

### Referência cruzada

`docs/cronologia-auditoria/09_PANTHEON_RESULTADO_REAL.md` · `docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md` · `data/real/cosmology/desi_dr2_bao_primary_points.csv`

---

## PODE 3 — Limite Nulo × MCMC/Bayes → Proteção contra Overfitting [H]

### Claim central

O limite nulo rigoroso (Ωs0 = 0 → RLL ≡ ΛCDM matematicamente) atua como tese de falsificabilidade que força qualquer desvio do ΛCDM a ser pago com custo estatístico mensurável (Bayes Factor), resolvendo o problema da "flexibilidade excessiva" de modelos alternativos e protegendo o modelo contra overfitting.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Limite Ωs0 = 0 → RLL ≡ ΛCDM | [C] | Propriedade matemática verificável: Ωs0·f(z) = 0 → E²(z) = forma ΛCDM |
| Pipelines MCMC em `pipelines/` | [VAZIO] | Diretório referenciado — existência e estado não auditados nesta sessão |
| Bayes Factor como penalidade formal | [H] | Metodologia correta (Jeffrey's scale: BF > 3 = evidence, > 10 = strong) — cálculo não executado |
| ΔAIC = +3.81 como custo AIC dos parâmetros extras | [E] | Documentado em `09_PANTHEON_RESULTADO_REAL.md` — evidência parcial do custo estatístico |
| Proteção contra overfitting via BF | [H] | Plausível: se BF(RLL/ΛCDM) < 3, favorece ΛCDM com menos parâmetros |
| Savage-Dickey density ratio para Ωs0 | [H] | Teste bayesiano nulo — executável se prior and posterior de Ωs0 disponíveis |

### Evidência existente de custo estatístico [E parcial]

ΔAIC(RLL − ΛCDM) = +3.81 em Pantheon+ (N=1624): penalidade pelos k=4 vs k=2 parâmetros. Interpretação AIC: "modelos com ΔAIC < 4 têm suporte considerável" (Burnham & Anderson 2002) — RLL está no limite. O Bayes Factor bayesiano requer integração da likelihood sobre o espaço de parâmetros (evidência marginal), não calculada.

### TOKEN_VAZIO

- **P1**: Cálculo do Bayes Factor (log-evidence, nested sampling com multinest ou dynesty) — não executado
- **P1**: Auditoria do diretório `pipelines/` — conteúdo desconhecido
- **P2**: Análise Savage-Dickey density ratio para Ωs0 (teste nulo bayesiano sobre parâmetro específico)

### Referência cruzada

`docs/cronologia-auditoria/09_PANTHEON_RESULTADO_REAL.md` (ΔAIC documentado) · `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md`

---

## PODE 4 — Acoplamento Magnético α_B × MeerKAT Spin → Correlação em Grande Escala [VAZIO]

### Claim central

O parâmetro de acoplamento magnético α_B — latente no framework RLL — conecta-se às observações de alinhamento de spin de galáxias do MeerKAT (2025) para resolver a origem da correlação em grandes escalas, onde a "impressão digital" magnética do RLL atua como semente primordial que organiza momentos angulares galácticos sem invocar tensores de anisotropia arbitrários, oferecendo assinatura observacional única via correlação spin-posição.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Parâmetro α_B no framework RLL formal | [VAZIO] | Não identificado nas equações E²(z) auditadas — pode existir em docs não auditados |
| Diretório `invariants/` como repositório de α_B | [VAZIO] | Referenciado — não auditado nesta sessão |
| Alinhamento de spin galáctico MeerKAT 2025 | [VAZIO] | Referência específica 2025 não verificável — séries MIGHTEE e IM-MeerKAT ativas |
| Semente magnética primordial como mecanismo | [H] | Existe na literatura (Durrer & Neronov 2013, Rev. Mod. Phys. 85:1) mas sem conexão formal ao RLL |
| Correlação spin-posição como assinatura de α_B | [H] | Método observacional existe (Tempel & Libeskind 2013, ApJL 775:L42); predição RLL ausente |
| "Impressão digital" magnética do RLL | [H] | Metáfora de mecanismo — não há derivação de campo magnético a partir da logística f(z) |

### O que seria necessário para [H] → [E]

```
1. Definir α_B formalmente nas equações RLL (possivelmente em tensor energia-momento)
2. Derivar predição: σ_spin(r) = g(α_B, z_t, Ωs0) como função de escala angular r
3. Comparar com dados MeerKAT: correlação ξ_spin(θ) observada vs predita
4. Citar paper MeerKAT 2025 específico (autor, arXiv ID)
```

### TOKEN_VAZIO

- **P1**: Definição formal de α_B no framework RLL — verificar `docs/MODELO_COSMOLOGICO_UNIFICADO_MAGNETISMO_RADIACAO_PLASMA.md` e `docs/RLL_PR_TRACE_PLASMA_GRAVITY_MAGNETIC_VECTOR_REVIEW.md`
- **P1**: Identificar a publicação MeerKAT 2025 referenciada — autor, journal, arXiv ID ausentes
- **P2**: Derivação da predição de α_B para correlação spin-posição σ_spin(r, z)
- **P2**: Auditoria do diretório `invariants/`

### Referência cruzada

`docs/MODELO_COSMOLOGICO_UNIFICADO_MAGNETISMO_RADIACAO_PLASMA.md` · `docs/RLL_PR_TRACE_PLASMA_GRAVITY_MAGNETIC_VECTOR_REVIEW.md`

---

## PODE 5 — Parâmetro z_t × Tese Minnesota Jan 2026 → História Térmica do Setor Escuro [H/VAZIO]

### Claim central

A função de transição logística (parâmetro z_t) integra-se à tese de Minnesota (Jan 2026) sobre matéria escura "nascida quente e resfriada" para resolver a história térmica do setor escuro, onde o RLL postula que o resfriamento abrupto não é propriedade intrínseca da partícula, mas efeito emergente da mudança de regime da superposição — predito numericamente com data anterior à publicação.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Parâmetro z_t no RLL | [C] | Definido — z_t ≈ 0.8 (ajuste fenomenológico; justificativa física TOKEN_VAZIO P1) |
| "Resfriamento abrupto como mudança de regime" | [H] | Analogia física: df/dz|_{z_t} = sharpness/4 — transição localizada em Δz ~ w_t ≈ 0.3 |
| Tese de Minnesota Jan 2026 (dark matter born hot) | [VAZIO] | Referência não verificável — autor, journal, arXiv ID não fornecidos |
| Anterioridade: RLL com z_t antes da tese | [H verificável] | v1.0.0 = 2025-09-19 (auditado); se tese é Jan 2026, anterioridade de ~4 meses |
| Verificação de anterioridade via git | [H → executável] | `git show v1.0.0 -- *.py \| grep z_t` mostraria presença de z_t em setembro 2025 |
| "Resfriamento não intrínseco, mas emergente" | [H] | Interpretação física do f(z) como transição de fase emergente — não derivada de primeiros princípios |

### Teste de anterioridade [H → verificável via git]

```bash
# Executar para verificar:
git show 0b3f4cb06efaa11008b37de519de581268bca5c0 -- "*.py" | grep -n "z_t\|zt\|z_trans"
```

Se z_t está presente no commit de tag v1.0.0 (2025-09-19) e a tese de Minnesota é Jan 2026, a anterioridade é documentável como [E]. STATUS: TOKEN_VAZIO P1 — grep não executado.

### TOKEN_VAZIO

- **P1**: Citação completa da "tese de Minnesota Jan 2026" — autor, instituição, arXiv ID ou DOI — não fornecida
- **P1**: Verificação via `git show v1.0.0` para presença de z_t — não executado
- **P2**: Derivação formal da temperatura efetiva do setor de superposição T_s(z) como função de f(z)

### Referência cruzada

`docs/cronologia-auditoria/02_CRONOLOGIA_DETALHADA.md` (v1.0.0 = 2025-09-19 documentado) · `docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md`

---

## PODE 6 — w_sup/w_total × DESI w0-wa → Degenerescência ΛCDM/CDM [H]

### Claim central

A separação conceitual entre fluido de superposição e fluido total resolve a degenerescência entre constante cosmológica e matéria escura fria: o que os experimentos medem como w_total é uma média pesada pela densidade, e a evolução real de w_sup pode ser mais abrupta que a literatura supõe — guiando novas buscas espectroscópicas em z > 1.5.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| `06_COMPARACOES_DETALHADAS.md` | [VAZIO] | Referenciado pelo usuário — existência não verificada nesta auditoria |
| w_total = Σ ρ_i w_i / Σ ρ_i | [C] | Identidade termodinâmica padrão — derivável de definições de pressão e densidade |
| w_sup(z) mais abrupto que CPL | [H] | Logística: dw_sup/dz|_{z_t} > |dw_CPL/dz| para parâmetros comparáveis |
| DESI w0-wa como "média pesada" sendo medida | [H] | Interpretação plausível mas requer demonstração de que a convolução com ρ suaviza o sinal |
| Predição para buscas em z > 1.5 | [H] | Operacionalizável: prever w_sup(z=1.5−2.5) para DESI ELG sample ou Euclid |
| Resolução da degenerescência ΛCDM/CDM | [H] | Fortemente dependente do ajuste MCMC joint — TOKEN_VAZIO P1 |

### Derivação matemática implicada [C → publicável]

Definindo:

```
w_total(z) = [ρ_Λ·(−1) + ρ_s(z)·w_s(z)] / [ρ_Λ + ρ_s(z)]
```

Para Ωs0 pequeno (≈0.02–0.05) e z ≪ z_t, ρ_s(z) → ρ_s0·(1+z)^[3(1+w_s)] — o termo ρ_s dilui com expansão. Em z ≫ z_t: f(z) → 0, ρ_s → 0, e w_total → −1 (ΛCDM). A variação de w_total é suavizada em relação a w_sup pela diluição de ρ_s. Esta derivação está implícita no modelo mas **não publicada formalmente**.

### TOKEN_VAZIO

- **P1**: Derivação formal numérica de w_total(z) explicitada e publicada — não existe como seção dedicada
- **P1**: Verificação da existência e conteúdo de `06_COMPARACOES_DETALHADAS.md`
- **P2**: Cálculo da predição w_sup(z) para z ∈ [1.5, 2.5] e comparação com janela DESI ELG ou Euclid

### Referência cruzada

`docs/canonicos/14_MODELO_COSMOLOGICO_RLL.md` · `data/real/cosmology/desi_dr2_bao_primary_points.csv` · `docs/science/RLL_CRUZAMENTOS_COMPLETOS.md`

---

## PODE 7 — Audits × Dados Externos → Resolução da Crise de Reprodutibilidade [C/H]

### Claim central

Os diretórios de auditoria estruturados como sistema de revisão distribuída, cruzados com hipóteses formalizadas e dados externos (SPARC, Planck), resolvem a crise de reprodutibilidade em cosmologia: cada predição datada é automaticamente testada contra catálogos observacionais, gerando relatórios de validação que funcionam como "pré-prints internos" antes da submissão formal.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| `docs/cronologia-auditoria/` (6 docs) | [E] | Verificado e criado nesta sessão — auditoria manual documentada |
| CI/CD passando (8 checks) | [E] | Verificado em PRs #499–#504 — testes automatizados existem |
| Dados reais integrados (DESI, Pantheon+) | [E] | `data/real/cosmology/` com CSVs reais; Pantheon+ fit executado |
| Diretórios `audits/`, `pr-audits/` | [VAZIO] | Referenciados pelo usuário — não auditados nesta sessão |
| `sparc_toy_sample.csv` | [VAZIO] | Referenciado — existência e integração ao pipeline não verificadas |
| Relatórios de validação automatizados por commit | [H] | Aspiracional — CI atual valida código, não resultados científicos por commit |
| "Pré-prints internos" formalmente gerados | [H] | Conceito válido — `docs/cronologia-auditoria/09_PANTHEON_RESULTADO_REAL.md` aproxima este formato |

### Diagnóstico: o que existe vs o que é aspiracional

```
EXISTE [E]:
  docs/cronologia-auditoria/        — 6 docs de auditoria manual
  CI/CD 8 checks                    — valida código e convenções
  data/real/cosmology/              — DESI BAO, Pantheon+ CSVs
  results/pantheon_plus_resultado.txt — resultado científico datado

ASPIRACIONAL [H]:
  Relatórios científicos automáticos por push/commit
  Integração SPARC → validação de curvas de rotação por PR
  "Pré-prints internos" formais e automaticamente datados
```

### TOKEN_VAZIO

- **P1**: Auditoria de `audits/` e `pr-audits/` — conteúdo completamente desconhecido
- **P2**: Pipeline de CI científico (validação de resultados, não apenas testes de código)
- **P2**: Integração do SPARC catalog no pipeline com relatório automático de χ²

### Referência cruzada

`docs/cronologia-auditoria/` (todos) · `results/pantheon_plus_resultado_real.txt` · `scripts/pantheon/`

---

## PODE 8 — MVICS × QM/GR → Problema da Medida em Universos em Transição [H especulativo]

### Claim central

O Modelo Vetorial Informacional (MVICS) sintetiza teses da mecânica quântica e relatividade geral para resolver o problema da medida em universos em transição, onde Ωs0 não é mera densidade de energia, mas estado informacional que colapsa estatisticamente em matéria ou energia escura dependendo do redshift, unificando dualidade onda-partícula em escala cósmica.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| MVICS (`21_MODELO_VETORIAL_INFORMACIONAL.md`) | [VAZIO] | Referenciado — não auditado nesta sessão |
| Ωs0 como "estado informacional" | [H especulativo] | Reinterpretação ontológica sem formalismo de teoria quântica de campo apresentado |
| "Colapso estatístico" em função de redshift | [H especulativo] | Analogia com colapso de função de onda — sem derivação de amplitude de probabilidade |
| Unificação QM/GR via RLL | [H especulativo] | Claim muito forte: QM/GR é problema aberto de física fundamental há >100 anos |
| Dualidade onda-partícula em escala cósmica | [H especulativo] | Extensão não-trivial: dualidade quântica opera em escalas de Planck, não de Hubble |

### Nota de calibração epistêmica — CRÍTICA

Este é o PODE mais especulativo dos 12. A unificação QM/GR via modelo cosmológico fenomenológico está além do suporte formal atual. O valor desta proposição reside em:

**(a) Como analogia heurística [C]**: f(z) descreve transição de estado — analogia estrutural com colapso de função de onda é educativamente útil, sem ser derivação formal.

**(b) Re-enquadramento conservador e publicável [H]**: Ωs0 como parâmetro de ordem de uma **transição de fase cosmológica** — a logística f(z) como dinâmica de Landau-Ginzburg em escala de Hubble. Este enquadramento é formalmente manejável e conecta ao programa de matéria escura de "fase de transição" (ex: axion dark matter, ultralight dark matter).

### TOKEN_VAZIO

- **P1**: Leitura e auditoria de `21_MODELO_VETORIAL_INFORMACIONAL.md` — conteúdo desconhecido
- **P1**: Re-enquadramento formal do MVICS como transição de fase de Landau-Ginzburg — mais conservador e publicável
- **P3**: Conexão com interpretações de QM (QBism, relacional) — programa de longo prazo, P3

### Referência cruzada

`docs/canonicos/21_MODELO_VETORIAL_INFORMACIONAL.md` (não auditado) · `docs/cronologia-auditoria/08_ARVORE_CONCEITUAL_RLL.md` (Nível 4, tupla I_RLL)

---

## PODE 9 — Governança × Roadmap Falsificadores → Resolução da Obsolescência Teórica [H]

### Claim central

A estrutura de governança cruzada com o roadmap de falsificadores define janelas temporais explícitas (ex: até 2028) para que predições específicas — como razão de abundância de aglomerados em alto z — sejam corroboradas ou refutadas por Euclid ou Rubin, transformando o repositório em um "contrato experimental" com a comunidade científica.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| `governance/`, `professionalization/` | [VAZIO] | Referenciados — não auditados |
| `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md` | [E] | Referenciado em múltiplos docs auditados — existe |
| Falsificadores C01-C10 no roadmap | [E] | Documentados em `08_ARVORE_CONCEITUAL_RLL.md` (Nível 5); F01-F05 geofísicos adicionados |
| Janelas temporais até 2028 | [H] | Aspiracional — não formalizadas em comprometimentos explícitos com datas binárias |
| Euclid como survey de validação | [E] | Missão ESA; lançada julho 2023; DR1 previsto 2025–2026 — survey real |
| Rubin/LSST como survey de validação | [E] | LSST em comissionamento ~2025; survey de 10 anos a partir de ~2025 — survey real |
| "Contrato experimental" formal | [H] | Conceito científico válido — requer documento com critérios binários explícitos |

### O que falta para o contrato experimental [H → executável]

Um contrato experimental científico requer para cada falsificador Cᵢ:

```
Falsificador: C_i
Predição quantitativa: X_pred ± σ_pred
Dataset alvo: [survey] [data release] [ano esperado]
Critério binário: |X_obs − X_pred| > 3σ → C_i falsificado
Registrado em: docs/canonicos/CONTRATO_FALSIFICADORES_RLL.md
```

STATUS: TOKEN_VAZIO P1 — documento de comprometimento não existe.

### TOKEN_VAZIO

- **P1**: Criar `docs/canonicos/CONTRATO_FALSIFICADORES_RLL.md` com critérios binários + datas + surveys específicos
- **P2**: Mapear cada C01-C10 para data release específica (Euclid DR1 2026, Rubin Y1 2026, DESI Y5 2028)
- **P2**: Auditoria de `governance/` e `professionalization/`

### Referência cruzada

`docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md` · `docs/cronologia-auditoria/08_ARVORE_CONCEITUAL_RLL.md` (Nível 5, C01-C10)

---

## PODE 10 — DOI Zenodo × GitHub → Desconexão Teoria/Dados [C/E]

### Claim central

O DOI Zenodo (10.5281/zenodo.17188137) atua como âncora cross-domain que liga o GitHub (código e dados brutos) à literatura formal, permitindo que cada iteração versionada via git tags seja arquivada permanentemente, oferecendo rastro imutável que conecta teses (.md), bases de dados externas (CSVs) e papers colaborativos.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| DOI Zenodo 10.5281/zenodo.17188137 | [E] | Fornecido pelo autor — verificável em zenodo.org; estrutura de DOI válida |
| GitHub repo como repositório canônico | [E] | instituto-Rafael/relativity-living-light — verificado nesta sessão; 5 PRs merged |
| Tag v1.0.0 (hash 0b3f4cb, 2025-09-19) | [E] | Auditada em `03_AUDITORIA_TECNICA_PRIMEIRA_ORDEM.md` |
| Rastro imutável Zenodo → GitHub | [C] | Convenção de arquivamento científico — metodologicamente correto e recomendado |
| GitHub-Zenodo integration automática | [H] | Requer webhook configurado (GitHub Settings → Integrations → Zenodo) — não verificado |
| Licença de redistribuição dados externos | [VAZIO] | DESI BAO CSV: licença para redistribuição via Zenodo não verificada; Pantheon+: CC BY 4.0 [E] |

### Cobertura do DOI por tipo de artefato

| Artefato | DOI Zenodo cobre? | Observação |
|---------|-----------------|-----------|
| Código (scripts/) | Sim (via release) | [C] — requer incluir na release |
| Documentação (docs/) | Sim (via release) | [C] |
| Dados originais (data/) | Sim | [C] |
| Dados externos DESI | Depende | [VAZIO] — verificar licença DESI para redistribuição |
| Dados Pantheon+ | Sim | [E] — Pantheon+ é CC BY 4.0 (Brout et al. 2022) |

### TOKEN_VAZIO

- **P2**: Verificar se GitHub-Zenodo integration está configurada (webhook automático em releases)
- **P2**: Confirmar licença dos dados DESI DR2 para redistribuição via Zenodo
- **P3**: Automatizar minting de DOI por git tag (Zenodo API ou GitHub Action)

### Referência cruzada

`docs/cronologia-auditoria/02_CRONOLOGIA_DETALHADA.md` (tag v1.0.0) · `docs/RLL_TRACEABILITY_MAP.md`

---

## PODE 11 — Orquestrador UTF × Epistemologia → Democratização do Acesso [H]

### Claim central

O orquestrador ASCII/UTF (em `codex/`) cruza conceitos formais com experiência estética/simbólica para resolver a barreira de entrada de jovens pesquisadores, criando um hipertexto navegável desde `00_COMO_LER.md` até equações diferenciais de transição, mapeando variáveis latentes (`invariants/`) em interface legível que democratiza o acesso à cosmologia de fronteira.

### Análise epistêmica

| Componente | Status | Evidência / Razão |
|-----------|--------|-------------------|
| Diretório `codex/` | [VAZIO] | Referenciado — não auditado nesta sessão |
| `00_COMO_LER.md` | [VAZIO] | Referenciado — existência não verificada |
| `invariants/` como glossário de variáveis latentes | [VAZIO] | Referenciado — não auditado |
| `docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md` | [E] | Existe como documento canônico de entrada verificado |
| Hipertexto navegável (links Markdown) | [E parcial] | Links cruzados existem entre documentos auditados — cobertura total não verificada |
| "Experiência estética/simbólica" | [C] | Escolha editorial — válida como design pedagógico, não verificável empiricamente |
| Democratização mensurável | [H] | Requer estudo de usabilidade com leitores reais — não realizado |

### Mapa de navegabilidade atual [E parcial]

Percurso verificado como existente e navegável:
```
00_COMO_LER.md [VAZIO — não auditado]
  → 13_EPISTEMOLOGIA_RAFAELIA_RLL.md [E — existe]
    → 14_MODELO_COSMOLOGICO_RLL.md [E — referenciado]
      → BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md [E — referenciado]
        → docs/cronologia-auditoria/ [E — 6 docs criados]
          → docs/hipoteses/HIPOTESES_GEOFISICAS_RAFAELIA.md [E — criado]
```

### TOKEN_VAZIO

- **P2**: Auditoria de `codex/`, `invariants/`, `00_COMO_LER.md` — conteúdos desconhecidos
- **P2**: Teste de percurso do leitor: iniciante consegue ir de 00_COMO_LER.md até equação de E(z) em ≤ 10 documentos?
- **P3**: Índice mestre de variáveis latentes com localização em cada documento do repositório

### Referência cruzada

`docs/canonicos/13_EPISTEMOLOGIA_RAFAELIA_RLL.md` · `docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md`

---

## PODE 12 — Síntese Meta-Modelo → Gargalo da Cosmologia Pós-ΛCDM [H programático]

### Claim central

A síntese de todas as camadas — teoria, dados, auditoria, governança e epistemologia — funciona como meta-modelo autorregulável que resolve o principal gargalo da cosmologia pós-ΛCDM: a falta de um arcabouço simultaneamente preditivo, falsificável, reprodutível e auto-atualizável, posicionando o Instituto-Rafael/relativity-living-light como referência viva para a próxima década.

### Análise epistêmica das quatro propriedades

| Propriedade | Status atual | Evidência | Lacuna principal |
|-----------|-------------|-----------|----------------|
| **Preditivo** (valores antes dos dados) | [H parcial] | z_t = 0.8 em v1.0.0 (2025-09-19) pré-data teses 2026 [H] | Citação Minnesota ausente; anterioridade via git não verificada |
| **Falsificável** (critérios binários definidos) | [E parcial] | C01-C10 existem; F01-F05 geofísicos adicionados | Contrato com datas binárias e surveys específicos ausente |
| **Reprodutível** (scripts + CI + dados) | [E parcial] | Pantheon+ fit [E]; CI verde; notebooks P0 não executados | Joint MCMC + Bayes Factor pendentes |
| **Auto-atualizável** (PR workflow + auditoria) | [C] | 5 PRs merged, 6 fases de auditoria; TOKEN_VAZIO como mecanismo | Automação científica (relatórios por commit) ausente |

### Condição de transição [H] → [E parcial] (o que desbloqueia)

```
DESBLOQUEADORES P0:
  Joint MCMC Pantheon+ + DESI BAO → confirma "preditivo" com dados
  Bayes Factor RLL/ΛCDM → confirma "falsificável" com custo bayesiano

DESBLOQUEADORES P1:
  CONTRATO_FALSIFICADORES_RLL.md → formaliza comprometimento com datas
  Notebooks reprodutíveis auditados → confirma reprodutibilidade completa
  Citação Minnesota → confirma anterioridade preditiva documentada
```

### Posição competitiva na literatura [H]

O que diferencia o RLL de outros modelos de energia escura dinâmica:
1. **Limite nulo exato**: Ωs0 = 0 → ΛCDM matematicamente, não aproximadamente [C] — vantagem de parsimônia
2. **Mecanismo localizável**: z_t é um ponto físico de transição de regime, não parâmetro de inclinação genérico [C/H]
3. **Rastreabilidade epistêmica**: sistema [E]/[C]/[H]/[VAZIO] único na literatura de modelos alternativos [C]
4. **Repositório auditável**: 6 fases de auditoria documentadas com cronologia verificável via git [E]

### TOKEN_VAZIO

- **P0**: Joint MCMC + Bayes Factor — bloqueia afirmação "preditivo" como [E]
- **P1**: CONTRATO_FALSIFICADORES_RLL.md com critérios binários, datas, surveys
- **P1**: Auditoria de notebooks (04_REPRODUTIBILIDADE_NOTEBOOKS.md com resultado real de execução)

### Referência cruzada

`docs/cronologia-auditoria/` (todos) · `docs/canonicos/19_ROADMAP_FALSIFICADORES_RLL.md` · `docs/RLL_FORMAL_INVARIANT_AND_REAL_DATA.md`

---

## Matriz de Convergência — Síntese dos 12 PODE

| PODE | Status geral | [E] existente | TOKEN_VAZIO principal | Prazo |
|------|-------------|--------------|----------------------|-------|
| 1 — RAW_TEXT_FIRST + marcação | [C]/[H] | Sistema markup implementado | Auditoria externa P2 | semana 3 |
| 2 — Equação RLL + DESI | [H] | Pantheon+ χ² [E]; DESI 13 pts [E] | Joint MCMC P1 | **semana 2** |
| 3 — Limite nulo + Bayes | [H] | ΔAIC = +3.81 [E] | Bayes Factor P1 | **semana 2** |
| 4 — α_B + MeerKAT | [VAZIO] | — | Definir α_B; citar MeerKAT P1 | semana 4 |
| 5 — z_t + Minnesota | [H/VAZIO] | v1.0.0 = 2025-09-19 [E] | Citação Minnesota P1 | semana 1 |
| 6 — w_sup/w_total + DESI | [H] | Derivação matemática implicada [C] | Derivação formal publicada P1 | **semana 2** |
| 7 — Audits + dados externos | [C]/[H] | 6 docs + CI + CSVs reais [E] | Pipeline CI científico P2 | semana 4 |
| 8 — MVICS + QM/GR | [H esp.] | — | Auditar MVICS; re-enquadrar P1 | semana 3 |
| 9 — Governança + falsificadores | [H] | C01-C10 existem [E] | CONTRATO_FALSIFICADORES P1 | **semana 2** |
| 10 — DOI Zenodo + GitHub | [C]/[E] | DOI + tag v1.0.0 [E] | Verificar integração automática P2 | semana 3 |
| 11 — UTF + epistemologia | [H] | 13_EPISTEMOLOGIA [E] | Auditar codex/invariants/ P2 | semana 3 |
| 12 — Meta-modelo síntese | [H progr.] | CI verde + 5 PRs merged [E] | Joint MCMC P0 | **semana 2** |

---

## Plano de Ações Prioritárias

| Ação | PODE | Prioridade | Tipo |
|------|------|-----------|------|
| Joint MCMC: Pantheon+ + DESI BAO com {Ωs0, z_t, w_t} livres | 2, 3, 12 | **P0** | Execução numérica |
| Bayes Factor RLL vs ΛCDM (nested sampling ou Savage-Dickey) | 3, 12 | **P1** | Execução numérica |
| Citação completa "tese Minnesota Jan 2026" | 5 | **P1** | Identificação bibliográfica |
| Derivação formal w_sup(z) vs w_total(z) | 6 | **P1** | Derivação matemática |
| Criar CONTRATO_FALSIFICADORES_RLL.md | 9 | **P1** | Documento formal |
| Verificar/definir α_B no framework RLL | 4 | **P1** | Auditoria de docs |
| Auditar: `codex/`, `invariants/`, `audits/`, `pipelines/`, `governance/` | 4,7,8,11 | **P2** | Auditoria de repositório |
| Verificar GitHub-Zenodo integration | 10 | **P2** | Configuração técnica |

---

## Adendo FASES 20–22 (2026-07-15/16)

Os desbloqueadores P0 citados ao longo deste documento foram executados e fechados.

### Gaps P0 — Estado Final

| Gap | Status (pré-FASE 20) | Status final | Resultado [E] |
|-----|---------------------|-------------|---------------|
| Joint MCMC Pantheon+ + DESI BAO | TOKEN_VAZIO P0 | ✅ FECHADO | Ωs0 UL95 = 0.00178 (emcee 32×1500, N=1677) |
| Bayes Factor RLL/ΛCDM | TOKEN_VAZIO P0 | ✅ FECHADO | ln(B₁₀) = −6.190 ± 0.691 (dynesty nlive=150) |

**ΛCDM fortemente preferido**: |ln B₁₀| = 6.19 > 5.0 → escala Jeffreys "evidência muito forte".

### Atualização do PODE 12 — Propriedade "Reprodutível"

A lacuna `Joint MCMC + Bayes Factor pendentes` (linha 467) foi resolvida:

| Propriedade | Status pós-FASE 20 |
|-------------|-------------------|
| Reprodutível | ✅ [E] — MCMC e Bayes Factor executados; resultados em `results/rll_fase20_mcmc_bayes.json` |

### Falsificadores — Estado Final

| F-COS | Resultado | Status |
|-------|-----------|--------|
| F-COS-01 | ΔAIC=3.805 | ✅ PASS [E] |
| F-COS-02 | χ²_red=0.4387 | ✅ PASS [E] |
| F-COS-03 | z_t_BAO=0.30 (fora [0.5,1.5]) | ✗ FAIL [E] |
| F-COS-04 | ln(B₁₀)=−6.190±0.691 | ✗ FAIL [E] |
| F-COS-05 | χ²_nom=93.81 | ✅ PASS [E] |

**CONTRATO final**: `2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO`. `claim_allowed = false` permanece — por resultado empírico, não por lacuna.

---

*"PODE é a forma gramatical da ciência: não afirma, pergunta com precisão suficiente para responder — e com falsificador suficiente para calar." — RAFAELIA*
