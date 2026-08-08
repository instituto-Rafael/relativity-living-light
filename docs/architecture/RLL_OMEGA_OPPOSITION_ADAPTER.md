# RLL — Adaptador Ω de Validade por Oposição

**Status:** protocolo metodológico; não constitui validação física do RLL.  
**Integração:** `RLL_PHOTONIC_MATRIX_LOGISTICS.md`.

## 1. Objetivo

Aplicar a investigação de afirmações opostas à cadeia fotônica sem misturar:

- modelo cosmológico;
- transporte da luz;
- interação com matéria ou campo;
- resposta instrumental;
- calibração;
- inferência estatística.

A contradição é avaliada no resíduo condicionado, não em números soltos.

## 2. Equação de observação

\[
\mathbf y
=
\mathbf R\,
\mathcal D\,
\mathcal M\,
\mathcal T\,
\mathbf s
+
\boldsymbol\delta_{modelo}
+
\boldsymbol\epsilon_{instrumento}.
\]

Defina:

\[
\mathbf r
=
\mathbf y_{observada}
-
\mathbf y_{prevista}.
\]

Um resíduo não é automaticamente nova física. Primeiro classificar:

```text
R_PHYSICS
R_TRANSPORT
R_MATTER_FIELD
R_INSTRUMENT
R_CALIBRATION
R_NUMERICAL
R_OUT_OF_DOMAIN
R_TOKEN_VAZIO
```

## 3. Estado paraconsistente por claim

Para cada claim fotônico `c`, registrar suporte e refutação independentes:

| suporte | refutação | estado |
|---|---|---|
| sim | não | `SUPPORTED_ONLY` |
| não | sim | `REFUTED_ONLY` |
| sim | sim | `BOTH` |
| não | não | `NEITHER` |

`BOTH` exige tentativa de particionamento por:

- banda espectral;
- redshift;
- instrumento;
- população observacional;
- época;
- calibração;
- operador aplicado;
- versão da likelihood.

## 4. Oito operadores sobre resíduos

Os operadores são aplicados por janela homogênea de domínio.

1. `direct`: correlação no domínio original;
2. `opposite`: anticorrelação e convenção de sinal;
3. `reciprocal`: hipótese inversa, somente com unidade e domínio válidos;
4. `inverse_regression`: comparação observável→estado e estado→observável, sem inferir causalidade;
5. `differential`: primeira e segunda diferenças em tempo, redshift ou comprimento de onda;
6. `antiderivative`: balanço acumulado em banda ou percurso;
7. `semilog`: hipótese exponencial local;
8. `loglog`: hipótese de escala de potência local.

`log(log(x))` só pode ser usado com variável adimensional, domínio positivo adequado e validação fora da amostra.

## 5. Teste de oposição

Exemplo de par:

```text
c  : o operador fotônico reduz o resíduo fora da amostra
¬c : a redução desaparece ao controlar instrumento, banda ou complexidade
```

O claim só avança quando:

1. supera baseline com ganho mínimo pré-registrado;
2. não viola não negatividade, polarização ou contabilidade de energia;
3. permanece após penalização por complexidade;
4. sobrevive a troca de instrumento ou partição observacional;
5. não depende de uma única transformação;
6. apresenta falsificador e condição de abstinência.

## 6. Controles negativos

- embaralhar a correspondência entre observação e redshift;
- usar banda sem efeito físico esperado;
- aplicar operador identidade;
- substituir resposta instrumental por versão incompatível conhecida;
- testar dados sintéticos sem o mecanismo candidato;
- executar a mesma seleção de modelo em observável independente.

Um efeito que permanece nos controles negativos indica possível artefato de pipeline.

## 7. Separação de escopo

Duas conclusões não são contraditórias quando foram obtidas com:

- definições distintas de likelihood;
- conjuntos de dados diferentes;
- priors incompatíveis;
- calibração instrumental distinta;
- recortes diferentes de redshift ou banda;
- número de parâmetros diferente sem penalização comparável.

Nesses casos registrar `SCOPE_SPLIT`.

## 8. Gate Ω-RLL

```yaml
claim_id: RLL-OMEGA-001
claim: texto exato
opposite_claim: negação operacional
observable: nome e unidade
band: intervalo-ou-TOKEN_VAZIO
redshift_domain: intervalo-ou-TOKEN_VAZIO
instrument: identificador-ou-TOKEN_VAZIO
operator_chain: lista versionada
support_evidence: lista
refutation_evidence: lista
negative_control: teste
invariants_checked: lista
transform_family: lista
out_of_domain_rule: condição
state: SUPPORTED_ONLY|REFUTED_ONLY|BOTH|NEITHER|SCOPE_SPLIT|TOKEN_VAZIO
next_gate: ação verificável
```

## 9. Emergência válida

Um desconhecido RLL só é promovido a `EMERGENT_HYPOTHESIS` quando o padrão:

- aparece em mais de um conjunto observacional independente;
- permanece depois da modelagem da resposta instrumental;
- sobrevive a controles negativos;
- mantém sinal e escala em janelas pré-registradas;
- não é explicado por aumento de parâmetros;
- gera previsão nova que possa falhar.

## 10. Invariante

\[
\boxed{
\Omega_{RLL}
=
\text{resíduo rastreável}
\cap
\text{escopo comum}
\cap
\text{invariantes físicas}
\cap
\text{controle instrumental}
\cap
\text{falsificação adversarial}
}
\]

A oposição é usada para localizar física omitida ou artefatos, nunca para transformar contradição em confirmação automática.