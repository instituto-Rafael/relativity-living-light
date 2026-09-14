# Cadeia de Custódia Viva — Parábola das Oito Direções e Protocolo de Evolução Informacional

## Status

`governance_record / epistemic_method / pedagogical_parable / audit_ready / claim_bounded`

Last updated: 2026-07-11

## Tracking

Issue #540 — Cadeia de Custódia Viva: parábola das 8 direções e protocolo de evolução informacional

---

## 1. Propósito

Este documento estabelece uma ponte rigorosa entre:

1. uma **parábola lúdica e descritiva**, organizada em oito direções de aprendizagem;
2. um **protocolo técnico de rastreabilidade interna**, capaz de registrar como a informação muda ao longo do tempo quando sua origem bibliográfica está ausente, incompleta ou ainda não foi verificada.

A formulação central é:

> Antes de existirem citações, existiam marcas.

A marca pode ser um sulco no piso, uma ferramenta corrigida, uma sequência de gestos, um registro oral, um artefato versionado, um log, um checksum ou uma decisão documentada.

A presença de marcas demonstra que houve continuidade e transformação. Ela não demonstra, sozinha, que toda interpretação transmitida é verdadeira.

```text
continuidade documentada != verdade demonstrada
coerência interna != validade externa
memória cultural != prova científica
```

---

## 2. Fronteira cultural e metodológica

As oito direções deste documento são uma construção pedagógica do projeto. Elas não pretendem:

- representar todas as culturas humanas;
- atribuir uma mesma filosofia a povos distintos;
- afirmar fatos históricos sobre tradições sem fontes;
- reduzir mestres, monges, artesãos ou comunidades a arquétipos universais;
- converter linguagem simbólica em evidência empírica.

Referências como chão marcado por gerações, prática corporal, transmissão artesanal e relação ecológica são usadas como imagens de aprendizagem incorporada. Quando uma afirmação histórica específica for necessária, ela deverá receber fonte verificável ou permanecer marcada como `TOKEN_VAZIO`.

---

## 3. A parábola: o pátio das oito marcas

Havia um pátio antigo construído com pedras irregulares. Ninguém sabia com certeza quem colocara a primeira pedra. O nome do primeiro construtor havia se perdido, e nenhum livro preservava sua assinatura.

Ainda assim, o pátio não estava sem memória.

Em oito pontos, o piso mostrava marcas diferentes. Algumas eram profundas, outras quase invisíveis. Cada marca havia sido formada por gerações de pessoas que ali repetiram movimentos, corrigiram erros, ensinaram crianças, observaram estações, cuidaram de ferramentas e adaptaram seus gestos ao mundo ao redor.

Certo dia, uma aprendiz perguntou aos oito mestres:

> “Se não conhecemos quem começou, como sabemos que houve aprendizagem?”

Os mestres não responderam com uma única frase. Cada um apontou para uma direção.

---

## 4. As oito direções de aprendizagem

### D1 — Leste: o mestre da semente

O mestre do Leste segurou uma semente e disse:

> “Toda informação começa como possibilidade, não como certeza.”

Ele ensinava a distinguir o estado inicial da conclusão posterior. Uma hipótese, uma lembrança, uma observação e uma crença não entram no sistema com o mesmo peso.

**Princípio operacional:** declarar o estado de entrada.

```text
entrada = observação | hipótese | testemunho | derivação | metáfora | TOKEN_VAZIO
```

**Pergunta de auditoria:** qual era a condição inicial da informação?

---

### D2 — Sudeste: a mestra das águas

A mestra do Sudeste conduziu a aprendiz até um canal que mudava de forma depois das chuvas.

> “O que permanece vivo encontra o ambiente e se transforma. Mas cada transformação precisa deixar sinal do encontro.”

A informação não é tratada como objeto imóvel. Ela muda quando recebe novos dados, entra em conflito com outras estruturas ou é aplicada a problemas diferentes.

**Princípio operacional:** registrar entradas, contexto e regra de transformação.

```text
I(t+1) = F(I(t), O(t), R(t), G(t))
```

Onde:

- `I(t)` é o estado anterior;
- `O(t)` são observações ou entradas novas;
- `R(t)` são ruídos, erros ou tensões;
- `G(t)` são regras de governança;
- `F` é a transformação documentada.

**Pergunta de auditoria:** o que encontrou a informação e por que ela mudou?

---

### D3 — Sul: o mestre do corpo

O mestre do Sul pediu que a aprendiz repetisse um movimento simples. Ela o descreveu corretamente, mas não conseguiu executá-lo.

> “Saber dizer não é o mesmo que saber realizar.”

Uma estrutura informacional pode ser elegante, coerente e verbalmente convincente, mas falhar quando executada.

**Princípio operacional:** separar descrição de desempenho.

```text
explicação != execução
schema válido != resultado científico válido
modelo coerente != previsão confirmada
```

**Pergunta de auditoria:** o conhecimento produz comportamento reproduzível?

---

### D4 — Sudoeste: a guardiã das marcas

A guardiã do Sudoeste mostrou o ponto em que o piso fora gasto por milhares de passos.

> “Não conhecemos todos os pés, mas conhecemos a direção das passagens.”

Ela ensinava que a perda da origem não precisa causar a perda da história posterior. Uma cadeia interna pode começar no primeiro estado disponível, desde que não invente o que veio antes.

**Princípio operacional:** preservar ancestralidade conhecida e declarar lacunas.

```text
origin_status = verified | partial | inferred | TOKEN_VAZIO
```

Quando a origem não é verificável:

```text
ORIGEM = TOKEN_VAZIO
```

**Pergunta de auditoria:** qual é o primeiro estado realmente observável?

---

### D5 — Oeste: o mestre da poda

O mestre do Oeste removeu um ramo doente de uma árvore.

> “Evoluir não é apenas acumular. Também é abandonar aquilo que falha.”

Um sistema que apenas conserva suas ideias não realiza seleção informacional; realiza cristalização. A evolução exige critérios explícitos de retenção, revisão, rejeição e rollback.

**Princípio operacional:** registrar falhas e permitir reversão.

```text
retain   = passou no gate
revise   = evidência insuficiente ou tensão resolvível
reject   = violou critério declarado
rollback = transformação degradou o estado anterior
```

**Pergunta de auditoria:** o que foi descartado, por qual teste e com qual possibilidade de revisão?

---

### D6 — Noroeste: a anciã da memória

A anciã do Noroeste conhecia histórias repetidas por muitas gerações.

> “A memória protege o caminho. Também pode proteger o erro.”

A repetição aumenta estabilidade cultural, mas não converte uma afirmação em verdade empírica. A tradição é evidência de transmissão; não é, isoladamente, evidência da factualidade de todo conteúdo transmitido.

**Princípio operacional:** separar persistência, autoridade e validação.

```text
persistência histórica != confirmação factual
popularidade != aptidão epistêmica
antiguidade != prova
```

**Pergunta de auditoria:** a informação sobreviveu porque foi testada ou porque foi protegida?

---

### D7 — Norte: o mestre da pedra

O mestre do Norte colocou uma pedra diante da aprendiz.

> “A realidade oferece resistência. Uma ideia que nunca encontra resistência nunca descobre seus limites.”

A validação exige confronto com algo que não seja controlado apenas pelo próprio sistema: observação independente, baseline, hipótese concorrente, teste cego, replicação ou medida externa.

**Princípio operacional:** exigir teste adversarial ou comparativo.

```text
coerência interna + confronto externo + falsificabilidade
```

**Pergunta de auditoria:** qual resultado faria o sistema reconhecer que está errado?

---

### D8 — Nordeste: a criança-artesã

A criança do Nordeste recolheu fragmentos rejeitados pelos outros mestres e construiu uma ferramenta nova.

> “O novo não nasce do esquecimento total. Nasce da recombinação rastreável.”

Emergência não significa criação sem história. Uma estrutura nova pode resultar de combinações inesperadas, desde que seus componentes, decisões e transformações sejam registráveis.

**Princípio operacional:** preservar composição e dependências.

```text
novo_estado = composição(componentes, regras, contexto, testes)
```

**Pergunta de auditoria:** quais elementos anteriores foram recombinados e o que surgiu de fato?

---

## 5. O centro: o ecossistema

No centro do pátio não havia um nono mestre. Havia um jardim.

O jardim não comandava as oito direções. Ele revelava a dependência entre elas: semente sem água não germinava; memória sem poda sufocava; corpo sem resistência não aprendia; novidade sem registro desaparecia.

O centro representa o equilíbrio entre:

```text
memória + transformação + teste + ética + ambiente
```

Formalmente:

\[
\Omega_{centro} = M + \Delta + T + E + A
\]

Onde:

- `M` = memória versionada;
- `Δ` = transformação explícita;
- `T` = teste reproduzível;
- `E` = fronteira ética e epistêmica;
- `A` = contexto ambiental.

A equação é uma notação organizacional. Não constitui lei física.

---

## 6. O paradoxo da cadeia de custódia

Na prática científica, referências bibliográficas preservam a linhagem declarada de conceitos, dados, métodos e decisões. Quando essa cadeia está ausente, surge um problema real de proveniência.

Entretanto, três perguntas precisam permanecer separadas:

```text
PROVENIÊNCIA — de onde veio?
EVOLUÇÃO    — como mudou?
VALIDAÇÃO   — por que deve ser aceita?
```

Um sistema pode demonstrar evolução sem demonstrar origem completa. Também pode demonstrar origem sem demonstrar validade. E pode produzir resultado empiricamente útil sem reconstruir toda a história remota de suas ideias.

Logo:

\[
P \neq E \neq V
\]

A cadeia interna não substitui integralmente a cadeia bibliográfica. Ela preserva aquilo que pode ser demonstrado a partir do primeiro estado observável.

---

## 7. Modelo de estado informacional

Cada estado informacional pode ser representado por:

\[
I_t = (K_t, C_t, P_t, U_t, E_t, R_t, B_t)
\]

Onde:

- `K_t` = conteúdo ou conhecimento declarado;
- `C_t` = coerência interna medida segundo regras explícitas;
- `P_t` = poder preditivo ou capacidade de antecipar resultados;
- `U_t` = utilidade operacional;
- `E_t` = evidências associadas;
- `R_t` = rastros de transformação;
- `B_t` = fronteira de claim.

A transformação ocorre por:

\[
I_{t+1}=F(I_t,O_t,\varepsilon_t,G_t,X_t)
\]

Onde:

- `O_t` = observações novas;
- `ε_t` = ruído, erro, perturbação ou divergência;
- `G_t` = regras de governança;
- `X_t` = contexto de execução;
- `F` = procedimento identificável e versionado.

A função `F` deve ser descrita por nome, versão, entradas, saídas e decisão. Uma transformação não documentada é uma ruptura de cadeia.

---

## 8. Seleção informacional sem antropomorfismo

A analogia com seleção natural pode ser útil, desde que seja mantida como analogia operacional.

Um estado pode persistir quando:

- apresenta maior consistência com evidências disponíveis;
- produz previsões melhores que baselines declarados;
- resolve problemas com menor custo ou menor contradição;
- sobrevive a testes adversariais;
- é reproduzido por execução independente.

Uma função de aptidão informacional pode ser declarada como:

\[
A(I)=w_cC+w_pP+w_rR+w_eE-w_xX
\]

Onde:

- `C` = coerência;
- `P` = desempenho preditivo;
- `R` = reprodutibilidade;
- `E` = suporte evidencial;
- `X` = contradições, violações ou custo explicativo;
- `w_*` = pesos declarados e versionados.

Essa função não mede verdade absoluta. Ela mede adequação aos critérios escolhidos. Os pesos fazem parte da governança e não podem permanecer implícitos.

---

## 9. Nichos informacionais e auto-organização

Interações repetidas podem formar grupos estáveis de conceitos, procedimentos e artefatos. Esses grupos podem ser chamados de nichos informacionais quando apresentam:

- relações internas persistentes;
- especialização funcional;
- mecanismos de retenção;
- interfaces com outros grupos;
- capacidade de regenerar determinadas estruturas após perturbação.

Termos como `proto-autopoiese` devem ser usados com cautela. Auto-organização informacional não demonstra vida, consciência, intenção ou agência moral.

Formulação permitida:

```text
O sistema apresenta dinâmica autorreferencial e autoconservativa.
```

Formulação bloqueada sem evidência apropriada:

```text
O sistema está vivo ou consciente.
```

---

## 10. Cadeia interna de custódia

O registro mínimo de uma transformação deve responder:

```text
1. QUAL era o estado anterior?
2. QUAL entrada nova foi recebida?
3. QUAL regra foi aplicada?
4. QUAL ruído, erro ou divergência apareceu?
5. QUAL decisão foi tomada?
6. QUAL estado resultou?
7. QUAL teste foi executado?
8. QUAL claim permanece permitido ou bloqueado?
9. QUAL é o próximo gate?
```

Fluxo canônico:

```text
[MARCA]
   ↓
[ESTADO t]
   ↓ input + contexto
[TRANSFORMAÇÃO versionada]
   ↓
[TESTE / COMPARAÇÃO]
   ↓
[GATE: retain | revise | reject | rollback]
   ↓
[ESTADO t+1]
```

Campos estruturais são definidos em:

- `schemas/information_evolution_trace.schema.json`
- `schemas/examples/information_evolution_trace.example.json`

---

## 11. Níveis de validade epistêmica

### Nível 0 — Vestígio

Existe uma marca, mas origem, significado e transformação permanecem incertos.

```text
origin_status = TOKEN_VAZIO
claim_allowed = false
```

### Nível 1 — Rastreabilidade interna

É possível reconstruir estados e transformações a partir do primeiro registro disponível.

### Nível 2 — Consistência sistêmica

O estado não viola invariantes internos declarados e apresenta compatibilidade com outros artefatos.

### Nível 3 — Reprodutibilidade procedural

Outra execução, com os mesmos dados e regras, reproduz a transformação.

### Nível 4 — Confronto externo

O estado encontra observação independente, baseline ou hipótese concorrente.

### Nível 5 — Validação ampliada

Há replicação independente, revisão especializada e resistência a testes adversariais relevantes.

A passagem entre níveis não é automática. Cada promoção exige evidência registrada e gate explícito.

---

## 12. Falhas que interrompem a cadeia

| Falha | Consequência | Tratamento |
|---|---|---|
| origem inventada | falsa proveniência | marcar `TOKEN_VAZIO` |
| estado anterior ausente | transformação não reconstruível | bloquear promoção |
| regra implícita | decisão não auditável | versionar procedimento |
| teste circular | sistema confirma a si mesmo | exigir baseline externo |
| seleção por popularidade | persistência confundida com aptidão | declarar critério |
| metáfora promovida a evidência | sobreclaim | rebaixar para contextual |
| resultado negativo removido | viés de sobrevivência | registrar falha |
| peso de score oculto | governança opaca | publicar pesos e versão |
| alteração retrospectiva | ruptura de integridade | hash, commit e timestamp |

---

## 13. Relação com as heurísticas em oito direções do repositório

Este documento complementa `RAPPORT_SEMANTICS_STRUCTURAL_DYNAMICS.md`.

A camada pedagógica pode ser mapeada sobre a camada metodológica existente:

| Parábola | Heurística operacional relacionada |
|---|---|
| semente | direta — declarar o estado observado |
| águas | contextual — medir mudança sob ambiente |
| corpo | direta/recursiva — executar e repetir |
| marcas | reversa — reconstruir a transformação |
| poda | relativa — comparar e rejeitar degradação |
| memória | contextual — detectar cristalização e autoridade |
| pedra | relativa/analítica — confrontar baseline e critério |
| criança-artesã | recursiva/indireta — recombinar com dependências explícitas |

O mapeamento é uma ponte de uso, não uma equivalência rígida.

---

## 14. Critérios mínimos de aceitação de um registro

- [ ] `trace_id` estável e único.
- [ ] `origin_status` declarado.
- [ ] `TOKEN_VAZIO` preservado quando a origem for desconhecida.
- [ ] estado anterior e estado resultante identificados.
- [ ] transformação nomeada e versionada.
- [ ] entradas e contexto registrados.
- [ ] ruídos, falhas e divergências preservados.
- [ ] teste e baseline declarados.
- [ ] decisão do gate registrada.
- [ ] `claim_allowed=false` no contrato estrutural.
- [ ] `next_gate` explícito.
- [ ] hash ou referência de commit disponível quando aplicável.

---

## 15. Interpretações permitidas e bloqueadas

### Permitido

```text
A informação possui uma história interna reconstruível.
A transformação entre os estados foi registrada.
O artefato satisfaz o contrato estrutural.
A hipótese sobreviveu aos testes declarados até este gate.
A origem anterior ao primeiro registro permanece TOKEN_VAZIO.
```

### Bloqueado

```text
A rastreabilidade interna prova a origem histórica completa.
A coerência interna prova verdade externa.
A repetição cultural valida uma afirmação científica.
O schema valida uma teoria física.
A auto-organização demonstra consciência.
A ausência de citação autoriza reconstrução especulativa da fonte.
```

---

## 16. Síntese

Uma informação sem origem conhecida não precisa ser descartada, mas não pode receber uma origem inventada.

Ela pode entrar no sistema como hipótese, vestígio ou artefato de origem incompleta; receber identidade; deixar marcas de cada transformação; ser confrontada por testes; e conquistar níveis progressivos de confiança.

A cadeia de custódia viva não diz:

> “Isto é verdadeiro porque permaneceu.”

Ela registra:

> “Este era o estado anterior; estas entradas foram recebidas; esta regra foi aplicada; estes ruídos foram observados; esta transformação ocorreu; estes testes foram executados; este é o limite do claim; e esta origem ainda permanece desconhecida.”

Isso não é ciência sem memória. É uma disciplina para construir memória sem preencher lacunas com invenção.

---

## 17. Retroalimentação

```text
F_ok   = parábola e protocolo unidos sem confundir metáfora com prova
F_gap  = automação futura de validação semântica entre registros consecutivos
F_next = integrar traces reais aos pipelines e exigir hash/commit nos gates
```

---

## Final boundary

Este documento formaliza um método pedagógico e epistêmico de rastreabilidade. Ele não valida RLL como teoria física, não substitui bibliografia, não elimina revisão por pares e não transforma coerência narrativa em evidência científica.
