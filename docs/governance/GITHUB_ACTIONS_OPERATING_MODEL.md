# GitHub Actions — Modelo Operacional Profissional RLL

Estado: `ACTIVE_GOVERNANCE`  
Efeito científico: `NONE`  
`claim_allowed=false`

## Invariante de sustentação

```text
Evento → Autoridade → Permissão mínima → Composição → Validação
→ Evidência/Receipt → Resíduo → Decisão → Feedback
```

Nenhuma quantidade de workflows substitui essa cadeia. Um workflow só participa
da promoção quando deixa explícitos o evento, a autoridade, as permissões, os
inputs, o limite de tempo, as dependências, a evidência produzida e o significado
da falha.

## Categorias do modelo GitHub adotadas

| capítulo operacional | implementação RLL | estado |
|---|---|---|
| sintaxe, eventos e expressões | auditor YAML + contrato executável | implementado |
| `GITHUB_TOKEN` e menor privilégio | permissões no topo e por job | implementado nos workflows geridos |
| ações de terceiros | SHA completo no novo plano de garantia | implementado; legado incremental |
| composição | orquestrador, aliases e `workflow_call` canônico | parcial |
| concorrência e limites | grupos, cancelamento e timeouts | parcial no legado |
| artefatos e receipts | upload `always()` e SHA-256 | implementado |
| revisão de dependências | job `dependency-review` | implementado |
| análise CodeQL | linguagens `actions` e `python`, `security-extended` | implementado |
| atualização de Actions | Dependabot com destino `rll/lab` | implementado |
| propriedade/revisão | CODEOWNERS | arquivo implementado; imposição externa não verificada |
| política de segurança | `.github/SECURITY.md` | implementado |
| regras, checks e ambientes | configuração do GitHub | `TOKEN_VAZIO_EXTERNAL_SETTING` |
| secret scanning e push protection | configuração do GitHub | `TOKEN_VAZIO_EXTERNAL_SETTING` |
| atestação de artefato/OIDC | somente release, com verificação posterior | desenhado; execução ainda vazia |
| logs e configuração organizacional | control plane | `TOKEN_VAZIO_EXTERNAL_SETTING` |

## Três planos, sem mistura

1. **Plano declarativo:** arquivos YAML roteiam eventos e jobs.
2. **Plano algorítmico:** scripts testados calculam inventário, maturidade e decisão.
3. **Plano de controle externo:** rulesets, ambientes, required checks, secret
   scanning e políticas da organização são verificados fora do Git.

Um arquivo não pode afirmar que um botão externo está habilitado. Essa fronteira
evita conformidade fictícia.

## Composição dos múltiplos workflows

Os workflows devem ser classificados por finalidade:

- estrutural: sintaxe, convenção, arquitetura, contratos;
- segurança: dependências, CodeQL, segredos e proveniência;
- dados: ingestão, manifesto, variância e integridade;
- científico-sombra: cálculo sem promoção automática de claim;
- orquestração: coordena sessões e espera conclusões;
- publicação: somente com ambiente protegido e autorização explícita.

A redução futura não será feita apagando workflows. Primeiro identifica-se
duplicação; depois extrai-se `workflow_call`, composite actions ou scripts; por
fim o alias antigo pode ser descontinuado com receipt.

## Segurança fail-closed

- `pull_request_target` permanece proibido por padrão;
- texto de issue/PR não é interpolado diretamente em `run`;
- ações novas são fixadas em SHA completo;
- checkout não persiste credenciais;
- jobs de análise possuem timeout;
- escrita é concedida por job e somente quando indispensável;
- falhas e lacunas permanecem registradas;
- `continue-on-error` exige decisão posterior e receipt.

## Atestação e conformidade

Artifact attestation estabelece procedência do artefato; não certifica teoria,
qualidade científica ou conformidade externa. A implementação só será promovida
quando um artefato de `rll/release` ou `main` for atestado e posteriormente
verificado, preservando URL, digest, workflow, commit e resultado da verificação.

```text
ARTIFACT_ATTESTATION_EXECUTION = TOKEN_VAZIO
EXTERNAL_COMPLIANCE = TOKEN_VAZIO_EXTERNAL_AUTHORITY
```

## F_next verificável

1. concluir os checks deste PR;
2. registrar os nomes exatos dos required checks;
3. verificar rulesets de cada branch de maturidade;
4. verificar secret scanning e push protection;
5. criar ambientes `release` e `publication` com revisores;
6. extrair famílias repetidas para reusable workflows;
7. atestar e verificar o primeiro artefato de release.
