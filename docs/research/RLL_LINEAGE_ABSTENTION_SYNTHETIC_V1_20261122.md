# RLL — Proveniência, informação incompleta e abstenção | Experimento sintético V1

**Estado:** `PASS_SCOPED_SYNTHETIC` para execução local, **NÃO há melhora geral comprovada**, `claim_allowed=false`. Não é resultado de cosmologia nem prova das 400 equações. Nenhum conteúdo literal do catálogo privado Mapa foi importado.

## Pergunta e hipóteses predefinidas

Pode um sistema que separa documentos copiados por identidade de origem e que se abstém perante contradições reduzir respostas erradas frente a baselines ingênuos, preservando dados ausentes como estados tipados?

- **H1:** decisões invariantes quando se adicionam documentos duplicados da mesma origem.
- **H2:** redução de erros absolutos frente à maioria por documento, mas verificar custo de cobertura e risco condicionado.
- **H3:** recusa de conclusão quando duas origens independentes se contradizem.
- **H0:** nenhuma melhoria demonstrada em fontes independentes ou fora dos fixtures sintéticos; ainda não testada com dados reais.

**Método:** 16 cenários criados manualmente × multiplicadores de cópias `{1,2,4,8}` = 64 avaliações **dependentes**, não 64 amostras independentes. Quatro políticas na mesma sequência e verdade artificial controlada: maioria por documento, maioria por origem independente, genealogia+bloqueio de contradição e abstenção total. `Known` pode votar; `Unknown`, `Absent`, `Null` não são convertidos em zero. Identidade de raiz **é fornecida** pelo fixture: descobri-la automaticamente não faz parte deste estudo.

Código exato: [tools/ci/rll_evidence_lineage_abstention_benchmark_v1.py](../../tools/ci/rll_evidence_lineage_abstention_benchmark_v1.py). SHA-256 dos bytes executados: `a2032b95f78fa623028f2a2303590ae97512aaf4ab1cbc6c9649bd171a9e5e28`. Git blob SHA-1: `c0b55cb13b25793241d99b324badebba4e0d3463`. **São identificadores com semânticas distintas.**

## Resultado observado em execução Python local

| Política | Respondidas/64 | Erradas/64 | Risco seletivo entre respostas | Violações do contrato de suporte |
|---|---:|---:|---:|---:|
| Maioria por documento | 44 | 12 | 12/44 = 27,27% | 24 |
| Maioria por origem independente | 40 | 8 | 8/40 = 20,00% | 20 |
| Genealogia + bloqueio de contradição | 20 | 8 | 8/20 = **40,00%** | **0** |
| Sempre se abster | 0 | 0 | **indefinido (zero respostas)** | 0 |

O guard teve **menos erros absolutos** que a maioria por documento (8 vs 12), mas **não melhorou** sobre a maioria deduplicada (8 vs 8), teve apenas metade da cobertura desse baseline (20 vs 40) e **pior risco seletivo** (40% vs 20%). Logo, não afirmar supremacia global ou melhoria de acurácia condicionada. A condição de "zero violações" é dada pela própria regra contratual: **não prova que a resposta seja verdadeira**.

**Por nível de duplicação:** na maioria por documento, erros foram `2,2,4,4` conforme multiplicador `1,2,4,8`; no guard, `2,2,2,2`. São casos artificiais que tornam o mecanismo de cópias observável, não estimativas de frequência no mundo.

**Testes**: 8 métodos `unittest` executados localmente, 8 aprovados, 0 falhas. A saída completa JSON local, 64 decisões por caso em CSV e manifesto de hashes SHA-256 foram construídos como pacote de evidências associado à sessão. O fluxo GitHub CI desse commit não foi declarado aprovado por esta execução local.

## Falsificações essenciais (não omitir)

1. **Duas fontes independentes concordando em falsidade**: o guard também responde errado. Proveniência é necessária para atribuir suporte, mas não basta para a verdade.
2. **Uma fonte copiada oito vezes com raízes falsamente distintas**: o guard passa de abstenção a resposta conhecida. A integridade do mapeamento de fontes é uma dependência crítica.

Ambos os contraexemplos foram efetivamente executados em domínio sintético. O resultado é uma fronteira operacional, não uma conclusão de validade científica geral.

## Antecedentes, rigor e proposta de extensão

- Cousot & Cousot (1977), *Abstract interpretation*, DOI: [10.1145/512950.512973](https://doi.org/10.1145/512950.512973).
- Green, Karvounarakis & Tannen (2007), *Provenance Semirings*, DOI: [10.1145/1265530.1265535](https://doi.org/10.1145/1265530.1265535).
- W3C, [PROV-O (2013)](https://www.w3.org/TR/prov-o/).
- Trabalhos recentes sobre predição seletiva e abstenção exigem avaliar **curvas risco-cobertura**, calibração e benchmarks independentes; o presente protocolo **não executa LLMs**.

Próxima etapa científica: comparar políticas em **cobertura equivalente**, definir identificação de dependência de fontes sob erros, criar conjunto de avaliação externo e cego, registrar controle de variáveis e estimar incerteza por clusters **independentes**. Testar adversários que compartilham uma mentira, inversão temporal e proveniência falsificada. Revisão por terceiros, licença, corpus e privacidade antes de qualquer publicação de dados privados.

## Auditoria e fronteiras

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. Estados: `TESTED_LOCAL_SYNTHETIC=PASS_SCOPED`; `CI_HEAD=TOKEN_VAZIO_UNVERIFIED`; `COSMOLOGY_E2E=NOT_RUN`; `FORMAL_PROOFS_400=NOT_RUN`; `INDEPENDENT_REPLICATION=NOT_RUN`; `NOVELTY_OF_400=NOT_ASSESSED`; `claim_allowed=false`.

Rollback por sucessor no ramo de pesquisa, sem merge, sem alteração de workflows, sem promoção de claims e sem modificar o produtor de cosmologia.

R3 = ⟨F_ok: 8/8 testes e tabela de 4 baselines em 64 fixtures; F_gap: risco seletivo desfavorável, comparação independente e fonte real ausentes; F_next: baseline a cobertura constante + teste de genealogia falsa⟩.
