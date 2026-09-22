# Dobramento modular, régua de gaps e ponte nuclear — hipótese auditável

Data: 2026-09-02  
Estado: DOCUMENTED + DERIVED_MATHEMATICALLY  
Claim científico novo: não promovido  
claim_allowed: false

## 1. Intenção preservada

Investigar se recorrências produzidas por dobras modulares, diferenças de gaps e diferenças de segunda ordem formam invariantes de grafo úteis como linguagem matemática para comparar escalas físicas. A analogia com "fluido da dobradura do espaço-tempo" permanece hipótese heurística até existir um modelo dimensional, uma previsão quantitativa e um teste contra baseline.

## 2. Separação de camadas

- Base numérica: muda a representação do valor; por si só não muda o objeto matemático.
- Módulo: identifica valores por classes de congruência e cria uma topologia discreta circular.
- Dinâmica: um operador iterado, por exemplo D_m(x)=2x mod m.
- Física: requer unidades, leis dinâmicas, parâmetros observáveis e comparação com dados.
- Claim: nenhuma recorrência modular isolada demonstra gravidade quântica, curvatura física ou unificação.

## 3. Primeiro caso pedido: sete em base 20 e módulo 10

O valor sete é 7 em base 10 e também 7 em base 20. Dobrar o valor e reduzir módulo 10 produz:

```
(2 * 7) mod 10 = 4
```

A escrita de 14 decimal em base 20 depende do alfabeto adotado (por exemplo, um dígito para o valor 14). Essa grafia não altera o resultado numérico acima. Concatenar dígitos seria outra operação e não deve ser confundida com multiplicação por 2.

## 4. Operador de dobra e órbitas observadas

Defina:

```
D_m(x) = 2x mod m
```

Para m=56:

```
7  -> 14 -> 28 -> 0 -> 0
35 -> 14 -> 28 -> 0 -> 0
50 -> 44 -> 32 -> 8 -> 16 -> 32 ...
56 -> 0
70 -> 14 -> 28 -> 0
```

Resultados derivados:

- 0 é ponto fixo;
- 7, 35, 56 e 70 entram no atrator 0;
- 50 entra no ciclo 32 -> 8 -> 16 -> 32, período 3;
- 14 e 70 colapsam na mesma classe módulo 56;
- números distintos podem compartilhar a mesma cauda orbital.

Para m=10:

```
7 -> 4 -> 8 -> 6 -> 2 -> 4 ...
```

Há transitório de comprimento 1 e ciclo de período 4.

## 5. Régua das distâncias e distância das distâncias

Distância circular:

```
d_m(a,b) = min(|a-b|, m-|a-b|)
```

Para uma sequência x_k:

```
gap_k = d_m(x_k, x_(k+1))
delta_gap_k = gap_(k+1) - gap_k
curv_k = delta_gap_(k+1) - delta_gap_k
```

Para evitar sinal artificial causado pelo corte do círculo, deve-se também testar uma versão orientada:

```
signed_gap_k = wrap_to_half_interval(x_(k+1)-x_k, m)
```

A "curvatura da curvatura" pode ser operacionalizada como terceira ou quarta diferença discreta, mas seu significado físico é TOKEN_VAZIO até haver uma ação/Lagrangiana ou equação de movimento que a conecte a um observável.

## 6. Bases coexistentes

Uma família de bases B={b_1,...,b_r} fornece representações diferentes do mesmo inteiro. Uma família de módulos M={m_1,...,m_s} fornece coordenadas num toro discreto/produto:

```
Phi_M(n) = (n mod m_1, ..., n mod m_s)
```

Se os módulos forem coprimos, o Teorema Chinês dos Restos controla quando a coordenada conjunta identifica n módulo do produto. Se não forem coprimos, a compatibilidade exige congruências coerentes nos gcds.

Candidatos de estabilidade do grafo:

1. pontos fixos: D_m(x)=x;
2. ciclos: D_m^p(x)=x;
3. classes com mesma cauda orbital;
4. recorrências simultâneas em vários módulos;
5. invariância da matriz de distâncias sob mudança de base;
6. estabilidade de espectro do Laplaciano do grafo;
7. persistência sob perturbação do conjunto inicial ou do multiplicador.

## 7. Falsificadores matemáticos

A hipótese forte "há uma invariante física nova" falha se:

- os padrões forem inteiramente explicados por congruência, gcd, ordem multiplicativa e Teorema Chinês dos Restos;
- a troca de base não mudar nenhuma quantidade independente da representação;
- a estabilidade desaparecer sob pequenas perturbações não escolhidas após observar o resultado;
- não houver previsão quantitativa distinta de relatividade geral, mecânica quântica, teoria quântica de campos ou física nuclear padrão;
- o ajuste só funcionar depois de escolher módulos/números a posteriori.

Baseline obrigatório: grafo modular aleatório com mesmo número de nós/graus; operador afim x -> ax+c mod m; e permutações dos rótulos.

## 8. Ponte física — correções factuais

### Forças e partículas

Há quatro interações fundamentais reconhecidas: forte, fraca, eletromagnética e gravitacional. O Modelo Padrão descreve as três primeiras; gravidade não está incorporada nele como teoria quântica completa.

### Átomo e "camada 8 com 2 / 2 com 8"

Elétrons não percorrem elipses planetárias clássicas. Estados eletrônicos são orbitais quânticos descritos por números quânticos. A regra 2n^2 é capacidade máxima idealizada de uma camada principal, não uma órbita elíptica. "2 e 8" recorda preenchimento de camadas em átomos leves, mas não é regra universal suficiente para ordem energética em átomos multieletrônicos.

### Fusão do hidrogênio em hélio

Na cadeia próton-próton estelar, o balanço líquido é aproximadamente:

```
4 p -> He-4 + 2 e+ + 2 nu_e + energia
```

Dois prótons são convertidos em nêutrons por interação fraca durante a cadeia. Não são necessários cinco hidrogênios para produzir um hélio-4, nem sobra obrigatoriamente um hidrogênio. A energia vem principalmente da diferença de massa/energia de ligação.

### Fusão versus fissão

- Fusão: núcleos leves unem-se; até a região do ferro/níquel pode liberar energia por aumento da energia de ligação por nucleon.
- Fissão: um núcleo pesado divide-se em fragmentos mais ligados, liberando energia, nêutrons e radiação.
- Estrelas massivas não sustentam geração de energia por fusão de ferro da mesma maneira; o colapso do núcleo pode levar a supernova e remanescente compacto.

### Quando estrelas compactas/supernovas "se encontram"

Não existe um único resultado. Depende de massas, composição, momento angular e razão de massa:

- duas estrelas de nêutrons podem produzir ondas gravitacionais, explosão curta de raios gama, kilonova, material rico em elementos pesados e remanescente temporário ou buraco negro;
- estrela de nêutrons + buraco negro pode produzir ejeção/kilonova se houver ruptura tidal fora do horizonte; caso contrário, pouca matéria é ejetada;
- dois buracos negros formam normalmente um buraco negro maior, emitindo energia e momento angular em ondas gravitacionais;
- supernovas que apenas se sobrepõem no espaço não equivalem automaticamente a uma fusão de remanescentes.

A observação GW170817 liga fusão de estrelas de nêutrons a kilonova e nucleossíntese por captura rápida de nêutrons. O destino final preciso depende da equação de estado da matéria densa: TOKEN_VAZIO para qualquer evento não especificado.

## 9. Zero absoluto

Zero absoluto é 0 K, limite termodinâmico, não um "número que a matéria procura". Sistemas quânticos podem conservar energia/movimento de ponto zero no estado fundamental; isso não é movimento térmico. Portanto:

```
temperatura -> 0 K
```

não implica, em geral:

```
energia total -> 0
```

## 10. Programa mínimo de teste

Entrada inicial: S={7,14,35,50,56,70}; módulos M={7,10,14,20,35,50,56,70}; operadores D_(m,a,c)(x)=a*x+c mod m.

Para cada combinação:

1. enumerar órbitas até recorrência;
2. registrar transitório, período e atrator;
3. calcular gaps circulares, diferenças segunda/terceira/quarta;
4. construir grafo direcionado e Laplaciano;
5. extrair componentes, ciclos, espectro e automorfismos;
6. comparar com baselines permutados;
7. aplicar correção por testes múltiplos;
8. separar invariância de valor de coincidência de grafia em bases diferentes.

Critério de avanço para física: formular uma quantidade dimensional e uma previsão nova, pré-registrada, que diferencie o modelo de um baseline físico conhecido.

## 11. Fontes primárias/institucionais registradas

- Acharya et al., Solar Fusion III (2025), revisão da física nuclear de queima de hidrogênio: https://doi.org/10.1103/8lm7-gs18
- CERN, The Standard Model: https://home.web.cern.ch/science/physics/standard-model
- NIST, Kelvin introduction e movimento de ponto zero: https://www.nist.gov/si-redefinition/kelvin-introduction
- NIST, energia vibracional de ponto zero: https://cccbdb.nist.gov/thermox.asp
- LIGO Scientific Collaboration, GW170817 multimessenger summary: https://ligo.org/science-summaries/gw170817mma/
- LIGO Scientific Collaboration, detection page for GW170817: https://ligo.org/detections/gw170817/

## 12. Gate RLL

Claim: a régua modular multi-base revela o fluido físico da dobra do espaço-tempo.  
Classe atual: NARRATIVE + MATHEMATICAL_HYPOTHESIS.  
Evidência matemática: exemplos derivados e reprodutíveis, ainda sem implementação anexada.  
Evidência física: TOKEN_VAZIO.  
Baseline/métrica: definidos, ainda não executados.  
Falsificador: seção 7.  
claim_allowed: false.  
F_next: implementar o enumerador determinístico e comparar invariantes contra baselines antes de qualquer ponte com observações RLL/cosmológicas.
