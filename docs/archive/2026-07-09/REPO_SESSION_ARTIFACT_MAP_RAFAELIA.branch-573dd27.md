<!--
Historical custody snapshot; not current authority.
Source branch: docs/workflow-master-index-rafaelia-20260709
Source head: 573dd27efbc6dec63b332b38bcf81cb2dfe2e88b
Source blob: 1494cb4e65e1831c7464b33c26d6640db85b68eb
Current authority remains workflows/REPO_SESSION_ARTIFACT_MAP_RAFAELIA.md.
claim_allowed=false
-->

# REPO_SESSION_ARTIFACT_MAP_RAFAELIA

> **Estado:** mapa inicial P0  
> **Data:** 2026-07-09  
> **Função:** ligar repositórios, sessões, artefatos, testes e lacunas  
> **Regra:** todo claim forte deve apontar para arquivo, teste, log, PR ou `TOKEN_VAZIO`.

---

## 0. Finalidade

Este arquivo cria a ponte operacional entre o diagnóstico das sessões e a execução real em repositórios.

```text
workflow → sessão → repo → artefato → teste/log → estado epistêmico → próxima ação
```

---

## 1. Matriz principal

| ID | Workflow/sessão | Repo principal | Artefatos conhecidos/esperados | Teste/log necessário | Estado | Próxima ação |
|---|---|---|---|---|---|---|
| `MAP-001` | RAFAELIA simbólica | `instituto-Rafael/relativity-living-light` | glossário, índice mestre, estados epistêmicos | revisão documental | `PARTIAL` | criar glossário canônico |
| `MAP-002` | RLL científico | `instituto-Rafael/relativity-living-light` | scripts de likelihood, MCMC, Bayes, relatórios | CI científico completo | `PARTIAL` | consolidar pipeline com evidência |
| `MAP-003` | Omega Kernel v2/v3 | `instituto-Rafael/relativity-living-light` ou repo de kernel dedicado | código C freestanding, headers, checkpoints | host_sim + determinismo + rollback | `PARTIAL` | criar suíte mínima de testes |
| `MAP-004` | Ω Governance Architecture | `instituto-Rafael/relativity-living-light` | schemas JSON, audit records, validators | schema parse + required fields + epistemic states | `PARTIAL` | ligar validação ao CI |
| `MAP-005` | Termux RAFCODEΦ | `rafaelmeloreisnovo/termux-app-rafacodephi` ou equivalente | bootstrap, pkg bridge, busybox, proot, shell | gates shell/pkg/apt/dpkg/proot/storage | `BLOCKED` | criar diagnóstico JSON |
| `MAP-006` | Vectras VM Android | `rafaelmeloreisnovo/Vectras-VM-Android` | UI, StartVM.env, MainService, ProotCommandBuilder, QEMU | gates shell→vm_boot | `BLOCKED` | criar matriz da cadeia VM |
| `MAP-007` | ChipQuantum geometria | `rafaelmeloreisnovo/ChipQuantum` | docpapers, definições, claims geométricos | revisão formal + scripts experimentais | `TOKEN_VAZIO` | criar definições mínimas |
| `MAP-008` | RafaeliaEngine | repo RAFAELIA/engine a definir | motor Python, FAISS, history.csv, plots | fixture + teste regressivo | `PARTIAL` | travar dataset mínimo |
| `MAP-009` | Middleware Android IA | repo Android/RAFAELIA a definir | MainActivity.kt, RafaeliaEngine.kt, JsBridge.js, frames_seed.json | build + limites éticos documentados | `PARTIAL` | documentar fronteiras |
| `MAP-010` | CompiladorLowFala | repo a definir | ISA, parser, bytecode JSONL | demo Gn 1:1 ou entrada mínima | `DECLARED` | criar spec ISA mínima |
| `MAP-011` | Bare-metal Edge | repo a definir | AVR/Raspberry examples, UART/SPI/ADC/GPIO | build/sim por placa | `PARTIAL` | separar por target |
| `MAP-012` | Drive/corpus/memória | Google Drive/local + repo de índice | dataset ledger, chunks, checksums | sample read + hash + privacidade | `TOKEN_VAZIO` | criar inventário de datasets |
| `MAP-013` | GitHub/agentes/Codex | todos os repos | PRs, issues, checklists, session cards | PR pequeno + template preenchido | `VERIFIED` | aplicar templates em PRs futuros |

---

## 2. Relação com PR #515

O PR #515 introduz o primeiro conjunto documental P0 de navegação:

```text
workflows/WORKFLOW_MASTER_INDEX_RAFAELIA.md
workflows/SESSION_CARD_TEMPLATE_RAFAELIA.md
workflows/TOKEN_VAZIO_LEDGER_RAFAELIA.md
workflows/REPO_SESSION_ARTIFACT_MAP_RAFAELIA.md
```

Este conjunto é documental. Ele não prova execução científica, Android, VM, kernel ou corpus por si só.

Ele cria a régua para que os próximos PRs sejam menores, testáveis e revisáveis.

---

## 3. Gates por repo/camada

### 3.1 RLL científico

```text
data_ok:
model_ok:
priors_ok:
likelihood_ok:
mcmc_ok:
bayes_ok:
figures_ok:
report_ok:
ci_ok:
```

### 3.2 Omega Kernel

```text
compile_host_ok:
freestanding_flags_ok:
no_malloc_ok:
static_memory_ok:
checkpoint_ok:
rollback_ok:
hash_determinism_ok:
audit_record_ok:
```

### 3.3 Termux RAFCODEΦ

```text
shell_ok:
prefix_ok:
busybox_ok:
pkg_ok:
apt_ok:
dpkg_ok:
proot_ok:
storage_ok:
permission_ok:
```

### 3.4 Vectras VM Android

```text
ui_ok:
startvm_env_ok:
service_ok:
terminal_command_ok:
proot_builder_ok:
proot_ok:
qemu_ok:
rootfs_ok:
console_or_vnc_ok:
vm_boot_ok:
```

### 3.5 ChipQuantum geometria

```text
definition_ok:
metaphor_marked_ok:
hypothesis_ok:
experiment_ok:
proof_or_token_vazio_ok:
```

### 3.6 Corpus/memória

```text
inventory_ok:
source_ok:
privacy_ok:
checksum_ok:
chunking_ok:
index_ok:
sample_read_ok:
reproducibility_ok:
```

---

## 4. Política de ligação entre sessão e commit

Cada PR deve apontar para pelo menos um destes:

```text
session card
issue
workflow master index item
TOKEN_VAZIO ledger item
repo-session-artifact map item
```

Exemplo:

```text
Refs: MAP-006, TV-011, TV-012
```

---

## 5. Critério de próximo PR

O próximo PR deve escolher apenas um bloco:

```text
A) TV-006 — testes mínimos Omega Kernel
B) TV-009/TV-010 — gates Termux RAFCODEΦ
C) TV-011/TV-012 — gates Vectras VM Android
D) TV-019 — dataset/corpus inventory
E) TV-013 — definições geométricas mínimas
```

Evitar PR único que misture todos.

---

## 6. Retroalimentação

```text
F_ok   = mapa inicial liga sessões a repos e gates
F_gap  = vários repos ainda estão como 'a definir' neste mapa
F_next = preencher caminhos reais à medida que os PRs forem abertos
```
