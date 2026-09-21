# Reproducibility — Formalismo de Linguagem, Entropia e Metáforas

**Status:** `planned`

## Ambiente mínimo

- Registrar sistema operacional, versão de Python/compilador, dependências e seeds.
- Preferir comandos determinísticos e arquivos versionados.
- Preservar logs em `results/` ou artefatos dedicados antes de promover status.

## Comandos previstos

```bash
# Inventário de fontes até 5 níveis, sem mover conteúdo
find RAFAELIA_COSMO_STRUCTURE_D/paper newadd docs -maxdepth 5 -type f | sort

# Auditoria de status das trilhas PapersPub
find PapersPub -maxdepth 2 -name draft.md -o -name data_manifest.md -o -name reproducibility.md | sort
```

## FAILSAFE

- Não atualizar status para `analysis_run` sem comando, saída, dataset e métrica.
- Não aceitar resultado sem baseline comparável quando a claim envolver superioridade.
- Não apagar artefatos legados durante preparação do paper.

## FAILOVER

- Se dataset real estiver indisponível, marcar como `planned` ou `data_ingested` parcial e não inferir validação real.
- Se pipeline principal falhar, registrar fallback e diferença metodológica antes de usar resultados.

## ROLLBACK

- Para qualquer migração futura, manter origem e destino documentados no `data_manifest.md`.
- Reverter promoção de status se testes, checksums ou métricas não forem reproduzíveis.

## Mitigação de risco científico

Resultados negativos, penalização por complexidade, p-valores desfavoráveis, vieses residuais e lacunas de dados devem aparecer no draft antes de submissão.


## Δ Protocolo de falsificação — semente/manifold multilíngue

**Parent:** `MU-RLL-LANG-MANIFOLD-SEED-20260920`

1. Fixar três línguas/edições e registrar licença, bytes e SHA-256.
2. Definir unidade de alinhamento (verso, sentença ou bloco) antes da análise.
3. Construir baseline independente por língua e um baseline compressor genérico.
4. Construir a representação por semente, contabilizando dicionário, índices, alinhamento, schema, proveniência e decoder.
5. Reconstruir cada versão.
6. Para modo lossless: exigir SHA-256 idêntico por arquivo reconstruído.
7. Para modo semântico: fixar métrica e limiar antes de observar os resultados.
8. Comparar tamanho total, latência, memória, qualidade de reconstrução e falhas.
9. Repetir em corpus de domínio diferente para testar se o efeito depende da organização bíblica.
10. Manter `claim_allowed=false` até execução reproduzível.

**Gate:** reorganização que apenas desloca bytes para um dicionário externo sem contabilizá-lo é FAIL. Redução de `H_ctx` deve ser operacional, relativa ao contexto declarado e separada de entropia termodinâmica.


## Execução SCD1 reproduzível

Script: `benchmark_scd1.py`  
Resultado de referência: `results/SCD1_20260920.json`

```bash
git clone https://github.com/BibleAquifer/WorldEnglishBible /tmp/web
git -C /tmp/web checkout bcb8b3edfb302863c241e3d1d2062cf51042d694

git clone https://github.com/BibleAquifer/ReinaValera1909 /tmp/rv
git -C /tmp/rv checkout 84a071324be17c7c66db17dd204d7804e66d728b

git clone https://github.com/blivre/BibliaLivre /tmp/bl
git -C /tmp/bl checkout a315a15e9f4d01883b62206fe441d57762f126b3

python3 PapersPub/09_language_entropy_formalism/benchmark_scd1.py \
  --eng-root /tmp/web --spa-root /tmp/rv --por-root /tmp/bl
```

Gate esperado: `normalized_json_equal=true` e SHA-256 baseline/reconstrução iguais a `960d1c6601229ff5dee138e21e826724e94ef4952536dcf97db5b46b70e82c8f`.

O benchmark normaliza para texto principal por versículo e não pretende reproduzir notas, marcação editorial ou metadados completos das fontes.
