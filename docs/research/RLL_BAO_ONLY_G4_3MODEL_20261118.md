# RLL Ω · DESI DR2 BAO-only ΛCDM × wCDM × RLL — correção de índice da covariância

**Atualização 2026-11-18.** `claim_allowed=false`, PR #1235 DRAFT/HOLD. Este documento sucede a primeira transcrição local, sem apagar seu registro. Código-fonte e observações não foram alterados.

## Falha falsificada e correção

O teste inicial esperava χ²=(10.902987, 7.467261, 6.474229), mas a suíte de CI no HEAD `c46fbf3eeeca71cda8f6ab8fe0303dc2cd4beac2` encontrou ΛCDM χ²=10.291044479494511. Causa confirmada: a matriz pública DESI/Cobaya nativa ordena **Lyman-α DH antes de DM**, enquanto o vetor Table IV no repositório ordena **DM antes de DH**. A transcrição local anterior usava incorretamente a matriz nativa como se tivesse a ordem do vetor. O G4 já implementava a permutação, portanto o erro era do **benchmark de referência/teste**, não das equações `g4.e2` ou da base observacional. A falha nunca deve ser escondida por ampliação arbitrária da tolerância.

Proveniência:

- `tools/build_desi_covariance_order_receipt.py` valida `G3_TABLE4_ORDER_VALUE_SIGMA_CORRELATION_CHECKED` e a bijeção com o Cobaya nativo;
- `tools/run_g4_background_tournament.py::load_desi()` aplica `matrix[np.ix_(permutation,permutation)]`, após validação de hash/ordem e Cholesky;
- `data/real/cosmology/desi_dr2_bao_primary_points.csv` blob Git `f6d05ead6fef7fea663eff8b31bc2c337dc30435`;
- `data/real/desi_dr2_bao_covariance.csv` blob Git `e01d0235a2f0e61d81af0c36a7338953f845f5c3`.
- Um teste de regressão agora exige permutação **[0..10,12,11]**, a covariância simétrica positiva e o par Lya na ordem DM,DH da tabela.

## Nova reprodução independente ligada ao G4, com ordem correta

13 observáveis e matriz 13×13. Mesmas regras de quadratura Gauss–Legendre 96/192, amplitude efetiva livre `q=c/(H0*r_d)`, mesmo otimizador multistart e bounds. Resultados reproduzidos localmente com o adaptador equivalente ao G4, sujeitos à verificação da CI do novo HEAD:

| Modelo | k | χ² | AICc | BIC |
|---|---:|---:|---:|---:|
| ΛCDM | 2 | 10.2910444795 | **15.4910444795** | **15.4209431944** |
| wCDM | 3 | 9.0274881328 | 17.6941547994 | 16.7223362051 |
| RLL | 5 | **7.8039737280** | 26.3754022994 | 20.6287205153 |

Parâmetros da melhor solução:
- ΛCDM: `q=29.5225994480; Ωm=0.2971567020`.
- wCDM: `q=30.0589082143; Ωm=0.2973710261; w=-0.9107922977`.
- RLL: `q=28.4039182605; Ωm=0.1340362727; Ωs0=0.1343514672; z_t=0.3988747690; w_t=0.05`.

19, 19, 20 iniciações no executor novo (todas as melhores soluções com otimizador `success=true`). O RLL atinge o limite `w_t=0.05`; o perfil de verossimilhança e incerteza dos parâmetros continuam `TOKEN_VAZIO`.

### Revisão dos resultados anteriores

Os χ² e derivados AICc/BIC do primeiro ensaio BAO-only sem permutação **não são comparáveis como resultados verificados** e ficam expressamente **SUPERSEDED_WRONG_COVARIANCE_INDEX**. O jackknife 7/7 e sensibilidade dos limites antes publicados com aquela matriz devem ser **RECOMPUTED_NOT_RUN**, nunca importados para estes resultados. Preservar o relatório anterior como evidência histórica do bug, não como valor canônico.

Critério de seleção com AICc e BIC ainda favorece ΛCDM sobre RLL; menor χ² do RLL apenas reflete maior liberdade paramétrica neste conjunto.

### Bloqueios explícitos

- `Pantheon+SH0ES_STAT+SYS.cov` oficial e sidecar SHA-256 ainda não disponíveis neste checkout: `TOKEN_VAZIO_FULL_COVARIANCE`. Não usar diagonal como substituto.
- Torneio G4 completo Pantheon+ + BAO + cronômetros cósmicos: `NOT_RUN` neste commit.
- Perfil de parâmetros / estimativa robusta de intervalos de confiança / replicação independente com arquivo Cobaya original: `NOT_RUN`.
- `claim_allowed=false`; PR DRAFT/HOLD; `main`, `rll/lab` e ciência observacional imutáveis.

## Comandos para verificação

```sh
OPENBLAS_NUM_THREADS=1 python -m pytest -q tests/test_bao_only_g4_v1.py
OPENBLAS_NUM_THREADS=1 python scripts/run_bao_only_from_g4_v1.py --starts-extra 18 --output artifacts/evidence/bao_g4_source_order_20261118.json
```

Saída append-only: escolher nome novo a cada execução. O comando rejeita um arquivo existente.

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM` / `IMPLEMENTED_UNTESTED != PASS`.
