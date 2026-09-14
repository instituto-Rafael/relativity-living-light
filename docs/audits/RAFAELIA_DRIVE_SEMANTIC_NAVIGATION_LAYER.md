# RAFAELIA Drive Semantic Navigation Layer

> Status: camada de navegação criada no Google Drive para reduzir esforço semântico de levantamento, leitura e correlação.

## Pasta raiz criada no Drive

- Nome: `RAFAELIA__Ω_NAVIGACAO_SEMANTICA__ψχρΔΣΩ__INDEX_RELACOES`
- URL: https://drive.google.com/drive/folders/1tncw3RYsQtLbV9Jz65NB4qyNoFrJrMY6

## Subpastas criadas

| Pasta | Função semântica |
|---|---|
| `00_MAPA_RAIZ` | entrada da navegação e trilhas de leitura |
| `01_ARTEFATOS` | documentos como unidades vivas de conhecimento |
| `02_EDGES` | relações, correlações, arestas, pesos e lacunas |
| `03_GOVERNANCA` | evidência, validação, auditoria, reversibilidade e estados epistêmicos |
| `04_KERNEL_RUNTIME_EDGE` | Omega Kernel, SIGIL_SOCKET, C14, runtime, edge e hardware |
| `05_LEDGER` | ledger mestre de famílias, status, risco e próxima ação |

## Princípio de nomeação

A estrutura usa nomes curtos, resistentes ao conector, mas semanticamente informativos. A intenção é que o nome do diretório já funcione como metadado navegável.

```text
prefixo numérico → ordem de leitura
nome curto → eixo semântico
subconteúdo → relação ou função
```

## Invariante

```text
Preservar relações coerentes enquanto o sistema evolui.
```

## Ciclo de navegação

```text
Intenção
→ Observação
→ Artefato
→ Relação
→ Evidência
→ Governança
→ Execução
→ Auditoria
→ Nova Memória
```

## Regra epistemológica

```text
símbolo ≠ hipótese ≠ prova ≠ código ≠ log ≠ execução
```

## Estados usados

| Estado | Uso |
|---|---|
| `VERIFIED` | evidência direta localizada |
| `DECLARED_BY_AUTHOR` | declarado, ainda sem validação independente |
| `TOKEN_VAZIO` | lacuna explícita |
| `CONTRADICTION` | evidência conflitante |
| `HYPOTHESIS` | hipótese útil a testar |
| `METAPHOR` | metáfora geradora, sem status probatório |

## Filtro de relação

```text
Peso = Evidência × Coerência × Reprodutibilidade
```

## Estrutura conceitual esperada

```text
RAFAELIA__Ω_NAVIGACAO_SEMANTICA__ψχρΔΣΩ__INDEX_RELACOES/
├── 00_MAPA_RAIZ/
├── 01_ARTEFATOS/
├── 02_EDGES/
├── 03_GOVERNANCA/
├── 04_KERNEL_RUNTIME_EDGE/
└── 05_LEDGER/
```

## Conteúdo planejado para os índices

### 00_MAPA_RAIZ

- README de navegação
- mapa de rotas
- ordem de leitura
- glossário mínimo

### 01_ARTEFATOS

- Arquitetura Cognitiva Evolutiva
- Integração de Conhecimento
- Integração de Conhecimento Vivo
- Parábolas e Estruturas Narrativas

### 02_EDGES

- relações fortes
- relações fracas
- lacunas TOKEN_VAZIO
- pesos de evidência/coerência/reprodutibilidade

### 03_GOVERNANCA

- ΩGA
- estados epistêmicos
- auditoria
- reversibilidade
- ética por design

### 04_KERNEL_RUNTIME_EDGE

- Omega Kernel v3/v4
- SIGIL_SOCKET
- C14 bridge
- BUFFER/ULTIMO_COMANDO
- AUTOCOGNICAO
- ULTRAVERBO
- Edge Cell

### 05_LEDGER

- ledger mestre
- família
- item
- função
- status
- risco
- próxima ação

## Observação operacional

A criação de pastas no Drive funcionou. A criação de Google Docs/Sheets nativos foi bloqueada pelo conector nesta sessão; por isso esta documentação foi salva no GitHub como espelho auditável da camada Drive.

## Próxima ação

Quando a permissão de criação/edição de Docs/Sheets no Drive estiver disponível, materializar dentro da pasta raiz:

1. `README_NAVIGACAO_RAFAELIA` como Google Doc;
2. `MAPA_RELACOES_RAFAELIA` como Google Doc;
3. `LEDGER_MESTRE_RAFAELIA` como Google Sheets;
4. `TOKEN_VAZIO_INDEX` como Google Sheets;
5. `EDGE_MAP_SIGIL_SOCKET_C14` como documento técnico.
