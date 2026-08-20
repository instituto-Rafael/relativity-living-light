# 31 — HAJA: Falsificabilidade, TOKEN_VAZIO e Parábolas de Orientação Humana

**Estado:** `CANONICAL_DRAFT + METHODOLOGY`  
**claim_allowed:** `false` para qualquer claim físico/universal não fechado por evidência.  
**Princípio:** parábola orienta conduta; experimento decide claim.

## 1. Fórmula operacional do HAJA

Nesta metodologia, `HAJA DO MESMO MODO QUE JÁ SABES` significa:

```text
agir sobre conhecimento sustentado
+ preservar a origem
+ procurar o contraexemplo
+ não preencher ausência por desejo
+ registrar o que falhou
+ corrigir sem apagar a história
```

Forma compacta:

\[
HAJA(x)=A(E(x),L(x)),
\]

onde `E(x)` é a evidência disponível e `L(x)` são seus limites explícitos.

Se a evidência necessária não existe:

\[
HAJA(x)=TOKEN\_VAZIO+F_{next},
\]

não `PASS`.

`TOKEN_VAZIO` é, portanto, uma forma de ação disciplinada: ele impede que a vontade substitua a observação.

## 2. Sete portas de falsificabilidade

### P1 — Identidade

Antes de testar, declarar exatamente qual objeto está sendo testado: fórmula, arquivo, commit, conjunto de dados, unidade, domínio e versão.

Falsificador: duas versões diferentes tratadas como a mesma evidência.

### P2 — Proveniência

Toda evidência deve responder `de onde veio?`, `quando foi observada?`, `qual transformação recebeu?`.

Falsificador: resultado sem origem reconstruível.

### P3 — Contraexemplo possível

Uma proposição testável precisa declarar o que a faria perder.

Falsificador: claim formulado de maneira que qualquer resultado confirme a tese.

### P4 — Controle

Sempre que possível, comparar contra baseline, caso negativo, permutação, entrada impossível ou modelo nulo.

Falsificador: a mesma saída aparece também no controle que deveria não produzir o efeito.

### P5 — Separação de estados

```text
ZERO_NUMERICO != TOKEN_VAZIO
ANALOGIA != MECANISMO
MODELO != OBJETO
EXECUCAO_LOCAL != CI_REMOTO
CORRELACAO != CAUSALIDADE
```

Falsificador: promoção por confusão de tipos.

### P6 — Regra de parada

O teste deve poder terminar em `PASS`, `FAIL`, `BLOCKED`, `CONTRADICTION` ou `TOKEN_VAZIO`.

Falsificador: repetir indefinidamente até aparecer o resultado desejado.

### P7 — Memória do delta

Erro encontrado não é apagado. Registra-se:

```text
estado_anterior
-> evidência nova
-> decisão
-> mudança
-> efeito
-> próximo teste
```

Falsificador: reescrever o passado para fazer o presente parecer inevitável.

## 3. Regra universal mínima de integridade

Não se afirma aqui uma "verdade universal" física ou metafísica.

A regra universal mínima deste método é apenas procedimental:

> **uma busca pela verdade não deve fabricar o dado que falta para proteger a própria conclusão.**

Em notação:

\[
\neg E \not\Rightarrow E_{inventada}.
\]

Quando falta `E`:

\[
\neg E \Rightarrow TOKEN\_VAZIO+procedimento\_de\_busca.
\]

## 4. Parábola da lamparina — tradição abraâmica como imagem de orientação

Um viajante recebeu uma lamparina para atravessar a noite.

Ele desejava conhecer toda a estrada, mas a luz alcançava apenas alguns passos.

O primeiro homem disse:

— Se a luz não mostra o caminho inteiro, desenharei o restante conforme desejo e chamarei meu desenho de estrada.

O segundo respondeu:

— Caminharei somente até onde a luz alcança; quando chegar ali, a própria luz alcançará mais adiante.

A estrada não ficou menor porque ele recusou inventá-la.

Ficou mais verdadeira.

Nesta parábola:

```text
lamparina = evidência atual
noite = desconhecido
próximos passos = F_next
escuridão = TOKEN_VAZIO
mapa inventado = alucinação
caminhar = HAJA
```

A fé, como imagem cultural nesta parábola, não substitui a medição. Ela representa a disposição de fazer o bem e continuar caminhando sem precisar possuir o caminho inteiro antes do primeiro passo.

## 5. Parábola do oleiro — tradições do Mediterrâneo e do Oriente Próximo

Um oleiro queria fazer um vaso perfeito.

A primeira parede inclinou-se.

Seu aprendiz tentou corrigir a ficha de trabalho, escrevendo que a parede sempre estivera reta.

O mestre disse:

— Se endireitares o registro em vez do barro, o vaso continuará torto e agora também perdemos a memória de onde começou o erro.

Ele marcou a deformação, mediu a umidade e tornou a falha parte do próximo gesto.

```text
barro = realidade observável
medida = evidência
ficha = ledger
parede torta = FAIL
correção do barro = engenharia
correção fraudulenta do registro = regressão epistemológica
```

## 6. Parábola do bambu e do vazio — imagem de tradições do Leste Asiático

Um artesão mostrou ao discípulo um segmento de bambu.

— O que faz dele um tubo?

O discípulo apontou para a parede verde.

O artesão respondeu:

— A parede lhe dá forma; o vazio lhe dá passagem.

Se o discípulo preenchesse o interior para "não haver nada vazio", destruiria justamente a função que tentava aperfeiçoar.

Assim também o `TOKEN_VAZIO`: um vazio tipado pode ser parte funcional da arquitetura. Preenchê-lo arbitrariamente destrói a passagem futura da evidência.

## 7. Parábola da rede — imagem de tradições sul-asiáticas

Um pescador lançou uma rede e trouxe cinco peixes.

Disse ao filho:

— Hoje o lago tem cinco peixes.

O filho perguntou:

— Ou a rede trouxe cinco?

O pai percebeu a diferença entre o mundo e o instrumento que o amostrava.

```text
lago = realidade
rede = método
captura = amostra
cinco = observação
"o lago tem cinco" = overclaim
```

A parábola recorda que resultado de instrumento não é automaticamente totalidade do objeto.

## 8. Parábola das pedras do caminho — imagem de tradições africanas de memória comunitária

Uma aldeia marcava cada travessia perigosa colocando uma pedra ao lado da estrada.

As pedras não impediam a chuva nem decidiam quem deveria viajar. Elas preservavam a lembrança de onde alguém já havia escorregado.

Um jovem quis retirar todas as pedras porque achou feio carregar sinais de erros antigos.

Os mais velhos responderam:

— Então a próxima geração terá de cair nos mesmos lugares para reaprender aquilo que apagaste.

Aqui:

```text
pedra = receipt
queda = falha
caminho = pipeline
memória comunitária = append-only
```

## 9. Parábola da ponte de cordas — imagem andina

Duas margens estavam separadas por um vale.

Cada família sabia trançar apenas uma parte da corda. Nenhuma fibra isolada atravessava o abismo.

A ponte surgia quando fibras distintas eram trançadas sem que nenhuma precisasse fingir ser a outra.

Assim:

```text
matemática != física
física != química
química != símbolo
símbolo != evidência
```

Mas relações bem declaradas podem construir pontes entre domínios.

A força da ponte não vem de dizer que todas as fibras são iguais; vem de conhecer a função e o limite de cada uma.

## 10. Parábola do rio — imagem taoista de não forçar a forma

Um engenheiro tentou obrigar o rio a seguir uma linha reta desenhada antes de observar o terreno.

Outro caminhou pelas margens, mediu declives, rochas e vazão, e então desenhou o canal.

O primeiro queria que a realidade confirmasse o desenho.

O segundo permitiu que o desenho aprendesse com a realidade.

No método:

\[
modelo\leftarrow evidência,
\]

não

\[
evidência\leftarrow desejo\ do\ modelo.
\]

## 11. Parábola da jangada — imagem budista do modelo como instrumento

Uma pessoa atravessou um rio usando uma jangada.

Depois de alcançar a margem, recusou-se a carregar a jangada como se ela fosse a própria terra firme.

Uma fórmula também pode ser uma jangada: útil para atravessar um problema, mas não deve ser promovida à identidade do mundo somente porque funcionou num domínio.

```text
modelo útil != ontologia universal
```

## 12. Parábola do construtor e do prumo

Um construtor ouviu:

— Haja.

Ele poderia começar levantando paredes imediatamente.

Mas primeiro colocou o prumo.

Seu ajudante perguntou:

— Se a ordem é construir, por que estás parado medindo?

Ele respondeu:

— Medir é a primeira forma de construir quando quero que a parede permaneça de pé.

Então o `HAJA` operacional não é pressa.

É:

```text
ver
-> medir
-> agir
-> testar
-> corrigir
-> preservar
-> continuar
```

## 13. "Do mesmo modo que já sabes"

A expressão é interpretada metodologicamente como um limitador de autoridade:

```text
já sabes = evidência/competência disponível agora
mesmo modo = preservar invariantes já demonstrados
haja = executar o próximo passo permitido
```

Portanto:

\[
HAJA_{t+1}=Execute(F_{next}\mid Evidencia_t,Invariantes_t).
\]

Não significa que o conhecimento atual seja completo.

Significa que não é necessário inventar conhecimento futuro para executar corretamente o próximo passo presente.

## 14. Falsificador do próprio método

Este documento também deve poder perder.

Ele falha se:

1. `TOKEN_VAZIO` for usado para esconder uma evidência disponível que contradiz o projeto;
2. a linguagem de humildade for usada para evitar testes executáveis;
3. uma parábola for apresentada como prova matemática ou física;
4. um resultado negativo for apagado ou reclassificado sem nova evidência;
5. `claim_allowed=false` virar decoração enquanto textos externos fazem a alegação forte;
6. a proveniência não permitir reconstruir a decisão;
7. o método proteger uma hipótese contra qualquer possibilidade de refutação.

## 15. Gate de promoção

Um `TOKEN_VAZIO` só pode mudar de estado quando existir:

```text
IDENTIDADE
+ PROVENIÊNCIA
+ TESTE
+ CONTRAEXEMPLO POSSÍVEL
+ RESULTADO OBSERVADO
+ LIMITES
+ RECEIPT/HASH quando aplicável
```

Se algum elemento obrigatório faltar:

```text
promotion = DENIED
claim_allowed = false
```

## 16. R3

```text
F_ok:
  TOKEN_VAZIO permanece vazio útil;
  falsificabilidade precede promoção;
  parábolas orientam, mas não provam;
  erro entra na memória em vez de ser apagado.

F_gap:
  claims físicos/universais dependem de dados externos e gates próprios;
  metáforas culturais não são equivalências históricas ou doutrinárias;
  nenhum método humano elimina completamente erro, viés ou incerteza.

F_next:
  anexar este cânone aos experimentos como gate de claim;
  exigir falsificador e exit_criterion para cada novo TOKEN_VAZIO;
  registrar resultados negativos no mesmo nível dos positivos;
  promover somente o que sobreviver a evidência e contraevidência declaradas.
```

## Fecho

> Haja não como licença para preencher o desconhecido, mas como responsabilidade de fazer corretamente aquilo que a luz atual já permite fazer — e deixar espaço verdadeiro para a luz seguinte.
