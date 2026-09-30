# RLL — fechamento do replay físico Termux V1

## Estado

```text
queue_item = RLL-P0-TERMUX-PHYSICAL-REPLAY
claim_allowed = false
physical_execution_observed = false
implementation_ready = true
```

Este contrato fecha a lacuna de engenharia do replay físico sem fingir que o aparelho já executou. A promoção para classe `E` ocorre somente quando a cápsula retornada passa pelo validador e contém identidade Android, commit, hashes dos dois ZIPs canônicos, duas saídas byte-idênticas, log bruto e checksums.

## Invariante

```text
script pronto != execução física
CI x86_64 != Android/Termux
receipt sem hashes != evidência
replay histórico != nova execução Pantheon
```

## Entradas canônicas

```text
Pantheon ZIP SHA-256:
c7b192cfa624dde19d5628781e120ba60d8628c792f3d7037e43c1092094f7e6

Bayes ZIP SHA-256:
6f5e11105d8cdd23586bd9b36238f705bf198f01f8dd662b34ea51cd29127078
```

Arquivos com hashes diferentes são bloqueados antes da reconciliação.

## Execução no aparelho

Na raiz clonada do repositório, usando o commit desejado:

```sh
chmod +x scripts/termux/rll_evidence_replay_v1.sh
scripts/termux/rll_evidence_replay_v1.sh \
  /caminho/rll-pantheon-31066012098.zip \
  /caminho/rll-bayes-bic-31066012098.zip
```

Saída padrão:

```text
artifacts/termux/rll-evidence-replay-v1/
├── TERMUX_RECEIPT.json
├── replay-1.json
├── replay-2.json
├── RUN.log
└── CHECKSUMS.sha256
```

## Validação

O próprio script executa:

```sh
python tools/validate_rll_termux_physical_replay.py \
  artifacts/termux/rll-evidence-replay-v1
```

O validador bloqueia:

- ausência de identificação Android ou modelo do aparelho;
- commit Git ausente ou inválido;
- hash de entrada diferente do canônico;
- replays não idênticos;
- adulteração de qualquer arquivo listado;
- `claim_allowed=true`;
- promoção incompatível com a fila histórica;
- receipt que tente saltar o próximo gate.

## Promoção permitida

Somente após validação física:

```text
P / TOKEN_VAZIO_PHYSICAL_EXECUTION
→
E / PASS_PHYSICAL_TERMUX_REPLAY
```

O receipt é compatível com `tools/rll_execution_queue_effective.py` e libera:

```text
RLL-P0-PANTHEON-SUCCESSOR-RUN
```

## O que não é promovido

Mesmo com replay físico válido, permanecem abertos:

- nova run Pantheon pela rota corrigida;
- Pantheon full covariance;
- nested sampling e `logZ` real;
- revisão científica independente;
- qualquer claim cosmológico.

## R₃

- **F_ok:** execução física ganhou contrato, identidade, hashes, repetição e validador.
- **F_gap:** a cápsula real ainda precisa retornar de um aparelho Android/Termux.
- **F_next:** executar no aparelho, preservar a pasta integral e aplicar o receipt à fila efetiva.
