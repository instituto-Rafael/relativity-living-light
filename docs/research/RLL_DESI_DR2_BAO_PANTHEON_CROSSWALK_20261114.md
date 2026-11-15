# RLL Ω — Auditoria inicial DESI DR2 × Pantheon+ × ΛCDM/wCDM/CPL/RLL (2026-11-14)

**Estado:** INVESTIGATION_SCOPED / BAO_ONLY_LOCAL_FIT / NOT_EXTERNAL_REPLICATION. **claim_allowed=false**. Não altera código cosmológico nem dados de origem. Sem merge, sem publicação de resultado como descoberta.

## Raízes consultadas

- Produtor RLL: `rll_vs_lcdm.py` na main (blob Git `6ff9d76d6dfa5859e139521af29f876bfc049c84`) e `VALIDATION_STATUS.md`, `NEXT_RLL_VALIDATION_STEP.md`.
- Observações materializadas no produtor: `data/real/cosmology/desi_dr2_bao_primary_points.csv` e `desi_dr2_bao_covariance_summary.csv` (13 observáveis, BGS + seis pares DM/DH). Origem indicada no CSV: DESI DR2 Results II, Table IV, arXiv:2503.14738; **conferência independente valor a valor com o download oficial ainda NOT_RUN**.
- Pantheon+ oficial: https://github.com/PantheonPlusSH0ES/DataRelease ; repositório RLL `data/real/cosmology/pantheon_plus`. O `VALIDATION_STATUS.md` documenta falta de arquivos Pantheon para seu CLI real anterior. **Este lote NÃO executou likelihood Pantheon+**.
- Corpus privado de artigos: `rafaelmeloreisnovo/papers` (leitura de README/AGENTS e paper de octógono), não copiar conteúdo privado para esta branch.
- Geometria autoral: arquivo `papers/octagon_k8_complete_geometry_v1/paper.md` (no repositório papers), com V=57/E=136/F=81; formalização geométrica NÃO determina H(z) nem um volume cosmológico observacional sem uma ponte dimensional, dinâmica e inferencial.
- Índice Drive `RAFAELIA — Formula & Calculation Memory Index Ω`, abas `FORMULAS_122_V1_20260915`, `GEOMETRY_V1_20260915`, etc. Primeiras linhas efetivamente lidas: `F001..F011` são majoritariamente simbólicas; não injetar `VQF`, `Ω=Amor+Ética+Coerência` como termos físicos. Identidade de fórmula, derivação e observação são tipos distintos.
- O repositório público `rafaelmeloreisnovo/math` declara no próprio README ser coleção de manuscritos gerados por modelo interno da OpenAI, muitos não formalizados; **não atribuir esses manuscritos como matemática de autoria RAFAELIA nem como teoremas verificados**.

## Modelo e método da comparação preliminar

Foram transcritos em arquivo local os **13 números e desvios** já exibidos pelo produtor RLL e seis coeficientes de correlação entre os pares DM/DH, tomando matriz bloco-diagonal e BGS isotrópico. A transcrição ainda requer comparação byte/row com a origem oficial. Cálculo local executado em Python/NumPy/SciPy, mínimos quadrados multistart, quadratura Gauss-Legendre de 48 pontos, sem ajuste de Pantheon/CMB/CC e sem priors cosmológicos externos. Parâmetro instrumental `q=c/(H0*r_d)`: BAO-only não separa H0 de r_d.

Parâmetros variáveis: ΛCDM `(q,Ωm)` k=2; wCDM `(q,Ωm,w)` k=3; CPL `(q,Ωm,w0,wa)` k=4; RLL logístico `(q,Ωm,Ωs0,zt,wt)` k=5. Outras parcelas (radiação/neutrinos/curvatura) omitidas neste escopo de redshift: **aproximação**, não pipeline Boltzmann completo. A forma RLL é a função `e_rll_logistic` no produtor.

Métrica: `χ² = r^T C^{-1} r` com cada par (DM,DH) correlacionado, `AIC=χ²+2k`, `AICc=AIC+2k(k+1)/(n-k-1)`, `n=13`. Sem `-2log|C|` porque a covariância é tratada como fixa e comum entre modelos (apenas diferenças interpretadas). Os parâmetros e limites foram escolhidos para exploração, **não** inferência final; RLL `wt ≥ 0.05`.

| Modelo | n | k | min χ² | AIC | AICc | Comentário |
|---|---:|---:|---:|---:|---:|---|
| ΛCDM | 13 | 2 | 10.53863 | 14.53863 | 15.73863 | Melhor AICc deste escopo |
| wCDM constante | 13 | 3 | 9.32424 | 15.32424 | 17.99091 | χ² menor, penalização maior |
| CPL w0waCDM | 13 | 4 | 5.81207 | 13.81207 | 18.81207 | χ² mínimo, complexidade maior |
| RLL logístico | 13 | 5 | 8.09884 | 18.09884 | 26.67026 | Nenhuma superioridade evidenciada |

Melhores parâmetros locais (ordem dos parâmetros acima):
- ΛCDM = `[29.521723, 0.297345]`;
- wCDM = `[30.038167, 0.297525, -0.914491]`;
- CPL = `[32.834733, 0.386167, -0.183275, -2.705491]`;
- RLL = `[28.450109, 0.139417, 0.130174, 0.397150, 0.050000]`.

**Falsificadores / riscos:** (i) RLL `wt` no limite inferior significa solução dependente de fronteira do otimizador: checar estabilidade, perfis e priors; (ii) avaliar convergência com 24/48/96/192 nós; (iii) usar matriz DESI oficial exata e tolerâncias de rounding; (iv) garantir independência entre H(z) do arquivo legado RLL e BAO (há linhas rotuladas `CC+BAO_BOSS` e `BAO_Lya`, que não podem ser simplesmente somadas ao likelihood BAO como medidas independentes); (v) não confundir redução de χ² com significância, posterior Bayesiano ou evidência de nova física; (vi) RLL aproxima ΛCDM em `Ωs0=0` e outros parâmetros ficam não identificáveis nessa fronteira; AICc é diagnóstico exploratório, não prova bayesiana; (vii) correções de covariância e sistemáticas entre levantamentos permanecem pendentes.

## Gate Pantheon+

**Pantheon+ ≠ Pantheon antigo ≠ SH0ES calibration.** A publicação oficial Scolnic et al. 2022 fornece 1701 curvas de luz de 1550 SNe Ia únicas. A comparação deve usar `Pantheon+SH0ES.dat` com **matriz STAT+SYS compatível**, seleção de redshifts, covariância completa e marginalização consistente da magnitude absoluta `M_B`/intercepto; evitar dobrar o prior de H0 do SH0ES. Fontes primárias: https://github.com/PantheonPlusSH0ES/DataRelease e doi:10.3847/1538-4357/ac8b7a. Input→ingestão→ajuste→posterior = **NOT_RUN neste lote**.

## Separação de tarefas

1. [N0] Existe código RLL para ΛCDM, CPL e RLL logístico e dados de 13 pontos BAO no GitHub. Este comparador **não implementa wCDM constante**; o ajuste acima foi feito em script local exploratório distinto.
2. [N0/local] Os quatro números de ajuste foram calculados sobre transcrição local dos 13 pontos materializados; **não têm o status** de execução CI na HEAD do RLL, nem de comparação DESI oficial verificada.
3. [N2] A geometria octogonal/hexagonal pode sugerir parametrização angular ou regularização de problemas inversos, mas deve produzir observáveis `D_M/r_d`, `D_H/r_d`, `D_V/r_d`, `μ(z)`, `H(z)` com unidades, transformação definida, balanço energético e equações diferenciais físicas; sem isso não é um modelo concorrente.
4. [N5] Likelihood oficial DESI 13×13 exata; Pantheon+ STAT+SYS processada; MCMC/nested sampling; previsões CMB/growth completas; inferência de novidade: **TOKEN_VAZIO/NOT_RUN**.

## Próximo delta mínimo

Construir teste automatizado de integridade *row-by-row* contra DESI Cobaya/DR2 oficial; readback e digest de inputs, import Pantheon+ oficial com covariância; comparar ΛCDM, wCDM, CPL e RLL pela **mesma likelihood** e mesma política de prior/nuisance; confrontar resultados com publicação DESI e estudos independentes em vez de ajustar dados artificiais. Só então testar se qualquer parâmetro geométrico prediz um observável novo.

**R3:** F_ok = fonte identificada, comparativo BAO-only exploratório calculado; F_gap = fonte oficial byte/row, Pantheon+, CI, estabilidade de ajuste; F_next = validação de integridade do vetor DESI e reexecução contra likelihood oficial. Rollback = descartar branch isolada, sem remover documentação ou mudar main. **claim_allowed=false.**
