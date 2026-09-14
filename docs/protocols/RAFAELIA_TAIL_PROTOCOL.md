# RAFAELIA Tail Protocol — RTP v1

> Status: especificação canônica inicial.
> Objetivo: permitir que títulos, assuntos de e-mail, eventos de calendário, documentos HTML e memorandos tenham uma parte humana limpa e uma cauda de máquina rastreável.

## 1. Princípio

O protocolo separa apresentação humana de metadado operacional:

```text
[HUMAN_VISIBLE_TITLE] || raf:v1;id=...;fam=...;st=...;dt=...;prev=...;link=...;hash=...
```

Regra:

```text
começo = humano
final = máquina
cor = sorter visual
label = classificação nativa
anexo/link = corpo da prova
hash/id = cadeia de custódia
grid oculta = dados para nerds
```

A parte humana deve permanecer legível, sem poluição visual. A cauda final é lida por parser, IA, script, rotina de auditoria ou indexador.

## 2. Motivação

A arquitetura RAFAELIA trata conhecimento como rede de relações, não sequência linear. O Tail Protocol aplica esse princípio a objetos cotidianos de trabalho: Gmail, Google Calendar, Drive, GitHub, HTML, Markdown e ledgers.

A inferência não substitui leitura real. Ela localiza o bloco. O protocolo aponta onde ler, como cruzar e como validar.

## 3. Modelo geral

```text
subject/event/title/html text
    ↓
last delimiter search: " || "
    ↓
left side  = visible human title
right side = machine trailer
    ↓
parse key=value pairs separated by semicolon
    ↓
build relation graph and custody chain
```

## 4. Delimitador

O delimitador canônico é:

```text
 || 
```

Motivos:

- simples de ler;
- fácil de localizar com `rsplit(" || ", 1)`;
- evita poluir o começo do título;
- permite títulos humanos livres;
- permite leitura da direita para a esquerda.

## 5. Campos mínimos

| Campo | Exemplo | Obrigatório | Função |
|---|---|---:|---|
| `raf` | `v1` | sim | versão do protocolo |
| `id` | `MAIL-0001` | sim | identificador do bloco |
| `fam` | `email` | sim | família semântica |
| `st` | `ev` | sim | estado epistêmico/operacional |
| `dt` | `20260710` | recomendado | data de referência compacta |
| `prev` | `MAIL-0000` | opcional | bloco anterior |
| `link` | `DRV-0001,GIT-0001` | opcional | relações cruzadas |
| `hash` | `ab12cd34` | opcional | digest curto |
| `cal` | `CAL-0001` | opcional | evento calendário associado |
| `thr` | `THR-0001` | opcional | thread Gmail associada |
| `grid` | `nerd` | opcional | indica presença de grid/revelação técnica |
| `dbg` | `1` | opcional | indica dados técnicos para inspeção |

## 6. Famílias canônicas

```text
email   cal   drive   git   llm   cti   socket   edge   gov   paper   ops   doc   audit
```

## 7. Status canônicos curtos

| Código | Estado | Uso |
|---|---|---|
| `ev` | evidence | evidência localizada |
| `hyp` | hypothesis | hipótese útil a testar |
| `act` | action | ação pendente |
| `gap` | TOKEN_VAZIO | lacuna explícita |
| `sens` | sensitive | material sensível |
| `done` | done | concluído |
| `rev` | review | revisão marcada |
| `err` | error | erro observado |
| `audit` | audit | auditoria/rastreio |

## 8. Grid oculta — Dados para nerds

A camada `Dados para nerds` é uma inspeção recolhida por padrão. Ela não deve poluir o título humano, mas deve deixar visível, quando aberta, os dados técnicos do bloco.

Uso recomendado em HTML:

```html
<details class="raf-nerd-grid">
  <summary>Dados para nerds</summary>
  <dl class="raf-grid">
    <dt>raf</dt><dd>v1</dd>
    <dt>id</dt><dd>MAIL-0007</dd>
    <dt>fam</dt><dd>email</dd>
    <dt>st</dt><dd>rev</dd>
    <dt>dt</dt><dd>20260710</dd>
    <dt>prev</dt><dd>MAIL-0006</dd>
    <dt>links</dt><dd>DRV-0001, CAL-0002, GIT-0093</dd>
    <dt>hash</dt><dd>ab12cd34</dd>
  </dl>
</details>
```

Regra:

```text
visível por padrão: título humano
recolhido por padrão: dados para nerds
machine-readable sempre: trailer ou data-raf-*
```

## 9. HTML object / visible-hidden model

### Forma com `data-*`

```html
<div class="raf-block"
     data-raf="v1"
     data-raf-id="MAIL-0007"
     data-raf-fam="email"
     data-raf-st="rev"
     data-raf-dt="20260710"
     data-raf-prev="MAIL-0006"
     data-raf-link="DRV-0001,GIT-0093,CAL-0002"
     data-raf-grid="nerd">
  <span class="raf-visible">Revisar navegação semântica do Drive</span>
  <details class="raf-nerd-grid">
    <summary>Dados para nerds</summary>
    <dl class="raf-grid">
      <dt>id</dt><dd>MAIL-0007</dd>
      <dt>links</dt><dd>DRV-0001,GIT-0093,CAL-0002</dd>
    </dl>
  </details>
</div>
```

### Forma com trailer escondido

```html
<div class="raf-block">
  <span class="raf-visible">Revisar navegação semântica do Drive</span>
  <span class="raf-tail" hidden aria-hidden="true">raf:v1;id=MAIL-0007;fam=email;st=ev;dt=20260710;prev=MAIL-0006;link=DRV-0001,GIT-0093;grid=nerd</span>
  <details class="raf-nerd-grid">
    <summary>Dados para nerds</summary>
    <pre>raf:v1;id=MAIL-0007;fam=email;st=ev;dt=20260710;prev=MAIL-0006;link=DRV-0001,GIT-0093;grid=nerd</pre>
  </details>
</div>
```

### Forma textual compatível com e-mail/calendário

```text
Revisar navegação semântica do Drive || raf:v1;id=MAIL-0007;fam=email;st=rev;dt=20260710;grid=nerd
```

Em Gmail/Calendar, preferir subject/title com trailer textual. Em documentos HTML próprios, usar `data-*`, `<details>` e/ou `<span hidden>`.

## 10. Cores e labels

Cores não carregam toda a semântica. Elas funcionam como sorter visual.

| Cor sugerida | Uso |
|---|---|
| azul | evidência/documento |
| verde | concluído/validado |
| amarelo | hipótese |
| vermelho | sensível/risco |
| cinza | gap/TOKEN_VAZIO |
| roxo | pesquisa profunda |
| laranja | ação pendente |

Labels Gmail e calendários podem repetir o status, mas a fonte técnica primária é o trailer.

## 11. Cadeia de custódia leve

Cada bloco pode referenciar o anterior:

```text
MAIL-0001 → CAL-0001 → DRV-0001 → GIT-0001 → MAIL-0002
```

Campos usados:

```text
id atual
prev id
thread id
event id
Drive id
Git commit SHA
hash do corpo
hash dos anexos
dados para nerds
```

Isto não exige blockchain pesado no início. A cadeia nasce como trilha auditável. Depois pode ser endurecida com SHA-256, assinatura e ledger versionado.

## 12. Parser mínimo

Pseudocódigo:

```python
def parse_raf_tail(text):
    if " || " not in text:
        return {"visible": text, "tail": None}
    visible, tail = text.rsplit(" || ", 1)
    fields = {}
    for part in tail.split(";"):
        if ":" in part and part.startswith("raf:"):
            fields["raf"] = part.split(":", 1)[1]
        elif "=" in part:
            k, v = part.split("=", 1)
            fields[k.strip()] = v.strip()
    return {"visible": visible.strip(), "tail": fields}
```

## 13. Regras de segurança

- Não colocar segredo, token, senha ou dado sensível no subject.
- Para material sensível, usar `st=sens` e apontar para cofre/arquivo seguro.
- Hash curto pode aparecer no subject; hash completo deve ficar no corpo/ledger.
- HTML oculto não é controle de segurança; é apenas organização visual.
- `Dados para nerds` é depuração/inspeção, não autenticação.
- A fonte de verdade deve ser o bloco auditável: e-mail, evento, anexo, Drive ID, Git SHA, hash e ledger.

## 14. Invariante

```text
Humano entende sem ruído.
Máquina rastreia sem adivinhar.
Dados para nerds aparecem só quando chamados.
```

## 15. Relação com RAFAELIA

O Tail Protocol implementa em escala cotidiana a invariante de preservação de relações:

```text
memória → relação → evidência → governança → execução → nova memória
```

Ele também respeita a separação:

```text
símbolo ≠ hipótese ≠ prova ≠ código ≠ log ≠ execução
```

## 16. Próximos passos

1. Criar parser Python/JS mínimo.
2. Criar fixtures para subject, calendar title, HTML e trailer expandido.
3. Validar `grid=nerd` e `dbg=1` no schema.
4. Criar relatório HTML com cards e grid `Dados para nerds`.
