# RLL × neutrinos × cosmologia — ponte de evidência (2026-10-28)

**Estado:** `METADATA_ONLY / FAIL_CLOSED`. Nenhum dado bruto, likelihood conjunta, incerteza propagada nem refit RLL foi executado neste delta. `claim_allowed=false`.

## Motivo e fronteira

A notícia [USP, 22/10/2026](https://jornal.usp.br/artigos/nobel-de-fisica-2026-e-neutrinos/) contextualiza o Nobel de Francis Halzen (IceCube) e motivou verificação observacional. A importância de neutrinos astrofísicos NÃO equivale à detecção de um termo cosmológico RLL. `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

RLL contém a matriz de falsificabilidade `RLL_FALSEABILITY_MATRIX.md` e o estado `docs/presentation/05_CURRENT_STATE_RLL.md`. Esta ponte complementa, sem substituir, a cadeia e sem editar a física.

## Fontes primárias modernas e limites corretos

| Fonte | O que existe | Limite de interpretação |
| --- | --- | --- |
| [IceTracks-DR2 / 21 maio 2026](https://doi.org/10.7910/DVN/MMIIZA) | 14 anos de tracks 2008–2022; release ~3.4 GB; V3.1 | Substitui DR1; **não combinar seus eventos com outros releases IceCube**. Requer IRF, exposição, backgrounds, trials e calibração para qualquer p-value |
| [KM3NeT / Nature 2025](https://doi.org/10.1038/s41586-024-08543-1) | Evento KM3-230213A de fev. 2023; energia de neutrino parental mediana 220 PeV | Sob espectro assumido E^-2, intervalo 68% **110–790 PeV**; 220 PeV não é energia exata nem prova de física além do padrão |
| [Planck 2018 VI](https://doi.org/10.1051/0004-6361/201833910) | N_eff = 2.99 ± 0.17, Σmν < 0.12 eV (95% CL, Planck+BAO) | Priors/likelihood/modelo importam; neutrino cosmológico ≠ evento PeV |
| [DESI DR2 / atualização julho 2026](https://data.desi.lbl.gov/doc/papers/dr2/) | BAO e análises Lyman-alpha, cosmology chains | Não afirmar possuir espectros/likelihood sem ingestão com hash |
| [DES Year 6](https://doi.org/10.48550/ARXIV.2601.14559) | Σmν < 0.14 eV (95% CL) em combinação especificada CMB+DES Y6+surveys, no contexto ΛCDM | Não apresentar 0.14 versus 0.12 como melhora ou contradição direta; combinações e priors diferem |

A publicação de 2026 de [MNRAS sobre DESI DR2+DES Y6](https://doi.org/10.1093/mnras/stag1607) relata preferência de ajuste para energia escura variável, **sem evidência Bayesiana decisiva**. Não transferir preferência para RLL.

## Prioridade DMAIC por redução de risco

| Prioridade | GAP | Fechamento verificável | Estado atual |
| --- | --- | --- | --- |
| P0 | Mistura incorreta de conjuntos/escala | Registrar releases, domínios, proibição de fusão; gate metadata offline | **FECHADO NO ESCOPO DE METADADOS** |
| P0 | `220 PeV` tratado como medição exata | Registrar mediana condicional, hipótese espectral e intervalo | **FECHADO NO ESCOPO DOCUMENTAL** |
| P0 | Claim cosmológico derivado da notícia | `claim_allowed=false` + ponte microfísica exigida | **BLOQUEADO (corretamente)** |
| P1 | Fonte IceCube apta a inferência | Obter somente arquivos e IRFs necessários sob limites de armazenamento; SHA-256 + licença/versão | `TOKEN_VAZIO_NOT_MATERIALIZED` |
| P1 | Modelos físicos concorrentes | Likelihood de ponto-fonte/fundo usando IRF, trials correction, null ensembles, negative controls | `TOKEN_VAZIO_NOT_RUN` |
| P1 | Cosmologia RLL confrontada com DR2 | Reexecutar ΛCDM, wCDM, CPL e RLL com covariâncias, priors, contagem k, held-out e posterior predictive checks | `TOKEN_VAZIO_NOT_RUN` |
| P2 | Ponte neutrino astrofísico → nova dinâmica RLL | Derivar previsão exclusiva dimensional, unidades, sinal e magnitude pré-registrados; comparar com modelos de fonte padrão | `TOKEN_VAZIO_UNMODELLED` |

## Falsificadores predefinidos

1. O resultado desaparece após convolução pela área efetiva, dispersão angular/energética, background atmosférico e correção por múltiplas buscas.
2. Um modelo de fonte padrão (p-p/p-gamma, cenários de blazar/AGN) explica os dados com qualidade igual ou melhor e menos parâmetros.
3. Um residual cosmológico RLL não melhora predição fora de amostra após custo de complexidade; dados Planck/DES/DESI o excluem.
4. A formulação não mapeia neutrinos PeV para os observáveis de fundo cosmológico com conservação, unidades e inferência causal: **sem bridge, não há claim**.

## Execução segura e recibo

```sh
python3 tools/validate_neutrino_registry.py --self-test
```

Sem bibliotecas externas, sem download, sem edição dos dados do produtor, sem alteração de `main`. O validador aceita somente `METADATA_ONLY` e **não** produz fit físico. A aprovação de metadados deve aparecer como `PASS_SCOPED_METADATA_ONLY`; execução ainda requer receipt versionado, avaliação externa e revisão de licenças. Não mesclar/reivindicar validação científica a partir de um PASS estrutural.

**Rollback:** remover a branch de trabalho ou reverter seus novos arquivos; nenhum arquivo de `main` é sobrescrito.

**R3:** F_ok = fontes identificadas e hipóteses separadas; F_gap = dados brutos/likelihood/replicação/ponte; F_next = reproduzir o benchmark IceTracks-DR2 com materialização seletiva, não baixar 3.4GB no Android.
