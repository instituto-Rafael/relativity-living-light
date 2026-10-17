# RLL — consumidor de pesquisa 10×7 · 2026-10-15

Autoridade editorial: `rafaelmeloreisnovo/papers`; código e dados cosmológicos não foram modificados.

# RAFAELIA Ω — 10 heurísticas × 7 direções — interfaces, fotônica e cosmologia

**Corte:** 2026-10-15. **Status:** proposta de pesquisa exploratória federada; `claim_allowed=false`; **sem merge automático**. **Escopo:** sessão inteira, do giro/coroas e gravidade à membrana, plasma, osmose, córnea, redox e α-shapes.

Esta não é uma demonstração de novas forças nem um inventário dos resultados físicos do RLL. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`; `TOKEN_VAZIO != 0`; `IMPLEMENTED_UNTESTED != PASS`.

A **régua de sete direções** é herdada literalmente de `papers/docs/matematica/PROTOCOLO_7_DIRECOES_PROGRAMAS_MATEMATICOS_V1.md` (blob `c972354d9f19aef4ee4ef94a5c364bb130daeab9`), sem a confundir com Route56 (8×7 rotas angulares ordenadas, outra autoridade).

**Sete direções:** fato → lacuna → invariante → variante → prova → parábola → retroalimentação. 10 objetos × 7 campos = 70 células editoriais, **não 70 experimentos**. Cada hipótese inclui fonte, status, equação, falsificador e controle negativo; nenhum item é novidade demonstrada.

**Âncora matemática prévia:** `RLL-CANONICAL-CROSS-SESSION-FORMULA-ATLAS-V1-20261015`, 86 expressões tipadas em ledger privado. As 86 não são recontadas como 86 provas. Referência Drive: `MU-RLL-FULL-SESSION-86-FORMULAS-REDOX-20261015`.

## Cadências de ocorrência e estados

1. **Por instante/evento:** entrada e saída de partícula, corrente, intensidade espectral, ROS; não inventar uma frequência fixa.
2. **Por dinâmica física:** tempo de trânsito, reação, difusão, Debye, advecção, rotação; compara `t_trânsito/t_processo` apenas se ambos pertencem ao mesmo regime.
3. **Por escala:** angström→nm→µm→tecido→corpo celeste; um mesmo número adimensional não constitui mesma causa.
4. **Por retorno temporal:** reversão de gradientes, de rotação, condição de contorno e queda da fonte; controles negativos obrigatórios.
5. **Por versão de fonte:** resultado histórico→preprint→revisão→reprodução; preservar ordem e supersessão, não substituir silêncio por aprovação.
6. **Por gate G0–G7:** escopo→origem→formal→código→experimento→replicação→revisão→publicação; manter HOLD quando faltarem campos.

**Tratamento de ocorrências 'ignoradas':** este catálogo identifica *vias subutilizadas nesta sessão* ou *fontes históricas facilmente omitidas em comparações de áreas*. Não afirma que a comunidade científica negligenciou quantitativamente um artigo sem bibliometria.


## Recepção: questões e fronteiras específicas de RLL

### HX01 — Córnea: interação O2 × osmolaridade × redox

- Formula/limite: `∂t C_O2 = ∇·(D∇C_O2) − q(C_O2); dROS/dt = P(C_O2,Osm,UV,metabolismo) − kROS`.
- Fato: Deng et al. (2015) observaram aumento de marcadores oxidativos sob hiperosmolaridade em cultura de epitélio corneano; transporte de O2 tem difusão e consumo.
- Lacuna: Dados pareados corneanos pO2×osmolaridade×ROS, com tempo, UV e metabolismo controlados: TOKEN_VAZIO.
- Falsificador: Pré-registrar desfecho ROS/GSH:GSSG, controles UV/viabilidade/temperatura e teste fora da amostra; rejeitar interação se intervalo cruzar zero ou vantagem desaparecer em replicação.
- Feedback: Se efeito nulo, catalogar prior art e manter apenas acoplamento convencional; se persistir, estimar mecanismo e replicar sem claim cosmológico.
- Status: `PRIOR_ART_FOUND + INCREMENTAL_HYPOTHESIS`. Fontes: DOI:10.1371/journal.pone.0126561; papers:delta_g_manifold_bioionic_v1.

### HX02 — Seleção contraintuitiva: íon menor não é sempre o mais móvel

- Formula/limite: `μ̃_i=μ_i°+RT ln a_i+z_iFψ; ΔG‡_i=ΔG_hidr+ΔG_coord+ΔG_elec`.
- Fato: Hidratação e interação com água podem fazer Li+ migrar mais lentamente que K+ em solução; seletividade não se reduz ao raio cristalográfico.
- Lacuna: Energia livre real de cada íon na membrana poly(fantrip), estados de hidratação e estrutura de parede: TOKEN_VAZIO.
- Falsificador: Fixar estado de solução/força iônica e confrontar hierarquia de corrente de Li+,Na+,K+ com medidas replicadas; controle de íons neutros e potenciais de junção.
- Feedback: Não importar efeito de um sal ou material para outro; usar pré-print apenas como candidato até revisão independente.
- Status: `PHYSICAL_BASELINE + RECENT_PREPRINT`. Fontes: arXiv:2601.08309; papers:delta_g_manifold_bioionic_v1.

### HX03 — Difusio-osmose em interface sem peneira ideal

- Formula/limite: `(J_v,J_s)^T = L·(ΔP,Δμ_s)^T (forças termodinâmicas conjugadas adequadamente normalizadas)`.
- Fato: Onsager (1931) e Kedem–Katchalsky (1958) trataram acoplamentos irreversíveis; Bocquet (2026) mostra difusio-osmose interfacial inclusive sem exclusão integral de soluto.
- Lacuna: Coeficientes cruzados, camada difusa e condições de deslizamento do nanocanal específico: TOKEN_VAZIO.
- Falsificador: Controles com superfície neutra e gradiente invertido; estimar matriz L a partir de dados e testar sinais, reciprocidade condicionada e balanço de energia.
- Feedback: Manter o termo superficial só onde ele aumenta predição fora da amostra; documentar quando camadas interfaciais se sobrepõem.
- Status: `PRIOR_ART_CLASSICAL + NEW_SYNTHESIS`. Fontes: DOI:10.1103/PhysRev.37.405; DOI:10.1016/0006-3002(58)90330-5; arXiv:2605.02419.

### HX04 — Nanoporo 2D polar: dipolo muda o fluxo com concentração

- Formula/limite: `G(c)=dI/dV; ∂ln G/∂ln c ≈ 0 (somente se confirmado no regime e no material do estudo)`.
- Fato: Preprint MoSSe (2026) reporta condutância iônica quase invariável ao longo de concentrações muito diferentes, associando efeito ao dipolo intrínseco e à água confinada.
- Lacuna: Reprodução independente e qualquer transferência desse efeito para poly(fantrip) são TOKEN_VAZIO.
- Falsificador: Extrair inclinação log(G)×log(c), erro por amostra, controles de vazamento/defeitos, e falsificar invariância se declive significativamente não nulo.
- Feedback: Classificar originalidade no contexto do artigo MoSSe e segurar claims de transposição para material diferente.
- Status: `PREPRINT_EMPIRICAL_NOT_POLYFANTRIP`. Fontes: arXiv:2603.21827; DOI:10.1038/nchem.2008.

### HX05 — Transição entre transporte gasoso, plasma e solução aquosa

- Formula/limite: `Kn=λ_mfp/d; λ_D=[ε0 kBT_e/(n_e e²)]^(1/2); N̄_e=n_e A L`.
- Fato: Um poro ~0,9nm é muito menor que o livre caminho médio do gás a 1atm e que λ_D para parâmetros de plasma ilustrativos; células e líquidos têm outros regimes.
- Lacuna: Distribuição real de energia, espécies, campo e colisões do isqueiro, rugosidade e estabilidade do poro: TOKEN_VAZIO.
- Falsificador: Testar limiares com sweeps de pressão, n_e e diâmetro; rejeitar modelo contínuo quando viola seus próprios critérios de escala.
- Feedback: Não mesclar resultados de regimes; classificar cada lacuna como parâmetro desconhecido, NOT_APPLICABLE ou medição faltante.
- Status: `STANDARD_REGIME_BOUNDARY`. Fontes: RLL:SGPT; arXiv:2605.02419.

### HX06 — Encaixe energético e angular versus aprisionamento no nanoporo

- Formula/limite: `E_perp=E cos²θ; τ≈L/(v cosθ); k∝exp(−ΔG‡/kBT) (domínios diferentes)`.
- Fato: Uma espécie pode encaixar geometricamente e ainda ser detida por uma barreira ou por adsorção à parede; energia normal e tempo de residência variam com ângulo.
- Lacuna: Potenciais ab-initio, energia de adsorção, rotação molecular, deformação do poro e distribuição de ângulos: TOKEN_VAZIO.
- Falsificador: Controles limite θ=0, E=0 e parede neutra; inspecionar monotonicidade e rejeitar máximo artificial criado pela discretização.
- Feedback: Ajustar o mínimo de parâmetros e aceitar falhas de encaixe como resultado útil com receita reproduzível.
- Status: `MODEL_COMPARISON_NOT_VALIDATED`. Fontes: papers:DELTA-G; arXiv:2601.08309.

### HX07 — Da partícula emissora ao espectro — não confundir cor com espécie

- Formula/limite: `hν=hc/λ; dℐ/ds=𝒥−𝒜ℐ; Q²+U²+V²≤I²`.
- Fato: Descargas no ar podem incluir linhas/bandas de N2/N2+ e outras espécies; brilho violeta não prova oxigênio como espécie emissora exclusiva.
- Lacuna: Espectros/tempo/temperatura de emissão do equipamento citado e resposta de detector calibrada: TOKEN_VAZIO.
- Falsificador: Decompor bandas/emissões por modelo e instrumento, com calibrador e amostra nula; rejeitar atribuição O2 exclusiva caso N2 explique os sinais.
- Feedback: Levar somente fótons observados aos operadores fotônicos RLL; partículas materiais têm kernel de transporte próprio.
- Status: `SPECTROSCOPY_BASELINE`. Fontes: RLL:PHOTONIC_MATRIX_LOGISTICS; papers:SGPT.

### HX08 — Separação superfluido He4 × barreira Josephson × descarga de plasma

- Formula/limite: `I=Ic sinΔφ (analogia Josephson sob contrato físico); ∆φ_Sagnac ∝(m/ℏ)ΩA`.
- Fato: Ellers et al propõem sensor superfluido He4 e barreira nanoporo candidata; isto não é plasma de isqueiro nem dispositivo validado.
- Lacuna: Ic experimental na barreira poly(fantrip), transporte de He4, estabilidade criogênica e noise floor real: TOKEN_VAZIO.
- Falsificador: Replicar limites de interferômetro sem arrastamento, inverter rotação e comparar sinais e incertezas físicas publicadas.
- Feedback: Guardar como estudo de literatura e proposta experimental; bloquear alegação de sensores físicos construídos.
- Status: `EXTERNAL_EXPERIMENT_PROPOSAL_ONLY`. Fontes: DOI:10.1103/q3v9-rjm9; DOI:10.1038/nchem.2008.

### HX09 — Coroas de momento angular, arrasto gravitacional e horizonte análogo

- Formula/limite: `Jz=∫r_perp²Ω dm; ΩFD≈2GJ/(c²r³) exterior fraco; ΔtS≈4ΩA/c²; |vflux|=cs (horizonte acústico)`.
- Fato: Rotação e translação têm efeitos distintos sobre geodésicas; horizonte acústico é efetivo para excitações, não horizonte de buraco negro causado por nanoporos.
- Lacuna: Perfil 3D densidade/Ω, métrica ligada ao RLL, sinal instrumental e comparação GR física: TOKEN_VAZIO.
- Falsificador: Teste radial ∝r^-3 no exterior e sinais de rotação; comparar Lense–Thirring, Sagnac e relógios em referenciais claramente declarados.
- Feedback: Classificar analogias gravitacionais como escala/regime dependente; sem derivação independente não promover efeito cosmológico RLL.
- Status: `GR_BASELINE + ANALOGUE_BOUNDARY`. Fontes: RLL:ROUTE56; papers:SGPT; arXiv:2512.24344.

### HX10 — α-shapes, topologia persistente e Oxi-Shapes redox: comparação sem identidade

- Formula/limite: `α-shape(P,α) pela triangulação Delaunay; x_i∈[0,1] para ocupação redox; χ=V−E+F (sob topologia declarada)`.
- Fato: α-shapes (1983) recortam nuvens de pontos em escalas; Oxi-Shapes (2026) é representação tropical de redox bounded, com dados de cérebros de camundongos; não são a mesma construção.
- Lacuna: Ponte formal isomórfica, unidade/normalização de medidas, ruído e resultados de ablações: TOKEN_VAZIO.
- Falsificador: Controles por permutação de labels, troca de métrica e ruído; falsificar correspondência se desaparecer ao congelar dados ou não superar baseline.
- Feedback: Separar nota matemática de validação bioquímica; reportar casos negativos e anterioridade explícita antes de qualquer paper.
- Status: `MATHEMATICAL_PRIOR_ART + OPEN_COMPARISON`. Fontes: DOI:10.1109/TIT.1983.1056714; arXiv:2602.08832; Matem-tica-:K8_Poincare.



## Recuperação de obras e ideias que não podem desaparecer

| Ano | Obra | Contribuição que limita claims atuais | Status nesta rodada |
|---|---|---|---|
| 1931 | Onsager, *Reciprocal Relations in Irreversible Processes*, DOI 10.1103/PhysRev.37.405 e 38.2265 | Fluxos acoplados e reciprocidade condicionada à microreversibilidade | BASELINE_HISTORICAL |
| 1958 | Kedem & Katchalsky, DOI 10.1016/0006-3002(58)90330-5 | Membranas soluto/solvente pedem coeficientes cruzados | BASELINE_HISTORICAL |
| 1983 | Edelsbrunner–Kirkpatrick–Seidel, DOI 10.1109/TIT.1983.1056714 | α-shapes, Delaunay e escala geométrica não são invenção desta sessão | PRIOR_ART_FOUND |
| 2014 | Kissel et al., DOI 10.1038/nchem.2008 | Membrana 2D porosa candidata não é junção He4 experimental já demonstrada | MATERIAL_SOURCE |
| 2015 | Deng et al., DOI 10.1371/journal.pone.0126561 | Hiperosmolaridade→ROS em epitélio corneano já estudada | PRIOR_ART_FOUND |
| 2016 | Steinhauer, DOI 10.1038/nphys3863 | Horizonte análogo quântico ≠ buraco negro real | ANALOGUE_PRIOR_ART |
| 2025–2026 | Preprints arXiv 2601.08309, 2602.08832, 2603.21827, 2605.02419 | Fricção da hidratação, redox bounded, dipolo polar e difusio-osmose | SOURCE_READ, NOT_INDEPENDENTLY_REPLICATED |

**alphaXiv (biblioteca privada):** coleção `RAFAELIA Ω — Interfaces e anterioridades 10×7 — 2026-10-15`, folder ID `01a140c0-1345-79de-99d9-dc129d481d02` com 7 referências arXiv adicionadas. O rótulo falado 'Alpha Shapes' não correspondeu a repositório próprio verificável; a coleção alphaXiv e a referência matemática de α-shapes são rotas separadas. Nenhum repositório de terceiros foi alterado.

## Integração de autoridade (sem overclaim)

- **papers:** editor e catálogo deste programa; fontes de cada paper e revisões.
- **RLL:** consumidor de operadores/falsificadores, não prova biologia pela cosmologia ou recíproco.
- **Matem-tica-:** formalismo de α-shapes, coordenadas, topologia e fronteira da interpretação física.
- **Google Drive:** custódia privada, ledger append-only, proveniência e recibos; material privado não copiado para repositórios públicos.
- **alphaXiv:** literatura externa organizada, não certificação de resultado.

Nenhum símbolo recorrente como √3/2, 42, 21 ou 56 vale como peso de evidência. Navier–Stokes 3D global, Yang–Mills mass gap e Riemann permanecem problemas não resolvidos por estas discretizações.

## R3

**F_ok:** 10 propostas e 70 células editoriais geradas com prior art, mecanismo, controles e falsificadores (não medidas físicas). **F_gap:** replicação e dados fora da amostra, parâmetros específicos de membrana e termos RLL próprios = TOKEN_VAZIO. **F_next:** executar estudo fonte-side 1D córnea oxigênio×osmolaridade×ROS e M0–M2 nanopore, com dados de referência calibrados e gates G0–G7, sem promoção.
