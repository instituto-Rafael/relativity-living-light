# Tokenização Semântica, Estruturas de Contexto e Governança de Dados

> Status: tese técnica canônica inicial.
> Escopo: RAFAELIA / RLL / arquitetura de conhecimento / IA / governança de dados.

## 1. Tese central

A tokenização tradicional é insuficiente como explicação completa do processamento de linguagem em modelos modernos quando o sistema promete compreensão contextual, raciocínio, recuperação, memória, agentes, ferramentas ou análise sobre dados privados.

Se uma arquitetura de IA processa conteúdo privado semanticamente, então ela deve possuir governança verificável sobre:

- finalidade do processamento;
- isolamento entre inferência e treinamento;
- retenção;
- exclusão;
- linhagem de dados;
- uso de metadados;
- acesso humano ou automatizado;
- auditoria;
- evidência de não incorporação indevida.

A exigência técnica não é apenas "como o texto vira token".

A exigência técnica é:

```text
como o conteúdo vira estrutura,
como a estrutura vira contexto,
como o contexto vira resposta,
e como se prova que isso não virou treinamento indevido.
```

## 2. Distinção crítica

Tokenização, no sentido comum de modelos de linguagem, costuma transformar texto em unidades computáveis.

Mas isso não equivale, por si só, a uma camada semântica governada.

```text
tokenização lexical/subpalavra ≠ compreensão semântica governada
embedding ≠ direito de reutilização
contexto privado ≠ dado livre para treinamento
inferência ≠ autorização de incorporação
retenção técnica ≠ consentimento
```

## 3. Exigência RAFAELIA

Uma arquitetura madura deveria declarar pelo menos três camadas:

```text
Camada 1 — Tokenização lexical
  caracteres, bytes, subpalavras, tokens, compressão

Camada 2 — Tokenização semântico-estrutural
  entidades, relações, forças, ausências, antagonismos, isogonias, dependências

Camada 3 — Governança de uso
  finalidade, autorização, isolamento, retenção, descarte, auditoria, prova negativa
```

Sem a terceira camada, a segunda vira risco de apropriação.

## 4. Tokenização semântico-estrutural

Uma tokenização tecnicamente mais honesta deveria mapear não apenas pedaços de texto, mas estruturas de sentido.

Exemplo geral:

```text
termo bruto
→ entidade
→ função
→ relação
→ força
→ oposição
→ dependência
→ lacuna
→ evidência
→ risco
```

No vocabulário desta tese:

- **isogônico**: elementos que compartilham orientação, função, simetria ou direção conceitual;
- **antagônico**: elementos que tensionam, contradizem, resistem ou limitam uma interpretação;
- **derivado**: consequência direta de uma estrutura;
- **antiderivado**: origem ou condição anterior de uma estrutura;
- **reverso**: efeito observado a partir da consequência;
- **inverso**: leitura do resultado de volta para a origem;
- **analítico**: decomposição em pesos, variáveis e evidências.

## 5. Exemplo: física, polias e rampas

Uma leitura pobre veria:

```text
polia móvel
rampa
força
peso
```

Uma leitura semântico-estrutural deveria abrir variáveis:

```text
massa
peso
força aplicada
atrito estático
atrito cinético
ângulo da rampa
comprimento da rampa
flexibilidade do cabo
peso do cabo
elasticidade
perda por deformação
raio da polia
inércia rotacional
atrito no eixo
número de segmentos de cabo
vantagem mecânica ideal
vantagem mecânica real
segurança estrutural
condição de contorno
incerteza de medição
```

A crítica é: se a arquitetura não abre esses índices, ela não amplia ponto de visão; apenas repete a superfície do problema.

## 6. O problema do espelhamento privado

Quando um usuário fornece conteúdo privado e o sistema produz resposta contextualizada, é tecnicamente plausível que ocorram operações semânticas internas como:

- segmentação;
- extração de padrões;
- associação;
- vetorização;
- recuperação;
- resumo;
- classificação;
- geração de relações;
- metadados de uso;
- avaliação de resposta.

Isso não prova, por si só, treinamento indevido.

Mas cria uma obrigação de governança:

```text
se o sistema processa semanticamente,
então deve provar o limite entre processamento temporário e incorporação persistente.
```

## 7. Formulação forte, sem acusação automática

A tese correta não é:

```text
todo processamento semântico é plágio
```

A tese correta é:

```text
todo processamento semântico de dado privado exige prova técnica de governança, isolamento e finalidade.
```

Sem essa prova, o risco de apropriação indevida não pode ser descartado apenas por declaração comercial.

## 8. Ônus de prova em sistemas de IA

Em sistemas que processam dados privados, o ônus técnico deveria ser invertido.

Não basta o fornecedor afirmar:

```text
não usamos indevidamente
```

Deveria existir evidência auditável:

```text
quais dados entraram
qual finalidade foi usada
qual pipeline os processou
quais metadados foram gerados
quanto tempo ficaram retidos
quem acessou
se foram usados em treinamento
como foram excluídos
como se prova a exclusão
```

## 9. Governança mínima exigível

Tabela mínima:

| Camada | Exigência |
|---|---|
| Entrada | origem, usuário, finalidade, consentimento |
| Tokenização | tipo de tokenização e perdas conhecidas |
| Semântica | entidades, relações e metadados derivados |
| Memória | se há memória temporária ou persistente |
| Treinamento | opt-in/opt-out e isolamento comprovável |
| Retenção | prazo e motivo |
| Exclusão | mecanismo e prova de exclusão |
| Auditoria | logs, hashes, política e revisão |
| Segurança | controle de acesso e criptografia |
| Governança | responsável, base legal e política de uso |

## 10. Tokenização semântica como requisito técnico

A tokenização avançada deveria ser declarada como um contrato:

```text
TokenSemanticUnit = {
  raw_span,
  lexical_tokens,
  entities,
  relations,
  domain_variables,
  isogonic_links,
  antagonic_links,
  missing_variables,
  evidence_refs,
  uncertainty,
  allowed_use,
  retention_policy,
  training_eligibility
}
```

A parte mais importante é que `training_eligibility` não pode ser inferida pela máquina sem governança explícita.

## 11. Aplicação ao Tail Protocol e Work Evidence Chain

O RAFAELIA Tail Protocol pode servir como defesa estrutural contra ambiguidade:

```text
Título humano || raf:v1;id=...;fam=...;st=...;dt=...;privacy=private;train=no;ret=ephemeral
```

Campos sugeridos:

```text
privacy=public|private|sensitive
train=no|yes_explicit|unknown
ret=ephemeral|session|workspace|archive
purpose=inference|audit|eval|training_explicit
owner=user|org|public
```

Assim, o próprio bloco carrega a política de uso.

## 12. TOKEN_VAZIO obrigatório

Quando a política de uso não estiver clara:

```text
train=unknown
privacy=unknown
ret=unknown
```

O estado correto é:

```text
TOKEN_VAZIO_GOVERNANCE
```

Não se deve tratar conteúdo como treinável, público ou reutilizável por silêncio.

Silêncio não é consentimento.

## 13. Métrica proposta

```text
Governance_Score = Origem × Consentimento × Isolamento × Retenção × Auditabilidade
```

Se qualquer fator for zero, a governança forte é zero.

```text
Sem consentimento explícito para treinamento,
training_eligibility = false
```

## 14. Crítica científica

Em ciência de dados, trabalhar com dados exige:

- origem;
- finalidade;
- amostragem;
- limpeza;
- transformação;
- metadados;
- viés;
- retenção;
- reprodutibilidade;
- controle de acesso.

Logo, se o sistema processa dados privados com semântica, ele não pode se esconder atrás de uma explicação simplificada de tokenização.

A tokenização lexical pode ser manualmente explicada como BPE, bytes ou subpalavras.

Mas a governança do significado exige outra documentação:

```text
não só como o texto foi quebrado;
mas como o sentido foi usado.
```

## 15. Formulação RAFAELIA

```text
Token não é só pedaço de texto.
Token, em arquitetura viva, é uma unidade de risco semântico.
```

E:

```text
Contexto privado não é matéria-prima livre.
É cadeia de custódia.
```

## 16. Separação final

```text
processar para responder ≠ treinar
resumir ≠ possuir
vetorizar ≠ autorizar
reter ≠ governar
memorizar ≠ validar
semântica ≠ licença
```

## 17. Invariante canônica

```text
Toda operação semântica sobre dado privado deve carregar finalidade, limite, rastreabilidade e prova de não uso indevido.
```

## 18. Próximos passos

1. Expandir o schema do RAFAELIA Tail Protocol com `privacy`, `train`, `ret`, `purpose` e `owner`.
2. Criar `semantic_token_unit.schema.json`.
3. Criar exemplos para física: polia, rampa, atrito, cabo, força real e vantagem mecânica real.
4. Criar política `TOKEN_VAZIO_GOVERNANCE`.
5. Criar auditoria para diferenciar inferência temporária, memória persistente e treinamento.
