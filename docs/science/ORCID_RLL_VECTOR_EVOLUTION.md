# ORCID ↔ RLL — Banco Vetorial de Evolução Científica

> **Estado:** implementação inicial auditável  
> **Claim global:** `claim_allowed=false`  
> **ORCID real:** `TOKEN_VAZIO_ORCID_ID`  
> **Princípio:** identidade bibliográfica ≠ validade científica

## 1. Objetivo

Este núcleo integra o registro público ORCID ao RLL para:

1. importar trabalhos e identificadores públicos;
2. confrontar metadados por DOI em DataCite, Crossref e OpenAlex;
3. classificar artefatos em matemática, física, física clássica, física quântica, química, biologia e fisiologia;
4. gerar vetores determinísticos de 32 dimensões para recuperação temática local;
5. preservar cada mudança como nova revisão, sem sobrescrever a anterior;
6. emitir relatórios e candidatos de atualização ORCID sem promover automaticamente autoria, prioridade ou conclusão científica.

A infraestrutura pode confirmar que fontes bibliográficas concordam sobre título, DOI, ano e ORCID. Ela **não** confirma, por esse fato, que uma equação, hipótese ou resultado físico seja verdadeiro.

## 2. Fronteira de identidade

O arquivo `data/CITATION.cff` continha o valor sintaticamente inválido `0000-0002-XXXX-YYYY`. Ele é removido nesta entrega. Nenhum ORCID real é inventado.

Até existir um iD autenticado e confirmado pelo titular:

```text
canonical_orcid = TOKEN_VAZIO_ORCID_ID
```

O comando de sincronização exige um ORCID que passe no checksum ISO 7064 MOD 11-2. Credenciais permanecem apenas no ambiente e nunca no banco ou repositório.

## 3. Arquitetura

```text
ORCID Public API ─┐
DataCite DOI API ─┤
Crossref DOI API ─┼─ ingestão normalizada ─ revisões append-only ─┐
OpenAlex API ─────┘                                                ├─ SQLite
                                                                    │  ├─ artifacts
                                                                    │  ├─ sources
texto título+resumo ─ hash embedding 32D ───────────────────────────┤  ├─ vectors
                                                                    │  └─ events SHA-256
consulta temática + filtros disciplinares ─────────────────────────┘
```

### 3.1 Camadas de evidência

| Camada | O que valida | O que não valida |
|---|---|---|
| ORCID | associação pública declarada de pessoa ↔ trabalho | conteúdo científico |
| DataCite | metadados de DOI para Zenodo e outros objetos de pesquisa | correção científica do artefato |
| Crossref | metadados registrados para publicações | correção do paper |
| OpenAlex | grafo bibliográfico e conceitos | autoria jurídica definitiva ou prova física |
| NCBI/PubMed, futuro adaptador | referência biomédica e identificadores | eficácia clínica ou diagnóstico |
| RLL claim gates | obrigações, falsificadores e recibos | nada sem execução e evidência suficientes |

## 4. Banco vetorial crescente

O backend inicial é SQLite, sem serviço externo obrigatório. Cada artefato possui:

- `logical_id` estável, preferencialmente `doi:<doi>`;
- revisão monotônica;
- elo para a revisão anterior;
- fontes com SHA-256 do payload;
- vetor `rll-hash32-v1` normalizado;
- classificação multidisciplinar;
- estado de validação de metadados;
- `claim_allowed=0`, reforçado por `CHECK` no banco;
- evento encadeado por hash.

Quando uma fonte acrescenta ou corrige informação, uma nova revisão é criada. Conteúdo idêntico é idempotente e não produz duplicata.

## 5. Estados

```text
ORCID_INGESTED
  ↓ concordância parcial
PARTIAL_METADATA
  ↓ concordância forte de DOI/título/ano/autor
VERIFIED_METADATA
```

Conflitos explícitos produzem `METADATA_CONFLICT`; registros marcados como retratados produzem `FLAGGED_RETRACTION`. Ausência de evidência suficiente produz `TOKEN_VAZIO`.

Nenhum desses estados altera `claim_allowed=false`.

## 6. Comandos

```bash
# preparar banco
rll-orcid --db artifacts/orcid_rll/orcid_rll.sqlite3 init

# teste offline com fixture explicitamente sintética
rll-orcid --db /tmp/rll-orcid.sqlite3 ingest-file \
  data/examples/orcid_record_synthetic.json \
  --orcid 0000-0000-0000-001X

# sincronização pública real: token e iD entram apenas em runtime
export ORCID_ACCESS_TOKEN='TOKEN_READ_PUBLIC'
rll-orcid sync --orcid 'ORCID_REAL_VALIDADO' --enrich

# pesquisa vetorial local
rll-orcid search 'geometria quântica e fisiologia' \
  --discipline physics.quantum \
  --discipline physiology

# auditoria
rll-orcid status
rll-orcid verify-chain
rll-orcid report --output artifacts/orcid_rll/ORCID_RLL_VECTOR_REPORT.md

# candidatos revisáveis; não escreve no ORCID
rll-orcid export-orcid \
  --output artifacts/orcid_rll/orcid_work_candidates.json
```

## 7. Escrita no ORCID

A sincronização implementada é de leitura. A exportação marca cada item como:

```text
TOKEN_VAZIO_MEMBER_API_OR_MANUAL_REVIEW
```

A atualização efetiva deve ocorrer por uma destas vias:

1. revisão e inclusão manual pelo titular no ORCID; ou
2. Member API com autorização OAuth e escopo de atualização apropriado.

Não se grava automaticamente para evitar associação autoral incorreta, vazamento de credenciais e promoção de artefatos ainda não revisados.

## 8. Disciplinas e expansão

A taxonomia inicial é hierárquica:

```text
mathematics
physics
├── physics.classical
└── physics.quantum
chemistry
biology
└── physiology
```

A classificação lexical é uma primeira camada reproduzível, não uma ontologia final. Versões futuras podem preservar lado a lado:

- `rll-hash32-v1` para determinismo e execução local;
- embeddings científicos externos, com nome, versão, licença e hash do modelo;
- vocabulários MeSH para biologia/fisiologia;
- conceitos OpenAlex;
- Mathematics Subject Classification e PACS/PhySH, quando juridicamente e tecnicamente apropriados.

Mudança de modelo gera novo registro vetorial; nunca substitui silenciosamente o vetor anterior.

## 9. Critérios de promoção de um artefato científico

Um artefato somente pode sair da zona de hipótese após registrar, conforme sua natureza:

- formulação dimensionalmente consistente;
- hipótese e contra-hipótese;
- dado bruto e proveniência;
- falsificador quantitativo;
- ambiente e comandos reproduzíveis;
- resíduos, incertezas e diagnósticos;
- comparação adversarial;
- reprodução independente;
- hashes dos artefatos produzidos.

Até lá:

```json
{"claim_allowed": false, "state": "TOKEN_VAZIO_PER_ARTIFACT"}
```

## 10. Segurança e privacidade

- somente metadados públicos entram por padrão;
- tokens OAuth e chaves de API não são persistidos;
- o banco gerado fica em `artifacts/orcid_rll/` e não deve ser commitado;
- payloads recebem SHA-256 para auditoria;
- não se infere identidade por nome aproximado;
- ORCID só é aceito após checksum e confirmação do titular;
- informações biomédicas pessoais não fazem parte desta ingestão.

## 11. Próximos gates verificáveis

1. resolver `TOKEN_VAZIO_ORCID_ID` com o iD real autenticado;
2. obter credencial pública ORCID de leitura;
3. executar sync real e armazenar o relatório, nunca o token;
4. revisar conflitos DOI/título/ano/autoria;
5. integrar NCBI E-utilities para corpus biomédico público;
6. conectar os artefatos aceitos aos ledgers científicos já existentes no RLL;
7. publicar somente itens que atravessem o gate específico de evidência.

## Retroalimentação

- **F_ok:** armazenamento crescente, vetorização, proveniência, busca e gates implementados.
- **F_gap:** ORCID real, credencial pública, sync externo e escrita autorizada permanecem `TOKEN_VAZIO`.
- **F_next:** executar a primeira sincronização real em modo somente leitura e auditar divergências antes de qualquer atualização do perfil.
