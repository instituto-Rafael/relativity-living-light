# RLL Ω — ZIP canônico de execução integral em um toque (v0.4.0)

## Intenção operacional
**Um único botão no topo da tela**: **GERAR ZIP CANÔNICO Ω — FAZER TUDO**. Não escolhe modelo, parâmetros, testes ou formato. O aplicativo executa a matriz completa de capacidades *atualmente implementadas*, inclusive as negativas, antes de oferecer o diálogo Android padrão para decidir a localização de **RLL_CANONICAL_OMEGA_ALL_EVIDENCE.zip**.

Não é uma promessa de gerar dados impossíveis, executar CLASS/CAMB não instalado, provar a hipótese de Poincaré em dados sem trajetórias ou produzir atestado físico independente sem testemunha externa. O estado dessas operações é **TOKEN_VAZIO tipado dentro do ZIP**. A exportação nativa é ZIP sem RAR externo ou dependência adicional.

## Orquestração canônica — execução
1. Aferição do JNI ARM32/ARM64 via 4 vetores (C vs Java); FAIL não interrompe os demais testes.
2. Recebimento **local** de campos do PackageManager (package, versionCode/name, instalação/atualização em milissegundos UTC, ABI, fabricante/modelo, SHA-256 do certificado/arquivo APK onde acessíveis); build inclui cabeçalho Git commit e run_id originados de variáveis GitHub Actions, rotulados como auto-relato. Sem identificador serial/IMEI/localização/screenshot ou telemetria.
3. Download do DESI DR2, 13 medições BAO e a matriz completa 13×13, via HTTPS com URL/commit GitHub **pinned**; hash Git blob, esquema e Cholesky SPD necessários antes de qualquer χ² real. Em falha, o ZIP ainda contém os cálculos não dependentes da rede e a classificação do problema. Dados externos são preservados apenas na cópia privada criada pelo usuário; direitos de redistribuição continuam P0/Token vazio.
4. Quatro modelos (LCDM, WCDM, CPL, RLL), 11 pontos cada em z∈[0,3] por passo 0.3 = **44 recibos individuais**, com todas as equações de fundo, distâncias, identidades, aproximações e lacunas aplicáveis. Usa parâmetros explícitos da implementação com E²(0)=1 por construção; não executa seleção automática de parâmetros ajustados aos observáveis.
5. Com dados reais válidos: χ² correlacionado para quatro fundos fixos, previsão × observação em cada um dos 13 pontos, sensibilidade por diferença finita pré-declarada (Ωm±0.005, H0±0.5, RLL zt±0.05). r_drag continua **proxy empírico**, não modelo físico independente.
6. Aferição da geometria paramétrica T² (R=2, r=0.7), **não** de um atrator ou teorema de recorrência dinâmico. A definição autoral RMRCTI DeltaP=P(stable_any|peak)-P(stable_any|nonpeak) depende de traços CTI que dados BAO não incluem.
7. Consulta do gate oficial de releases Android no GitHub: ausência, candidata com SHA-256 publicado ou falha de provider entram no mesmo ZIP. Consulta não instala releases e não verifica compatibilidade de assinatura.
8. Encadeia INDEX/ATLAS (caminhos, byte counts e SHA-256), gates TSV, source contract, receipts, CSV, referências e MANIFEST_SHA256. Hash do ZIP total é exibido após serialização (não pode ser colocado dentro de si mesmo). Após o usuário escolher o destino, o app reabre a URI fornecida pelo Android e compara os bytes salvos por SHA-256; divergência recebe FAIL_SAVE_READBACK_SHA256, ausência de permissão para reabrir recebe TOKEN_VAZIO e não é classificada como PASS. Todo arquivo dentro do ZIP é verificado pelo manifesto.

## Estrutura de saída
- `00_START_HERE.txt`: governança, separação SOURCE/ARTIFACT/EXECUTION/EVIDENCE/CLAIM e limites;
- `01_ATLAS.tsv`, `02_GATES.tsv`, `03_RECEIPT.txt`, `MANIFEST_SHA256.txt`;
- `10_DEVICE/native_jni_score_receipt.txt`, `installed_package_self_report.txt`, `release_discovery_receipt.txt`;
- `20_FORMULAS/[LCDM|WCDM|CPL|RLL]/parameters.txt`, `grid.csv`, onze `point_NN.receipt.txt`, `formula_catalog.tsv`;
- `30_DATA/source_contract.txt` e, somente após hash, `raw/[mean,cov]`;
- `31_REAL_DATA_CALCULATIONS/*`: quatro χ² e linhas observadas/calculadas se fonte genuína, ou TOKEN_VAZIO explicando bloqueio;
- `40_STABILITY/toroid_geometry.txt`, `rmrcti_delta_p_source_boundary.txt`;
- `50_REFERENCES/papers_and_tools.txt`.

## Falhas, segurança, direitos e atualização
- Todos os estágios locais são executados sem precisar de rede; falha de rede **não** apaga evidências JNI/install/fórmulas.
- Hash ou covariância inválida impõe FAIL_CLOSED; dados suspeitos não são promovidos a fonte real.
- Arquivo dentro de ZIP tem nome limitado, tamanho limitado, nenhum diretório relativo/absoluto; digest SHA-256 por item. Sem uploads de artefatos privados para GitHub nem cópia automática para Google Drive.
- Android `ACTION_CREATE_DOCUMENT` é a **única seleção** indispensável por autorização do sistema: onde salvar seu ZIP. A conexão de rede ocorre após clicar no botão; não exige permissões de armazenamento amplas.
- Instalação é auto-observada; comprovação independente, assinatura de upgrade, instalação de outro dispositivo e ciência cosmológica seguem TOKEN_VAZIO até evidências externas.
- Build debug incrementa `versionCode=4`, `versionName=0.4.0`; assinaturas debug anteriores podem impedir instalação em cima do APK já instalado.
- Fonte de RMRCTI autoral: `rafaelmeloreisnovo/llamaRafaelia/rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md`. alphaXiv: 2503.14738, 2504.06118, 2606.18455, 2608.01215, 2609.22470 são referências de falsificação, **não endossos de RLL**.

## CI/receipts/rollback
- `sh app/verify_formula_engine.sh`: regressões algébricas.
- `sh app/verify_real_bao_engine.sh`: covariância e parâmetros em matriz sintética.
- `sh app/verify_canonical_omega.sh`: ZIP offline completo, 44 recibos, SHA/manifesto, invariantes e bloqueio de fonte adulterada.
- Android compile ARM32/ARM64 debug e validationUnsigned, sem publicar assinatura release.
- Gate de fonte DESI via workflow `rll-desi-dr2-live-data.yml` separado; seu SUCCESS não prova que o app foi instalado ou baixou no dispositivo.
- Reversão somente da feature com classe canônica, botão/exposição, BuildConfig e testes, sem alterar modelos físicos, arquivos upstream, direitos ou evidência anterior.
- `claim_allowed=false` e `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.
