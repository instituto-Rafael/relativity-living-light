# RLL Edge Science — Água, Geoquímica, Nitrogênio, Biologia e Operadores Ω

Status: `structural_and_scientific_custody_contract`  
Claim gate: `claim_allowed=false`  
Training gate: `training_allowed=false`  
Dependências: **Python stdlib; nenhum workflow/YML novo**

## 1. Delta desta evolução

A matriz multifísica anterior preservou eletricidade, magnetismo, spray, calor, pele, respiração, coração, acústica e segurança. Esta evolução acrescenta a cadeia que começa antes da torneira:

```text
bacia / nascente / solo / rocha / uso do solo
→ fluxo e tempo de residência
→ pH / oxigênio / redox / matéria orgânica
→ especiação de ferro, manganês e nitrogênio
→ partículas, coloides e biofilmes
→ microbiologia
→ tratamento
→ exposição
→ medição
→ token semântico
→ operador matemático
→ visualização
→ claim gate
→ receipt longitudinal
```

Invariantes:

```text
observável ≠ composição
cor ≠ identificação mineral
origem natural ≠ potabilidade
contexto de mata ≠ concentração de nitrato
nome do filtro ≠ capacidade comprovada
semelhança vetorial ≠ causalidade
```

## 2. Água avermelhada, fundo vermelho e lodo

Coloração avermelhada ou alaranjada é compatível com ferro oxidado, mas também pode envolver partículas minerais, corrosão, biofilmes de organismos oxidantes de ferro, matéria orgânica ligada a metais e sedimentos.

```text
cor vermelha → hipótese de ferro
cor vermelha ↛ concentração
cor vermelha ↛ espécie mineral
cor vermelha ↛ potabilidade
```

O Brasil estabelece VMP organoléptico de ferro de `0,3 mg/L` na Portaria GM/MS 888/2021. A régua não substitui caracterização química, microbiológica e sanitária.

## 3. Água de mata e ciclo do nitrogênio

A presença de mata não autoriza declarar nitrato elevado. A concentração depende de deposição atmosférica, mineralização da matéria orgânica, nitrificação, desnitrificação, oxigênio dissolvido, redox, fertilização, esterco, fossas, esgoto, chuva, erosão, fluxo e tempo de residência.

As espécies permanecem separadas:

\[
N_{total}\neq NH_4^+-N\neq NO_2^--N\neq NO_3^--N
\]

Caminho candidato:

```text
nitrogênio orgânico
→ amonificação/mineralização
→ amônio
→ nitrificação
→ nitrito
→ nitrato
→ desnitrificação
→ N2 / N2O
```

A sequência real depende do ambiente e não é uma esteira obrigatória em todo ponto e instante.

## 4. Nitrato, nitrito e padrão brasileiro

Na Portaria GM/MS 888/2021:

```text
nitrato como N: 10 mg/L
nitrito como N:  1 mg/L
```

Além dos limites individuais:

\[
\frac{NO_3^--N}{10}+\frac{NO_2^--N}{1}\le1
\]

A relação exige análise válida. Não se aplica a valor inferido por cor, gosto, aplicativo, tira não validada ou resultado sem unidade.

A formulação “prejudicial e acumulativo” precisa de precisão: nitrato não é tratado aqui como substância que simplesmente se bioacumula indefinidamente. O risco depende de dose, conversão a nitrito, população suscetível e exposição. Bebês são especialmente vulneráveis à metemoglobinemia associada ao nitrito.

## 5. A “pedra vulcânica branca”

O nome popular pode representar materiais diferentes:

- zeólita natural;
- pedra-pomes;
- perlita;
- calcita;
- cerâmica porosa;
- vidro expandido;
- mídia comercial composta ou modificada.

Sem mineralogia e ficha técnica:

```text
white_volcanic_stone = TOKEN_VAZIO_MATERIAL_IDENTITY
```

Zeólitas naturais possuem estrutura com carga negativa e são conhecidas sobretudo por troca de cátions, inclusive amônio. Nitrato é ânion. A literatura registra que a zeólita natural, sem modificação, não adsorve nitrato eficientemente por padrão; modificações de superfície podem criar afinidade por ânions.

```text
remove amônio ≠ remove nitrato
zeólita natural ≠ resina aniônica
mídia branca ≠ desempenho comprovado
```

Rotas candidatas para nitrato incluem troca aniônica, osmose reversa, eletrodiálise e desnitrificação biológica controlada. Cada uma exige controle de rejeito, concentrado, salmoura, breakthrough, microbiologia e regeneração.

## 6. Tratamento de ferro e manganês

A seleção depende de Fe(II)/Fe(III), pH, oxigênio, matéria orgânica, manganês e carga particulada. Rotas usuais incluem:

```text
aeração ou outro oxidante
→ conversão de Fe(II) solúvel
→ precipitação de Fe(III)
→ sedimentação/filtração
```

Também podem entrar mídia catalítica, greensand/dióxido de manganês, troca iônica em condições específicas e controle de corrosão quando a fonte é a instalação.

Remover cor não prova que nitrato, nitrito, microrganismos ou outros contaminantes foram removidos.

## 7. Ferver não remove nitrato

Fervura pode inativar muitos microrganismos, mas não remove nitrato. Como a água evapora e o nitrato permanece, a concentração pode aumentar. O sistema bloqueia:

```text
BOILING_REMOVES_NITRATE
```

## 8. Tokenização científica contextual

A unidade mínima deixa de ser palavra ou número solto:

\[
\tau_i=\langle
literal,papel,fonte,amostra,tempo,local,escala,fase,
gradeza,unidade,valor,incerteza,método,LD,LQ,estado,
falsificador,parent\_hash
\rangle
\]

Exemplo de observável:

```json
{
  "literal": "fundo avermelhado",
  "semantic_role": "OBSERVABLE",
  "quantity": "color_state",
  "value_or_token_vazio": "RED_ORANGE",
  "unit": "categorical",
  "epistemic_state": "OBSERVED",
  "claim_block": "COLOR_IS_NOT_MINERAL_IDENTIFICATION"
}
```

Exemplo de constituinte ainda não medido:

```json
{
  "literal": "ferro total",
  "semantic_role": "CONSTITUENT",
  "quantity": "iron_total_mg_L",
  "value_or_token_vazio": "TOKEN_VAZIO_UNMEASURED",
  "unit": "mg/L",
  "epistemic_state": "TOKEN_VAZIO_UNMEASURED"
}
```

Os tokens se relacionam; um não substitui o outro.

## 9. Vetor multifísico e biogeoquímico

\[
\mathbf W(t,\mathbf x)=[
T,p,Q,\tau_r,pH,Eh,DO,EC,Turb,
Fe_T,Fe^{2+},Fe^{3+},Mn_T,
NO_3-N,NO_2-N,NH_4-N,TN,DOC,
E.coli,Coliformes,B,\nabla B,d_p,\chi_p]
\]

Cada componente carrega unidade, método, timestamp, validade, incerteza, limite de detecção, limite de quantificação, fonte e estado epistemológico.

```text
below_detection ≠ zero
not_sampled ≠ below_detection
not_applicable ≠ token_vazio_unknown
```

## 10. Operadores protegidos

### Derivada

\[
D_i=\frac{y_{i+1}-y_i}{x_{i+1}-x_i}
\]

Mede mudança por eixo declarado, como `mg/L por hora`, `mg/L por metro` ou `NTU por mm de chuva`. Não prova causa.

### Antiderivada

\[
Y(x)=Y(x_0)+\int_{x_0}^{x}D(\xi)d\xi
\]

Exige condição de contorno. Sem ela, existe uma família de origens possíveis.

### Reversiva

\[
E_{rec}=RMSE(\mathbf y,\hat{\mathbf y}_{reverse})
\]

Mede perda de reconstrução; não prova origem única.

### Recíproca

Quando `x=0`, o motor abstém:

```text
ABSTAIN_TOKEN_VAZIO_DOMAIN
```

### `log1p` roundtrip

\[
z=\log(1+x),\qquad x'=e^z-1
\]

Mede perda numérica, não verdade física.

### Log–log

\[
\log y=a+b\log x
\]

Uma reta log–log é candidata a lei de potência. Exige `x>0`, `y>0`, modelo concorrente, resíduos, AIC, faixa de escala, mecanismo e teste fora da amostra.

### Log de log

\[
\log(\log x)
\]

Exige `x>1` e finalidade declarada. Serve para exploração multiescala; não cria mecanismo.

## 11. Visualização holística sem colapso

A visualização holística é um conjunto de vistas com os mesmos IDs:

1. mapa da bacia: fonte, geologia, uso do solo e risco sanitário;
2. Sankey: N orgânico → NH4 → NO2 → NO3 → N2;
3. especiação: Fe(II)/Fe(III), dissolvido/coloidal/particulado;
4. série temporal: chuva, vazão, turbidez, ferro, nitrato e microbiologia;
5. mapa pH–Eh com limites declarados;
6. curva de breakthrough entrada/saída;
7. grafo claim–evidência–falsificador;
8. mapa de discrepância instrumento/instalação/modelo;
9. painel de `TOKEN_VAZIO` tipado;
10. árvore antiderivada retornando à amostra, método e origem.

Uma vista não apaga a outra.

## 12. Falsificabilidade

| Claim candidato | Falsificador mínimo |
|---|---|
| Cor vermelha causada principalmente por ferro | análise demonstra ferro baixo e outra causa dominante |
| Água da mata possui nitrato alto | amostragem sazonal certificada permanece baixa |
| Mídia branca remove nitrato | curva entrada/saída sem remoção ou breakthrough imediato |
| Mídia é zeólita | XRD/mineralogia incompatível |
| Filtro de ferro torna água potável | nitrato, nitrito ou microbiologia fora do padrão após filtração |
| Ímã desviou partículas de ferro | água destilada desvia de modo equivalente ou partículas magnéticas não são encontradas |
| Reta log–log demonstra lei de potência | modelo concorrente generaliza melhor ou expoente não se mantém |

Estados permitidos:

```text
SUPPORTED_ONLY
REFUTED_ONLY
BOTH
NEITHER
TOKEN_VAZIO
```

## 13. Excelência operacional para Edge Science

Ciência de fronteira recebe mais rastreabilidade, não menos rigor:

```text
pergunta
→ claim tipado
→ origem
→ estado da arte
→ mecanismo concorrente
→ modelo de medição
→ pré-registro
→ controles positivo e negativo
→ calibração
→ experimento
→ resultado negativo preservado
→ sensibilidade
→ reprodução
→ claim gate
→ receipt
```

```text
novidade ≠ verdade
anomalia ≠ nova física
resíduo ≠ descoberta
p > alfa ≠ ausência de efeito
não refutado ≠ provado
modelo bonito ≠ mecanismo
```

Promoção:

\[
P=O\land U\land M\land D\land Q\land A\land F\land R\land S
\]

- `O`: origem;
- `U`: unidades;
- `M`: método;
- `D`: dado;
- `Q`: QA/QC;
- `A`: alternativas;
- `F`: falsificador;
- `R`: reprodução;
- `S`: segurança.

Sem qualquer termo:

```text
claim_allowed=false
```

## 14. Gate experimental seguro

### A — inspeção e laboratório

- inspeção sanitária da nascente/bica;
- amostragem por laboratório habilitado;
- coliformes e *E. coli*;
- nitrato, nitrito e amônio;
- ferro e manganês;
- pH, turbidez e condutividade;
- método, LD, LQ e incerteza.

### B — repetição sazonal

- chuva/seca;
- vazão;
- oxigênio dissolvido;
- redox;
- carbono orgânico;
- duplicatas e branco.

### C — caracterização e tratamento

- Fe(II)/Fe(III);
- particulado/dissolvido;
- mineralogia da mídia e do sedimento;
- influente/efluente;
- curva de breakthrough;
- rejeito e regeneração.

### D — ciência de fronteira

- operadores matemáticos;
- modelos concorrentes;
- DAG causal candidato;
- controles negativos;
- teste fora da amostra;
- replicação independente.

Nenhum estágio autoriza consumo humano sem atendimento regulatório e avaliação sanitária.

## 15. Artefatos executáveis

```text
data/manifests/rll_edge_science_water_chem_bio.v1.json
data/fixtures/rll_edge_science_water_operators.v1.json
scripts/rll_edge_science_operators.py
scripts/validate_rll_edge_science_water_matrix.py
tests/test_rll_edge_science_water_matrix.py
```

```bash
python3 scripts/validate_rll_edge_science_water_matrix.py --write-report
python3 -m unittest tests/test_rll_edge_science_water_matrix.py
```

## 16. Referências-raiz

- Ministério da Saúde. Portaria GM/MS nº 888/2021.  
  https://bvsms.saude.gov.br/bvs/saudelegis/gm/2021/prt0888_24_05_2021_rep.html
- WHO. Guidelines for drinking-water quality, 2026.  
  https://www.who.int/publications/i/item/9789240121225
- WHO. Nitrate/nitrite fact sheet.  
  https://www.who.int/publications/m/item/chemical-fact-sheets--nitrate-nitrite
- CDC. Guidelines for Testing Well Water.  
  https://www.cdc.gov/drinking-water/safety/guidelines-for-testing-well-water.html
- USGS. Reddish drinking-water color and iron.  
  https://www.usgs.gov/faqs/what-can-be-causing-our-drinking-water-have-a-reddish-color
- USGS. Oxidation/Reduction.  
  https://www.usgs.gov/mission-areas/water-resources/science/oxidationreduction-redox
- USGS. Nitrate transport and redox gradients.  
  https://www.usgs.gov/publications/influence-redox-gradients-nitrate-transport-landscape-groundwater-and-streams
- US EPA. Drinking-water treatment technologies.  
  https://www.epa.gov/sdwa/overview-drinking-water-treatment-technologies
- US EPA. Iron/manganese treatment survey guide.  
  https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P100XHB2.TXT
- Lu et al. Modified natural zeolites for anion removal. DOI `10.1039/D2EW00478J`.

## 17. Fechamento Ω

**F_ok**

- ferro, nitrogênio, microbiologia, tratamento, magnetismo, operadores e tokenização ficaram separados e ligados;
- a regulação brasileira foi incorporada;
- zeólita natural não foi promovida silenciosamente a removedor de nitrato;
- derivada, antiderivada, reversão, log–log e log(log) possuem domínio e falsificador;
- nenhum workflow/YML novo foi criado.

**F_gap**

- material da “pedra branca” não identificado;
- nenhuma amostra local certificada;
- nenhuma série sazonal;
- nenhuma curva de breakthrough;
- nenhum receipt independente.

**F_next**

```text
inspeção sanitária
→ amostragem certificada
→ série sazonal
→ caracterização de mídia
→ tratamento entrada/saída
→ operadores
→ oposição
→ replicação
→ claim gate
```

> A bica é um canal, não um certificado. A cor é uma pista, não uma fórmula. O filtro é uma hipótese operacional até que a água entre, saia e deixe um recibo.
