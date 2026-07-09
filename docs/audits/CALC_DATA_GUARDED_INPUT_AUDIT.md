# Calc Data Guarded Input Audit

Data: 2026-07-09

## Escopo

Revisão do workflow `Calcular/Processar dados reais — guarded audit` após falha por caminho inexistente:

```text
Input file not found: data/raw/data.json
```

A correção não baixa, não fabrica e não commita dados brutos. Ela apenas aponta o workflow para arquivos JSON/CSV já commitados no repositório.

## Correção principal

O input padrão antigo:

```text
data/raw/data.json
```

foi substituído por caminho local existente:

```text
data/real/Hz_data_real.csv
```

O campo `input_path` agora é uma lista controlada (`type: choice`) com arquivos locais já existentes.

## Allowlist local adicionada

Arquivos aceitos pelo workflow guardado:

```text
data/real/Hz_data_real.csv
data/real/BAO_data_real.csv
data/real/CMB_shift_real.json
data/real/cosmology/fsigma8_growth_real.csv
data/real/cosmology/desi_dr2_bao_primary_points.csv
data/real/cosmology/RLL_ALL_REAL_DATA_MASTER.csv
data/real/cosmology_observational_seed_2026.csv
```

## Itens revisados

| Item | Estado | Ação |
|---|---:|---|
| `.github/workflows/calc-data.yml` | corrigido | `data/raw/data.json` removido; default passa a local existente; allowlist adicionada. |
| `scripts/calc_data.py` | corrigido | leitura CSV/JSON robustecida; manifesto com `input_sha256`; serialização sem `NaN`. |
| `scripts/import_data.py` | corrigido | exemplo antigo `data/raw/data.json` trocado por `_audit/raw/data.json`; cria diretório de saída. |
| `.github/workflows/import-data.yml` | revisado | mantém URL obrigatória; correto para artifact temporário; não deve apontar para arquivo local fixo. |
| `.github/workflows/real-data-complete-execution.yml` | revisado | já usa registro e caminhos reais; não foi alterado. |
| `.github/workflows/rll-validacao-cientifica-completa.yml` | revisado | já verifica `data/real/cosmology/desi_dr2_bao_primary_points.csv`; Pantheon+ permanece condicional/TOKEN_VAZIO quando ausente. |
| `data/real/cosmology/observational_sources_manifest.json` | revisado | mantém `TOKEN_VAZIO` em fontes ainda apenas registradas; fontes locais canônicas já estão listadas na seção `canonical_local_real_sources`. |

## Regra aplicada para brancos / TOKEN_VAZIO

Não preencher lacuna científica/documental com caminho parecido.

Preencher apenas quando todos os pontos forem verdadeiros:

1. o arquivo existe no repositório;
2. o formato é compatível com o script chamado;
3. o caminho não promove mock/synthetic/example como dado real;
4. a mudança não implica validação científica;
5. a fronteira de claim permanece explícita.

## Fronteira de claim

Este ajuste corrige rota operacional e auditabilidade de artefato estatístico.

Ele não valida RLL, matéria escura, energia escura, superioridade cosmológica ou qualquer hipótese científica.

Ω = caminho existente + checksum + artifact guardado + sem promoção indevida.
