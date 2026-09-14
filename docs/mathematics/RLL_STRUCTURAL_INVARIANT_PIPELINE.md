# RLL — Pipeline de Invariantes Estruturais e Artefatos Matemáticos

**Estado:** implementação computacional de Estágio 0  
**Escopo:** consistência algébrica, derivadas, geometria FLRW, observáveis de fundo e cadeia de custódia  
**Fronteira de claim:** `PASS` estrutural não confirma o RLL observacionalmente e não demonstra superioridade sobre modelos adversários.

---

## 1. Função no pipeline científico

O estágio estrutural antecede ingestão de dados, likelihood e seleção de modelos:

```text
parâmetros
  → transição logística
  → setor RLL
  → expansão E²(z)
  → derivadas analíticas
  → diagnósticos cinemáticos/geometria FLRW
  → observáveis de fundo
  → invariantes e resíduos
  → artefato com hashes
  → dados reais / covariância / inferência
```

A separação é deliberada:

1. **Estágio 0 — estrutura:** prova que as expressões implementadas são internamente coerentes;
2. **Estágio 1 — dados:** verifica proveniência, unidades, versões e covariâncias;
3. **Estágio 2 — inferência:** ajusta parâmetros e registra likelihood/posterior;
4. **Estágio 3 — confronto:** compara ΛCDM, w0waCDM e RLL;
5. **Estágio 4 — publicação:** materializa relatório, tabelas, figuras, manifesto e checksums.

Nenhum estágio herda automaticamente o estado epistemológico do anterior. Um `PASS` algébrico significa apenas que o cálculo pode seguir para teste observacional.

---

## 2. Equações canônicas implementadas

Definindo:

```math
a=(1+z)^{-1}
```

```math
f(z)=\frac{1}{1+\exp((z-z_t)/w_t)},\qquad w_t>0
```

```math
g(z)=f(z)+[1-f(z)](1+z)^3
```

A normalização em `z=0` usa `g(0)=1`:

```math
\Omega_\Lambda=
1-\Omega_m-(\Omega_r+\Omega_{B0}+\Omega_{P0})-\Omega_{s0}
```

Assim:

```math
E^2(z)=
\Omega_m(1+z)^3
+(\Omega_r+\Omega_{B0}+\Omega_{P0})(1+z)^4
+\Omega_\Lambda
+\Omega_{s0}g(z)
```

A implementação canônica está em:

- `rll_core/structural_invariants.py`;
- `scripts/rll_structural_invariants.py`;
- `tests/test_rll_structural_invariants.py`.

---

## 3. Derivadas analíticas

A transição possui:

```math
f'=-\frac{f(1-f)}{w_t}
```

```math
f''=\frac{f(1-f)(1-2f)}{w_t^2}
```

Com `u=1+z`:

```math
g'=f'(1-u^3)+3(1-f)u^2
```

```math
g''=f''(1-u^3)-6f'u^2+6(1-f)u
```

Chamando `S(z)=E²(z)`:

```math
S'=3\Omega_m u^2+4\Omega_R u^3+\Omega_{s0}g'
```

```math
S''=6\Omega_m u+12\Omega_R u^2+\Omega_{s0}g''
```

onde:

```math
\Omega_R=\Omega_r+\Omega_{B0}+\Omega_{P0}
```

As derivadas são verificadas contra diferenças finitas em uma malha configurável. O erro numérico é registrado; ele não é removido do relatório.

---

## 4. Diagnósticos cinemáticos

São definidos dois operadores adimensionais:

```math
D_1(z)=\frac{d\ln E}{d\ln(1+z)}
      =\frac{(1+z)S'}{2S}
```

```math
D_2(z)=\frac{dD_1}{d\ln(1+z)}
```

Deles seguem:

```math
q(z)=-1+D_1(z)
```

```math
w_{\mathrm{geom}}(z)=-1+\frac{2}{3}D_1(z)
```

```math
j(z)=q(2q+1)+D_2
```

`w_geom` é um diagnóstico efetivo do fundo de expansão. Ele não deve ser apresentado como equação de estado microfísica sem uma derivação adicional do setor material/campos.

---

## 5. Invariantes geométricos sob FLRW plano

Sob a hipótese explícita de fundo FLRW espacialmente plano, o pipeline calcula escalares de curvatura normalizados:

### Ricci normalizado

```math
\bar R(z)=\frac{R c^2}{H_0^2}=6E^2(z)[2-D_1(z)]
```

### Kretschmann normalizado

```math
\bar K(z)=\frac{K c^4}{H_0^4}=12E^4(z)[1+q^2(z)]
```

Esses objetos são escalares geométricos dentro do modelo FLRW assumido. Eles não provam que a parametrização RLL corresponde a uma teoria fundamental de gravitação ou a um tensor energia-momento específico.

---

## 6. Observáveis de fundo

O mesmo núcleo materializa:

```math
\chi(z)=\frac{c}{H_0}\int_0^z\frac{dz'}{E(z')}
```

```math
\frac{D_H}{r_d}=\frac{c}{H_0E(z)r_d}
```

```math
\frac{D_M}{r_d}=\frac{\chi(z)}{r_d}
```

```math
\frac{D_V}{r_d}=\frac{[zD_M^2D_H]^{1/3}}{r_d}
```

A integração usa Simpson determinístico. A etapa estrutural não estima `r_d`; apenas registra o valor fornecido. A inferência cosmológica completa deve derivar ou marginalizar `r_d` conforme o desenho científico adotado.

---

## 7. Invariantes de sustentação

O job falha quando qualquer gate obrigatório cai:

| Gate | Expressão | Critério padrão |
|---|---|---|
| Normalização | `E²(0)-1` | `|resíduo| ≤ 1e-12` |
| Limite nulo | `Os0=OB0=OP0=0` | igualdade com ΛCDM até `1e-12` |
| Positividade | `min E²(z)` | estritamente positiva |
| Limite logístico | `0≤f≤1` | nenhuma violação relevante |
| Monotonicidade | `f′≤0` para `wt>0` | obrigatória |
| Derivada `f′` | analítica vs. numérica | resíduo relativo `≤1e-7` |
| Derivada `f″` | analítica vs. numérica | resíduo relativo `≤2e-6` |
| Derivada `E²′` | analítica vs. numérica | resíduo relativo `≤2e-7` |
| Derivada `E²″` | analítica vs. numérica | resíduo relativo `≤2e-6` |
| Relação legada | novo núcleo vs. `validacao_real` | `PASS`, `LIMITED` ou `TOKEN_VAZIO` documentado |

O limite nulo é o principal invariante relacional:

```math
\Omega_{s0}=\Omega_{B0}=\Omega_{P0}=0
\quad\Rightarrow\quad
E^2_{RLL}(z)=E^2_{\Lambda CDM}(z)
```

Se essa identidade falhar, o pipeline observacional não deve prosseguir.

---

## 8. GitHub Actions

Workflow:

```text
.github/workflows/rll-structural-math-artifacts.yml
```

Acionamentos:

- `pull_request` quando o núcleo, testes, schema ou documentação mudam;
- `push` em `main` para as mesmas rotas;
- `workflow_dispatch` com `z_max`, número de pontos e parâmetros de transição.

Ordem operacional:

```text
checkout sem credencial persistida
→ Python 3.11
→ dependências de validação
→ testes regressivos
→ geração de artefatos
→ validação JSON Schema
→ validação do registro de 23 fórmulas
→ validação do grafo estrutural
→ SHA-256
→ GitHub artifact
```

O workflow não faz `git push` e não promove automaticamente resultados para o repositório.

---

## 9. Conteúdo do artefato

Diretório lógico:

```text
artifacts/rll-structural-math/
```

Arquivos:

| Arquivo | Função |
|---|---|
| `formula_registry.json` | 23 expressões, dependências, unidades e estado |
| `structural_map.json` | nós e arestas do cálculo completo |
| `invariant_scan.csv` | valores por redshift, incluindo geometria e BAO de fundo |
| `summary.json` | parâmetros, resíduos e veredito validado por schema |
| `REPORT.md` | leitura humana com fronteira de claim |
| `MANIFEST.json` | tamanhos, hashes e próximo estágio |
| `CHECKSUMS.sha256` | cadeia final de integridade do job |

O nome publicado pelo Actions inclui `github.run_id`, evitando colisão entre execuções.

---

## 10. Execução local

```bash
python -m unittest discover \
  -s tests \
  -p 'test_rll_structural_invariants.py' \
  -v

python scripts/rll_structural_invariants.py \
  --output artifacts/rll-structural-math \
  --z-max 3.0 \
  --points 301 \
  --os0 0.02 \
  --zt 1.0 \
  --wt 0.3 \
  --cross-check-existing
```

---

## 11. Resultado mínimo necessário

O estágio está operacionalmente encerrado somente quando:

```text
testes = PASS
schema = PASS
registro de fórmulas = PASS
grafo estrutural = PASS
invariantes = PASS
artefato = publicado
checksums = presentes
```

Se um arquivo, dependência, fórmula ou comparação não puder ser executado, o estado correto é `TOKEN_VAZIO` ou falha explícita — nunca preenchimento automático.

---

## 12. Próximo desenrolar científico

Depois do Estágio 0, a sequência adequada é:

1. usar o `summary.json` como contrato de entrada do workflow canônico de dados reais;
2. transportar o identificador das fórmulas para tabelas de likelihood;
3. registrar covariâncias e versão dos datasets;
4. ajustar ΛCDM, w0waCDM e RLL sob as mesmas fronteiras;
5. executar estabilidade entre seeds e perfis de largura `wt`;
6. calcular AIC, AICc, BIC e, quando viável, evidência Bayesiana;
7. publicar conjuntamente o artefato estrutural e o observacional.

A invariante de sustentação do sistema completo torna-se:

```math
\text{claim válido}
=
\text{estrutura coerente}
\cap
\text{dados rastreáveis}
\cap
\text{inferência reproduzível}
\cap
\text{falsificador ativo}
```

---

**Regra final:** o artefato demonstra o caminho do cálculo; os dados decidem a hipótese.
