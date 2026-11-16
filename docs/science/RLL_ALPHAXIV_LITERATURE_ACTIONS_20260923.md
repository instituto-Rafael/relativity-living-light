# RLL — Aplicação científico-bibliográfica alphaXiv — 2026-09-23

**Estado:** `IMPLEMENTED_FAIL_CLOSED`  
**Claim boundary:** `claim_allowed=false`  
**Matriz executável:** `data/science/perturbations/RLL_ALPHAXIV_LITERATURE_ACTION_MATRIX_20260923_V1.json`  
**BibTeX:** `PapersPub/01_cosmology_pantheon_desi/references.bib` e `PapersPub/02_cosmology_growth_structure_d/references.bib`

## Regra de uso

A referência bibliográfica identifica a origem de dados, método, comparação ou falsificador. Ela não converte uma equação externa em equação RLL e não resolve um `TOKEN_VAZIO`.

[
\text{REFERENCE} \neq \text{DERIVATION} \neq \text{EXECUTION} \neq \text{EVIDENCE} \neq \text{CLAIM}.
]

## Mapa paper → atitude aplicada

| Chave | Papel | Evidência bibliográfica usada | Atitude aplicada no RLL |
|---|---|---|---|
| `DESI2025DR2BAO` | `DATA_AUTHORITY` | DESI DR2 Results II, arXiv:2503.14738 | DESI DR2 deve ser ligado ao vetor, ordem, covariância e hashes primários; materialização de dados não implica suporte ao RLL. |
| `Brout2022PantheonPlus` | `DATA_AUTHORITY` | Pantheon+ Analysis, arXiv:2202.04077 | catálogo e covariância STAT+SYS precisam de proveniência; nuisance/calibração e corte em redshift permanecem parte do contrato. |
| `Sharma2026GEDE` | `COMPARATOR` | Sharma et al., arXiv:2607.25539 | GEDE funciona como controle contemporâneo; resultado de background não é promovido a preferência física sem posterior/CMB. |
| `Wang2026DarkSectorDESIDR2` | `COMPARATOR_AND_FALSIFIER_GUIDE` | Wang, Yu & Wu, arXiv:2609.03062 | degenerescência background entre dinâmica de DE e interação exige (P(k)), (f\sigma_8), RSD, lensing e clustering antes de claim de interação/crescimento. |
| `LiZhang2023IDECAMB` | `IMPLEMENTATION_REFERENCE` | Li & Zhang, arXiv:2306.01593 | se a rota B for escolhida, (Q_\mu) deve fechar (Q), (delta Q) e transferência de momento; (Q(a)) isolado é insuficiente. |
| `Pan2025ConsistentICs` | `IMPLEMENTATION_REFERENCE` | Pan et al., arXiv:2506.17411 | C07 exige ICs super-horizonte consistentes com a teoria congelada; copiar ICs GR não é default aceitável. |
| `Lesgourgues2011CLASSCAMB` | `NUMERICAL_PARITY_REFERENCE` | Lesgourgues, arXiv:1104.2934 | CLASS/CAMB devem ser implementações independentes, com inputs equivalentes e sweeps de convergência; ~0,01% em ΛCDM é referência histórica, não tolerância automática do RLL. |

## Aplicação nas equações e gates

### Interação

A literatura IDE formaliza a troca covariante por

[
\nabla_\nu T^{\nu}_{\mu,de}=-\nabla_\nu T^{\nu}_{\mu,c}=Q_\mu,
]

e decompõe a interação em background, perturbação da transferência de energia e transferência de momento [`LiZhang2023IDECAMB`].

**Aplicação RLL:** isto não define (Q_\mu^{RLL}). Define o contrato mínimo que uma futura rota interagente RLL deve satisfazer. Enquanto isso:

[
Q_\mu^{RLL}=\texttt{TOKEN\_VAZIO}
]

na rota que não tenha derivação covariante própria.

### Condições iniciais

ICs de uma teoria estendida precisam ser consistentes com suas próprias equações no regime inicial/super-horizonte [`Pan2025ConsistentICs`].

**Aplicação RLL:** `C07_GAUGE_AND_INITIAL_CONDITIONS` permanece bloqueado até existir uma série inicial derivada da mesma closure que define C01/C02 e que passe restrições/conservação.

### Paridade CLASS/CAMB

A comparação independente CLASS↔CAMB mostra que alta precisão exige a mesma história física, parâmetros compatíveis e estudos explícitos de convergência [`Lesgourgues2011CLASSCAMB`].

**Aplicação RLL:** a sequência obrigatória é:

[
\text{closure congelada}
\rightarrow CLASS_{RLL}
\parallel CAMB_{RLL}
\rightarrow \text{baseline recovery}
\rightarrow \text{convergence sweep}
\rightarrow \epsilon_{RLL}^{\rm prereg}
\rightarrow \text{parity}.
]

A tolerância RLL continua `TOKEN_VAZIO_PREREGISTRATION_REQUIRED`.

### Dados e inferência

DESI DR2 [`DESI2025DR2BAO`] e Pantheon+ [`Brout2022PantheonPlus`] são autoridades de dados. Trabalhos GEDE/IDE recentes [`Sharma2026GEDE`; `Wang2026DarkSectorDESIDR2`] são controles comparativos e de falsificação.

**Aplicação RLL:** G4/G5 de background não podem fechar G6/G8/G9. Em particular:

[
\text{background fit} \not\Rightarrow \text{microphysical identification}.
]

## Workstreams vinculados

- **WS02:** `DESI2025DR2BAO`, `Brout2022PantheonPlus`, `Sharma2026GEDE`.
- **WS03:** `LiZhang2023IDECAMB`, `Pan2025ConsistentICs`, `Wang2026DarkSectorDESIDR2`.
- **WS04/WS05/WS06:** `Lesgourgues2011CLASSCAMB`, `Pan2025ConsistentICs`.
- **WS07:** `Wang2026DarkSectorDESIDR2`.
- **WS10:** `DESI2025DR2BAO`.

## Estado falsificável

[
\boxed{\texttt{claim\_allowed=false}}
]

A bibliografia foi aplicada como autoridade de proveniência e desenho de testes. C01, C02, C07, C08, a closure física, CLASS/CAMB e a tolerância de paridade continuam sujeitos aos gates próprios.

## Referências

As entradas completas e machine-readable estão nos arquivos `references.bib` canônicos. Para uso humano, ver:

- `PapersPub/01_cosmology_pantheon_desi/references.md`
- `PapersPub/02_cosmology_growth_structure_d/references.md`
