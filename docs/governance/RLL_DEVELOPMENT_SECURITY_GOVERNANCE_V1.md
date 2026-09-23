# RLL — Governança de Desenvolvimento, Segurança e Privacidade V1

**Estado:** ACTIVE_GOVERNED_DRAFT  
**Modo:** desenvolvimento de software; não treinamento de modelo  
**Agente autônomo:** proibido nesta fronteira  
**Claim científico:** `claim_allowed=false`

## 1. Princípio

O RLL pode evoluir como programa. O programa não recebe autoridade ilimitada.

```text
humano define objetivo
        ↓
operação declarada
        ↓
policy gate deny-by-default
        ↓
programa determinístico
        ↓
artefato/evidência
        ↓
receipt
        ↓
humano/review decide próximo escopo
```

Nenhum componente desta fronteira pode se autoautorizar, criar objetivo novo ou ampliar escopo sozinho.

## 2. Autoridade

São reconhecidos três papéis operacionais:

- **human_operator** — inicia comando local ou aprova nova mudança;
- **reviewed_ci_workflow** — executa código previamente versionado/revisado;
- **deterministic_program** — executa somente o contrato recebido.

`autonomous_agent` não é uma autoridade válida desta rota.

O modo de autoridade é registrado no preflight, mas **não constitui prova de identidade pessoal**.

## 3. Capabilities

Regra: tudo começa bloqueado.

Capacidades permitidas precisam ser explicitamente enumeradas. A rota Rx atual permite somente:

- leitura do repositório;
- gravação em superfícies de resultado;
- computação/comparação científica;
- hash/proveniência;
- receipt;
- `git rev-parse`/leitura;
- leitura de rede em hosts públicos declarados.

Continuam proibidos:

- shell livre;
- execução arbitrária;
- leitura/exportação de credenciais;
- force push/ref delete;
- escrita arbitrária;
- rede de escrita;
- host arbitrário;
- vigilância/perfil de pessoas;
- objetivo ou expansão autônoma.

## 4. Dados e privacidade

O runtime científico aceita por padrão apenas:

```text
PUBLIC_NON_PERSONAL_SCIENTIFIC_DATA
PUBLIC_NON_PERSONAL_DOCUMENTATION
REPOSITORY_SOURCE_CODE
DERIVED_NON_PERSONAL_RESULTS
```

Classes pessoais, localização precisa de pessoa, biometria, saúde, credenciais, comunicações privadas e dados privados de terceiros não autorizados são bloqueados por padrão.

Classe desconhecida = `HUMAN_REVIEW`, nunca “provavelmente pública”.

O registro canônico de finalidade é:

`data/governance/RLL_DATA_USE_PURPOSE_REGISTRY_V1.json`.

## 5. Rede

Rede é `OFF` por padrão.

A rota Rx calcula com os snapshots commitados. O probe remoto é opcional e só pode ser habilitado explicitamente:

```bash
RX_NETWORK_PROBE=1 python3 -m validacao_real.run_rx_pipeline
```

Mesmo habilitado:

- HTTPS obrigatório;
- hostname exato;
- sem userinfo;
- sem query;
- sem fragment;
- sem porta customizada;
- sem redirect para outro host;
- somente GET/HEAD;
- sem credencial;
- resposta amostrada e limitada.

A rede não é requisito para o cálculo.

## 6. Filesystem

O guard aceita somente caminhos relativos ao repositório e prefixes de escrita declarados.

Durante a rota Rx, política, fontes canônicas, workflows e `.git/` não são superfícies de escrita autorizadas.

Resultado não pode modificar silenciosamente sua própria política de execução.

## 7. Segredos

Segredos não entram na rota Rx.

Se uma rota futura precisar de credencial, ela precisa de outro contrato específico com autoridade, finalidade e workflow próprios. O repositório já mantém política separada de credenciais.

Nunca registrar:

- valor;
- hash;
- tamanho;
- Authorization header;
- dump de ambiente.

## 8. Defesa em duas linhas

### Linha 1 — policy preflight

`internal/governance/development_guard.py`

Valida operação, autoridade, capacidades, dados, rede, escrita e claim.

### Linha 2 — source audit

`tools/rll_security_surface_audit.py`

Procura em AST, entre outros:

- `eval` / `exec`;
- `os.system`;
- `shell=True`;
- desserialização perigosa;
- rede direta fora do guard;
- import/exec dinâmicos para revisão.

Um PASS não é certificação de segurança.

## 9. Uso, motivo e retenção

Cada rota deve responder:

```text
quem executa?
por que executa?
quais dados entram?
quais dados saem?
há dado pessoal?
há segredo?
há rede?
onde pode escrever?
por quanto tempo persiste?
quem pode promover resultado?
```

Se não houver resposta: `TOKEN_VAZIO` ou `HUMAN_REVIEW`.

## 10. Incidente

### Segredo exposto

```text
STOP
→ não commitar
→ revogar/rotacionar no provedor
→ remover exposição pública sem apagar cadeia de auditoria
→ receipt sem valor sensível
→ revisar causa e autorização
```

### Dado pessoal inesperado

```text
STOP
→ quarentena local
→ não commitar
→ classificar finalidade/autoridade
→ revisão humana
→ somente depois decidir descarte ou tratamento permitido
```

### Bypass de política

```text
STOP
→ preservar logs não sensíveis
→ bloquear execução
→ rollback se houve mutação
→ abrir gap
→ corrigir por novo commit/receipt
```

Detalhes de vulnerabilidade, credenciais ou exploit funcional não devem ser publicados em issue aberta; seguir `.github/SECURITY.md`.

## 11. Ameaças principais

O registro estruturado está em:

`data/governance/RLL_SECURITY_PRIVACY_RISK_REGISTER_V1.json`.

As classes principais incluem:

- expansão indevida de capacidade;
- rede arbitrária;
- injeção de comando;
- vazamento de segredo;
- entrada de dado pessoal;
- path traversal;
- adulteração de proveniência;
- supply chain;
- vazamento em logs;
- retenção excessiva;
- side effects externos;
- drift/bypass de política;
- expansão autônoma;
- overclaim;
- falsa certificação.

## 12. O que esta camada não prova

```text
POLICY_PASS != SECURITY_CERTIFICATION
AST_PASS != ABSENCE_OF_VULNERABILITIES
AUTHORIZED_EXECUTION != SCIENTIFIC_VALIDATION
PRIVACY_BY_DESIGN != LEGAL_COMPLIANCE_CERTIFICATION
TOKEN_VAZIO != 0
```

Continuam dependentes de controle externo/revisão:

- sandbox real do SO;
- branch protection;
- secret scanning/push protection;
- revisão independente de segurança;
- revisão jurídica/compliance;
- migração das rotas Python legadas.

## 13. Condição sustentável

Uma nova funcionalidade RLL só entra na fronteira governada quando possui:

```text
purpose
+ authority
+ capabilities
+ data classes
+ network contract
+ write contract
+ failure semantics
+ audit receipt
+ rollback
+ claim boundary
```

Sem isso, a funcionalidade pode existir como código experimental, mas não como rota operacional promovida.

## R3

`F_ok`: autoridade, capacidades, privacidade, rede, filesystem, segredos, auditoria e incidente agora têm contrato unificado.

`F_gap`: sandbox de SO, controles externos do GitHub, revisão independente e migração total do legado permanecem TOKEN_VAZIO.

`F_next`: executar os gates no Termux/CI; depois usar o mesmo envelope para promover Rx 45→64 e demais rotas, uma operação declarada por vez.
