# Rota RLL de fragmentos de pesquisa, bibliografia e Pages

Status: implementação manual, claim-gated, em branch de pesquisa com destino a `rll/lab`. Esta rota cria um intake por execução; não há polling agendado.

## 1. Objetivo e fronteira

Costurar metadados bibliográficos, relações candidatas, artefatos canônicos, receipts e uma visualização navegável, preservando:

```text
SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM
```

Título, autor, citação, similaridade de termos ou aresta de grafo não valida uma hipótese RLL. Uma relação candidata aponta à fonte e ao digest que a originaram, guarda uma justificativa humana e continua revisável.

## 2. Estado inicial

O repositório já contém o pacote `ACADEMIC_CORR_001`, o ledger relacional, schemas e validador estrutural. O pacote permanece `RELATIONAL_PENDING` com `claim_allowed: false`.

A rota adiciona um índice bibliográfico curado; intake de um ID arXiv por execução; arestas opcionais quando a pessoa fornece alvos existentes e nota; dados de página com hashes do grafo, pacote e bibliografia; e um build Jekyll entregue como artifact de preview.

A validação estrutural e o hash confirmam formato e custódia. Não confirmam a interpretação do paper nem a relação sugerida.

## 3. Modelo de dados e identidade

| Entidade | Identificador | Regra |
|---|---|---|
| Trabalho | `arxiv:<id>v<n>` ou `doi:<doi>` | Uma versão de preprint e um DOI publicado são referências relacionadas. |
| Pessoa | `orcid:<id>` após verificação | Nome isolado nunca funde duas pessoas. |
| Instituição | `ror:<id>` após verificação | Afiliação textual não comprova identidade institucional. |
| Dataset | DOI ou accession do provedor | Guardar provedor, versão, licença, checksum e locator. |
| Artefato | `gh:<repo>@<commit>:<path>#sha256=<digest>` | Commit, caminho e bytes dão referência reprodutível. |
| Claim | ID estável do registro RLL | Texto e estado ficam no registro científico correspondente. |
| Execução | `ghrun:<repo>/<run_id>` | Guardar ref, commit, workflow, inputs, conclusão e hashes. |

As arestas de intake guardam `from`, `to`, `edge_type`, `source_locator`, `source_sha256`, `relation_note`, `review_state: RELATIONAL_PENDING` e `claim_allowed: false`. Os alvos e a nota vêm de uma pessoa; o código não deduz relações pelo nome, título ou abstract.

## 4. Fluxo de intake

```text
arXiv ID inserido no workflow
→ uma resposta Atom bruta + SHA-256 + instante de coleta
→ metadados normalizados e versão conferida
→ candidato opcional ligado a nós existentes + nota humana
→ testes de endpoints, digest e claim boundary
→ receipt do intake + dados Jekyll
→ preview artifact para revisão
```

Cada execução faz no máximo uma consulta por ID. A rota não varre categorias do arXiv nem cria schedule. O manual oficial da API documenta `id_list` e pede intervalo de três segundos entre chamadas sucessivas; este fluxo faz apenas uma por execução: https://info.arxiv.org/help/api/user-manual.html

O receipt preserva ID pedido e retornado, título, autores como metadados públicos, datas, categorias, DOI, referência de periódico, locator, endpoint, ator, run ID, bytes Atom e digest. A validação rejeita troca de versão ou de ID.

ORCID e ROR não são inferidos. Esses nós entram apenas após resolver um identificador oficial e registrar a fonte.

## 5. Perfis e orçamento do pipeline

O catálogo v3 separa inventário exaustivo e execução: `workflow_inventory.patterns` serve somente para varredura read-only; dispatch depende dos manifestos explícitos em `workflows/tower/` e `workflows/research/`.

| Perfil | Escopo | Soma máxima dos timeouts filhos |
|---|---|---:|
| `quick_session` | sintaxe, contrato, regressão e governança | 120 min |
| `transit_refactor` | controles operacionais da torre | 190 min |
| `real_data_session` | custódia de dados e auditorias de metadados | 185 min |
| `full_session` | torre e dados reais; exclui ciência shadow | 305 min |
| `science_shadow_session` | pipeline determinístico e fronteira de pesquisa | 190 min |
| `literature_session` | pacote acadêmico, intake opcional e preview | 15 min |
| `pages_preview_session` | preview Jekyll do grafo e bibliografia | 15 min |

A execução é sequencial, fail-fast e single-flight. O maior perfil deixa 55 minutos no limite pai de 360 minutos. Os workflows longos de ciência shadow ficam isolados, reduzindo o budget do `full_session` para 305 minutos. O contrato está em `.github/workflow-contract.yml`.

O PR segue a topologia `research/* → rll/lab → rll/integration → rll/release → main`. O gate de maturidade valida a transição; não se promove diretamente ao `main`.

## 6. Preview Jekyll e GitHub Pages

A fonte do preview fica em `pages/rll-research/`. O build gera `_data/research_graph.json` durante o job e mostra referências, hashes, grafo, estado da relação, fronteira epistêmica e receipt.

O workflow usa o build Jekyll oficial e guarda o resultado como artifact. Não pede `pages: write` ou `id-token: write`, não executa deploy e não altera a origem do Pages existente. A configuração de publicação permanece não verificada nesta rota; o preview permite revisar a página antes de integrar ao site publicado.

## 7. Tokens e comunicação

Esta implementação usa o `GITHUB_TOKEN` com as permissões declaradas: dispatch requer `actions: write`; intake e preview usam `contents: read`. Nenhum valor de PAT foi lido ou necessário.

A comunicação entre fragmentos começa como aresta navegável no artifact. Este corte não envia email, Slack ou convite a pesquisadores. Ainda não há mapa verificado `fragmento → responsável/canal`; também não há união automática de pessoas por nome.

## 8. Próximas verificações

1. Conferir os anchors bibliográficos contra os registros oficiais e capturar snapshots/digests numa atualização futura.
2. Revisar uma relação candidata com trecho e contexto da fonte, método, baseline, incerteza e teste de contradição.
3. Resolver ORCID/ROR por APIs oficiais antes de consolidar identidade.
4. Verificar a origem/branch configurada para GitHub Pages antes de propor deploy.
5. Definir mapeamento explícito fragmento → responsável antes de enviar notificações.
6. Definir governança de monitoramento contínuo antes de schedule; por enquanto, o intake é manual e por paper.

## 9. Referências iniciais

- DESI Collaboration, *DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints*, arXiv:2503.14738v3, *Phys. Rev. D* 112, 083515 (2025), DOI 10.1103/tr6y-kpc6. https://arxiv.org/abs/2503.14738v3
- Planck Collaboration, *Planck 2018 results. VI. Cosmological parameters*, arXiv:1807.06209v4, *A&A* 641, A6 (2020), DOI 10.1051/0004-6361/201833910. https://arxiv.org/abs/1807.06209v4

São âncoras bibliográficas para contexto e baseline. A citação não endossa nem valida RLL.

## R3

```text
F_ok   = perfis explícitos com budgets sob o limite do job; intake arXiv manual com hash; arestas pendentes; preview em artifact.
F_gap  = deploy Pages, resolver ORCID/ROR, snapshots curados e canal de notificação ainda não configurados.
F_next = executar uma intake por arXiv ID, revisar o receipt e só então avaliar a relação.
```
