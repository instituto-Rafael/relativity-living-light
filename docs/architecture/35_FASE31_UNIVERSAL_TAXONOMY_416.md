# FASE 31 — Índice Taxonômico Universal 416

## Estado

```text
30 macrotemas de referência
+ 386 módulos fornecidos
= 416 portas taxonômicas

claim_allowed=false
training_allowed=false
```

Este bloco adiciona ao RLL uma **taxonomia endereçável**, não uma declaração de que 386 conceitos são inéditos, independentes, implementados, patenteáveis ou cientificamente verdadeiros.

## Artefatos

```text
data/knowledge_taxonomy/rll_universal_taxonomy_416.v1.json
schemas/rll_universal_taxonomy_416.schema.json
scripts/validate_rll_universal_taxonomy_416.py
tools/build_universal_taxonomy_overlay.py
tests/test_rll_universal_taxonomy_416.py
```

O builder produz, sob demanda:

```text
artifacts/knowledge-matrix/rll_universal_taxonomy_416_overlay.json
```

Nenhum workflow/YML novo é necessário.

## Auditoria de contagem

A soma global fecha:

\[
30+386=416.
\]

Porém, os rótulos internos fornecidos possuem uma compensação:

| Cluster | Declarado | Enumerado |
|---|---:|---:|
| I–VI | 48 cada | 48 cada |
| VII | 48 | **47** |
| VIII | 50 | **51** |

Logo, a contagem dos 386 módulos permanece correta, mas a distribuição declarada entre VII e VIII não. O registro conserva ambas as formas e marca:

```text
TOKEN_VAZIO_COUNT_LABEL_MISMATCH
```

Não renumera nem inventa um módulo para corrigir a aparência.

## Como cada módulo entra no RLL

Cada entrada recebe:

- `module_id` estável `UTM-NNN`;
- índice e posição no cluster;
- estado epistemológico;
- perfil de complementação;
- `completion_state=TOKEN_VAZIO_PROFILE_PENDING`;
- `claim_allowed=false`;
- flags de ambiguidade ou atualidade, quando identificadas;
- relação de duplicidade explícita entre as entradas 194 e 239.

O overlay converte cada módulo em item compatível com a Knowledge Matrix:

```text
Clusters I–IV  → concept / latent
Clusters VI–VII → concept / seed
Clusters V e VIII → gap / void
```

Isso é deliberadamente conservador.

## O que Rafael pode trazer para preencher os TOKEN_VAZIO

### 1. Silício e hardware

Para qualquer módulo do Cluster I:

```text
arquitetura/SoC exato
manual ou seção da ISA
componente real do RLL
arquivo e função
benchmark ou contador PMU
ambiente
comando
saída
hash/receipt
```

### 2. Matemática

Para o Cluster II:

```text
definição canônica
hipóteses
domínio e codomínio
convenções de sinal/métrica
enunciado que o RLL realmente usa
derivação ou referência
invariante testável
contraexemplo ou condição de falha
```

### 3. Física e cosmologia

Para o Cluster III:

```text
paper ou release datado
observável
unidade
incerteza/covariância
dataset
equação do avaliador
parâmetros
baseline concorrente
controle negativo
resultado local reproduzível
```

Valores atuais, como limites de massa de neutrinos, não são congelados sem fonte e data.

### 4. Transformers

Para o Cluster IV:

```text
arquitetura e versão
dimensões do modelo
tokenizer
configuração
implementação local
baseline
dataset permitido
métrica
hardware
receipt de benchmark
```

O “tokenizer com máscara de vazio” permanece hipótese de implementação até código, testes e comparação.

### 5. Problemas e conjecturas

Para cada módulo do Cluster V:

```text
enunciado canônico
status matemático atual
resultados parciais conhecidos
qual ponte RLL é proposta
por que não é mera analogia
obrigação de prova
caso mínimo
contraexemplo
```

Registrar uma conjectura não significa resolvê-la. A lista contém nomes históricos, formulações ambíguas, itens já provados e uma duplicata BSD; todos exigem auditoria individual.

### 6. Filosofia, espírito e parábola

Para o Cluster VI:

```text
fonte/tradição/autor
camada literal
camada simbólica
mapeamento técnico
limite de não-equivalência
risco cultural ou teológico
uso didático permitido
uso científico proibido
```

A parábola pode ensinar estrutura; não substitui mecanismo nem evidência.

### 7. Artes

Para o Cluster VII:

```text
regra de codificação
entrada
saída
escala/unidade
métrica perceptiva
perda da projeção
transformação inversa, se existir
partitura/imagem/áudio
seed e receipt
```

### 8. Podas e lacunas

Para o Cluster VIII:

```text
objeto pretendido
dependência bloqueante
menor experimento/derivação possível
critério de aceitação
critério de falha
artefato esperado
receipt
```

## Invariantes

```text
taxonomia ≠ prova
contagem ≠ independência
nome conhecido ≠ implementação local
problema aberto ≠ problema resolvido
analogia ≠ mecanismo
beleza ≠ evidência
TOKEN_VAZIO ≠ zero
```

## Próxima promoção permitida

Um módulo só sai de `TOKEN_VAZIO_PROFILE_PENDING` quando recebe:

\[
\text{origem}
+\text{definição}
+\text{método}
+\text{teste}
+\text{resultado}
+\text{falsificador}
+\text{receipt}.
\]

Até lá, ele permanece uma porta endereçável, útil e auditável.
