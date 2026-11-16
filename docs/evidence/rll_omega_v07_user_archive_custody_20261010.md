# RLL Ω V07 — Casa de Provas — Custódia de arquivos do usuário (2026-10-10)

Status: EVIDENCE_INGESTED_LOCAL / STATIC_VERIFICATION_PASS_SCOPED / PHYSICAL_ATTESTATION_OPEN
μID: MU-20261010-RLL-V07-USER-ARCHIVES-CUSTODY-S1
Policy: SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM; TOKEN_VAZIO != 0; claim_allowed=false.
Autoridade: repo produtor instituto-Rafael/relativity-living-light; alteração documental apenas, sem alterações em modelo, aplicativos, dados ou workflows.

## Entradas recebidas (SHA-256 computado sobre os bytes da sessão)
- RLL_CANONICAL_OMEGA_ALL_EVIDENCE (8).zip | 154534 bytes | d17553c231f276a016fa54f210273c1e0415939d54d92559e33517d20b80cb56 | autocaptura 2026-10-09, Motorola ARMv7
- RLL_CANONICAL_OMEGA_ALL_EVIDENCE.zip | 154139 bytes | 45ce461450c25e6ef380de04cb9238040c34e5119d68edfbacfdafb7ba8d4df6 | autocaptura 2026-10-10, Samsung ARM64
- RLL_OMEGA_V07_INDEPENDENT_LIVE_RUNTIME_AUDIT_RECEIPTS_20261009.zip | e83e0cbee7e225858d40405d32e59f3b569aa90bb830f6aeaa677dfe4b92f12d | 4 arquivos de auditoria; relatório descreve cinco capturas anteriores; apenas a captura (8) desse grupo está anexada neste lote
- RLL_OMEGA_V07_ONE_CLICK_ALL_FORMULAS_KERNEL_JNI_SYSTEM_FINAL.apk | 109222 bytes | 586072a56852dcbde73bc3e04dca1e8fe111c5da46dffc31043271b9a90301ab | APK com bibliotecas ARMv7 e ARM64.

## Verificações estáticas executadas na sessão
- Os dois ZIPs canônicos possuem 177 caminhos cada. CRC íntegro, 176 caminhos listados em MANIFEST_SHA256.txt por ZIP, 176/176 hashes iguais aos bytes (cada ZIP). 
- Conjuntos de caminhos idênticos, 166 entradas com bytes iguais e 11 entradas diferentes (dados de processo e dispositivo, timestamps, logs, congelamento de inputs, ATLAS, MANIFEST). Fórmulas e dados científicos em comum não mudaram.
- Vetores JNI 80+1 por captura: cálculo independente 162/162 coerente com os registros, sem alegação de controle físico externo.
- Ambos os auto-relatos PackageManager citam o mesmo SHA-256 do APK verificado. Isso é consistência de identidade relatada, não testemunho ADB independente.

## Limites e riscos (não promovidos)
- APK Signature Scheme v2/v3: TOKEN_VAZIO_NOT_VERIFIED.
- Testemunha externa do dispositivo e cadeia de instalação: TOKEN_VAZIO_NOT_ATTESTED.
- CLASS/CAMB, posterior DESI oficial, crescimento, estabilidade dinâmica e replicação cosmológica independente: TOKEN_VAZIO_NOT_RUN.
- Direitos/licenças de redistribuição de dados/artefatos: TOKEN_VAZIO_UNVERIFIED; preservar entradas brutas sob custódia privada.
- V07 é histórico em relação ao V08: PR#1098 e PR#1099 estão merged em rll/lab, este registro não reverte nem declara a validação física de V08.
- O audit ZIP adicional é evidência documental; suas cinco capturas históricas não foram reimportadas integralmente nesta sessão, portanto não afirmar inspeção atual dos cinco ZIPs brutos.

## Linhagem source/artifact/evidence
- Producer: https://github.com/instituto-Rafael/relativity-living-light
- V07 upstream: https://github.com/instituto-Rafael/relativity-living-light/pull/1098
- V08 successor: https://github.com/instituto-Rafael/relativity-living-light/pull/1099
- CI original v07 referida em receipt: run 38001728566, artifact 11649862361. Identidade exata CI→APK exige observação do artefato pelo verificador; não confundir com conclusão baseada em autorrelato.
- Fontes acadêmicas pré-existentes alphaXiv RLL — Perturbations & DESI DR2; referências são PRIOR_ART, não validação de hipótese.

## Reproduzir e falsificar
1. Recalcular SHA-256 dos 4 arquivos brutos; falha se divergente.
2. Reabrir cada ZIP, testar CRC, nomes únicos e os 176 hashes do manifesto; falha em qualquer mismatch.
3. Fazer diff por caminho e por bytes, sem colapsar 11 diferenças de contexto em erro científico.
4. Recomputar JNI com oracle ((x*31) XOR (y*17))+32 conforme domínio numérico; testar negativos, limites e divergências.
5. Se houver testemunho autorizado: ADB externo, pacote instalado, SHA exact APK e apksigner v2/v3; sem essas provas manter TOKEN_VAZIO.
6. Para cosmologia: usar parâmetros/priors declarados, DESI 13×13, comparação LCDM/CPL/RLL com likelihood identicamente parametrizada, CLASS/CAMB e dados independentes, falsificadores pre-registrados. Não derivar preferência cosmológica dos passes de software.

## Custódia/rollback
RAW_USER_DEVICE_ZIPS: não reproduzidos neste arquivo de GitHub público.
Nenhum código/fórmula/ci modificado. Branch audit apenas, PR draft até revisão humana. Reversão: fechar PR sem merge; em Drive usar μWRITE supersedes, nunca apagar trilha.
R3 = <F_ok: arquivo/hash/manifesto/JNI escopado; F_gap: assinatura, hardware independente, posterior físico; F_next: readback GitHub/Drive, verificador v08 e falsificação científica independente>.
