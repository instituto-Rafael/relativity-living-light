# RLL — RafaelOS 400 | Protocolo profissional de garantia sintética V1

**Estado**: `PASS_SCOPED_LOCAL_SYNTHETIC` exclusivamente para o módulo genérico de álgebra do desconhecido; `claim_allowed=false`. Nenhuma validação das 400 equações, modelo de cosmologia, certificação, propriedade autoral ou revisão por pares foi reivindicada.

## Questão e escopo

Representar dados incompletos sem confundir `Known(0)`, `Unknown`, `Absent`, `Null` e `Invalid`. Verificar se um mapa total e constante pode gerar saída conhecida sob entrada desconhecida, e se o refinamento da informação preserva respostas conhecidas.

**Fronteira de custódia**: este RLL é PÚBLICO, enquanto o catálogo de 400 entradas permanece no Mapa privado. Aqui há somente algoritmo de domínio finito, documentação metodológica e receipt minimizado. Nenhum corpus, fórmula literal privada, dado astronômico, log pessoal ou hash de conteúdo privado foi introduzido. Não alterar o ajuste cosmológico, dados reais, ponteiros, workflows ou branch main.

## Formalismo matemático

Para T=U={0,1}, γ(Known(x))={x} e γ(Unknown)=T. Os demais estados carecem de política explícita e resultam em `BLOCKED_TYPED_POLICY`. Seja f:T→U uma função total. Define-se o levantamento:

\[
\widehat f(a)=\begin{cases}\operatorname{Known}(y),& f[\gamma(a)]=\{y\},\\
\operatorname{Unknown},& |f[\gamma(a)]|>1.
\end{cases}
\]

P1 (somente sob as hipóteses): se \(\widehat f(a)=\operatorname{Known}(y)\) e \(x\in\gamma(a)\), então \(f(x)=y\), pela definição de imagem de conjunto.

P2 (somente sob as hipóteses): se \(\gamma(b)\subseteq\gamma(a)\), então \(f[\gamma(b)]\subseteq f[\gamma(a)]\). A demonstração é a monotonicidade da imagem de conjuntos.

Contraexemplo: f(0)=f(1)=0 produz \(\widehat f(Unknown)=Known(0)\); portanto, propagação incondicional de Unknown é incorreta. A identidade preserva Unknown. **P1/P2 são argumentos matemáticos condicionais, ainda não verificados por um assistente de provas.**

## Testes e artefatos efetivamente produzidos

- Fonte exata: `tools/ci/rll_rafaelos400_typed_unknown_gate_v1.py`
- SHA-256 dos bytes: `04395efc6193912795073342203750d5c4a0414242c3033fcb0052964fffdcf4`
- Identificador Git blob SHA-1: `ec8d3548c6836a1d694c80b37ea804adf1727f18` (não é o mesmo que o SHA-256).
- Execução: contêiner Python local, 2026-11-22T07:17:21.875501Z; **13/13 testes `unittest` passaram**, 0 falhas; sem CI, ARM, dados reais ou observações astronômicas.
- Propriedade sintética de soundness: 4 funções totais binárias × 3 estados de entrada = 12 instâncias percorridas dentro de um método de teste. Refinamento: 4 funções × 2 entradas conhecidas = 8 instâncias. Essas instâncias não são 20 equações independentes.
- Receipt versionado: `receipts/rafaelos400_typed_unknown_local_v1.json`.
- Reprodução em checkout: `python tools/ci/rll_rafaelos400_typed_unknown_gate_v1.py --output /tmp/typed_unknown_receipt.json`.
- Fidelidade literal das 400 ao material original: `NOT_RUN`. Provas por equação: `0/400`. Inferência cosmológica: `NOT_APPLICABLE`. Reexecução externa independente: `NOT_RUN`.

## Qualificação acadêmica

| Eixo separado | Situação |
|---|---|
| Classe do artefato | METHOD_VALIDATOR, não teoria física |
| Tipo epistemológico das 400 | UNCLASSIFIED_TOKEN_VAZIO até revisão individual |
| Provas formais P1/P2 | Dedução condicionada, sem assistente de provas |
| Execução local do validador | PASS_SCOPED_LOCAL_SYNTHETIC, 13/13 |
| Evidência de fenômeno físico | NOT_RUN |
| RLL versus ΛCDM | Nenhum fit executado neste estudo |
| Reprodutibilidade independente | NOT_RUN |
| Originalidade acadêmica das 400 | NOT_ASSESSED |
| Autorização de claim global | false |

Metadados do Mapa privado registram 400 entradas em 30 famílias e 28 alertas de revisão (12 na coleção I, 16 na II). **28/400 não é taxa estimada de erros**, e ausência de flag não significa equação correta. 40 entradas sobre vazio tipado e proveniência foram selecionadas para revisão preliminar, das quais cinco já têm flags; testes genéricos executados não fecham essas flags automaticamente.

## Antecedentes e padrões de pesquisa

- Cousot, P.; Cousot, R. (1977), Abstract Interpretation (POPL): https://doi.org/10.1145/512950.512973
- W3C (2013), PROV-O: https://www.w3.org/TR/prov-o/
- Wilkinson et al. (2016), FAIR Principles, Scientific Data 3:160018: https://doi.org/10.1038/sdata.2016.18
- Sandve et al. (2013), Ten Simple Rules for Reproducible Computational Research: https://doi.org/10.1371/journal.pcbi.1003285

Essas referências são antecedentes da metodologia e não estabelecem, por si, originalidade das formulações.

## Controle e falsificação

G0 fonte literal: TOKEN_VAZIO; G1 metadados indexados: PASS_SCOPED; G2 teste genérico: PASS_SCOPED_LOCAL; G3 repetição independente: NOT_RUN; G4 provas 400: NOT_RUN; G5 revisão sistemática de literatura: NOT_RUN; G6 observações cosmológicas: NOT_APPLICABLE; G7 autorização de promoção: BLOCKED.

Rollback: manter branch separada e adicionar sucessor corretivo se houver falsificação. **Sem merge, deleção de histórico ou habilitação de novos workflows**.

R3 = <F_ok: byte identity + 13 unit tests; F_gap: proof, replication, 400-specific review; F_next: revise first 40 with source, counterexample, independent runtime>.
