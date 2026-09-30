# EVOLUTION ROADMAP — RLL JSON Evolution Watcher

**Última atualização:** 2026-07-03  
**Princípio:** cada fase é autônoma, plug-n-play e entrega valor imediato —  
não precisa da fase seguinte para funcionar.

## Status de implementação (2026-07-03)

| Fase | Status | Nota |
|---|---|---|
| Fase 0 — Bootstrap | **Implementada** | `tools/bootstrap_failsafe.py`; ver `docs/audits/EVOLUTION_WATCHER_IMPLEMENTATION_NOTE.md`. |
| Fase 1 — Watcher | **Implementada** (local-first, sem rede) | `tools/rll_json_watcher.py`. Nunca baixa nem sobrescreve dado real commitado; o arquivo git é sempre a fonte de verdade. |
| Fase 2 — CI/CD | **Não promovida de propósito** | `to_Add/data_evolution_watch.yml` usa `permissions: contents: write` + auto-commit (`git-auto-commit-action`), o que viola a política `audit_real_workflow_policy` adicionada em `tools/audit_github_workflows.py` (workflows "real data" devem ter `permissions.contents: read`, sem push automático). Precisa de redesenho como job read-only + upload-artifact antes de ir para `.github/workflows/`. |
| Fase 3 — Documentação de auditoria | **Parcial** | `tools/generate_yml_audit_docs.py` já existe mas audita todo o repositório (não é específico à trilha); não implementa os comandos `--config/--trail/--output docs/audit/` descritos abaixo — essa seção do roadmap é aspiracional. |
| Fase 4 — Promoção de órfãos | **Não implementada** | Fora de escopo desta rodada; `tools/promote_orphan.py` não existe ainda. |

Fontes reais registradas em `RLL_JSON_EVOLUTION_WATCHER.yml`: `hz_cosmic_chronometers`, `desi_dr2_bao`, `pantheon_plus_shoes`, `planck_2018_cmb`, `fsigma8_growth`.

---

## Mapa de dependências entre arquivos

```
RLL_JSON_EVOLUTION_WATCHER.yml          ← configuração central
    │
    ├─ tools/bootstrap_failsafe.py       ← Fase 0: inicialização única
    │       └─ cria: data/failsafe/, schemas/fingerprints/,
    │                artifacts/, results/manifest.json
    │
    ├─ tools/rll_json_watcher.py         ← Fase 1: execução principal
    │       ├─ lê: sources[*]
    │       ├─ chama: scripts/test_optimizer_scaling.py  (gate)
    │       ├─ grava: artifacts/EVOLUTION_TRAIL.jsonl
    │       └─ grava: results/manifest.json
    │
    ├─ .github/workflows/data_evolution_watch.yml  ← Fase 2: CI/CD
    │       ├─ mode=bootstrap  → bootstrap_failsafe.py
    │       ├─ mode=run        → rll_json_watcher.py
    │       ├─ mode=rollback   → rll_json_watcher.py --rollback
    │       └─ mode=audit      → generate_yml_audit_docs.py
    │
    ├─ tools/generate_yml_audit_docs.py  ← Fase 3: documentação
    │       ├─ lê: EVOLUTION_TRAIL.jsonl
    │       └─ gera: docs/audit/{EPISTEMIC_AUDIT, ORPHAN_REGISTRY,
    │                             SCHEMA_DRIFT_LOG, CONTRADICTION_LOG}.md
    │
    ├─ tools/promote_orphan.py           ← Fase 4: promoção de órfãos
    │       ├─ lê:  EVOLUTION_TRAIL.jsonl + manifest.json
    │       ├─ move: orphan → docs/canonicos/NN_nome.md
    │       └─ emite: ORPHAN_PROMOTED na trilha
    │
    └─ schemas/evolution_event.schema.json  ← validação formal da trilha
```

---

## Fase 0 — Bootstrap (uma vez)

**O que faz:** cria toda a estrutura de diretórios e snapshots iniciais.

```bash
pip install -r requirements.txt
python tools/bootstrap_failsafe.py --config RLL_JSON_EVOLUTION_WATCHER.yml
```

**Saída esperada:**
```
data/failsafe/desi_dr2_bao_FROZEN.json        ← snapshot congelado
data/failsafe/pantheon_plus_FROZEN.json
data/failsafe/planck_2018_FROZEN.json
data/failsafe/zenodo_doi_rll_FROZEN.json      (= data/zenodo.json existente)
schemas/fingerprints/desi_dr2_bao.sha256      ← DNA do schema inicial
schemas/fingerprints/pantheon_plus.sha256
artifacts/EVOLUTION_TRAIL.jsonl               ← iniciado com eventos BOOTSTRAP
results/manifest.json                         ← iniciado com estados iniciais
```

**Estado epistêmico inicial de cada fonte:**

| Fonte | Estado inicial | Razão |
|---|---|---|
| `desi_dr2_bao` | TOKEN_VAZIO → VERIFIED | confirmado no fetch se chaves presentes |
| `pantheon_plus_shoes` | TOKEN_VAZIO | depende do gate `optimizer_scaling_guard` passar |
| `planck_2018_cmb` | VERIFIED | snapshot estático confiável |
| `zenodo_doi_rll` | DECLARED_BY_AUTHOR | janela indiciária confirmada; awaiting full VERIFIED |
| `internal_manifest` | VERIFIED | arquivo local, chaves verificáveis |

---

## Fase 1 — Execução principal (diária ou por push)

```bash
# Todas as fontes
python tools/rll_json_watcher.py --config RLL_JSON_EVOLUTION_WATCHER.yml

# Fonte específica
python tools/rll_json_watcher.py --config ... --source desi_dr2_bao

# Dry-run (sem modificar nenhum arquivo)
python tools/rll_json_watcher.py --config ... --dry-run
```

**Fluxo por fonte:**
```
FETCH (primary)
  ├─ OK → TEST GATES
  │         ├─ PASS → CHECKPOINT → ARTIFACT → TRAIL(FETCH, VERIFIED)
  │         ├─ WARN → continua, registra na trilha
  │         └─ FAIL → depende de on_fail:
  │                    ├─ FAILOVER    → tenta mirror[2] → mirror[3] → FAILSAFE
  │                    └─ CONTRADICTION → ROLLBACK se trigger, emite CONTRADICTION
  └─ FAIL → mirror[2] → mirror[3] → FAILSAFE
                                       └─ snapshot_path (max_age_days)
                                           └─ epistemic rebaixado para TOKEN_VAZIO
```

**Gate crítico — optimizer_scaling_guard:**
```
L-BFGS-B (unscaled)  →  Δχ²(bug)
                               ↓
Differential Evolution →  Δχ²(correto)
                               ↓
|Δχ²(bug) - Δχ²(correto)| > 0.5 → CONTRADICTION (alpha era artefato)
|Δχ²(bug) - Δχ²(correto)| ≤ 0.5 → PASS (resultado do fit confiável)
```

---

## Fase 2 — CI/CD (GitHub Actions)

Após o bootstrap, o workflow `.github/workflows/data_evolution_watch.yml`  
passa a rodar automaticamente:

```
cron 06:00 UTC todo dia
  └─ mode=run → rll_json_watcher.py → upload trail artifact

push em data/** ou schemas/**
  └─ mode=run → detecta drift automático

workflow_dispatch
  ├─ mode=bootstrap  → bootstrap_failsafe.py --force
  ├─ mode=rollback   → rll_json_watcher.py --rollback --source X
  └─ mode=audit      → generate_yml_audit_docs.py
```

**Fluxo de rollback manual via Actions:**
1. Actions → Run workflow → mode=rollback → source_id=pantheon_plus_shoes
2. Actions executa `rll_json_watcher.py --rollback --source pantheon_plus_shoes --checkpoint latest`
3. Snapshot anterior é restaurado em `data/failsafe/`
4. Evento `ROLLBACK` é emitido na trilha
5. Commit automático atualiza o repo

---

## Fase 3 — Documentação de auditoria

```bash
python tools/generate_yml_audit_docs.py \
  --config RLL_JSON_EVOLUTION_WATCHER.yml \
  --trail  artifacts/EVOLUTION_TRAIL.jsonl \
  --output docs/audit/
```

**Documentos gerados:**

| Arquivo | Conteúdo |
|---|---|
| `EPISTEMIC_AUDIT.md` | tabela de todos os estados por fonte |
| `ORPHAN_REGISTRY.md` | documentos latentes/esquecidos com status e condição |
| `SCHEMA_DRIFT_LOG.md` | histórico de drifts de schema (fingerprint antes/depois) |
| `CONTRADICTION_LOG.md` | contradições registradas + rollbacks executados |

---

## Fase 4 — Promoção de artefatos órfãos

**Órfãos registrados no YAML:**

| Arquivo | Status atual | Próxima ação |
|---|---|---|
| `Rafael te.md` | orphan_outside_canonical_track | verificar conteúdo → promover |
| `Rafafinsnce.md` | orphan_outside_canonical_track | verificar conteúdo → promover |
| `temp.md` | orphan_staging | avaliar se conteúdo merece canonização |
| `Rsfael` (sem ext) | **migrated_text_stub** | identificado como `text/plain`; corpo preservado em `docs/legacy/root/raw/Rsfael.txt`; raiz = stub |
| `to_Add/` | staging_directory_pending_promotion | inventariar item por item |

**Protocolo de promoção:**
```bash
# Ver todos os órfãos
python tools/promote_orphan.py --list-orphans

# Promover um arquivo (dry-run primeiro)
python tools/promote_orphan.py \
  --file "Rafael te.md" \
  --epistemic DECLARED_BY_AUTHOR \
  --note "verificado por Rafael em 2026-07" \
  --dry-run

# Executar promoção
python tools/promote_orphan.py \
  --file "Rafael te.md" \
  --epistemic DECLARED_BY_AUTHOR \
  --update-config
```

**O que acontece:**
```
Rafael te.md
  → docs/canonicos/22_Rafael_te.md   (próximo número disponível)
  → EVOLUTION_TRAIL.jsonl += {action: ORPHAN_PROMOTED, epistemic_after: DECLARED_BY_AUTHOR}
  → results/manifest.json atualizado
  → RLL_JSON_EVOLUTION_WATCHER.yml: removido de registered_orphan_artifacts
```

---

## Fase 5 — Adicionar nova fonte (plug-n-play)

Para qualquer novo dataset (ex: DESI DR3, JWST Early Release Science):

1. Copiar bloco `_template_nova_fonte` do YAML
2. Preencher: id, label, url, tests mínimos
3. Rodar bootstrap para essa fonte:
   ```bash
   python tools/bootstrap_failsafe.py --config ... --source NOME_NOVO --force
   ```
4. A próxima execução do watcher já inclui a fonte automaticamente.

**Nenhuma edição nas seções globais do YAML é necessária.**

---

## Evolução epistêmica esperada ao longo do tempo

```
TOKEN_VAZIO ──(fetch OK + gates pass)──► DECLARED_BY_AUTHOR
                                                │
                              (independente confirma)
                                                │
                                                ▼
                                           VERIFIED
                                                │
                            (evidência contrária encontrada)
                                                │
                                                ▼
                                        CONTRADICTION
                                                │
                              (rollback + novo método)
                                                │
                                                ▼
                                        TOKEN_VAZIO   (ciclo recomeça)
```

---

## Conexão com os textos do projeto

| Texto | Conceito central | Mapeamento no sistema |
|---|---|---|
| *O Lobo que Só Atravessa no Silêncio* | detecção imperfeita | gate `optimizer_scaling_guard`: o barulho da checagem (L-BFGS-B mal escalado) espantava o resultado real |
| *Barrabás, o Beijo e o Galo* | dois tipos de falha (Judas vs Pedro) | CONTRADICTION (fraude de dados / método) vs TOKEN_VAZIO (ausência honesta de evidência) |
| Quatro estados epistêmicos | recusa do par binário verdadeiro/falso | VERIFIED / DECLARED_BY_AUTHOR / TOKEN_VAZIO / CONTRADICTION — quatro, não dois |
| Fadiga metálica (Comet) | acúmulo invisível | schema drift: cada fingerprint diferente é um ciclo de pressurização — só visível pela trilha acumulada |


### Wave 2A — 2026-09-29

A promoção de órfãos deixou de significar necessariamente `docs/canonicos/`: itens sem autoridade científica suficiente podem ser movidos para `docs/legacy/root/<classe>/`, preservando o corpo original e um stub de compatibilidade. `Rsfael` foi identificado como texto bruto e migrado para `.txt`; isso resolve o **tipo do arquivo**, não promove seu conteúdo epistemicamente.
