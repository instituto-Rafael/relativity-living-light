# 24 — ΣE, fissão nuclear e acoplamento matéria↔campo

**Status:** canônico complementar / claim-gated  
**Data:** 2026-08-24  
**Função:** formalizar a leitura `E = mc² → fissão → radiação → matéria/campo` sem promover analogia a evidência.

## 0. Estados epistemológicos

- `[E]` — física estabelecida / identidade contábil bem definida.
- `[C]` — conexão ou modelagem condicionada ao sistema físico.
- `[H]` — hipótese RLL/RAFAELIA a testar.
- `[VAZIO]` — falta estado, observável, dado ou falsificador suficiente.

Regra local:

```text
massa residual ≠ defeito de massa ≠ energia radiada ≠ prova de entrelaçamento
```

## 1. Invariante físico: balanço total de energia [E]

Para um evento nuclear isolado, a leitura segura é conservação de energia total:

```math
\Sigma E_{in}=\Sigma E_{out}.
```

Uma decomposição útil para fissão é

```math
M_i c^2 + K_i
=
\sum_j m_j c^2
+
\sum_j K_j
+
E_{rad}
+
E_{other}.
```

onde `M_i` representa a massa de repouso total do estado inicial; `m_j` as massas de repouso dos produtos finais massivos; `K` os termos cinéticos; `E_rad` os canais radiativos; e `E_other` outros canais necessários ao fechamento do balanço.

Definindo o defeito de massa da reação:

```math
\Delta m = M_{rest,in} - \sum_j m_{j,rest},
```

segue, para o valor-Q da reação,

```math
Q = \Delta m\,c^2.
```

### Interpretação

Na fissão nuclear, **a massa de repouso não é toda convertida em energia liberada**. A maior parte permanece como massa de repouso dos fragmentos e demais produtos massivos. A energia liberada corresponde à diferença entre a massa de repouso total inicial e a soma apropriada das massas de repouso finais, respeitando o balanço completo.

Portanto:

```text
M_res := Σ massa-de-repouso dos produtos finais massivos
Δm    := M_rest,in − M_res  (na contabilidade apropriada da reação)
Q     := Δm c²
```

`M_res` não é "massa que falhou em virar energia"; é o setor de massa de repouso do estado final.

## 2. Semântica canônica de ΣE no RLL [E/C]

Neste documento, `ΣE` significa **ledger de energia total por evento**:

```math
\Sigma E
=
E_{rest}
+
E_{kin}
+
E_{rad}
+
E_{field/other},
```

com os setores explicitados conforme o problema físico.

`ΣE` não é uma nova lei e não substitui `E=mc²`. Ele funciona como operador de contabilidade que impede que massa de repouso, energia cinética, radiação e termos de campo sejam misturados semanticamente.

Nó semântico:

```text
E=mc² → Δm c² → Q
              ↘
             ΣE_event = fechamento energético
```

## 3. Fissão, radiação e campo [E/C]

A cadeia já presente no corpus RAFAELIA — `Nuclear Energy → Radiation → Heat & Plasma → Toroidal Vortex` — deve ser tipada assim:

```text
liberação nuclear → canais cinéticos/radiativos       [E]
radiação/partículas → deposição de energia / calor    [E/C]
energia depositada → ionização/plasma                 [C]
plasma → organização toroidal                         [H/C]
```

O último elo requer geometria, condições de contorno e dinâmica específicas. A existência de vórtices ou configurações toroidais em outros sistemas não prova organização toroidal universal.

## 4. Matéria ↔ campo: correlação não é automaticamente entrelaçamento [E/H]

Interações entre graus de liberdade materiais e campos podem produzir correlações e, em regimes quânticos apropriados, estados entrelaçados. Porém, **massa residual de uma reação nuclear, sozinha, não é testemunha de entrelaçamento**.

Definimos a hipótese de trabalho:

```text
H_MF := a dinâmica matéria↔campo de um processo especificado
        produz correlação quântica não-separável mensurável
        entre uma bipartição material M e uma bipartição de campo F.
```

A informação mútua pode quantificar correlação total:

```math
I(M:F)=S(\rho_M)+S(\rho_F)-S(\rho_{MF}),
```

mas `I(M:F)>0` não prova, por si só, entrelaçamento. A promoção de `H_MF` exige um critério de não-separabilidade apropriado ao estado e à bipartição — por exemplo, negatividade, testemunha de entrelaçamento, critério de separabilidade ou teste equivalente adequado ao sistema.

### Estado atual de H_MF

```text
bipartição M|F definida?          TOKEN_VAZIO
Hamiltoniano/dinâmica definida?   TOKEN_VAZIO
estado ρ_MF especificado?         TOKEN_VAZIO
witness de entrelaçamento?        TOKEN_VAZIO
dado experimental/simulado?       TOKEN_VAZIO
claim_allowed                      false
```

Assim, a formulação preserva a intuição `matéria ↔ campo`, mas impede o salto lógico `massa restante → entrelaçamento`.

## 5. Ponte com o material de som [E/C]

O material canônico de ondas do RLL separa onda acústica, dinâmica neural e amplitude quântica. A ponte legítima entre som e radiação é, primeiro, **espectral/matemática**:

```math
x(t) \leftrightarrow X(f),
```

com frequência, fase, espectro, coerência e resposta de sistemas como ferramentas comuns.

Fisicamente:

```text
som no ar       = onda mecânica de pressão em meio material
radiação EM     = excitação/propagação do campo eletromagnético
```

Portanto:

```text
SOUND_SPECTRAL_BRIDGE = [E/C]
SOUND_IS_RADIATION_EM  = false
```

Uma ligação física som↔radiação só pode ser promovida quando houver mecanismo concreto de transdução ou acoplamento (por exemplo, eletromecânico, optomecânico, piezoelétrico ou outro sistema explicitamente modelado).

## 6. Grafo não-ordinal / Memória N

Este nó segue a orientação de memória não-ordinal: centro + eixos + relações, em vez de capítulo isolado.

```text
                        ┌→ M_res (produtos massivos)
estado nuclear inicial ─┤
                        ├→ K_products
                        ├→ E_rad
                        └→ E_other/field
                               │
                               ▼
                          ΣE_out = ΣE_in

Δm = M_rest,in − Σm_rest,out
Q  = Δm c²

matéria M ↔ campo F
      │
      └→ H_MF [TOKEN_VAZIO até witness]

frequência/espectro
   ├→ acústica
   └→ radiação EM
       (mesma matemática espectral possível; setores físicos distintos)
```

Identificadores do nó:

```text
SIGMA_E_EVENT
M_RES
DELTA_M_FISSION
Q_MASS_DEFECT
E_RAD
H_MF
SOUND_SPECTRAL_BRIDGE
```

## 7. Gate de falsificabilidade para H_MF

Para sair de `[VAZIO]`, uma implementação futura deve fornecer, no mínimo:

1. reação ou sistema físico específico;
2. graus de liberdade e bipartição `M|F`;
3. Hamiltoniano ou mapa dinâmico;
4. estado inicial e estado final/densidade reduzida;
5. observável ou witness de entrelaçamento;
6. baseline separável/clássico;
7. predição quantitativa e incerteza;
8. dado experimental ou simulação reproduzível com hashes.

Critério de rejeição mínimo:

```text
se o witness não distingue H_MF de um estado separável
ou se o efeito desaparece sob controles adequados,
H_MF não é promovida.
```

## 8. Claim boundary

Permitido:

```text
A fissão preserva massa de repouso nos produtos finais e libera energia associada ao defeito de massa.
ΣE é usado aqui como contabilidade do balanço energético total.
Interações matéria-campo podem produzir correlações e, em certos regimes, entrelaçamento.
O RLL registra H_MF como hipótese falsificável ainda não demonstrada neste contexto.
```

Não permitido:

```text
A massa que sobra prova entrelaçamento matéria-campo.
Toda massa não convertida permanece como energia escondida no campo.
Som e radiação eletromagnética são o mesmo fenômeno.
A cadeia nuclear→plasma→toro prova o RLL.
```

## 9. Proveniência interna

Este nó cruza:

- material Drive que relaciona `E=mc²`, energia nuclear, radiação, calor/plasma e geometria toroidal;
- `docs/canonicos/17_ONDA_VERBO_FISICA_NEURO_LINGUAGEM.md`, que separa ondas físicas e analogias;
- `docs/CONVERGENCIA_NUCLEAR_CHRYSOPOEIA_MAPA_ROTAS.md`, que já impõe fronteira de claim para mecanismos nucleares;
- `rll_equation_registry.yml`, como registro operacional de equações;
- `docs/RLL_TRACEABILITY_MAP.md`, como mapa de responsabilidade/evidência.

## 10. Síntese

```text
E=mc² não diz "toda massa vira energia".
Fissão: Δm mede o defeito; M_res permanece nos produtos; Q=Δm c².
ΣE fecha o evento sem misturar setores.
matéria↔campo é uma interação física; entrelaçamento exige witness.
som↔radiação compartilha ferramentas espectrais, não identidade física.
TOKEN_VAZIO protege exatamente a parte ainda não demonstrada.
```
