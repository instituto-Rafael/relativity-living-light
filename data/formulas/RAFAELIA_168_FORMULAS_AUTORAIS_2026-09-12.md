# RAFAELIA — 168 Fórmulas Autorais / Candidatas Matemáticas
**Data:** 2026-09-12  
**Estado:** registry_candidate  
**claim_allowed:** false
> **Nota de autoria.** “Autoral” neste registro significa: fórmula, operador, índice, composição ou definição formulada/composta no projeto RAFAELIA. Não significa, por si só, novidade mundial, descoberta física, patenteabilidade ou validação por pares.
## Regras
- `SOURCE != EXECUTION != EVIDENCE != CLAIM`.
- `TOKEN_VAZIO != 0`.
- Fórmulas clássicas usadas como componentes não contam, sozinhas, como autoria RAFAELIA.
- Fórmulas de física recebem status de **diagnóstico/roteador candidato** até validação no domínio.
- Cada fórmula tem um teste/falsificador mínimo.
## Índice de famílias
- Epistemologia e Proveniência
- Geometria de Observação
- Recorrência Rafaeliana e Multibase
- Toro T7 e Ω7
- RMRCTI e Estabilidade ΔP
- Cascata, Avalanche e Cadeia de Eventos
- Worldlines e Tempos Múltiplos
- Magnetismo, Plasma e GRMHD
- Cosmologia e Roteamento de Modelos
- Informação, Hashing e Compressão
- Grafos, Semântica e Complementaridade
- Falsificabilidade, Gaps e Governança
## Registro completo
### Epistemologia e Proveniência
**AFR-001 — Índice de completude evidencial**
\[C_E = (S+E+R+F)/(4+V)\]
- **Estado:** `project-defined audit score`
- **Pai/proveniência:** RMRCTI/512 seeds
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Recompute from declared binary/weighted fields; reject if denominator semantics change.
- **claim_allowed:** `false`
**AFR-002 — Déficit de proveniência**
\[D_P = 1 - P_src·P_hash·P_time\]
- **Estado:** `project-defined audit deficit`
- **Pai/proveniência:** SOURCE≠EVIDENCE
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Each factor in [0,1]; reject if missing provenance is silently set to 1.
- **claim_allowed:** `false`
**AFR-003 — Peso de evidência rastreável**
\[W_E = 0.45P + 0.30R + 0.25F\]
- **Estado:** `project-defined weighted score`
- **Pai/proveniência:** 512 seeds weighting
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Verify weights sum to 1 and sensitivity to each component.
- **claim_allowed:** `false`
**AFR-004 — Vazio normalizado**
\[V_∅ = N_∅/(N_obs+N_∅)\]
- **Estado:** `project-defined missingness ratio`
- **Pai/proveniência:** TOKEN_VAZIO≠0
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Reject any pipeline converting TOKEN_VAZIO into observed zero.
- **claim_allowed:** `false`
**AFR-005 — Assimetria observado-vazio**
\[A_OV = (N_obs-N_∅)/(N_obs+N_∅)\]
- **Estado:** `project-defined audit asymmetry`
- **Pai/proveniência:** TOKEN_VAZIO
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Boundary test for all observed/all missing.
- **claim_allowed:** `false`
**AFR-006 — Energia de contradição**
\[E_C = Σ_i w_i·1[claim_i ⟂ evidence_i]\]
- **Estado:** `project-defined contradiction score`
- **Pai/proveniência:** governance invariants
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Each contradiction must carry a source ref and reversible flag.
- **claim_allowed:** `false`
**AFR-007 — Densidade de receipts**
\[ρ_R = N_receipts/N_actions\]
- **Estado:** `project-defined governance density`
- **Pai/proveniência:** append-only receipts
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Reject if actions without receipt are excluded from denominator.
- **claim_allowed:** `false`
**AFR-008 — Continuidade de proveniência**
\[K_P = Π_j c_j\]
- **Estado:** `project-defined chain continuity`
- **Pai/proveniência:** source→artefact→execution
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Each c_j∈[0,1]; zero if any required link absent.
- **claim_allowed:** `false`
**AFR-009 — Grau de reversibilidade**
\[R_v = N_reversible/N_mutations\]
- **Estado:** `project-defined rollback metric`
- **Pai/proveniência:** reverse_rollback
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Audit mutations and rollback paths.
- **claim_allowed:** `false`
**AFR-010 — Índice de não-regressão**
\[N_R = 1 - N_regressions/max(1,N_checks)\]
- **Estado:** `project-defined regression metric`
- **Pai/proveniência:** non_regression
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Replay prior checks on same fixture.
- **claim_allowed:** `false`
**AFR-011 — Entropia de estados epistemológicos**
\[H_E = -Σ_s p_s log2 p_s\]
- **Estado:** `project-defined epistemic distribution`
- **Pai/proveniência:** E/C/H/VAZIO states
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Check normalized probabilities.
- **claim_allowed:** `false`
**AFR-012 — Distância claim-evidência**
\[d_CE = ||v_claim-v_evidence||_W\]
- **Estado:** `project-defined semantic/audit distance`
- **Pai/proveniência:** claim boundary
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Unit-test metric symmetry only if W symmetric.
- **claim_allowed:** `false`
**AFR-013 — Taxa de promoção legítima**
\[Π_L = N_promoted_with_gate/N_promotion_attempts\]
- **Estado:** `project-defined promotion rate`
- **Pai/proveniência:** claim gate
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Any promotion without satisfied gate counts 0.
- **claim_allowed:** `false`
**AFR-014 — Pressão de falsificação**
\[F_P = N_active_falsifiers/(1+N_unfalsified_claims)\]
- **Estado:** `project-defined falsifier pressure`
- **Pai/proveniência:** falsifiability ladder
- **Domínio:** Epistemologia e Proveniência
- **Teste/falsificador:** Recompute under removal/addition of falsifiers.
- **claim_allowed:** `false`
### Geometria de Observação
**AFR-015 — Centro ponderado de janela**
\[c_W = Σ_i w_i x_i / Σ_i w_i\]
- **Estado:** `project-defined window centroid`
- **Pai/proveniência:** U3/U4/U5 shells
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Weights nonnegative; compare against unweighted centroid.
- **claim_allowed:** `false`
**AFR-016 — Raio epistemológico**
\[r_E = max_i ||x_i-c_W||·q_i\]
- **Estado:** `project-defined window radius`
- **Pai/proveniência:** observation shells
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** q_i must be declared confidence.
- **claim_allowed:** `false`
**AFR-017 — Espessura de casca**
\[Δ_C(k)=max_{i∈C_k}d_i-min_{i∈C_k}d_i\]
- **Estado:** `project-defined shell thickness`
- **Pai/proveniência:** C0/C1/C2
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Zero for degenerate shell.
- **claim_allowed:** `false`
**AFR-018 — Simetria twin**
\[S_T = 1-|d_+-d_-|/(d_++d_-+ε)\]
- **Estado:** `project-defined symmetry score`
- **Pai/proveniência:** U4_twins
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Swap invariance.
- **claim_allowed:** `false`
**AFR-019 — Assimetria radial**
\[A_R = Σ_i w_i sign(x_i-c)|x_i-c| / Σ_i w_i|x_i-c|\]
- **Estado:** `project-defined directional asymmetry`
- **Pai/proveniência:** observation geometry
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Mirror should flip sign.
- **claim_allowed:** `false`
**AFR-020 — Cobertura angular**
\[C_θ = |∪_i I_i|/(2π)\]
- **Estado:** `project-defined angular coverage`
- **Pai/proveniência:** observation windows
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Intervals modulo 2π.
- **claim_allowed:** `false`
**AFR-021 — Sobreposição de linha de visada**
\[O_LOS = Σ_{i<j} p_i p_j K(d_i,d_j)\]
- **Estado:** `project-defined superposition risk`
- **Pai/proveniência:** SAME_IMAGE≠SAME_EVENT
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Kernel K must be normalized.
- **claim_allowed:** `false`
**AFR-022 — Separação de épocas**
\[Δ_T = |t_emit,a-t_emit,b|/(1+|t_obs,a-t_obs,b|)\]
- **Estado:** `project-defined temporal separation`
- **Pai/proveniência:** multi-time observation
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Unit consistency required.
- **claim_allowed:** `false`
**AFR-023 — Índice de mistura foreground/background**
\[M_FB = H({p_fore,p_back,p_assoc})/log2 3\]
- **Estado:** `project-defined classification ambiguity`
- **Pai/proveniência:** foreground/background
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** 0 deterministic, 1 uniform.
- **claim_allowed:** `false`
**AFR-024 — Dispersão de redshift robusta**
\[D_z = MAD(z_i)/(1+median|z_i|)\]
- **Estado:** `project-defined robust dispersion`
- **Pai/proveniência:** observational windows
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Compare with bootstrap.
- **claim_allowed:** `false`
**AFR-025 — Coerência multi-banda**
\[C_MB = (2/(m(m-1)))Σ_{a<b} corr(r_a,r_b)\]
- **Estado:** `project-defined cross-band coherence`
- **Pai/proveniência:** multi-band observations
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Require common sampling or resampling receipt.
- **claim_allowed:** `false`
**AFR-026 — Desalinhamento espacial-espectral**
\[D_SE = 1-cos(angle(g_spatial,g_spectral))\]
- **Estado:** `project-defined misalignment`
- **Pai/proveniência:** cross-modal gradients
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Check undefined zero-gradient case -> TOKEN_VAZIO.
- **claim_allowed:** `false`
**AFR-027 — Densidade observacional**
\[ρ_O = N_valid/(Ω_sky·Δt·Δν)\]
- **Estado:** `project-defined observation density`
- **Pai/proveniência:** window metadata
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** All denominators must be positive and declared.
- **claim_allowed:** `false`
**AFR-028 — Índice de janela confiável**
\[J_W = C_θ·(1-V_∅)·(1-M_FB)·(1-D_z*)\]
- **Estado:** `project-defined composite window score`
- **Pai/proveniência:** window gate
- **Domínio:** Geometria de Observação
- **Teste/falsificador:** Each component normalized to [0,1].
- **claim_allowed:** `false`
### Recorrência Rafaeliana e Multibase
**AFR-029 — Rafaeliana inteira**
\[R_{n+1}=R_n+R_{n-1}+1\]
- **Estado:** `recovered/project sequence`
- **Pai/proveniência:** R_n=F_{n+3}-1
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Verify closed form against recurrence.
- **claim_allowed:** `false`
**AFR-030 — Fechamento Fibonacci-Rafael**
\[R_n-F_{n+3}+1=0\]
- **Estado:** `derived identity`
- **Pai/proveniência:** Rafaeliana inteira
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Induction on n.
- **claim_allowed:** `false`
**AFR-031 — Incremento Rafaeliano**
\[ΔR_n=R_{n+1}-R_n=R_{n-1}+1\]
- **Estado:** `derived identity`
- **Pai/proveniência:** R recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Algebraic check.
- **claim_allowed:** `false`
**AFR-032 — Curvatura discreta Rafaeliana**
\[κ_R(n)=R_{n+1}-2R_n+R_{n-1}=1-R_{n-1}+R_{n-2}\]
- **Estado:** `project-derived diagnostic`
- **Pai/proveniência:** R recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Verify simplification per chosen indexing.
- **claim_allowed:** `false`
**AFR-033 — Razão local regularizada**
\[q_R(n)=(R_{n+1}+1)/(R_n+1)\]
- **Estado:** `project-defined ratio`
- **Pai/proveniência:** R_n+1=F_{n+3}
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Compare asymptotic φ.
- **claim_allowed:** `false`
**AFR-034 — Erro áureo Rafaeliano**
\[e_φ(n)=|q_R(n)-φ|\]
- **Estado:** `project-defined convergence error`
- **Pai/proveniência:** golden-ratio limit
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Check tends downward after transient.
- **claim_allowed:** `false`
**AFR-035 — Energia de recorrência**
\[E_R(n)=|R_{n+1}-R_n-R_{n-1}-1|\]
- **Estado:** `project-defined residual`
- **Pai/proveniência:** R recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Must be 0 for exact sequence.
- **claim_allowed:** `false`
**AFR-036 — Recorrência perturbada**
\[R^ε_{n+1}=R^ε_n+R^ε_{n-1}+1+ε_n\]
- **Estado:** `project-defined perturbation model`
- **Pai/proveniência:** R recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Zero ε recovers base.
- **claim_allowed:** `false`
**AFR-037 — Resposta acumulada à perturbação**
\[A_ε(N)=Σ_{n≤N}|R^ε_n-R_n|\]
- **Estado:** `project-defined stability diagnostic`
- **Pai/proveniência:** perturbed recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Monotone in N by definition.
- **claim_allowed:** `false`
**AFR-038 — Recorrência modular**
\[R^{(m)}_n=R_n mod m\]
- **Estado:** `project-defined modular projection`
- **Pai/proveniência:** bases 7..14000
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Check periodicity empirically.
- **claim_allowed:** `false`
**AFR-039 — Período modular candidato**
\[P_R(m)=min{p>0:(R_{n+p},R_{n+p+1})≡(R_n,R_{n+1}) mod m}\]
- **Estado:** `project-defined period`
- **Pai/proveniência:** modular recurrence
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Brute-force finite-state verification.
- **claim_allowed:** `false`
**AFR-040 — Dobra modular Rafaeliana**
\[D_R^{(m)}(n)=min(R_n mod m, m-(R_n mod m))\]
- **Estado:** `project-defined fold`
- **Pai/proveniência:** modular fold
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Range [0,floor(m/2)].
- **claim_allowed:** `false`
**AFR-041 — Complemento Rafaeliano**
\[C_R^{(m)}(n)=(-R_n) mod m\]
- **Estado:** `project-defined complement`
- **Pai/proveniência:** modular symmetry
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** Double complement returns original residue.
- **claim_allowed:** `false`
**AFR-042 — Índice multibase Rafaeliano**
\[M_R(n)=Σ_{b∈B} w_b D_R^{(b)}(n)/⌊b/2⌋\]
- **Estado:** `project-defined multibase score`
- **Pai/proveniência:** B={7,14,35,50,70,140,...}
- **Domínio:** Recorrência Rafaeliana e Multibase
- **Teste/falsificador:** All terms normalized; test sensitivity to B.
- **claim_allowed:** `false`
### Toro T7 e Ω7
**AFR-043 — Estado toroidal 7D**
\[T_t=(θ_1,...,θ_7)_t ∈ (R/2πZ)^7\]
- **Estado:** `project-defined state space`
- **Pai/proveniência:** T^7/Ω7
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Check wrap invariance.
- **claim_allowed:** `false`
**AFR-044 — Passo toroidal acoplado**
\[θ_i'=(aθ_i+bθ_{i+1}+η_i) mod 2π\]
- **Estado:** `project-defined transition`
- **Pai/proveniência:** toro coupled state
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** a,b,η declared.
- **claim_allowed:** `false`
**AFR-045 — Distância circular por eixo**
\[d_i=min(|Δθ_i|,2π-|Δθ_i|)\]
- **Estado:** `project-defined per-axis fold`
- **Pai/proveniência:** toro
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Range [0,π].
- **claim_allowed:** `false`
**AFR-046 — Distância Ω7 ponderada**
\[D_Ω=√(Σ_i w_i d_i²)\]
- **Estado:** `project-defined Ω7 metric`
- **Pai/proveniência:** Ω7
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** w_i≥0.
- **claim_allowed:** `false`
**AFR-047 — Persistência Ω7**
\[P_Ω(t)=Σ_i w_i d_i(T_t,T_{t-1})\]
- **Estado:** `project-defined persistence`
- **Pai/proveniência:** Ω7
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** PERSISTENCE!=TRUTH.
- **claim_allowed:** `false`
**AFR-048 — Tremor direcional**
\[τ_{t,d}=dist(P_d(S_t),P_d(S_{t-1}))\]
- **Estado:** `recovered/project diagnostic`
- **Pai/proveniência:** Ω7 cascade
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Compare across directions.
- **claim_allowed:** `false`
**AFR-049 — Anisotropia Ω7**
\[A_Ω=max_d τ_{t,d}-min_d τ_{t,d}\]
- **Estado:** `project-defined anisotropy`
- **Pai/proveniência:** Ω7
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Zero if all equal.
- **claim_allowed:** `false`
**AFR-050 — Entropia direcional Ω7**
\[H_Ω=-Σ_d p_d log2 p_d, p_d=τ_d/Στ\]
- **Estado:** `project-defined direction entropy`
- **Pai/proveniência:** Ω7
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Handle Στ=0 as TOKEN_VAZIO/zero-tremor state.
- **claim_allowed:** `false`
**AFR-051 — Fluxo de contexto Ω**
\[Φ_Ω=τ_{t,Ω}/(ε+Σ_{d≠Ω}τ_{t,d})\]
- **Estado:** `project-defined context ratio`
- **Pai/proveniência:** Ω_CONTEXT
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** ε declared.
- **claim_allowed:** `false`
**AFR-052 — Retorno toroidal**
\[R_T(k)=1/(1+D_Ω(T_t,T_{t-k}))\]
- **Estado:** `project-defined recurrence score`
- **Pai/proveniência:** toro recurrence
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Peak at repeated states.
- **claim_allowed:** `false`
**AFR-053 — Bacia empírica toroidal**
\[B_T(δ)=P[D_Ω(T_t,T*)≤δ]\]
- **Estado:** `project-defined basin occupancy`
- **Pai/proveniência:** candidate attractor
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Requires declared T*,δ.
- **claim_allowed:** `false`
**AFR-054 — Curvatura de trajetória discreta**
\[K_T(t)=D_Ω(T_{t+1}-T_t,T_t-T_{t-1})\]
- **Estado:** `project-defined turn metric`
- **Pai/proveniência:** toro path
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Coordinate difference defined with wrap.
- **claim_allowed:** `false`
**AFR-055 — Energia de fechamento**
\[E_cl(T)=Σ_i sin²(θ_i/2)\]
- **Estado:** `project-defined closure energy`
- **Pai/proveniência:** toro origin closure
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Zero at all θ_i=0 mod 2π.
- **claim_allowed:** `false`
**AFR-056 — Índice Ω de estabilidade contextual**
\[S_Ω=(1/(1+P_Ω))(1/(1+A_Ω))(1+Φ_Ω)^{-1}\]
- **Estado:** `project-defined stability score`
- **Pai/proveniência:** Ω routing
- **Domínio:** Toro T7 e Ω7
- **Teste/falsificador:** Only operational, not physical.
- **claim_allowed:** `false`
### RMRCTI e Estabilidade ΔP
**AFR-057 — Delta-P canônico**
\[ΔP=P(stable|peak)-P(stable|nonpeak)\]
- **Estado:** `recovered/project metric`
- **Pai/proveniência:** gbs3_color.c
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Recompute from counts.
- **claim_allowed:** `false`
**AFR-058 — Erro-alvo 0.18**
\[e_18=|ΔP-0.18|\]
- **Estado:** `project-defined candidate distance`
- **Pai/proveniência:** ΔP candidate
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Not a physical error; compare across independent traces.
- **claim_allowed:** `false`
**AFR-059 — Score de faixa candidata**
\[S_18=max(0,1-e_18/δ)\]
- **Estado:** `project-defined band score`
- **Pai/proveniência:** target 0.18±δ
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** δ predeclared.
- **claim_allowed:** `false`
**AFR-060 — Integral cumulativa de contraste**
\[I_k=Σ_{i≤k}s_i(p_i/N_P-(1-p_i)/N_N)\]
- **Estado:** `recovered/project path lift`
- **Pai/proveniência:** RMRCTI integral
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Terminal identity I_N=ΔP on matching encoding.
- **claim_allowed:** `false`
**AFR-061 — Deriva local de ΔP**
\[v_Δ(t)=ΔP_t-ΔP_{t-1}\]
- **Estado:** `project-defined drift`
- **Pai/proveniência:** moving ΔP
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Zero under stationary candidate.
- **claim_allowed:** `false`
**AFR-062 — Aceleração de ΔP**
\[a_Δ(t)=v_Δ(t)-v_Δ(t-1)\]
- **Estado:** `project-defined second difference`
- **Pai/proveniência:** moving ΔP
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Noise sensitivity test.
- **claim_allowed:** `false`
**AFR-063 — Recuperação pós-perturbação**
\[R_Δ(k)=1-|ΔP_{t+k}-ΔP_pre|/(ε+|ΔP_post-ΔP_pre|)\]
- **Estado:** `project-defined recovery`
- **Pai/proveniência:** HETE loop
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Interpret only when denominator > ε.
- **claim_allowed:** `false`
**AFR-064 — Tempo de retorno ΔP**
\[T_ret=min{k>0:|ΔP_{t+k}-ΔP_pre|≤δ}\]
- **Estado:** `project-defined return time`
- **Pai/proveniência:** perturbation recovery
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** TOKEN_VAZIO if no return.
- **claim_allowed:** `false`
**AFR-065 — Persistência de faixa**
\[P_δ=(1/N)Σ_t 1[|ΔP_t-0.18|≤δ]\]
- **Estado:** `project-defined band persistence`
- **Pai/proveniência:** candidate target
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Independent-window requirement.
- **claim_allowed:** `false`
**AFR-066 — Robustez por seed**
\[R_seed=1-MAD_s(ΔP_s)/(δ+ε)\]
- **Estado:** `project-defined seed robustness`
- **Pai/proveniência:** multi-seed
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Clip/report raw if negative.
- **claim_allowed:** `false`
**AFR-067 — Separação de nulo**
\[Z_Δ=(ΔP_obs-median ΔP_null)/(MAD_null+ε)\]
- **Estado:** `project-defined robust null separation`
- **Pai/proveniência:** falsifier
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Null generation predeclared.
- **claim_allowed:** `false`
**AFR-068 — Penalidade de seleção pós-hoc**
\[Q_post=Z_Δ/√(1+log(1+N_trials))\]
- **Estado:** `project-defined search penalty`
- **Pai/proveniência:** multiple search
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Operational only.
- **claim_allowed:** `false`
**AFR-069 — Índice de bacia ΔP**
\[B_Δ=P(|ΔP-0.18|≤δ | admissible θ)\]
- **Estado:** `project-defined parameter basin`
- **Pai/proveniência:** parameter sweep
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Admissible region fixed before measurement.
- **claim_allowed:** `false`
**AFR-070 — Gate RMRCTI composto**
\[G_R=1[e_18≤δ]·1[R_seed≥r0]·1[Z_Δ≥z0]\]
- **Estado:** `project-defined gate`
- **Pai/proveniência:** claim ladder
- **Domínio:** RMRCTI e Estabilidade ΔP
- **Teste/falsificador:** Thresholds predeclared; false if any missing.
- **claim_allowed:** `false`
### Cascata, Avalanche e Cadeia de Eventos
**AFR-071 — Estado por evento**
\[X_k^+={x^μ,u^μ,p^μ,τ,g,F,ρ,T,B,c,prov,Σ}\]
- **Estado:** `project-defined event state`
- **Pai/proveniência:** worldline router
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Schema completeness test.
- **claim_allowed:** `false`
**AFR-072 — Propagação segmentada**
\[X_{k+1}^-=Φ_k(X_k^+;C_k)\]
- **Estado:** `project-defined segment map`
- **Pai/proveniência:** event-chain
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Zero-event chain should reduce to propagation.
- **claim_allowed:** `false`
**AFR-073 — Atualização por evento**
\[X_{k+1}^+=E_{k+1}(X_{k+1}^-;ξ_{k+1})\]
- **Estado:** `project-defined event operator`
- **Pai/proveniência:** event-chain
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Identity event recovers pre-event.
- **claim_allowed:** `false`
**AFR-074 — Composição causal**
\[Ψ_{0:n}=E_n∘Φ_{n-1}∘...∘E_1∘Φ_0\]
- **Estado:** `project-defined causal composition`
- **Pai/proveniência:** event-chain
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Order sensitivity explicit.
- **claim_allowed:** `false`
**AFR-075 — Jacobian local**
\[J_k=∂F_k/∂X_k\]
- **Estado:** `standard derivative used in project diagnostic`
- **Pai/proveniência:** cascade sensitivity
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Finite-difference cross-check.
- **claim_allowed:** `false`
**AFR-076 — Amplificação de cascata**
\[A_{i→j}=||J_{j-1}...J_i||\]
- **Estado:** `project-defined cascade diagnostic`
- **Pai/proveniência:** cascade
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Matrix norm declared.
- **claim_allowed:** `false`
**AFR-077 — Log-amplificação**
\[Λ_{i→j}=Σ_{k=i}^{j-1} log(||J_k||+ε)\]
- **Estado:** `project-defined stable diagnostic`
- **Pai/proveniência:** cascade log
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Compare to log of product when stable.
- **claim_allowed:** `false`
**AFR-078 — Ganho marginal de evento**
\[G_k=||X_k^+-X_k^-||/(ε+||X_k^-||)\]
- **Estado:** `project-defined event gain`
- **Pai/proveniência:** event impact
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Dimensionless after normalization.
- **claim_allowed:** `false`
**AFR-079 — Acoplamento cascata-observável**
\[C_CO=||∂O/∂X · ∂X/∂ξ||\]
- **Estado:** `project-defined sensitivity bridge`
- **Pai/proveniência:** observability
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Requires differentiable local model.
- **claim_allowed:** `false`
**AFR-080 — Memória de evento**
\[M_E(m)=corr(r_k,r_{k-m})\]
- **Estado:** `project-defined event memory`
- **Pai/proveniência:** residual chain
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Use robust corr for heavy tails.
- **claim_allowed:** `false`
**AFR-081 — Índice de avalanche**
\[A_V=max(0,Λ)/(1+N_events)\]
- **Estado:** `project-defined avalanche score`
- **Pai/proveniência:** computational sensitivity
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Not a physical law.
- **claim_allowed:** `false`
**AFR-082 — Índice de contração**
\[C_V=max(0,-Λ)/(1+N_events)\]
- **Estado:** `project-defined contraction score`
- **Pai/proveniência:** recovery
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Complementary to A_V.
- **claim_allowed:** `false`
**AFR-083 — Ressonância de eventos**
\[R_E=Σ_{i<j} w_ij cos(φ_i-φ_j)\]
- **Estado:** `project-defined phase coherence`
- **Pai/proveniência:** event timing
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** Phases must be defined from observables.
- **claim_allowed:** `false`
**AFR-084 — Score causal auditável**
\[S_CA=K_P·exp(-D_model)·(1-V_∅)\]
- **Estado:** `project-defined causal audit score`
- **Pai/proveniência:** provenance+cascade
- **Domínio:** Cascata, Avalanche e Cadeia de Eventos
- **Teste/falsificador:** D_model normalized/nonnegative.
- **claim_allowed:** `false`
### Worldlines e Tempos Múltiplos
**AFR-085 — Vetor de tempos**
\[T5=(τ_prop,t_coord,t_emit,t_arr,t_obs)\]
- **Estado:** `project-defined time tuple`
- **Pai/proveniência:** multi-time router
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** All entries tagged with frame.
- **claim_allowed:** `false`
**AFR-086 — Atraso de propagação observado**
\[Δt_prop=t_arr-t_emit\]
- **Estado:** `project-defined observed delay`
- **Pai/proveniência:** emission/arrival
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Frame and cosmological model declared.
- **claim_allowed:** `false`
**AFR-087 — Defasagem observador-emissor**
\[D_OE=(t_obs-t_arr)-(t_emit-τ_ref)\]
- **Estado:** `project-defined timing residual`
- **Pai/proveniência:** observer/emitter
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Reference τ_ref declared.
- **claim_allowed:** `false`
**AFR-088 — Dobra temporal normalizada**
\[F_T=Δτ/(|Δt_coord|+ε)\]
- **Estado:** `project-defined proper/coordinate ratio`
- **Pai/proveniência:** relativistic routing
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** No universal threshold.
- **claim_allowed:** `false`
**AFR-089 — Incompatibilidade de simultaneidade**
\[I_S=|t_emit,a-t_emit,b|/(|t_obs,a-t_obs,b|+ε)\]
- **Estado:** `project-defined simultaneity mismatch`
- **Pai/proveniência:** same image
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Large value flags projection mismatch.
- **claim_allowed:** `false`
**AFR-090 — Idade aparente corrigida**
\[A_app=t_obs-t_emit-model_delay\]
- **Estado:** `project-defined apparent-age residual`
- **Pai/proveniência:** observation
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Model delay explicit.
- **claim_allowed:** `false`
**AFR-091 — Sequência causal temporal**
\[Q_T=Π_k 1[t_{k+1}^{emit}≥t_k^{cause}]\]
- **Estado:** `project-defined causal ordering gate`
- **Pai/proveniência:** event chain
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Fail on causal inversion unless model explains.
- **claim_allowed:** `false`
**AFR-092 — Compactação temporal**
\[C_T=Σ_k Δτ_k / (Σ_k Δt_k+ε)\]
- **Estado:** `project-defined cumulative timing ratio`
- **Pai/proveniência:** worldline segments
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** All intervals same units.
- **claim_allowed:** `false`
**AFR-093 — Dispersão de tempos próprios**
\[D_τ=MAD(Δτ_k)/(|median Δτ_k|+ε)\]
- **Estado:** `project-defined proper-time dispersion`
- **Pai/proveniência:** segments
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Robustness check.
- **claim_allowed:** `false`
**AFR-094 — Peso temporal de evento**
\[w_k^T=exp(-|t_obs-t_k|/T0)\]
- **Estado:** `project-defined recency kernel`
- **Pai/proveniência:** event weighting
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** T0 declared.
- **claim_allowed:** `false`
**AFR-095 — Memória temporal ponderada**
\[M_T=Σ_k w_k^T r_k/Σ_k w_k^T\]
- **Estado:** `project-defined time-weighted residual`
- **Pai/proveniência:** longitudinal
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Check T0 sensitivity.
- **claim_allowed:** `false`
**AFR-096 — Divergência de relógios**
\[D_clk=||T5_a-T5_b||_W\]
- **Estado:** `project-defined multi-clock distance`
- **Pai/proveniência:** multi-object timing
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** W defines comparable axes.
- **claim_allowed:** `false`
**AFR-097 — Índice de horizonte operacional**
\[H_op=1/(1+|dτ/dt|/h0)\]
- **Estado:** `project-defined routing proxy`
- **Pai/proveniência:** strong-field selection
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Not a horizon detector; h0 declared.
- **claim_allowed:** `false`
**AFR-098 — Gate temporal multiframe**
\[G_T=1[frame_known]·1[clock_map_known]·1[causal_order_ok]\]
- **Estado:** `project-defined time gate`
- **Pai/proveniência:** worldline
- **Domínio:** Worldlines e Tempos Múltiplos
- **Teste/falsificador:** Fail closed on unknown mapping.
- **claim_allowed:** `false`
### Magnetismo, Plasma e GRMHD
**AFR-099 — Razão magneto-dinâmica RAFAELIA**
\[Λ_B=μ|∇B|/(m a_eff+ε)\]
- **Estado:** `recovered/project diagnostic`
- **Pai/proveniência:** magnetism notes
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Dimensionless consistency depends on μ definition.
- **claim_allowed:** `false`
**AFR-100 — Coerência orbital de disrupção**
\[C_P=τ_disruption/(τ_orbital+ε)\]
- **Estado:** `recovered/project timescale ratio`
- **Pai/proveniência:** magnetism notes
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Compare domain timescales.
- **claim_allowed:** `false`
**AFR-101 — Compactação gravitacional local**
\[K_R=r_g/(r+ε)\]
- **Estado:** `recovered/project compactness proxy`
- **Pai/proveniência:** magnetism notes
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** r_g convention declared.
- **claim_allowed:** `false`
**AFR-102 — Índice triplo magneto-gravito**
\[M_G=log(1+Λ_B)·log(1+C_P)·log(1+K_R)\]
- **Estado:** `project-defined composite`
- **Pai/proveniência:** magneto-gravity routing
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Operational triage only.
- **claim_allowed:** `false`
**AFR-103 — Desbalanço pressão-campo**
\[D_PB=(p_B-p_gas)/(p_B+p_gas+ε)\]
- **Estado:** `project-defined normalized imbalance`
- **Pai/proveniência:** MHD routing
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Range approx [-1,1] for nonnegative pressures.
- **claim_allowed:** `false`
**AFR-104 — Coerência helicidade-fluxo**
\[C_HF=|H_m|/(Φ_B²/L+ε)\]
- **Estado:** `project-defined helicity normalization`
- **Pai/proveniência:** plasma memory
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Geometry L declared.
- **claim_allowed:** `false`
**AFR-105 — Persistência de fluxo**
\[P_Φ=Φ_B(t+Δt)/(Φ_B(t)+ε)\]
- **Estado:** `project-defined flux persistence`
- **Pai/proveniência:** post-disruption plasma
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Check sign/absolute choice.
- **claim_allowed:** `false`
**AFR-106 — Índice de reconexão observável**
\[R_rec=ΔΦ_lost/(Φ_initial+ε)\]
- **Estado:** `project-defined flux-loss proxy`
- **Pai/proveniência:** reconnection
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Requires flux accounting.
- **claim_allowed:** `false`
**AFR-107 — Acoplamento magneto-térmico**
\[C_MT=|ΔT|·|ΔB|/(T0 B0+ε)\]
- **Estado:** `project-defined coupling indicator`
- **Pai/proveniência:** plasma
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Not causal by itself.
- **claim_allowed:** `false`
**AFR-108 — Gradiente de Alfvén relativo**
\[G_A=|∇v_A|/(|v_A|/L+ε)\]
- **Estado:** `project-defined gradient score`
- **Pai/proveniência:** MHD
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** L declared.
- **claim_allowed:** `false`
**AFR-109 — Torção toroidal de campo**
\[T_B=∮ B·dl /(L·B_rms+ε)\]
- **Estado:** `project-defined loop twist score`
- **Pai/proveniência:** toroidal plasma
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Path declared.
- **claim_allowed:** `false`
**AFR-110 — Índice de pluma magnetizada**
\[P_M=T_B·C_HF·(1-|D_PB|)\]
- **Estado:** `project-defined plume score`
- **Pai/proveniência:** toroidal plume
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Only comparative within same definition.
- **claim_allowed:** `false`
**AFR-111 — Resíduo GRMHD de rota**
\[R_GM=||O_obs-O_GRMHD||_W\]
- **Estado:** `project-defined fit residual`
- **Pai/proveniência:** GRMHD comparison
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Observable covariance W.
- **claim_allowed:** `false`
**AFR-112 — Gate magneto-físico**
\[G_M=1[units_ok]·1[regime_MHD]·1[source_B]·1[claim_boundary]\]
- **Estado:** `project-defined domain gate`
- **Pai/proveniência:** magneto router
- **Domínio:** Magnetismo, Plasma e GRMHD
- **Teste/falsificador:** Fail closed.
- **claim_allowed:** `false`
### Cosmologia e Roteamento de Modelos
**AFR-113 — Resíduo cosmológico tipado**
\[r_C=O_obs-O_model(θ,regime)\]
- **Estado:** `project-defined typed residual`
- **Pai/proveniência:** RLL router
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Observable units/covariance declared.
- **claim_allowed:** `false`
**AFR-114 — Energia residual normalizada**
\[E_COS=r_C^T C^{-1} r_C / N\]
- **Estado:** `project-defined normalized residual`
- **Pai/proveniência:** real data
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** C positive-definite.
- **claim_allowed:** `false`
**AFR-115 — Score de rota cosmológica**
\[S_route=exp(-E_COS)·G_T·G_M·(1-V_∅)\]
- **Estado:** `project-defined route score`
- **Pai/proveniência:** multi-regime
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Not model evidence by itself.
- **claim_allowed:** `false`
**AFR-116 — Separação background-local**
\[B_L=||r_background||/(||r_local||+ε)\]
- **Estado:** `project-defined residual ratio`
- **Pai/proveniência:** background vs local
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Model decomposition explicit.
- **claim_allowed:** `false`
**AFR-117 — Índice de contaminação LOS**
\[C_LOS=O_LOS·M_FB\]
- **Estado:** `project-defined contamination score`
- **Pai/proveniência:** line of sight
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Uses prior defined terms.
- **claim_allowed:** `false`
**AFR-118 — Ganho de inclusão de regime**
\[G_reg=E_before-E_after\]
- **Estado:** `project-defined improvement`
- **Pai/proveniência:** regime selection
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Penalize complexity separately.
- **claim_allowed:** `false`
**AFR-119 — Penalidade de regime**
\[P_reg=k_reg log(N+1)/N\]
- **Estado:** `project-defined complexity penalty`
- **Pai/proveniência:** model routing
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** k_reg declared.
- **claim_allowed:** `false`
**AFR-120 — Valor líquido de regime**
\[V_reg=G_reg-P_reg\]
- **Estado:** `project-defined net route value`
- **Pai/proveniência:** model selection
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Positive is operational preference only.
- **claim_allowed:** `false`
**AFR-121 — Compatibilidade multissonda**
\[C_MS=1/(1+Σ_j E_COS,j)\]
- **Estado:** `project-defined multi-probe score`
- **Pai/proveniência:** BAO/CMB/SN/growth
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Shared nuisance handled.
- **claim_allowed:** `false`
**AFR-122 — Tensão entre sondas**
\[T_MS=max_{a<b}||θ_a-θ_b||_{Σ_ab^{-1}}\]
- **Estado:** `project-defined parameter tension metric`
- **Pai/proveniência:** multi-probe
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Σ_ab covariance declared.
- **claim_allowed:** `false`
**AFR-123 — Estabilidade de calibração**
\[S_cal=1-MAD_s(θ_s)/(scale_θ+ε)\]
- **Estado:** `project-defined calibration robustness`
- **Pai/proveniência:** resampling
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** scale declared.
- **claim_allowed:** `false`
**AFR-124 — Índice de desdobramento causal**
\[D_causal=N_linked_observables/N_candidate_links\]
- **Estado:** `project-defined causal-link density`
- **Pai/proveniência:** scientific graph
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Only links passing provenance gate.
- **claim_allowed:** `false`
**AFR-125 — Prioridade de experimento**
\[P_exp=impact·uncertainty_reduction/(cost+ε)\]
- **Estado:** `project-defined experimental triage`
- **Pai/proveniência:** F_next
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Factors predeclared.
- **claim_allowed:** `false`
**AFR-126 — Gate de interpretação cosmológica**
\[G_C=G_T·1[covariance_ok]·1[primary_source]·1[regime_valid]\]
- **Estado:** `project-defined claim gate`
- **Pai/proveniência:** RLL
- **Domínio:** Cosmologia e Roteamento de Modelos
- **Teste/falsificador:** Fail closed.
- **claim_allowed:** `false`
### Informação, Hashing e Compressão
**AFR-127 — Identidade de fragmento composto**
\[ID_F=H(path||offset||length||crc||version)\]
- **Estado:** `project-defined content identity`
- **Pai/proveniência:** hash/provenance
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Collision resistance depends on H.
- **claim_allowed:** `false`
**AFR-128 — Continuidade hash temporal**
\[H_t=H(H_{t-1}||event_t)\]
- **Estado:** `project-defined append-only chain`
- **Pai/proveniência:** ledger
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Genesis fixed.
- **claim_allowed:** `false`
**AFR-129 — Distância de hashes semânticos**
\[D_H=hamming(sig_a,sig_b)/L\]
- **Estado:** `project-defined signature distance`
- **Pai/proveniência:** BITRAF/hash
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Fixed length L.
- **claim_allowed:** `false`
**AFR-130 — Compressão lógica observada**
\[C_L=1-bytes_index/(bytes_raw+ε)\]
- **Estado:** `project-defined logical compression`
- **Pai/proveniência:** compression
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Report physical and logical separately.
- **claim_allowed:** `false`
**AFR-131 — Redundância útil**
\[R_U=bytes_recoverable_redundancy/(bytes_raw+ε)\]
- **Estado:** `project-defined redundancy ratio`
- **Pai/proveniência:** archive nesting
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Recovery test required.
- **claim_allowed:** `false`
**AFR-132 — Eficiência de índice**
\[E_I=hits_valid/(bytes_index·latency+ε)\]
- **Estado:** `project-defined retrieval efficiency`
- **Pai/proveniência:** indexing
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Units treated as operational score.
- **claim_allowed:** `false`
**AFR-133 — Densidade semântica**
\[ρ_S=N_relations/N_tokens\]
- **Estado:** `project-defined semantic density`
- **Pai/proveniência:** semantic graph
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Tokenizer version fixed.
- **claim_allowed:** `false`
**AFR-134 — Entropia de zona**
\[H_Z=-Σ_b p_b log2 p_b\]
- **Estado:** `project-defined byte-zone entropy`
- **Pai/proveniência:** CTI
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Standard entropy used as component.
- **claim_allowed:** `false`
**AFR-135 — Deriva de zona**
\[D_Z=|H_Z(t)-H_Z(t-1)|+D_H(sig_t,sig_{t-1})\]
- **Estado:** `project-defined zone drift`
- **Pai/proveniência:** CTI
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Replay on unchanged source -> 0 ideally.
- **claim_allowed:** `false`
**AFR-136 — Fidelidade de reconstrução**
\[F_R=1-D_bytes·w_b-D_struct·w_s-D_sem·w_m\]
- **Estado:** `project-defined reconstruction fidelity`
- **Pai/proveniência:** reconstruction
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Weights sum≤1 and metrics normalized.
- **claim_allowed:** `false`
**AFR-137 — Profundidade de proveniência**
\[P_D=max path_length(source→claim)\]
- **Estado:** `project-defined provenance depth`
- **Pai/proveniência:** knowledge graph
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Longer not automatically better.
- **claim_allowed:** `false`
**AFR-138 — Custo de consulta normalizado**
\[Q_C=(tokens+α·io+β·cpu)/(useful_hits+ε)\]
- **Estado:** `project-defined query cost`
- **Pai/proveniência:** retrieval
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** α,β declared.
- **claim_allowed:** `false`
**AFR-139 — Score de cache auditável**
\[S_cache=hit_rate·freshness·K_P\]
- **Estado:** `project-defined cache score`
- **Pai/proveniência:** pipeline cache
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** Freshness defined.
- **claim_allowed:** `false`
**AFR-140 — Gate de artefato reprodutível**
\[G_A=1[hash]·1[version]·1[source]·1[replay]\]
- **Estado:** `project-defined artifact gate`
- **Pai/proveniência:** reproducibility
- **Domínio:** Informação, Hashing e Compressão
- **Teste/falsificador:** All terms required.
- **claim_allowed:** `false`
### Grafos, Semântica e Complementaridade
**AFR-141 — Peso relacional**
\[w_ij=P_ij·R_ij·F_ij\]
- **Estado:** `project-defined edge weight`
- **Pai/proveniência:** semantic graph
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Components normalized.
- **claim_allowed:** `false`
**AFR-142 — Centralidade de proveniência**
\[C_P(v)=Σ_{u→v} w_uv K_P(u→v)\]
- **Estado:** `project-defined provenance centrality`
- **Pai/proveniência:** knowledge graph
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** No truth implication.
- **claim_allowed:** `false`
**AFR-143 — Distância semântica auditável**
\[d_S(a,b)=αd_embed+βd_symbolic+γd_provenance\]
- **Estado:** `project-defined hybrid distance`
- **Pai/proveniência:** semantic indexing
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** α+β+γ=1.
- **claim_allowed:** `false`
**AFR-144 — Coerência de caminho**
\[K_path=Π_{e∈path}w_e\]
- **Estado:** `project-defined path coherence`
- **Pai/proveniência:** graph
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Long paths naturally penalized.
- **claim_allowed:** `false`
**AFR-145 — Surpresa de ligação**
\[I_link=-log2(P(edge|context)+ε)\]
- **Estado:** `project-defined link surprise`
- **Pai/proveniência:** relation discovery
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Probability model declared.
- **claim_allowed:** `false`
**AFR-146 — Complementaridade científica**
\[C_AB=I_link·K_path·(1-overlap_AB)\]
- **Estado:** `project-defined complementarity score`
- **Pai/proveniência:** paper linking
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Overlap metric declared.
- **claim_allowed:** `false`
**AFR-147 — Utilidade transversal**
\[U_T=Σ_domains gain_d/(1+cost_d)\]
- **Estado:** `project-defined cross-domain utility`
- **Pai/proveniência:** transversal view
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Gains empirically defined.
- **claim_allowed:** `false`
**AFR-148 — Pontuação de ponte distante**
\[B_D=C_AB·log2(1+graph_distance)\]
- **Estado:** `project-defined distant-bridge score`
- **Pai/proveniência:** cross-institution links
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Distance alone not evidence.
- **claim_allowed:** `false`
**AFR-149 — Conflito semântico**
\[C_S=Σ_k w_k·1[sign_a,k≠sign_b,k]\]
- **Estado:** `project-defined semantic conflict`
- **Pai/proveniência:** contradiction graph
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Requires aligned propositions.
- **claim_allowed:** `false`
**AFR-150 — Reconciliação mínima**
\[R_min=min_{path∈P(a,b)} Σ_e cost(e)\]
- **Estado:** `project-defined reconciliation cost`
- **Pai/proveniência:** graph search
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Edge costs nonnegative.
- **claim_allowed:** `false`
**AFR-151 — Índice de recorrência conceitual**
\[R_C=frequency(concept across independent sources)/N_sources\]
- **Estado:** `project-defined recurrence ratio`
- **Pai/proveniência:** corpus
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Independence tagged.
- **claim_allowed:** `false`
**AFR-152 — Densidade de antiderivadas**
\[A_D=N_valid_backtraces/N_observations\]
- **Estado:** `project-defined inverse-link density`
- **Pai/proveniência:** backtrace
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Valid means passes provenance gate.
- **claim_allowed:** `false`
**AFR-153 — Cobertura longitudinal**
\[L_C=N_events_linked/N_events_known\]
- **Estado:** `project-defined temporal graph coverage`
- **Pai/proveniência:** longitudinal
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Known event denominator explicit.
- **claim_allowed:** `false`
**AFR-154 — Gate de notificação científica**
\[G_N=1[C_AB≥c0]·1[K_P≥k0]·1[primary_sources]·1[human_review]\]
- **Estado:** `project-defined notification gate`
- **Pai/proveniência:** researcher notification
- **Domínio:** Grafos, Semântica e Complementaridade
- **Teste/falsificador:** Human review mandatory.
- **claim_allowed:** `false`
### Falsificabilidade, Gaps e Governança
**AFR-155 — Prioridade de gap**
\[P_gap=log2(I)+log2(U)-log2(E)\]
- **Estado:** `recovered/project triage`
- **Pai/proveniência:** gap retrofeedback
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** I,U,E positive discrete factors.
- **claim_allowed:** `false`
**AFR-156 — Urgência ajustada por dependência**
\[U_D=P_gap/(1+N_blockers)\]
- **Estado:** `project-defined dependency score`
- **Pai/proveniência:** critical path
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Blockers counted from DAG.
- **claim_allowed:** `false`
**AFR-157 — Ganho de evidência**
\[G_E=U_before-U_after\]
- **Estado:** `project-defined uncertainty gain`
- **Pai/proveniência:** retrofeedback
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Uncertainty metric declared.
- **claim_allowed:** `false`
**AFR-158 — Eficiência de falsificação**
\[E_F=G_E/(cost+ε)\]
- **Estado:** `project-defined falsifier efficiency`
- **Pai/proveniência:** experiment planning
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Cost model declared.
- **claim_allowed:** `false`
**AFR-159 — Cobertura de falsificadores**
\[C_F=N_hypotheses_with_falsifier/N_hypotheses\]
- **Estado:** `project-defined falsifier coverage`
- **Pai/proveniência:** governance
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Hypothesis registry fixed.
- **claim_allowed:** `false`
**AFR-160 — Risco de claim**
\[R_C=(1-K_P)(1-C_F)(1-N_R)\]
- **Estado:** `project-defined claim risk`
- **Pai/proveniência:** claim governance
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** All components [0,1].
- **claim_allowed:** `false`
**AFR-161 — Maturidade de evidência**
\[M_E=(R_level/6)·K_P·C_F\]
- **Estado:** `project-defined rigor score`
- **Pai/proveniência:** R0..R6 ladder
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** R_level integer 0..6.
- **claim_allowed:** `false`
**AFR-162 — Taxa de contradição preservada**
\[T_C=N_contradictions_preserved/N_contradictions_found\]
- **Estado:** `project-defined audit integrity`
- **Pai/proveniência:** append-only
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Must approach 1.
- **claim_allowed:** `false`
**AFR-163 — Índice de supersessão limpa**
\[S_S=N_superseded_with_predecessor/N_superseded\]
- **Estado:** `project-defined genealogy quality`
- **Pai/proveniência:** append-only
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Predecessor links verified.
- **claim_allowed:** `false`
**AFR-164 — Débito de TOKEN_VAZIO**
\[D_V=Σ_g urgency_g·1[state_g=TOKEN_VAZIO]\]
- **Estado:** `project-defined missingness debt`
- **Pai/proveniência:** gaps
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Urgency rubric fixed.
- **claim_allowed:** `false`
**AFR-165 — Velocidade de fechamento**
\[V_F=ΔN_closed/Δt\]
- **Estado:** `project-defined operational velocity`
- **Pai/proveniência:** project management
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** No quality claim.
- **claim_allowed:** `false`
**AFR-166 — Qualidade de fechamento**
\[Q_F=mean(K_P·C_F·N_R | closed)\]
- **Estado:** `project-defined closure quality`
- **Pai/proveniência:** gap closure
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Closed set fixed.
- **claim_allowed:** `false`
**AFR-167 — Regra de parada evidencial**
\[STOP=1[G_marginal<G_next]∨1[fail_closed]∨1[budget≤0]\]
- **Estado:** `project-defined stop condition`
- **Pai/proveniência:** bounded permutation
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** Each trigger logged.
- **claim_allowed:** `false`
**AFR-168 — Score de excelência operacional**
\[X_O=Q_F·N_R·Π_L·(1-V_∅)\]
- **Estado:** `project-defined operational excellence score`
- **Pai/proveniência:** program governance
- **Domínio:** Falsificabilidade, Gaps e Governança
- **Teste/falsificador:** No scientific truth implication.
- **claim_allowed:** `false`
## R3
**F_ok:** 168 fórmulas registradas em 12 famílias, com IDs estáveis, proveniência e testes mínimos.
**F_gap:** novidade externa não auditada; várias fórmulas são definições/diagnósticos candidatos e não leis físicas.
**F_next:** executar deduplicação contra o registro de 512 sementes, ligar cada fórmula aos pais exatos e promover apenas as que sobreviverem a testes simbólicos/numericos e de domínio.