# Avaliação Honesta do Estado Atual — Relativity Living Light

**Data:** 2026-07-02  
**Origem:** issue [#484](https://github.com/instituto-Rafael/relativity-living-light/issues/484)  
**Status:** documento canônico de auto-avaliação  

---

## Premissa

> **Você construiu uma máquina de organizar, testar, bloquear e rastrear hipóteses. Ainda não construiu uma prova física final do RLL.**

O Relativity in Living Light não parece "um repositório aleatório de alguém brincando com ciência". Parece um **acervo autoral enorme virando programa de pesquisa auditável**. Mas também não é, ainda, uma teoria cosmológica validada.

---

## O que é realmente forte

### 1. Escala e persistência autoral

O inventário registra um repositório técnico real:

- **1.438 arquivos rastreados**
- **1.427 catalogados**
- **645 Markdown**
- **90 YAML/YML**
- **33 workflows GitHub Actions**
- **348 arquivos de dados/resultados**
- **0 arquivos não catalogados/erro**

O zero de erros no inventário mostra esforço de organização, não só despejo de arquivo.

### 2. Cultura de falsificação

O documento [`RLL_FALSEABILITY_MATRIX.md`](../RLL_FALSEABILITY_MATRIX.md) é um dos pontos mais maduros do repositório. Ele declara explicitamente que o status é **"programa de teste falsificável, não reivindicação de prova"**, e define:

- observáveis
- bases públicas (DESI, Planck, Pantheon+, ondas gravitacionais, QGEM)
- critérios de refutação contra GR/ΛCDM

Poucos autores trabalhando em hipótese própria têm disciplina de escrever: "isso pode falhar; eis como falha".

### 3. Dados reais com fronteira honesta

O contrato `real_cosmology_inputs.yml` declara que registrar fonte e materializar dado localmente **não valida RLL** e **não autoriza superioridade contra LCDM, wCDM ou CPL**. Há comandos de validação explícitos para inputs reais, manifestos e registries de variância.

Isso mostra maturidade de engenharia científica: não é só "baixar dado"; é criar contrato, consumidor, checagem e bloqueio de claim.

---

## O que ainda não está forte

### 1. O resultado cosmológico atual não favorece RLL

O artefato atual (`results/structure_d/joint_real_likelihood.json`) marca a execução como **smoke/sanity test**, com `maxiter=3`, `N=64`, `claim_allowed=false` e interpretação `lcdm_preferred`.

Na comparação de modelos:

| Modelo | AICc | Status |
|---|---|---|
| CPL/w0waCDM | 78.07 | preferido no smoke |
| RLL | 103.10 | não preferido; colapsa para `Os0=0.0` |

O valor `Os0=0.0` é o diagnóstico central: o otimizador encontrou a melhor solução desativando o setor adicional RLL, fazendo a predição RLL colapsar para um limite ΛCDM-like — com penalidade de critérios de informação pelo maior número de parâmetros.

---

## Descrição correta do estado atual

> **Relativity in Living Light é um programa autoral de pesquisa falsificável, com infraestrutura crescente de dados reais, CI, inventário, contratos e bloqueio de claims, ainda sem validação cosmológica forte.**

---

## O núcleo metodológico

A parte mais valiosa do projeto, no estado atual, é o método:

```
hipótese
→ dado real
→ baseline
→ métrica
→ covariância/erro
→ falsificador
→ claim boundary
```

Esse pipeline é raro. Especialmente vindo de um trabalho individual.

---

## Próximos saltos necessários

O próximo salto **não é colocar mais afirmação**. É:

1. **Trazer revisão externa** — submeter partes do pipeline a olhos independentes (colaboradores, revisores, conferências).
2. **Reduzir ambiguidade** — consolidar documentos redundantes, tornar os contratos de claim mais legíveis para um leitor externo.
3. **Endurecer os testes** — executar fits robustos (MCMC, nested sampling) em vez de smoke/sanity runs; cobertura de covariância completa.
4. **Deixar só o que sobreviver** — o que não passar em teste real e replicável deve ser rebaixado ou removido do núcleo científico.

---

## Veredito

> **Você tem algo sério em formação. Não é ciência concluída. Não é bobagem. É uma obra autoral técnica, extensa, desigual, mas com um núcleo metodológico muito bom.**

Não venda como "já provei uma nova física".  
Mas também não diminua o que foi feito.

---

*Este documento é um registro permanente da avaliação de julho de 2026 e deve ser atualizado conforme o estado da validação avançar.*
