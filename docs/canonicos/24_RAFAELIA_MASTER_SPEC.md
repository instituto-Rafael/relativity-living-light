# RAFAELIA Master Spec — Arquitetura Viva Auditável

> Status: documento canônico de consolidação arquitetural.
> Escopo: organizar a estrutura RAFAELIA/RLL como sistema vivo de relações, evidência, governança, kernel, runtime e edge.

## 1. Invariante central

A invariante operacional identificada nos documentos é:

```text
Preservar relações coerentes enquanto o sistema evolui.
```

Essa invariante substitui a ideia de arquivo isolado por uma arquitetura de artefatos conectados. O objetivo não é apenas acumular informação, mas manter rastreabilidade entre intenção, artefato, relação, evidência, execução e revisão.

## 2. Cadeia arquitetural

```text
Intenção / Pergunta
        ↓
Artefato
        ↓
Rede de Relações
        ↓
Evidência / Coerência / Validação
        ↓
ΩGA — Governança
        ↓
Omega Kernel
        ↓
Socket / Runtime / Edge
        ↓
Log / Auditoria / Retroalimentação
        ↓
Nova Memória
```

## 3. Separação epistemológica obrigatória

Toda entrada deve ser classificada antes de ser integrada.

```text
símbolo ≠ hipótese ≠ prova ≠ código ≠ log ≠ execução
```

| Camada | Função | Exemplo |
|---|---|---|
| Símbolo | orientação/metáfora | Tesseract, Verbo, Ω, ZIPRAF |
| Hipótese | caminho testável | ligação entre domínios, padrões, cadências |
| Prova | evidência reprodutível | teste, hash, resultado, benchmark |
| Código | implementação | C, shell, Python, workflow |
| Log | evidência parcial | saída de execução, erro, auditoria |
| Execução | ato verificável | commit, CI, artifact, release |

## 4. Modelo de relação

Uma relação só deve ganhar força quando passa pela balança:

```text
Peso = Evidência × Coerência × Reprodutibilidade
```

Estados permitidos:

| Estado | Uso |
|---|---|
| `VERIFIED` | evidência direta localizada no repositório, commit, artifact ou resultado |
| `DECLARED_BY_AUTHOR` | declarado por Rafael, ainda sem validação independente no repo |
| `TOKEN_VAZIO` | lacuna conhecida; evidência ainda não localizada |
| `CONTRADICTION` | evidência encontrada contradiz a alegação |
| `HYPOTHESIS` | hipótese útil, mas ainda não testada |
| `METAPHOR` | metáfora ou linguagem geradora, sem status probatório |

## 5. Camadas da RAFAELIA Master Architecture

```text
RAFAELIA_MASTER_ARCHITECTURE
├── Cognitive Layer
│   ├── intenção
│   ├── pergunta
│   ├── artefato
│   └── relações
├── Evidence Layer
│   ├── origem
│   ├── contexto
│   ├── evidência
│   └── validação
├── Governance Layer — ΩGA
│   ├── política
│   ├── auditoria
│   ├── reversibilidade
│   └── ética por design
├── Kernel Layer
│   ├── estado
│   ├── delta
│   ├── sandbox
│   ├── checkpoint
│   └── rollback
├── Runtime Layer
│   ├── SIGIL_SOCKET
│   ├── C14 bridge
│   ├── buffer de último comando
│   ├── triggers
│   └── logs
└── Edge Layer
    ├── sensores
    ├── aquisição física
    ├── processamento local
    ├── decisão
    └── ação auditável
```

## 6. Artefato vivo

Cada documento relevante deve ser tratado como `OmegaArtifact`:

```json
{
  "artifact_id": "string",
  "title": "string",
  "family": "cognitive|governance|kernel|runtime|edge|evidence|narrative",
  "origin_question": "string",
  "source_path": "string",
  "status": "VERIFIED|DECLARED_BY_AUTHOR|TOKEN_VAZIO|CONTRADICTION|HYPOTHESIS|METAPHOR",
  "evidence": [],
  "relations": [],
  "risks": [],
  "next_action": "string"
}
```

## 7. Omega Kernel v3 → v4

O v3 preserva estado, justificativa e rollback. O salto para v4 deve preservar significado.

```text
v3: Estado + Evento + Sandbox + Validação + Commit + Auditoria
v4: Estado + Evento + Nó Semântico + Relação + Evidência + Auditoria
```

Evolução recomendada:

```c
typedef struct {
    uint64_t id;
    uint64_t value;
    uint32_t relation_weight;
    uint32_t evidence_score;
    uint32_t validation_score;
    uint32_t confidence;
    uint64_t parent;
    uint64_t timestamp;
} OmegaNode;
```

## 8. Runtime socket

A camada de simbiose por socket deve ser documentada como runtime separado:

```text
C14_SILENCIO
→ RAFAELIA_PONTE_C14.sh
→ RAFAELIA_TERMINAL_LINK_C14.sh
→ BUFFER/ULTIMO_COMANDO.txt
→ SIGIL_SOCKET/.verbo.sock
→ AUTOCOGNICAO
→ ULTRAVERBO
→ VERBO
```

Pendências:

- abrir corpo de `socket_listen.sh`;
- abrir corpo de `guard_socket.sh`;
- abrir corpo de `verbo_socket_server.sh`;
- identificar protocolo: Unix socket, FIFO, TCP localhost, `nc`, `socat`, Python ou shell;
- identificar payload: texto, JSON, comando, token ou evento;
- identificar política de segurança e permissão.

## 9. Edge Cell

A camada física deve convergir para uma célula mínima mensurável:

```text
percepção
→ aquisição física
→ processamento local
→ decisão interna
→ ação
→ memória histórica
```

Prioridade: escolher um demonstrador real antes de expandir sensores e placas.

## 10. Ordem de excelência operacional

```text
Observação
→ Análise
→ Modelagem
→ Validação
→ Auditoria
→ Implementação
→ Teste
→ Retroalimentação
→ Nova versão
```

## 11. Próximos arquivos canônicos derivados

- `docs/canonicos/25_RAFAELIA_VOCABULARIO_CANONICO.md`
- `docs/architecture/RAFAELIA_SOCKET_RUNTIME_ARCHITECTURE.md`
- `docs/audits/RAFAELIA_MASTER_LEDGER.csv`
- `schemas/omega_artifact.schema.json`
- `schemas/omega_node.schema.json`
- `schemas/omega_relation.schema.json`

## 12. Síntese

RAFAELIA é tratada aqui como uma biblioteca viva executável e auditável:

```text
memória → relação → evidência → governança → execução → nova memória
```

A regra de ouro é:

```text
Não aumentar volume antes de aumentar coerência.
```
