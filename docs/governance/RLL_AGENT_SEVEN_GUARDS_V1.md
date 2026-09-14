# RLL Agent — sete eixos operacionais

Estado inicial: IMPLEMENTED_UNTESTED. claim_allowed=false.

## O que os secrets fazem

Secrets são credenciais guardadas pelo GitHub. Variables são configurações
não sigilosas. Agents e Actions são superfícies separadas. No Copilot cloud
agent, Agents secrets/variables chegam como variáveis de ambiente; o prefixo
COPILOT_MCP_ é reservado ao uso por servidores MCP.

Fonte: [GitHub — Agents secrets and variables](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/configure-secrets-and-variables).

Os nomes abaixo foram informados pelo proprietário em 2026-09-14. A função
GitHub/Climate é uma ligação candidata baseada nos nomes e contratos existentes;
os valores, validade e permissões ainda dependem de observação no runtime.

| Ambiente | Nome | Uso no código |
|---|---|---|
| Agents / organização | PATGITHUB | alias GitHub do agente |
| Agents / organização | CLIMATE | alias Climate do agente |
| Agents / repositório | GIT | TOKEN_VAZIO_ROLE; sem seleção automática |
| Actions / repositório | GITPAT | assurance manual de autenticação/leitura |
| Actions / repositório | CLIMA | Climate nos jobs manuais existentes |
| Actions / token da plataforma | GITHUB_TOKEN | proveniência GitHub da calibração |

Selecionar um alias não comprova equivalência entre os valores de secrets
diferentes. O conector GitHub usado para preparar o PR tem credencial própria.

## Sete eixos em um recibo

| Eixo | Registro verificável |
|---|---|
| Proveniência | repositório, commit local e SHA-256 das fontes utilizadas |
| Contexto | runtime solicitado, objetivo e fronteira da verificação |
| Evidência | presença booleana dos bindings e resultado do contrato da matriz |
| Contradição | diferença entre o nome histórico e o atual; falhas de resolução |
| Incerteza | autenticação, permissões, função de GIT e gates científicos pendentes |
| Reprodução | comando, versão Python, fontes e escopo do resultado |
| Rollback | commit anterior, instrução de reversão e executed=false |

A matriz científica existente permanece a fonte:
data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json.
O novo executor verifica o contrato e registra uma projeção operacional;
ele não fecha lacunas científicas.

## Executar

A partir da raiz do repositório, sem acesso de rede:

```sh
python -m tools.agent.rll_agent_seven_guards --runtime offline
```

Dentro do Copilot cloud agent, exigindo os bindings:

```sh
python -m tools.agent.rll_agent_seven_guards --runtime agents --require-bindings
```

Se houver vários aliases, definir somente o nome da variável desejada:

```sh
export RLL_AGENT_GITHUB_PAT_ENV=PATGITHUB
export RLL_AGENT_CLIMATE_KEY_ENV=CLIMATE
```

Esses seletores são configurações não sigilosas. Os valores das credenciais
continuam no ambiente do agente; não devem ser inseridos nos comandos.

Cada execução cria um novo JSON em artifacts/rll-agent-authority/.
A opção --output aceita um destino novo; um arquivo existente é recusado.
O campo payload_sha256 cobre o JSON ordenado, UTF-8, indentação de 2 espaços,
com newline final, antes de acrescentar esse próprio campo.

O copilot-setup-steps existente executa os testes focados e gera o recibo.
Quando esse workflow roda como Actions comum, ausência dos secrets Agents
é uma lacuna esperada. runtime_requested não é atestado de identidade do runtime.

## Resultado e limites

- structural_status=PASS: arquivos/contrato do preflight válidos.
- BINDINGS_PRESENT_AUTH_UNVERIFIED: valores presentes no processo, autenticação não testada.
- BLOCKED_BINDING: ausência ou resolução ambígua.
- --require-bindings retorna 3 quando os bindings não estão prontos.
- Falha estrutural retorna 1; destino de recibo já existente retorna 2.
- claim_allowed permanece false em todos esses estados.

Autenticação usa os probes já existentes. Ações Climate com rede continuam
manuais, com dataset/parâmetros declarados. Nenhuma chamada externa é feita
pelo executor dos sete eixos.

O filtro de comandos do agente rejeita refspecs de exclusão/force, opções
de mirror/prune, destinos diferentes da branch de trabalho e formas de gh api
que implicam escrita ou sobrescrevem host/autorização. Ele é uma restrição
dos comandos que passam pelo helper, não uma redução das permissões intrínsecas
do PAT nem um sandbox do sistema operacional.

## Verificar e reverter

```sh
python -m unittest -v tests.test_rll_agent_authority tests.test_rll_agent_seven_guards tests.test_rll_dual_api_real_climate_calibration tests.test_rll_credential_authority tests.test_rll_climate_engine_live_probe
python tools/validate_rll_credential_authority.py --strict
```

Os testes de credenciais usam valores sintéticos e mocks; não são evidência
de execução autenticada. A validação de workflows usa a dependência PyYAML
já declarada pelo repositório.

Âncora anterior: 2a6e80ad0efa182217aa76c55665a4c98a4e5523.
Reverter o commit deste PR em uma branch work/ e encaminhar a rll/lab.
Preservar receipts anteriores; registrar correções como novos eventos.
Rollback não foi executado.
