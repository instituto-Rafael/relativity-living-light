# Sincronização do Contrato de Workflows

Estado: `ACTIVE_GOVERNANCE`  
Efeito científico: `NONE`  
`claim_allowed=false`

## Invariante

```text
arquivos executáveis → inventário derivado → contrato → validação → receipt → revisão
```

A quantidade de workflows não é mantida por memória humana nem por um número
espalhado em testes. A fonte executável é o conjunto direto de arquivos
`.github/workflows/*.{yml,yaml}`; o contrato registra uma expectativa revisável.

## Modos

### Verificação

```bash
python tools/workflow_contract_sync.py --write-report
```

Retorna código não zero quando a contagem real difere de
`inventory.active_workflows`. Nenhum arquivo é alterado.

### Correção local em branch de revisão

```bash
python tools/workflow_contract_sync.py --write --write-report
```

Somente o escalar `inventory.active_workflows` é alterado. O comando não cria
commit, não faz push e não muda configurações do GitHub.

### Pre-commit versionado

```bash
sh scripts/install_repo_hooks.sh
```

O instalador configura `core.hooksPath=.githooks`. O hook executa a mesma
verificação usada pela CI, evitando duas implementações concorrentes.

### Proposta automática com revisão

O workflow `.github/workflows/workflow-contract-sync.yml` possui modo manual
`propose`. Ele:

1. faz checkout de `rll/lab` sem persistir credenciais;
2. sincroniza o contrato no workspace;
3. cria branch `automation/workflow-contract-sync-<run_id>`;
4. tenta abrir PR para `rll/lab`;
5. publica receipt mesmo quando a permissão externa impede a proposta.

Commit direto em `main` é proibido por desenho. Se a configuração **Allow GitHub
Actions to create and approve pull requests** ou a permissão de escrita estiver
indisponível, o estado é:

```text
TOKEN_VAZIO_EXTERNAL_SETTING
```

## Relação com a topologia de maturidade

```text
feature/automation → rll/lab → rll/integration → rll/release → main
```

Sincronizar a contagem não autoriza promover a arquitetura. Cada aresta continua
exigindo seus próprios checks e receipts.

## HOTFIX correto

Um HOTFIX de contagem tem escopo mínimo:

1. confirmar o arquivo extra;
2. atualizar o contrato por ferramenta determinística;
3. executar testes e arquitetura;
4. abrir PR para a camada adequada;
5. preservar o motivo da divergência no receipt.

A correção imediata resolve o incidente. O sincronizador, o hook e o workflow
resolvem a classe de incidentes.

## Fronteiras

- contrato coerente não comprova branch protection;
- PR criado não comprova revisão humana;
- CI verde não comprova validade científica;
- arquivo versionado não comprova configuração externa;
- `claim_allowed=false` permanece invariável.
