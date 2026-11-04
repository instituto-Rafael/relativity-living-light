# Registro observacional — LHCb, B0 → μ+ μ− e “zeptoverso”

**Data:** 2026-11-04 (America/Sao_Paulo)  
**Chave:** RLL-OBS-2026-11-04-LHCB-B0-MUMU  
**Classe:** física de partículas / decaimento raro / inferência indireta  
**Estado:** REFERENCED_PREPRINT; triagem documental; execução RLL NOT_RUN  
**Autoridade científica:** colaboração LHCb. RLL é curador, não autor do experimento.  
**PV:** SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM  
**claim_allowed para nova física, matéria escura ou confirmação RLL:** false

## Fonte e proveniência

1. **Preprint primário:** LHCb Collaboration, *Evidence for the decay B0 → μ+ μ− and improved measurements of the decay Bs0 → μ+ μ−*, arXiv:2611.00230, submetido 2026-10-30. https://arxiv.org/abs/2611.00230
2. **Divulgação da colaboração, 2026-11-03:** https://lhcb-outreach.web.cern.ch/2026/11/03/evidence-for-the-decay-b0%E2%86%92%CE%BC%CE%BC-and-improved-measurements-of-bs0%E2%86%92%CE%BC%CE%BC/
3. **Comunicado CERN, 2026-11-03:** https://home.cern/lhcb-finds-evidence-of-one-in-ten-billion-particle-decay/
4. **Jornalismo:** recorte BBC News Brasil fornecido pelo usuário, 2026-11-04, título “O que é o zeptoverso descoberto por cientistas, mundo 100 bilhões de vezes menor que um átomo”. O título não representa descoberta literal de um universo separado.

## Fatos observacionais versus hipóteses

- Canal: decaimento de méson B0 (quark beauty/bottom + antiquark down) em dois múons de cargas opostas.
- Evidência para B0 → μ+ μ−: 3,0 sigma em Run 3 (2024–2025) e 3,2 sigma combinando Run 1+2+3; **não** atingiu 5 sigma de observação consolidada.
- O Modelo Padrão prevê ramificação de ordem 1/10 bilhões desses decaimentos, o que não é contagem direta de 10 bilhões de ocorrências vistas.
- Dados Run 3: luminosidade integrada de 18 fb^-1 a energia de colisão de 13,6 TeV, segundo o abstract arXiv.
- O mesmo estudo melhora medidas de Bs0 → μ+ μ−; vida efetiva reportada 1,60 ± 0,16 (estat.) ± 0,01 (sist.) ps, segundo LHCb Outreach.
- **Compatível com Modelo Padrão**. Nenhuma partícula de matéria escura, nova força ou nova cosmologia foi observada nesse resultado.
- Status do artigo: preprint disponibilizado e submetido para publicação; revisão/publicação final não verificada nesta triagem.

## Checagem da escala “zeptoverso”

- 1 zeptômetro = 10^-21 m; tamanho atômico característico ~10^-10 m, razão de ordens de grandeza ~10^11.
- “Zeptoverso” é linguagem de divulgação para efeitos possíveis de física a pequenas distâncias. O detector **não formou uma imagem espacial de resolução 1 zeptômetro**; mediu decaimentos e suas distribuições, capazes de impor restrições indiretas, dependentes do modelo, a novos processos de alta energia.
- A duração típica ~1,5 ps da divulgação refere-se a hádrons com quark beauty, não ao decaimento experimental de um quark livre e isolado.
- Possíveis novas partículas (Higgs adicional, bóson Z', leptoquarks) são hipóteses que poderiam alterar amplitudes; **não** foram detectadas aqui.

## Fronteira com RLL — Relativity Living Light

**Transferível como método:** fonte original → previsão → observável → incerteza → falsificador → resultados negativos → revisão e reprodução.

**Não transferível sem equação:** B0/Bs0 → μμ mede dinâmica de sabor em física de partículas. Não testa diretamente H(z), Ω_s0, plasma cosmológico nem propagação fotônica RLL. Para haver ponte física, formalizar um acoplamento/operador explícito, previsão diferencial da taxa/tempo efetivo e um likelihood comparável ao Modelo Padrão, com propagação de incerteza e falsificador pré-definido.

**RLL_LHCB_PHYSICAL_BRIDGE:** TOKEN_VAZIO_TIPADO; não confundir proximidade conceitual com evidência causal.

## Gates, lacunas e rollback

1. TOKEN_VAZIO_PUBLICATION_FINAL: verificar peer review, versão final, correções.
2. TOKEN_VAZIO_LIKELIHOOD: obter material estatístico público suficiente para reprodução independente; dados brutos LHCb não reprocessados nesta triagem.
3. TOKEN_VAZIO_RLL_PREDICTION: derivar observável próprio antes de aplicar um teste RLL.
4. TOKEN_VAZIO_INDEPENDENT_REPLICATION: resultado da colaboração não constitui execução feita pelo RLL.
5. Proibido promover “matéria escura encontrada”, “zeptômetro fotografado”, “RLL comprovado”, “nova física demonstrada” ou “5 sigma alcançados”.

Mudança permitida: **registro + ponte de índice, sem código, dados, workflows ou ajuste cosmológico**. Branch draft reversível; correção por novo commit, nenhuma exclusão silenciosa. claim_allowed=false para todas as extrapolações.

**R3:** F_ok = fonte primária + classificação verificadas; F_gap = publicação final, likelihood e previsão física RLL; F_next = revisão técnica independente, sem promoção de claim.

**μID:** MU-RLL-LHCB-ZEPTOVERSE-20261104-S1 | parent=CURRENT_STATE_20261104 | kind=SOURCE_TRIAGE | routes=P,C,R,I,E | rollback=DRAFT_CLOSE.
