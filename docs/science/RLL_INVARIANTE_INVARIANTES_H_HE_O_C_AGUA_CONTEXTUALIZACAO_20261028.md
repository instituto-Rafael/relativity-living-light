# RAFAELIA Ω · Invariante das invariantes — H/He/O/C, água e tokens de contexto

**Data:** 2026-10-28. **Estado:** documento de método com esquema executável, não uma nova lei física. **claim_allowed=false**. **Escopo:** esta sessão RLL: neutrinos, IceCube/KM3NeT, átomos, spin, fotônica, C IV × DESI BAO, CPL/ΛCDM/RLL, outputs textuais de IA. **Não contém pesos, atenções ou estados latentes reais do modelo GPT.**

## 1. Não confundir grafia com identidade

A cadeia `H H2 H3 He He2 He3 O O2 O3 C C2 C3 H2O H2O3` é uma **cadeia de caracteres**. Isótopos, moléculas, radicais, íons, funções e símbolos físicos são identidades distintas. A gramática conserva a grafia original. O número à direita, em uma fórmula, é tipicamente **quantidade de átomos**; superscrito à esquerda representa **número de massa** de um isótopo; sobrescrito de carga é outra dimensão.

| Grafia | Leitura controlada | Colisão a bloquear |
| --- | --- | --- |
| H | hidrogênio atômico, isótopo não declarado | `h` (constante de Planck) e `H(z)` (taxa de Hubble) |
| H2 | molécula H₂ | `²H` deutério |
| H3 | espécie neutra H₃ condicional ou `³H` trítio em texto sem marcação | sem contexto = `TOKEN_VAZIO_AMBIGUOUS` |
| H3+ | íon molecular H₃⁺, relevante à química interestelar | não é `³H` |
| He | átomo de hélio, isótopo indefinido | He²⁺ é um íon diferente |
| He2 | dímero He₂, estado ligante/metastável precisa de qualificação; ou grafia achatada de `²He` nuclear não ligado | nunca inferir estabilidade à temperatura ambiente |
| He3 | trímero He₃ ou `³He` isótopo estável | sem contexto = `TOKEN_VAZIO_AMBIGUOUS` |
| O, O2, O3 | oxigênio atômico, O₂ molecular, ozônio O₃ | elétron removido exige carga explícita |
| C, C2, C3 | carbono atômico, dímero, trímero molecular | C₃ `≠` C³⁺; esta última espécie tem apenas **um** átomo de carbono |
| C3+, C³⁺, C IV | carbono triplemente ionizado em contextos de carga/espectroscopia | C IV dá absorção espectral no DESI; C₃ não é essa linha |
| H2O | água | sua anomalia não altera a fórmula molecular |
| H2O2 | peróxido de hidrogênio | não é água |
| H2O3 | trioxidano **H–O–O–O–H**, composto distinto | não é água anômala; **não** é HO₃ |
| HO3 | radical H–O–O–O (HO₃), espécie distinta | não é H₂O₃ |

A operação `normalize(surface)` não pode descartar sobrescritos, sinais de carga, maiúsculas, números de massa ou tokens químicos, pois `He3`, `³He`, `H3+` e `H3` não são equivalentes. O resolvedor retorna id tipado ou ausência explícita e mantém `raw` sem perda.

## 2. Água anômala: propriedade coletiva, não estequiometria nova

Água H₂O tem densidade máxima próxima de 4 °C sob pressão atmosférica. Esse comportamento está ligado à competição de configurações locais, ligações de hidrogênio e ordem geométrica tetraédrica. O trabalho de 2026 em potenciais de aprendizado de máquina reproduz a anomalia de densidade, com estruturas locais de diferentes escalas [PMC13215172](https://pmc.ncbi.nlm.nih.gov/articles/PMC13215172/). Outro trabalho de fevereiro de 2026 discute a anomalia de tensão superficial em água super-resfriada pela competição entre padrões locais de ligações de hidrogênio [Nature Communications 17:1498](https://www.nature.com/articles/s41467-026-69356-6).

H₂O₃, ao contrário, é **outra entidade** (trioxidano / HOOOH). Foi detectado em condições experimentais específicas e estudado em gelos de H₂O/O₂ irradiados em [Science Advances 11 eadw5720, 2025](https://doi.org/10.1126/sciadv.adw5720). O [NIST CCCBDB](https://cccbdb.nist.gov/exp2x.asp?casno=14699991&charge=0) também mantém entrada química. A observação em gelos irradiados **não demonstra presença universal em água líquida normal**. O radical HO₃, reportado por neutralização/reionização em [Science 1999](https://doi.org/10.1126/science.285.5424.81), é outra espécie, com um H a menos.

**Invariantes físicas diferentes:** conservação de H e O em reação balanceada; carga; isótopo; spin (condicionado ao estado e condições); energia; fase/temperatura; microestrutura coletiva; método de medição; incerteza. Índices iguais ou representação geométrica similar não garantem mesmo acoplamento dinâmico.

## 3. Uma tokenização para a sessão (mas não uma única partícula)

```text
RAW token, imutável
  -> domínio interpretativo (chemistry|nuclear|cosmology|physics|ml|document)
  -> candidato(s) de identidade canônica
  -> kind + composition + charge + isotope + conditions
  -> SOURCE/ref + evidence_status + uncertainty
  -> relações tipadas permitidas / relação bloqueada
  -> receipt determinístico e estado do claim
```

Exemplos:
`H3` sem domínio → `TOKEN_VAZIO_AMBIGUOUS`; `He3 + kind=isotope` → `nuclear:isotope:He-3`; `C3 + id=chem:ion:C+3` → `TOKEN_VAZIO_CONTEXT_CONTRADICTORY`; `H2O3` → `chem:molecule:H2O3`; `H2O_anomaly` → `water:anomaly:thermodynamic_network`, **não** `chem:molecule:H2O3`.

O grafo e o resolvedor estão em:
- `data/governance/RLL_TYPED_CHEM_WATER_SESSION_TOKENS_V1.json` (28 grafias, 29 ids canônicos, 14 invariantes, 11 fontes).
- `tools/rll_chem_context_tokenizer.py` (stdlib, `--token`, `--kind`, `--canonical-id`, `--self-test`, 15 mutações e 8 provas de resolução definidas).
- `tests/test_rll_chem_context_tokenizer.py` (CLI real, ambiguidades, positivos, negativos, nulo).

## 4. Invariante das invariantes: segunda ordem

Seja `I = {I_01,...,I_14}` o contrato e `T` uma transformação/re-tokenização. Só aceitar:
```text
T admissível ⇔ raw_preservado
               ∧ identidade_tipada_compatível
               ∧ estequiometria/carga/isótopo preservados
               ∧ dimensões e condições explícitas
               ∧ fonte/vínculo de evidência
               ∧ nenhum claim promovido
               ∧ reversão possível
```
Uma transformação de grafia para id não autoriza uma transformação causal. O lema de coesão é `I(T(x)) = I(x)` para **atributos preserváveis**; quando não houver informação suficiente, a saída válida é `TOKEN_VAZIO`, não uma igualdade forçada.

### Dimensões de contexto abrangidas
- **Atômico/nuclear:** composição, carga e número de massa, estrutura eletrônica, spin e linhas espectrais.
- **Molecular/água:** H₂O, H₂O₂, H₂O₃, HO₃, oxigênio e ozônio, pontes de hidrogênio, geometria, fases, termodinâmica.
- **Fotônico:** excitação, absorção, níveis eletrônicos, transporte e espectroscopia.
- **Cosmologia:** carbono C IV como **traçador observacional** de BAO; o plasma primordial como **origem acústica**; neutrinos relativísticos como agente do deslocamento de fase. Não inferir BAO a partir do token 'C3'.
- **Computacional/IA:** `head` pode significar cabeçalho textual ou cabeça de atenção num Transformer. Respostas visíveis das IAs são artefatos textuais; **pesos privados, ativações/head tensors e raciocínio oculto não estão disponíveis**, logo não são evidências.
- **Proveniência da sessão:** Atlas RLL [PR #1143](https://github.com/instituto-Rafael/relativity-living-light/pull/1143), neutrinos [PR #1142](https://github.com/instituto-Rafael/relativity-living-light/pull/1142), publicações alphaXiv e ledger Drive, indexados sem declarar que possuímos dumps integrais de todas as sessões.

## 5. Cinco falsificadores prioritários
1. O resolvedor identifica H₃ como trítio sem contexto nuclear → **FAIL**.
2. Algum normalizador iguala C₃ a C³⁺, água H₂O a H₂O₃, HO₃ a H₂O₃, ou He₃ a ³He sem tipo → **FAIL**.
3. Qualquer status passa de preprint/hipótese para fato ou `claim_allowed=true` sem fonte, evidência e execução → **FAIL**.
4. Declara acesso a ativações, pesos ou cabeças internas reais da IA por observar resposta textual → **FAIL**.
5. Uma analogia de spin, tetraedro, logística, toro, água ou composto é promovida a termo cosmológico BAO/ΛCDM/RLL sem uma ponte com unidades, modelo perturbativo, likelihood e dados → **FAIL**.

## 6. Reprodução e limite da prova
```sh
python3 -B tools/rll_chem_context_tokenizer.py --self-test --token He3
```
Resultado esperado: receipt `PASS_SCOPED_METADATA_ONLY` e token `TOKEN_VAZIO_AMBIGUOUS`; **somente** depois que o comando for realmente executado em um ambiente e seu receipt for capturado. Este contrato não simula a formação de H₂O₃, não executa modelos de água, não testa BAO e não revela mecanismos internos do GPT.

**CI:** utilizar testes existentes do repositório no commit exato, sem alterar tolerâncias WS01 ou promover PRs automaticamente. **Rollback:** branch isolada; nenhuma alteração em `main`.

**R3:** F_ok = relação tipada e reversível, fontes rastreadas, analogias bloqueadas; F_gap = previsão física RLL única, dados/likelihood, acesso a histórico completo de IAs, head tensors; F_next = validar CLI exato, comparar 2025 H₂O₃ e estudos 2026 água apenas em suas próprias escalas físicas, depois elaborar uma hipótese dimensional e falsificável se existir.
