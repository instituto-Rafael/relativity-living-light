# RLL — Matriz de papers modernos, variância, incerteza e urgência — 2026-08-07 V1

Status epistemológico: **auditável / fail-closed / claim_allowed=false / publication_ready=false**.

Esta matriz não converte papers em evidência do RLL. Ela registra como cada resultado moderno altera o desenho dos testes, quais variâncias precisam ser medidas e qual receipt deve existir para fechar cada lacuna.

## Definições operacionais de variância

- **observacional-estatística**: covariance/precision/error model do produto observacional;
- **sistemática**: calibração, seleção, foreground, escala, nuisance e modelagem instrumental/astrofísica;
- **amostra/calibração**: mudança ao trocar Pantheon+/DES-SN5YR/Dovekie/Union etc.;
- **multiseed/otimizador**: spread entre starts; mede estabilidade numérica, não posterior;
- **prior/bound**: dependência de prior e parâmetros que terminam em limites;
- **identificabilidade**: parâmetro só é interpretável quando o dado possui suporte para restringi-lo;
- **backend**: CLASS/CAMB/integração/tolerâncias/versionamento;
- **seleção de modelo**: chi2/AIC/BIC/profile/logZ não são intercambiáveis;
- **proveniência**: hash, release, ordenação, semântica da matriz, licença e cadeia de custódia.

## Evidência já materializada

Pantheon+ e DES-Dovekie possuem execuções full-matrix no PR #651. Pantheon+ usa full covariance e Dovekie usa a `STAT+SYS.npz` oficial como **precision/inverse covariance**. O resultado RLL em ambos é praticamente aninhado em LambdaCDM e os melhores `z_t` ficam além do suporte em redshift das amostras. Isso bloqueia interpretação dos parâmetros RLL em SN-only, mesmo quando o otimizador converge.

- Pantheon+: `z_t/z_max = 4.12917`, Δχ²(RLL−LCDM) ≈ `4.55e-13`, ΔBIC `+22.2383`.
- Dovekie: `z_t/z_max = 3.75392`, Δχ²(RLL−LCDM) ≈ `−7.50e-8`, ΔBIC `+22.5198`.
- Dovekie CPL: `wa=-3.0`, exatamente no bound inferior declarado; interpretação de `wa` permanece bloqueada.

## Paper → variância → ajuste obrigatório

| Paper / fonte | O que muda no RLL | Variância crítica | Ajuste obrigatório | Prioridade |
|---|---|---|---|---|
| DESI DR2 Results II, arXiv:2503.14738 | Benchmark oficial BAO/CMB/SN e referências LCDM/w0wa | amostra, modelo, proveniência | reproduzir chains/posterior maxima oficiais; residual por tracer; rd explícito | P0 |
| DESI DR2 galaxy/QSO validation, arXiv:2503.14742 | tensão pode ser localizada por tracer/data-vector | sistemática, tracer | leave-one-tracer-out + covariance provenance | P0 |
| DESI DR2 extended DE, arXiv:2503.14743 | informação sobre DE é redshift-dependent | identificabilidade | profile/ablation de `z_t` por janela de redshift | P0 |
| DES-Dovekie, MNRAS 548/stag632 | recalibração altera Omega_m e reduz preferência por DE dinâmica | calibração, sistemática | Pantheon+ Hubble-flow-only com nuisance idêntico ao Dovekie | P0 |
| Dynamic or Systematic?, MNRAS stag615 | offset low-z/high-z pode competir com DE dinâmica em Bayes | sistemática, modelo | incluir modelo explícito de offset e competir contra CPL/RLL em logZ | P0 |
| Bayesian view of DESI DR2, arXiv:2603.05472 | Ockham/prior-volume pode inverter leitura de Delta-chi2 | prior, modelo | nested sampling real + logZ error + profile likelihood + réplica independente | P0 |
| ACT DR6 likelihoods, arXiv:2503.14452 | CMB independente TT/TE/EE e lensing | foreground, backend | likelihood ACT real, nuisance foreground versionado, LCDM reproduzido primeiro | P1 |
| ACT DR6 foreground validation, arXiv:2506.06274 | foreground é eixo explícito de robustez | sistemática | baseline-vs-extended foreground receipt | P1 |
| ACT DR6 extended models, JCAP 2025/11/063 | combinação de datasets altera extensões | modelo, combinação | contribuição de logL/chi2 por likelihood e substituições Planck/ACT/WMAP, DESI/BOSS | P1 |
| DES Y6 3x2pt, arXiv:2601.14559 | testa crescimento/S8, ausente em SN-only | covariance, sistemática, backend | likelihood Y6, scale cuts, nuisance, S8 via perturbation backend | P1 |
| DES Y6 analysis framework, arXiv:2601.14859 | posterior projection, baryons e galaxy bias entram no gate | prior, sistemática | matriz de scale cuts + posterior-projection + nuisance versionado | P1 |
| DESI-independent DES Y6 angular BAO, arXiv:2601.14864 | fornece teste sem sobreposição espacial DESI | correlação/amostra | cross-check BAO não sobreposto; proibir combinação ingênua de amostras correlacionadas | P1 |
| CAMB v2, arXiv:2607.14854 + CLASS | eleva referência numérica de perturbações | backend, física | CLASS×CAMB LCDM/CPL e contrato perturbativo RLL explícito | P1 |
| H0 corrected Pantheon+/Dovekie, arXiv:2607.24443 | atualização muito recente do ladder | calibração, modelo | WATCH: não promover sozinho; exigir likelihood reproduzível e separar early/late-time | P2 |

## Ignorados/deixados que agora entram no controle

1. **Registry SN envelhecido**: o V1 dizia “full likelihood ausente”; após as execuções, isso ficou parcialmente superado. O vazio correto é nuisance comum + boundary + identificabilidade.
2. **DESI DR2 chains**: os cosmology chains e posterior-maximization products foram publicados em 2025-10-06. Não faz mais sentido manter reprodução oficial como dependência abstrata; os produtos derivados estão acessíveis e devem ser materializados.
3. **Magnitude offset low-z/high-z**: não estava no gate original e agora vira concorrente explícito de CPL/RLL.
4. **BAO overlap/correlation**: a análise DES Y6 DESI-independent mostra que sobreposição/correlação pode alterar a significância; vira gate de correlação.
5. **Posterior projection**: DES Y6 metodologia trata isso explicitamente; convergência MCMC não basta.
6. **ACT foreground variance**: spectra high-l exigem sensibilidade ao modelo de foreground.
7. **RLL perturbation closure**: importabilidade de CLASS/CAMB nunca fecha o gap; é necessário definir sound speed/anisotropic stress/PPF ou teoria equivalente e estabilidade.
8. **H0 em SN-only**: com magnitude absoluta perfilada, H0 não é medido pela forma do Hubble diagram; qualquer claim de H0 deve vir de likelihood de calibração/distance ladder separada.

## Fila operacional

P0: DESI DR2 reprodução → Bayes/profile real → SN common-nuisance → RLL identifiability → CPL bound sensitivity → systematic-vs-dynamic model selection.

P1: CLASS/CAMB perturbations → DES Y6 3x2pt → ACT DR6 → BAO overlap control → H0 formal.

P2: licença/redistribuição e watch de resultados muito recentes ainda não promovidos a referência canônica.

## Regra de encerramento

Nenhuma lacuna fecha por paper, citação, melhor-fit, BIC ou import de backend. Fecha somente por **receipt materializado**, com input hashes/release IDs, nuisance/prior contract, método, incerteza/variância correspondente, output hashes, teste adversarial aplicável e `claim_allowed=false` até revisão independente.
