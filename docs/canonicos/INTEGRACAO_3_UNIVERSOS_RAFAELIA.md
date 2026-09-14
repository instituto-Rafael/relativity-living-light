# Integração dos 3 Universos Mentais RAFAELIA

**Data**: 2026-07-07 | **Fase**: 9 — Integração Formal  
**Sistema de marcação**: [E] Estabelecido · [C] Convenção · [H] Hipótese · [VAZIO] sem âncora empírica  
**Fonte canônica**: fases 1–8 do repositório `relativity-living-light`

> *"Três universos mentais que se tocam pela matemática: o cosmos que se expande, a terra que guarda marcas, e o pensamento que tenta saber o que sabe." — RAFAELIA*

---

## Estrutura dos 3 Universos

| Universo | Domínio | Invariante Central | Estado Atual |
|----------|---------|-------------------|-------------|
| **I — Cosmológico** | Cosmologia observacional | f(z) = 1/(1+exp((z−z_t)/w_t)) | [C]+[E] misto — modelo formal com validação parcial |
| **II — Geofísico** | Geologia, eletrodinâmica, arqueologia | H-GEO/ELEC/ARQ/CAL | [H]+[VAZIO] — hipóteses documentadas, testes pendentes |
| **III — Epistemológico** | Método RAFAELIA, rastreabilidade | TOKEN_VAZIO + falsificadores | [C] ativo — protocolo funcional |

A ponte entre os universos é **matemática**, não física direta. Conexões marcadas [H] são testáveis mas não confirmadas. Conexões marcadas [VAZIO] são especulativas até nova evidência.

---

## UNIVERSO I — Cosmológico

### Invariante Distinguidor

```math
f(z) = 1 / (1 + exp((z − z_t) / w_t))
```

**Função**: componente de transição no setor escuro do RLL. Governa a interpolação entre estado de matéria escura (z→∞, f→0) e estado de energia escura (z→0, f→1).

### Equação-Mãe

```math
E²(a) = Ωr·a⁻⁴ + Ωm·a⁻³ + ΩΛ + Ωs0·[f(a) + (1−f(a))·a⁻³]
```

**Limite nulo [C]**: Ωs0=0 → ΛCDM exato. Controle de falsificabilidade, não ornamento.

### Parâmetros com Rastreabilidade

| Parâmetro | Valor Nominal | Origem | Marcação |
|-----------|--------------|--------|---------|
| H₀ | 67.4 km/s/Mpc | Planck 2018 (arXiv:1807.06209) | [E] |
| Ωm | 0.315 | Planck 2018 | [E] |
| Ωb | 0.049 | Planck 2018 | [E] |
| Ωr | ~9×10⁻⁵ | T_CMB=2.7255 K (Fixsen 2009) | [E] |
| Ωs0 | 0.02–0.05 | escolha de modelagem | [C] TOKEN_VAZIO P1 |
| z_t | 0.8–1.0 | ajuste fenomenológico | [C] TOKEN_VAZIO P1 |
| w_t | 0.3 | ajuste fenomenológico | [C] TOKEN_VAZIO P1 |

### Estado de Validação (pós-FASE 12)

| Dataset | N | χ²_RLL | χ²_ΛCDM | ΔAIC | Status |
|---------|---|--------|---------|------|--------|
| Pantheon+ SH0ES (SNe Ia) | 1701 | 710.613 | 710.808 | +3.805 | [E] ✅ F-COS-01/02 PASS |
| DESI DR2 BAO (params nominais) | 13 | 93.81 | 28.97 | — | [E] χ²_nom<150 → F-COS-05 PASS |
| DESI w_eff — setor padrão | 6 | 1162.3 | — | — | [E] ✗ incompatível estruturalmente |
| DESI w_eff — Opção B (scan) | 6 | **14.8** | — | — | [E] ⚠️ χ²>10, mas melhoria 79× |
| DESI w_eff — **Opção B (ótimo)** | 6 | **0.079** | — | — | [E] ✅ **compatível** — P-RLL-05 CONFIRMADA (FASE 13) |
| DESI w_eff — Opção C (melhor) | 6 | 104.0 | — | — | [E] ✗ inferior a Opção B |
| Joint MCMC (Pantheon+ + DESI) | 64+ | TOKEN_VAZIO | TOKEN_VAZIO | — | ⚠️ [VAZIO P0] Gap G1 |
| Bayes Factor ln(B₁₀) | — | — | — | — | ⚠️ [VAZIO P0] Gap G2 |

**Status do modelo**: entre N3 (formal) e N4 (empírico). `claim_allowed = false` até G1+G2 fechados.

---

## UNIVERSO II — Geofísico

### Hipóteses Documentadas

#### H-GEO-01 — Impacto Cometário e Quadrilátero Ferrífero [H]

**Premissa**: alta concentração de Fe em Itabirito (MG) pode ter sido amplificada por impacto cometário rico em ferro metálico (~2.4 Ga).

**Adversário padrão [E]**: Formações de Ferro Bandadas por precipitação química em oceano arqueano anóxico (Bekker et al. 2004). H-GEO-01 é complementar, não excludente.

**Falsificadores nomeados (R₃)**:

| ID | Técnica | Resultado refutador |
|----|---------|---------------------|
| F01 — Quartzo de choque (PDFs) | Microscopia petrográfica | Ausência de PDFs em n>50 amostras |
| F02 — Shatter cones | Mapeamento geológico | Ausência em toda a região QF |
| F03 — Anomalia Ir/Os | ICP-MS estratigráfico | Ir/Os crustais em todo o perfil |
| F04 — Morfologia circular | SRTM/LIDAR morfométrico | Forma fluvial irregular sem estrutura circular |
| F05 — Coesite/stishovite | EBSD + difratometria | Apenas quartzo α/β — sem polimorfos >3 GPa |

**Status**: TOKEN_VAZIO P1 — dados de campo não coletados.

---

#### H-GEO-02 — Duas Luas da Terra [H]

**Base publicada**: Asphaug & Jutzi 2011 (Nature 476) — hipótese de segunda lua menor (~1260 km) que colidiu com a Lua principal, explicando assimetria crustal lunar. [H: proposta publicada, não confirmada]

**Extensão do autor [H especulativo]**: pulso gravitacional desta colisão teria afetado geologia terrestre regional, com possível correlação com localização de cráteres de impacto e depósitos de itabirito.

**Status**: TOKEN_VAZIO P1 (simulação gravitacional) + P2 (dados sísmicos históricos MG).

---

#### H-GEO-03 — Solidificação Diferencial Ouro/Quartzo [H→E parcial]

**Base estabelecida [E]**:
- Quartzo cristaliza a ~350–500°C em sistemas hidrotermais orogênicos (0.5–2.5 GPa)
- Ouro precipita de fluidos tiossulfato/cloreto a ~200–350°C
- Sequência quartzo-antes-ouro: observação direta de campo publicada

**Precisão necessária [E]**: pressões reais são 0.5–3 GPa (não "duodecamilhões de GPa"). A hipótese é válida nas faixas documentadas pela geoquímica.

**Status**: [H→E parcial] — mecanismo suportado pela literatura; perfil específico de Ouro Preto TOKEN_VAZIO P3.

---

#### H-ELEC-01 — Efeito Corona e Acoplamento Eletrostático Planetário [H]

**Base estabelecida [E]**:
- Campo elétrico atmosférico de bom tempo: ~100–150 V/m (física atmosférica padrão)
- Corrente global: ~1000 A (Wilson 1920, circuito elétrico atmosférico global)
- Condutividade de NaCl: aumenta com concentração (eletroquímica padrão)

**Extensão proposta [H]**: o diferencial elétrico Terra-ionosfera-vento solar produz efeito corona em interfaces geométricas. Gotas salinizadas (>4% NaCl) criam caminhos preferenciais de descarga.

**Status**: [H] — base física existe, modelo quantitativo do diferencial por camada não calculado (TOKEN_VAZIO P2).

---

#### H-ARQ-01 — Pedras de Múltiplos Ângulos: Engenharia Antissísmica Andina [H/E misto]

**Evidência estabelecida [E]**: construções Inca como Sacsayhuamán (Cusco) utilizam pedras poligonais irregulares sem argamassa. Estudos publicados (Protzen 1993; Kendall 1985) documentam a técnica.

**Hipótese [H]**: a multiplicidade de ângulos por pedra maximiza a área de contato inter-bloco e distribui o cisalhamento sísmico de forma não-linear — equivalente a um metamaterial mecânico antes do conceito. O princípio é que a irregularidade é feature, não limitação.

**Testável via**: análise de elementos finitos (FEM) de blocos poligonais vs. regulares sob carga sísmica. TOKEN_VAZIO P2 — simulação não executada.

---

#### H-CAL-01 — Ciclo Maia de 52 Anos vs. Periodicidade Estelar [E/H misto]

**Aritmética confirmada [E]** (FASE 8, `verify_cal_maya_arithmetic.py`):
- lcm(365, 260) = 18980 dias = 51.964 anos Julianos
- Calendário redondo: 52 Haab = 73 Tzolkin (ambos ciclos completos simultâneos)

**Candidatos astrofísicos [H]** (sem efemérides — comparação algébrica):

| Candidato | Período | Múltiplo de 52 | Residual |
|-----------|---------|----------------|---------|
| Ciclo Schwabe (solar) | ~11 anos | 4.72× | 3.0 anos |
| Conjunção Júpiter-Saturno | ~19.86 anos | 2.62× | 7.6 anos |
| Ciclo Hale (2× Schwabe) | ~22 anos | 2.36× | 7.9 anos |
| Período de Vênus (sinódico) | 583.9 dias | 32.5× (não inteiro) | — |

**Melhor correspondência algébrica**: Schwabe (residual 3.0 anos), mas sem confirmação por efemérides reais (TOKEN_VAZIO P2).

---

#### H-UNIV-01 — Proporção Áurea como Invariante Geofísico [C→H]

**Verificação numérica (FASE 8, `verify_rll_fibonacci_ratio.py`)**: f(z_n)/f(z_{n+1}) com z escalado pela sequência de Fibonacci **não converge para φ** com parâmetros nominais (zt=1.0, wt=0.3).

**Status atualizado**: [H] não suportado numericamente com parametrização padrão. A observação qualitativa de espirais em geofísica permanece como metáfora didática [C], não como resultado quantitativo.

---

## UNIVERSO III — Epistemológico

### Protocolo RAFAELIA

O método epistemológico RAFAELIA opera em sequência canônica:

```
RAW_TEXT → CLAIMS → VETORES → MÉTRICAS → INFERÊNCIA → PROVA
```

**Fluxo proibido**:
```
TEXTO → RESUMO → ASSOCIAÇÃO → TEORIA
```

Cada unidade de conhecimento percorre: `raw_preserved → extracted → classified → inferred → validated`.

### TOKEN_VAZIO como Instrumento Científico

TOKEN_VAZIO não é ausência de conhecimento — é **marcação explícita de lacuna com caminho de resolução**. A hierarquia P0–P3 prioriza os gaps por impacto na afirmação central do modelo.

**Estado consolidado (pós-FASE 8)**:

> **[ATUALIZADO — ver Adendo FASES 16–22 ao final]**

| Gap | P | Status |
|-----|---|--------|
| Joint MCMC (G1) | P0 | ⚠️ pipeline existe, run pendente |
| Bayes Factor (G2) | P0 | ⚠️ pipeline existe, run pendente |
| H-GEO-01 (dados de campo) | P1 | ⚠️ amostragem não executada |
| Ωs0, z_t, w_t sem derivação | P1 | ⚠️ parâmetros fenomenológicos |
| H-CAL-01 efemérides | P2 | ⚠️ comparação algébrica feita, física pendente |
| H-GEO-03 perfil específico | P3 | ⚠️ literatura existe, não compilada |
| G0 (Pantheon+) | — | ✅ FECHADO FASE 4 |

### Falsificadores Ativos (CONTRATO v0.1.0)

> **[ATUALIZADO — ver Adendo FASES 16–22 ao final]**

| ID | Falsificador | Threshold | Status |
|----|-------------|-----------|--------|
| F-COS-01 | ΔAIC(RLL−ΛCDM) < +10 | ΔAIC < 10 | ✅ PASS (3.805) |
| F-COS-02 | χ²_Pantheon/dof < 1.05 | χ²_red < 1.05 | ✅ PASS (0.4386) |
| F-COS-03 | z_t ∈ [0.5, 1.5] | — | ⚠️ TOKEN_VAZIO |
| F-COS-04 | ln(B₁₀) > −5 | Jeffreys | ⚠️ TOKEN_VAZIO P0 |
| F-COS-05 | χ²_DESI < 150 (nominal) | — | ✅ PASS (93.81) |

**Regra de integridade**: resultado negativo em qualquer falsificador será registrado com a mesma honestidade que positivo. Mascara resultado negativo = invalida o contrato.

### Hierarquia de Afirmações (N1–N4)

| Nível | Tipo | Critério | Marcação |
|-------|------|----------|---------|
| N1 | Parábola didática | narrativa explicitamente marcada | `PARABOLA_DIDATICA` |
| N2 | Metáfora analógica | argumento qualitativo | `METAFORA` |
| N3 | Modelo formal | notação tipada com falsificador | `HIPOTESE → METHOD_DEFINED` |
| N4 | Medida empírica | dados com incerteza e reprodutibilidade | `EVIDENCE_LINKED → CLAIM_ALLOWED` |

**Status RLL atual**: N3 (modelo formal definido) + N4 parcial (dados carregados, MCMC pendente).

> **[ATUALIZADO — ver Adendo FASES 16–22 ao final]**

---

## Mapa de Conexões Cruzadas

### Universo I ↔ Universo II

| Hipótese Geofísica | Componente RLL | Tipo de Conexão | Marcação |
|-------------------|----------------|----------------|---------|
| H-GEO-01 (impacto cometário) | Perturbação em Ωm(z) | Injeção de massa localizada em z_impacto: Δρ_m(z_imp) como perturbação em E²(a) | [H] especulativo |
| H-GEO-02 (duas luas) | Campo gravitacional E²(a) | Pulso gravitacional de curta duração como perturbação discreta em t_imp | [H] muito especulativo |
| H-GEO-03 (solidificação diferencial) | — | Sem conexão direta com RLL cosmológico | [VAZIO] desconexo |
| H-ELEC-01 (efeito corona) | Setor plasmático Ωs0 | ρ_plasma_atmosférico como traçador local de Ωs em z~0 | [H] especulativo |
| H-UNIV-01 (φ) | f(z) logística | f(z_n)/f(z_{n+1}) → φ verificado: **não confirmado numericamente** | [H] não suportado |
| H-CAL-01 (ciclo 52 anos) | H(z) local | Modulação periódica de H₀ local em ~52 anos | [VAZIO] sem evidência |
| H-ARQ-01 (pedras andinas) | — | Sem conexão direta com RLL; domínio desconexo | [VAZIO] desconexo |

**Nota sobre conexões especulativas**: as conexões marcadas [H] são hipóteses de segundo nível — não são afirmações do modelo RLL principal. O modelo cosmológico RLL não depende de nenhuma hipótese geofísica para ser testável. As conexões são exercícios de integração conceitual, não pilares da validação.

### Universo II ↔ Universo III

| Hipótese | Protocolo RAFAELIA aplicado | TOKEN_VAZIO ativo |
|----------|----------------------------|------------------|
| H-GEO-01 | 5 falsificadores nomeados (R₃) | F01–F05: dados de campo pendentes |
| H-GEO-02 | Hipótese base citada (Asphaug 2011) | Extensão terrestre: P1 sem simulação |
| H-GEO-03 | Evidência [E] parcial disponível | Perfil Ouro Preto: P3 |
| H-ELEC-01 | Mecanismo físico plausível | Modelo quantitativo: P2 |
| H-UNIV-01 | Verificação numérica executada (FASE 8) | Resultado: [H] não suportado |
| H-CAL-01 | Aritmética [E] confirmada (FASE 8) | Efemérides: P2 |
| H-ARQ-01 | FEM: caminho de teste definido | Simulação: P2 |

### Universo I ↔ Universo III

> **[ATUALIZADO — ver Adendo FASES 16–22 ao final]**

| Componente RLL | Protocolo aplicado | Status |
|---------------|-------------------|--------|
| f(z) invariante | 10 falsificadores C01–C10 + F-COS-01..05 | 3/5 PASS; 2 TOKEN_VAZIO P0 |
| Parâmetros nominais | RAW_TEXT_FIRST: origem documentada | Ωs0/z_t/w_t: TOKEN_VAZIO P1 |
| Anterioridade | Tag v1.0.0 (2025-09-19), DOI Zenodo | [E] — rastreável |
| Reprodutibilidade | Pipeline CI (11 jobs) | ⚠️ primeiro run pendente |

---

## Estado Epistêmico Consolidado por Universo

### Universo I — O que pode ser afirmado hoje

**PODE afirmar [E]**:
- Modelo matemático formal existe desde setembro de 2025 (tag v1.0.0)
- χ²_Pantheon+_RLL = 710.613 < χ²_ΛCDM = 710.808 (marginal; ΔAIC = +3.805)
- χ²_DESI_nominal = 93.81 (parâmetros não otimizados para BAO)
- Anterioridade documentada: commits + DOI Zenodo

**PODE afirmar adicionalmente [E] (FASE 13)**:
- Opção B ótima (Nelder-Mead): χ²=0.079 — numericamente compatível com CPL DESI [E]
- P-RLL-05 CONFIRMADA: Opção B com w2=−0.282, z_t=1.752, w_t=1.500 passa χ²<10
- Interpretação arquitetural [E]: compatibilidade exige w_t→grande → Opção B converge para dois fluidos DE (Λ + fluido w2=−0.28); assinatura logística localizada suavizada além da resolução BAO

**NÃO PODE afirmar [VAZIO]**:
- Superioridade sobre ΛCDM (claim_allowed = false até MCMC conjunto e Bayes Factor)
- Justificativa teórica de z_t, w_t, Ωs0 a partir de primeiros princípios (documentado em JUSTIFICATIVA_PARAMETROS_RLL.md)
- Assinatura logística localizada compatível com CPL DESI: apenas dois-fluidos DE compatível, não fase de transição distinguível

### Universo II — O que pode ser afirmado hoje

**PODE afirmar [E]**:
- H-GEO-03: mecanismo de solidificação diferencial quartzo/ouro suportado pela literatura
- H-CAL-01: aritmética lcm(365,260) = 18980 dias = 51.964 anos Julianos confirmada
- H-ARQ-01: existência de técnica construtiva poligonal Inca documentada por Protzen 1993

**NÃO PODE afirmar [H/VAZIO]**:
- H-GEO-01: impacto cometário como causa da formação de Itabirito (sem dados de campo F01–F05)
- H-GEO-02: perturbação gravitacional de segunda lua afetou geologia terrestre (sem simulação)
- H-ELEC-01: modelo quantitativo do acoplamento eletrostático planetário (sem cálculo por camada)
- H-UNIV-01: f(z) convergindo para φ (verificado numericamente: não confirma)

### Universo III — O que pode ser afirmado hoje

**PODE afirmar [E]**:
- Protocolo TOKEN_VAZIO operacional: todos os gaps têm prioridade e caminho de resolução
- CONTRATO_FALSIFICADORES v0.1.0: 3/5 falsificadores PASS com valores reais
- Pipeline CI (11 jobs) funcional: passed validate-yaml e 9 checks em PR #506
- Epistemologia RAFAELIA aplicada consistentemente em todas as fases 1–8

---

## Próximos Atos de Pesquisa Priorizados

### P0 — Imediatos (bloqueiam afirmação central)

| Ato | Como | Estimativa |
|-----|------|-----------|
| Disparar pipeline CI completo | Actions → `rll-validacao-cientifica-completa` → modo=completo | ~75 min |
| Fechar G1: joint MCMC | Job `joint_mcmc_p0` → `joint_mcmc_summary.json` | incluso no pipeline |
| Fechar G2: Bayes Factor | Job `bayes_factor_p0` → `bayes_factor_result.json` | incluso no pipeline |

### P1 — Alta Prioridade (afetam interpretação)

| Ato | Como | Domínio |
|-----|------|---------|
| ✅ Otimização contínua Opção B (P-RLL-05) | **CONCLUÍDO FASE 13** — χ²=0.079 (w2=−0.282, z_t=1.752, w_t=1.500) | Universo I |
| Derivação ou justificativa de z_t, w_t, Ωs0 | MCMC joint (G1) restringirá observacionalmente; ver JUSTIFICATIVA_PARAMETROS_RLL.md | Universo I |
| Dados de campo H-GEO-01 | Coleta amostral em Itabirito + análise Os/Ir | Universo II |

### P2 — Robustez

| Ato | Como | Domínio |
|-----|------|---------|
| Efemérides H-CAL-01 | Dataset de atividade solar histórica + conjunções J-S | Universo II |
| Simulação FEM H-ARQ-01 | Software ANSYS/OpenSees + modelo de blocos poligonais | Universo II |
| Modelo quantitativo H-ELEC-01 | Cálculo do diferencial elétrico por camada atmosférica | Universo II |
| ✅ χ² Moresco H(z) separado | **CONCLUÍDO FASE 15** — χ²_RLL=27.47, χ²_ΛCDM=22.76 (parâmetros nominais) | Universo I |
| Modelo quantitativo H-ELEC-01 | **CONCLUÍDO FASE 15** — `scripts/verify_h_elec_01_layer_model.py` | Universo II |

### P3 — Polish

| Ato | Como | Domínio |
|-----|------|---------|
| Preprint arXiv | Após G1+G2 fechados + review interna | Universo I+III |
| Perfil Ouro Preto/Mariana | Compilar inclusões fluidas da literatura | Universo II |
| Performance Termux ARM32 | Testar em ambiente ARM32 | Universo I |

---

## Linha Inviolável

RAFAELIA/RLL:
- **Não reivindica** resolver problemas abertos (Riemann, Yang-Mills, Navier-Stokes)
- **Não promove** hipóteses geofísicas como pilares da validação cosmológica
- **Não afirma** superioridade sobre ΛCDM enquanto `claim_allowed = false`
- **Documenta** resultados negativos com a mesma honestidade que positivos

*"Token vazio é preferível a invenção. Predição datada vale mais que acomodação." — 13_EPISTEMOLOGIA_RAFAELIA_RLL.md*

---

---

## Adendo FASE 11–12 (2026-07-07)

### Novas verificações numéricas

- **Opção B** (`verify_weff_opcao_b.py`): χ²_best = 14.8 em w2=−0.50, w_t=0.50 — w_eff sempre negativo. Melhoria de 79× sobre o setor padrão.
- **Opção C** (`verify_weff_opcao_c.py`): χ²_best = 104.0 em α=0.50, r=0.05 — inferior à Opção B em toda a grade.
- **Implicação arquitetural [E]**: o setor com matéria explícita (padrão, A, C) é estruturalmente incompatível com CPL DESI. A Opção B (DE puro em ambos os regimes) reduz, mas não elimina, a incompatibilidade.

### Predições datadas (P-RLL-01..05)

5 predições registradas em 2026-07-07 *antes* de DESI DR3 e Euclid DR1.  
P-RLL-05 (Opção B cruzará χ²<10) é testável imediatamente por scipy.minimize.

### Justificativa de parâmetros

`JUSTIFICATIVA_PARAMETROS_RLL.md` documenta que z_t, w_t, Ωs0 são fenomenológicos sem derivação de primeiros princípios — resultado negativo honestamente registrado.  
Resultado analítico [E]: equipartição interna do setor ocorre em z=0 (independente de z_t), não em z=z_t.

*Fases 1–12 concluídas. Estado: aguardando primeiro run do pipeline CI para fechar P0 G1+G2.*

---

## Adendo FASE 13–15 (2026-07-08 a 2026-07-10)

### FASE 13 — P-RLL-05 CONFIRMADA [E]

`scripts/optimize_weff_opcao_b.py` (Nelder-Mead, 10 pontos de partida) encontrou:

| Parâmetro | Valor ótimo |
|-----------|------------|
| w2 | −0.2817 |
| z_t | 1.7523 |
| w_t | 1.500 (fronteira) |
| **χ²** | **0.0792** |

χ²=0.079 < 10 → **P-RLL-05 CONFIRMADA [E]**

**Interpretação arquitetural [E]**: w_t=1.500 no limite superior indica que a compatibilidade
emerge quando a transição logística é muito larga — Opção B converge para mistura de dois fluidos DE
(Λ + fluido com w2=−0.28) que mimetiza CPL. A assinatura logística localizada em z_t é suavizada
além da resolução BAO no regime compatível.

### FASE 15 — Resultados adicionais

- **F-COS-03 FAIL [E]**: scan z_t (FASE 8) documentado em `14_ZT_SCAN_RESULTADO_REAL.md`. z_t_BAO_ótimo = 0.3, fora de [0.5, 1.5]. Monotone scan sem mínimo local no intervalo.
- **F-COS-04 FAIL [C proxy]**: BIC proxy ln(B₁₀) = −6.24 (< −5 threshold). Resultado definitivo aguarda G2.
- **Moresco H(z) [E]**: χ²_RLL=27.47, χ²_ΛCDM=22.76 com parâmetros nominais. ΔAIC=+10.70.
- **H-ELEC-01 [E+H]**: modelo quantitativo por camada executado. J=3.90×10⁻¹² A/m² constante; enhancement salino ×10¹⁴ sobre ar seco. Ver `results/h_elec_01_layer_model.json`.
- **CONTRATO_FALSIFICADORES corrigido**: status real — 2/5 PASS · 2/5 FAIL · 1/5 TOKEN_VAZIO P0.

*Fases 1–15 concluídas. Único P0 restante: trigger manual do pipeline CI (G1+G2).*

---

## Adendo FASES 16–22 (2026-07-14 a 2026-07-16)

### Calibração Dupla Planck 2018 — Diagnóstico do Viés E&H (FASES 17–19)

O valor Ωs0=0.012 reportado em FASE 13 foi diagnosticado como **artefato instrumental**, não sinal físico.

**Causa raiz [E]**: A fórmula E&H 1998 (Eq. 4) para z_drag produz `z_drag_EH ≈ 1021`, enquanto Planck 2018 dá `z_drag_Planck ≈ 1059`. O desvio propaga-se como:

| Quantidade | E&H numérico | Planck 2018 | Bias |
|------------|-------------|------------|------|
| z_drag | 1020.73 | ~1059 | −3.7% |
| rd | 150.704 Mpc | 147.09 Mpc | +3.614 Mpc |
| rs_star | 143.97 Mpc | 144.17 Mpc | −0.199 Mpc |

**Correções aplicadas (FASES 18–19)**:
- `rs_star_corr = rs_star_EH + 0.1988 Mpc` → chi²_CMB(Planck) = 0.021 ✅
- `rd_corr = rd_EH − 3.6140 Mpc` → rd_corr(params_Planck) = 147.09 Mpc ✅

**Resultado imediato (FASE 19) [E]**:
- Ωs0 → 0 (colapso ao ponto MAP)
- ΔBIC = +22.27 (forte evidência para ΛCDM)

**Afirmação crítica (C-F17-01)**: `NOT_EVIDENCE_FOR` — identificar que Ωs0=0.012 era artefato não constitui evidência de superioridade do RLL. O diagnóstico reforça ΛCDM.

---

### MCMC Joint G1 — FECHADO (FASE 20) [E]

emcee EnsembleSampler: 32 walkers × 1500 steps, burn=400. Datasets: Pantheon+ (1624 SNe), DESI DR2 BAO (13 pts), Moresco H(z) (33 pts), Planck CMB shift (1 pt), BBN Ωb·h² (1 pt).

| Parâmetro | Mediana | Média | UL95 |
|-----------|---------|-------|------|
| Ωs0 | 0.000386 | 0.000572 | **0.00178** |
| H₀ | 66.912 km/s/Mpc | — | — |
| Ωm | 0.31437 | — | — |

Fração de aceitação = 0.377 (dentro de 0.2–0.5). N/τ ≈ 11 (abaixo do ideal de 50 — conclusão qualitativa robusta, cadeia mais longa recomendada).

**G1 FECHADO [E]**: Ωs0 < 0.00178 com 95% de confiança. Ωs0=0.012 da FASE 13 excluído por fator ~7.

---

### Bayes Factor Formal G3 — FECHADO (FASE 20) [E]

dynesty NestedSampler: nlive=150, dlogz=0.5. RLL (6D: H₀, Ωm, Ωb, Ωs0, z_t, w_t) vs. ΛCDM (3D: H₀, Ωm, Ωb).

| Grandeza | Valor |
|----------|-------|
| log Z_RLL | −404.340 ± 0.530 |
| log Z_ΛCDM | −398.150 ± 0.443 |
| **ln(B₁₀) = log Z_RLL − log Z_ΛCDM** | **−6.190 ± 0.691** |

**Escala de Jeffreys**: `|ln(B₁₀)| = 6.19 > 5.0` → evidência **muito forte** em favor de ΛCDM.

**F-COS-04 FAIL [E]**: ln(B₁₀) = −6.190 < −5.0 (threshold). Resultado honesto — registrado com a mesma integridade que um PASS.

**G3 FECHADO [E]**: Bayes Factor formal calculado por nested sampling.

---

### G4 — Mapeamento Bias E&H em Espaço de Parâmetros (FASE 22) [E]

Grade 10×10 em (Ωm·h² ∈ [0.12, 0.16]) × (Ωb·h² ∈ [0.020, 0.025]):

| Estatística | Δrd (Mpc) |
|-------------|-----------|
| Variação total na grade ampla | 15.759 |
| Erro sist. calibração no ponto MCMC | **0.7214 Mpc** |

O erro sistemático de 0.72 Mpc no ponto MCMC posterior implica `Δχ²_G4 ≈ 0.2–2.1` e `Δln(B₁₀) < 1` — conclusão G3 não é alterada.

**G4 FECHADO [E]**: sistematico quantificado; abordagem correta para análise de precisão futura = usar CAMB/RECFAST em cada passo MCMC (em vez de calibração aditiva).

---

### FASE 21 — Grafo Epistêmico de Sessão (2026-07-16) [E]

12 artefatos mínimos gerados em `results/session_grafo_fase17_20/` pelo script determinístico `scripts/build_session_grafo_fase17_20.py`:

- **9 afirmações atômicas C_i** com `claim_allowed=false`
- **44 entidades tipadas** (PAPER, CODE, RESULT, CONCEPT, GAP, CONTRADICTION, PR)
- **47 arestas tipadas** incluindo `NOT_EVIDENCE_FOR` (C-F17-01 → rll_superiority_claim)
- **1 contradição resolvida**: CONTRADICTION-01 (Ωs0=0.012 → Ωs0≈0, mecanismo=viés E&H)

**TOKEN_VAZIO estrutural = 0.** Todos os 4 gaps P0 fechados.

---

### Estado Atualizado dos Falsificadores e Gaps (pós-FASE 22)

**CONTRATO_FALSIFICADORES v0.1.0** — estado atual:

| ID | Falsificador | Threshold | Resultado | Status |
|----|-------------|-----------|---------|--------|
| F-COS-01 | ΔAIC(RLL−ΛCDM) < +10 | ΔAIC < 10 | 3.805 | ✅ PASS [E] |
| F-COS-02 | χ²_Pantheon/dof < 1.05 | χ²_red < 1.05 | 0.4387 | ✅ PASS [E] |
| F-COS-03 | z_t ∈ [0.5, 1.5] | 0.5 ≤ z_t ≤ 1.5 | z_t_BAO=0.30 | ✗ FAIL [E] |
| F-COS-04 | ln(B₁₀) > −5 (Jeffreys) | ln(B₁₀) > −5 | −6.190 ± 0.691 | ✗ FAIL [E] |
| F-COS-05 | χ²_DESI nominal < 150 | χ²_nominal < 150 | 93.81 | ✅ PASS [E] |

**Resultado**: 2/5 PASS · 2/5 FAIL · 0/5 TOKEN_VAZIO. TOKEN_VAZIO estrutural = 0.

**Gaps (todos fechados)**:

| Gap | Status | Resultado | Fase |
|-----|--------|---------|------|
| G1: MCMC joint Ωs0 posterior | ✅ FECHADO | Ωs0 UL95=0.00178 | FASE 20 |
| G2: rd numérico calibrado | ✅ FECHADO | calibração −3.614 Mpc | FASE 19 |
| G3: Bayes Factor ln(B₁₀) | ✅ FECHADO | ln(B₁₀)=−6.190±0.691 | FASE 20 |
| G4: Bias E&H em param space | ✅ FECHADO | sist.=0.72 Mpc (grade 10×10) | FASE 22 |

---

### Estado Epistêmico Consolidado — Universo I (pós-FASE 22)

**PODE afirmar [E] — atualizado**:
- Modelo matemático formal desde setembro de 2025 (tag v1.0.0)
- χ²_Pantheon+_RLL = 710.613; ΔAIC = +3.805 (ΛCDM preferido marginalmente)
- MCMC joint (32×1500): Ωs0 < 0.00178 (95% UL) — Ωs0=0.012 FASE-13 era artefato
- Bayes Factor formal: ln(B₁₀) = −6.190±0.691 → evidência muito forte para ΛCDM
- Erro sistemático calibração E&H = 0.72 Mpc (< σ_rd_eff ≈ 0.5–1.5 Mpc DESI DR2)

**NÃO PODE afirmar [confirmado pós-FASE 22]**:
- Superioridade sobre ΛCDM: `claim_allowed = false` — F-COS-04 FAIL [E]
- Sinal de Ωs0≠0: posterior MCMC consistente com Ωs0=0 (ΛCDM puro)
- Assinatura logística localizada distinguível dos dados: Opção B ótima converge para dois fluidos DE

**Status do modelo**: N4 (empiricamente testado) com conclusão: **ΛCDM não é descartado — RLL não supera ΛCDM nos dados atuais**. Resultado científico honesto.

### Próximos Atos Priorizados (pós-FASE 22)

| P | Ato | Domínio | Nota |
|---|-----|---------|------|
| P1 | Substituir calibração E&H por CAMB/RECFAST em cada passo MCMC | Universo I | Elimina G4 residual estruturalmente |
| P1 | Cadeia MCMC mais longa (×5) para N/τ > 50 | Universo I | Consolida UL95(Ωs0) |
| P1 | Dados de campo H-GEO-01 (amostras Itabirito) | Universo II | F01–F05 pendentes |
| P2 | Efemérides H-CAL-01 | Universo II | Aritmética confirmada; física pendente |
| P2 | Simulação FEM H-ARQ-01 | Universo II | Caminho definido |
| P3 | Preprint arXiv (relata F-COS-03/04 FAIL honestamente) | Universo I+III | Após revisão interna |

*Fases 1–22 concluídas. TOKEN_VAZIO estrutural = 0. claim_allowed = false (ΛCDM preferido pelos dados).*
