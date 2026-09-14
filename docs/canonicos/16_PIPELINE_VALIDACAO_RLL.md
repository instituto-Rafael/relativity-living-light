# 16 — Pipeline de Validação RLL

**Status:** canônico complementar  
**Origem:** extraído de `docs/canonicos/BIBLIA_CONHECIMENTO_RAFAELIA_RLL.md` e ampliado por execução CI  
**Função:** registrar estrutura executável, funções-núcleo, invariantes e critérios mínimos de reprodutibilidade.

---

## 1. Composição canônica por estágios

```text
Estágio 0 — matemática estrutural e invariantes
Estágio 1 — dados reais, proveniência, unidades e covariância
Estágio 2 — likelihood, otimização e posterior
Estágio 3 — falsificadores e seleção de modelos
Estágio 4 — relatório, manifesto, hashes e artefato
```

O `Estágio 0` é condição necessária, mas não suficiente, para qualquer claim científico. Ele demonstra que a formulação implementada é calculável e internamente coerente; não confirma verdade física.

---

## 2. Estrutura executável

```text
relativity-living-light/
├── .github/workflows/
│   ├── rll-structural-math-artifacts.yml
│   ├── real-data-complete-execution.yml
│   ├── validacao_real.yml
│   └── cosmology_validation.yml
├── rll_core/
│   ├── __init__.py
│   └── structural_invariants.py
├── scripts/
│   ├── rll_structural_invariants.py
│   └── compute_validation.py
├── tests/
│   └── test_rll_structural_invariants.py
├── schemas/
│   └── rll_structural_math_artifact_v1.schema.json
├── validacao_real/
│   ├── sources.yml
│   ├── fetch_real_data.py
│   ├── compute_validation.py
│   ├── make_figures.py
│   ├── render_report.py
│   ├── data/
│   │   ├── desi_dr2_bao.yml
│   │   └── hz_cosmic_chronometers.yml
│   └── caminhos/
│       ├── CAMINHOS_VALIDACAO_NOVOS.yml
│       └── TEXTO_DESCRITIVO_ANALITICO_TECNICO.md
├── docs/mathematics/
│   └── RLL_STRUCTURAL_INVARIANT_PIPELINE.md
└── orquestrador/
    └── rafaelia_orquestrador.py
```

---

## 3. Funções estruturais canônicas

```python
RLLParameters(...)
transition_f(z, params)
sector_g(z, params)
e2(z, params)
e2_prime(z, params)
e2_second(z, params)
log_hubble_slope(z, params)       # D1
log_hubble_curvature(z, params)   # D2
deceleration_q(z, params)
effective_w_geometry(z, params)
jerk_j(z, params)
ricci_bar(z, params)
kretschmann_bar(z, params)
DM_over_rd(z, params)
DH_over_rd(z, params)
DV_over_rd(z, params)
scan_invariants(params, z_grid)
```

Os escalares `ricci_bar` e `kretschmann_bar` são válidos sob a hipótese explícita de fundo FLRW espacialmente plano:

```math
\bar R=Rc^2/H_0^2=6E^2(2-D_1)
```

```math
\bar K=Kc^4/H_0^4=12E^4(1+q^2)
```

---

## 4. Funções de inferência e confronto

```python
Ez_LCDM(z, Om, Or=8.6e-5)
Ez_w0wa(z, Om, w0, wa, Or=8.6e-5)
Ez_RLL(z, Om, Os0, zt, wt, OB0=0.0, OP0=0.0, Or=8.6e-5)
chi2_bao(Ez, H0, rd, data)
aic(chi2, k)
aicc(chi2, k, n)
bic(chi2, k, n)
w_eff_RLL(a, zt, wt)
```

As implementações de fundo usadas na inferência devem ser comparadas numericamente com `rll_core/structural_invariants.py`. Divergência não explicada bloqueia publicação.

---

## 5. Invariantes obrigatórios do Estágio 0

Toda execução estrutural deve verificar:

- `E²(0)=1` dentro da tolerância;
- `Ωs0=ΩB0=ΩP0=0` recupera exatamente o baseline ΛCDM declarado;
- `E²(z)>0` em toda a região calculada;
- `0≤f(z)≤1` e `f′(z)≤0` quando `wt>0`;
- derivadas analíticas concordam com diferenças finitas;
- registro de fórmulas possui identificadores únicos e dependências válidas;
- grafo estrutural não contém aresta para nó inexistente;
- resumo final é válido contra JSON Schema;
- artefato contém manifesto e hashes.

Detalhes e tolerâncias: `docs/mathematics/RLL_STRUCTURAL_INVARIANT_PIPELINE.md`.

---

## 6. Critérios mínimos da validação observacional

Toda execução com dados deve registrar:

- commit de referência;
- artefato estrutural de entrada ou commit que o reproduz;
- versão e proveniência dos dados;
- parâmetros, priors e limites usados;
- matriz de covariância ou justificativa explícita de diagonalização;
- número de observáveis e parâmetros livres;
- χ², AIC, AICc e BIC;
- seeds, convergência e estabilidade;
- interpretação com limites claros.

---

## 7. Regra de não-alucinação computacional

Se o pipeline não encontrou dado, matriz, arquivo, dependência ou referência, deve retornar `TOKEN_VAZIO`/falha explícita. É proibido preencher automaticamente números ausentes.

`PASS` estrutural significa somente:

```text
as expressões implementadas satisfizeram os gates declarados na malha escolhida
```

Ele não significa:

```text
confirmação observacional
superioridade estatística
teoria fundamental estabelecida
patenteabilidade
```

---

## 8. GitHub Actions e artefatos

### Matemática estrutural

```text
.github/workflows/rll-structural-math-artifacts.yml
```

Produz:

- `formula_registry.json`;
- `structural_map.json`;
- `invariant_scan.csv`;
- `summary.json`;
- `REPORT.md`;
- `MANIFEST.json`;
- `CHECKSUMS.sha256`.

### Dados reais

```text
.github/workflows/real-data-complete-execution.yml
```

Consome a formulação após os gates estruturais e produz relatórios observacionais separados. Os workflows não fazem push automático de resultados; promoção para o repositório exige PR revisada.

---

## 9. Ambiente Termux ARM32

Preferir pacotes do sistema:

```bash
pkg install python python-numpy python-matplotlib
```

Para o Estágio 0, o núcleo matemático usa biblioteca padrão; `pyyaml` é necessário apenas para a comparação relacional com o motor legado.

---

## 10. Saída mínima publicável

```text
estrutura PASS
+ dados rastreáveis
+ inferência reproduzível
+ adversário científico adequado
+ falsificador ativo
+ manifesto e checksums
```

Sem essa interseção, o resultado permanece hipótese, simulação ou execução parcial.

---

*Pipeline é prova de trabalho; artefato é cadeia de custódia; dado decide a hipótese.*
