# RLL Studio UX V1

**Status:** LAB / claim-bounded  
**Objetivo:** transformar a complexidade do RLL em uma experiência científica fluida, prática, interoperável e auditável sem alterar a autoridade do núcleo científico.

## 1. Princípio central

A interface é uma camada de apresentação e orquestração. Ela **não calcula autoridade científica** e não promove `PASS` por aparência, navegação, conclusão de formulário ou sucesso de renderização.

Fluxo de autoridade:

```text
Scientific Core
  -> execution/result
  -> validator
  -> evidence receipt
  -> experiment manifest
  -> RLL Studio
```

`UI render PASS != scientific PASS`.

## 2. Experiência principal

O usuário percorre cinco atos cognitivos:

1. **Dados** — fonte, versão, hash e disponibilidade.
2. **Modelo** — hipótese, comparador e parâmetros.
3. **Executar** — método, ambiente, commit e receipt.
4. **Comparar** — resultados e baseline sem sobreclaim.
5. **Evidência** — estado, limitação e próximo gate.

A tela inicial responde primeiro a quatro perguntas:

- O que foi executado?
- O que foi observado?
- O que ainda não está comprovado?
- O que posso fazer em seguida?

Detalhes de baixo nível permanecem disponíveis por progressive disclosure.

## 3. Arquitetura de informação

A navegação canônica contém cinco áreas:

- **Início:** estado global, claim gate e resumo acionável.
- **Experimento:** identidade, dataset, modelo, parâmetros e interoperabilidade.
- **Resultados:** narrativa curta, métricas, parâmetros e comparação.
- **Evidências:** matriz filtrável + detalhe de proveniência/limitação/próximo gate.
- **Biblioteca:** modelos, datasets, papers e artefatos vinculados ao contexto atual.

Nenhuma área exige que o usuário conheça a árvore interna do GitHub.

## 4. Estados humanos derivados de estados técnicos

| Estado interno | Linguagem de UX |
|---|---|
| `PASS` | Verificado |
| `FAIL` | Não passou |
| `BLOCKED` | Bloqueado |
| `OBSERVED` | Observado |
| `OBSERVED_LIMITED` | Evidência parcial |
| `TOKEN_VAZIO` | Ainda não comprovado |
| `NOT_MEASURED` | Não executado |
| `UNAVAILABLE` | Indisponível |
| `INVALIDATED` | Invalidado |

A tradução melhora compreensão, mas o estado original permanece no manifest.

## 5. Interoperabilidade

A unidade transportável é `rll-experiment-manifest/1.0.0`, validada por:

`schemas/rll-experiment-manifest.v1.schema.json`

O mesmo contrato deve servir progressivamente a:

```text
RLL Studio <-> JSON <-> CLI <-> Python/Jupyter <-> CI <-> receipts
```

Adapters para CLASS/CAMB, Drive e outros sistemas devem consumir/produzir o contrato sem criar semânticas paralelas.

## 6. Conforto e usabilidade

Baseline V1 implementada:

- layout responsivo para desktop e Android;
- navegação curta e persistente;
- modo claro/escuro local;
- foco visível e navegação por teclado;
- skip link;
- `aria-live` para feedback de importação;
- respeito a `prefers-reduced-motion`;
- linguagem orientada a ação;
- resumo antes dos detalhes;
- filtros de evidência;
- import/export JSON;
- limite de 5 MiB para importação local;
- sem dependências CDN/front-end;
- sem telemetria nesta versão;
- sem mutação do núcleo científico.

## 7. Fail-closed UX

Um novo experimento começa como:

```text
manifest_state=NOT_MEASURED
execution.state=NOT_MEASURED
claim.allowed=false
claim.state=BLOCKED
```

Regras:

1. ausência não vira `PASS`;
2. `TOKEN_VAZIO` é visível e explicável;
3. importação inválida é rejeitada;
4. UI não infere claim a partir de métricas;
5. `claim.allowed=true` exige `claim.state=PASS` no schema;
6. resultados de demonstração não são evidência científica;
7. CI da interface não valida física, cosmologia ou dataset externo.

## 8. Qualidade percebida

O RLL Studio separa três profundidades sem criar três produtos:

- **Leitura rápida:** resumo, estado, ação seguinte.
- **Leitura científica:** parâmetros, comparação, incertezas.
- **Leitura de auditoria:** fonte, commit, receipt, limitação, próximo gate.

A complexidade é preservada, mas deslocada para o nível em que ela é útil.

## 9. Segurança e privacidade

V1 é local-first e não envia manifests para serviço remoto. Dados importados permanecem no contexto do navegador. Conteúdo dinâmico é inserido por `textContent` em vez de HTML arbitrário.

Limites:

- o navegador continua sujeito ao ambiente do usuário;
- exportação gera arquivo local, não receipt científico;
- não há autenticação ou controle multiusuário nesta camada estática.

## 10. Gates de maturidade

### Gate A — contrato estático

- `node --check studio/app.js` PASS;
- schema V1 válido;
- testes `tests/test_rll_studio_contract.py` PASS;
- ausência de CDN externa;
- baseline de acessibilidade presente.

### Gate B — usabilidade humana

`TOKEN_VAZIO` até execução real em desktop e Android:

- completar importação sem instrução externa;
- localizar claim gate;
- explicar por que um eixo está bloqueado;
- encontrar próximo gate;
- exportar manifest;
- registrar erros, tempo de tarefa e pontos de confusão.

### Gate C — interoperabilidade executável

`TOKEN_VAZIO` até adapters reais:

- CLI -> manifest;
- notebook -> manifest;
- CI/receipt -> manifest;
- manifest -> visualização sem perda semântica.

### Gate D — release

Somente após revisão humana, acessibilidade prática, device smoke, compatibilidade de browser e integração com um produtor real de receipts.

## 11. Métricas de UX recomendadas

Para futura medição:

- sucesso de tarefa sem ajuda;
- tempo até primeiro resultado compreendido;
- tempo para localizar limitação crítica;
- taxa de importação válida/inválida;
- erros de interpretação de `PASS`/`BLOCKED`/`TOKEN_VAZIO`;
- número de ações até evidência;
- recuperação após erro;
- satisfação pós-tarefa;
- legibilidade em viewport Android.

Nenhuma dessas métricas deve ser declarada antes de observação real.

## 12. Próxima evolução

Prioridade recomendada:

1. ligar um receipt/resultado real ao manifest V1;
2. criar adapter CLI/Python;
3. executar teste humano em Android;
4. adicionar visualizações científicas somente quando houver dados reais tipados;
5. avaliar PWA/offline installable após o fluxo principal estar estável.

## F_ok / F_gap / F_next

- **F_ok:** shell profissional, arquitetura de informação, manifest V1, fail-closed, responsividade e CI contratual.
- **F_gap:** uso humano físico, adapter científico real e acessibilidade prática ainda não medidos.
- **F_next:** conectar uma execução real RLL -> receipt -> manifest -> Studio e medir a tarefa ponta a ponta.
