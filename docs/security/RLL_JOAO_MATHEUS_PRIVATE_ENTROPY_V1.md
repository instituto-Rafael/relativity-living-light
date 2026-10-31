# RLL × Voynich — Matrizes João/Matheus, execução privada V1

Estado: PROPOSED / LOCAL_TESTED_SCOPED / DRAFT_HOLD. claim_allowed=false.

## Autoridades e fronteiras

Produtor de código: instituto-Rafael/relativity-living-light.
Fonte CTI: rafaelmeloreisnovo/llamaRafaelia/rmrCti.
Fonte experimental Voynich: rafaelmeloreisnovo/Rafaelia_Private/native/voynich_impl.

RapidTools e Conversation Check: identidade canônica exata e custódia do secret ainda TOKEN_VAZIO_UNRESOLVED_AUTHORITY; não foi criada integração presumida. O secret RLL GITPAT tem destino exclusivo no workflow rll-repository-pat-assurance.yml e NÃO é reutilizado. Um PAT com push/admin é rejeitado. Nenhuma autoridade sobre Mapa ou outros repositórios decorre da presente implementação.

O repositório RLL é público. Código ou imagens que precisam permanecer confidenciais NÃO devem ser commitados nele. Esta proposta só publica o motor genérico, testes inteiramente sintéticos e esta especificação; resultados detalhados e source hashes ficam dentro do envelope cifrado.

## Matrizes de observação antes da física

Dividir uma imagem confiável em malha 4 × 4. Para cada quadrante medir:
- entropia de Shannon de luminância quantizada em 4 bits, normalizada;
- entropia residual horizontal quantizada;
- compressibilidade zlib (bytes por pixel quantizado);
- fração de pixels escuros como proxy, sem alegação de segmentação semântica.

O escore heurístico é 0.4*H_pixel + 0.3*H_residual + 0.3*min(zlib_ratio,1). É proxy de complexidade gráfica e NÃO mede diretamente entendimento, semântica ou evidência cosmológica.

JOAO classifica os mesmos 16 quadrantes do menos complexo para o mais complexo. MATHEUS faz a classificação inversa. As matrizes são duas vistas das MESMAS medições; ordenações não podem alterar dados brutos. Preregistrar tolerância a ruído, escala, rotação, textura do papel, resolução e negativos/controles antes de inferir padrões.

## Execução e autorização

O único caminho de produção deste V1 é a execução INTERATIVA LOCAL, depois de aprovação humana e configuração da origem privada:

1. RLL_ENTROPY_OPERATOR_KEY precisa existir no ambiente confiável; operador digita chave num prompt oculto, com comparação constante. Isso não comprova a origem Conversation Check até attestation externa.
2. Operador digita separadamente PAT GitHub limitado a leitura do próprio RLL, em prompt oculto. Programa consulta exclusivamente GET https://api.github.com/repos/instituto-Rafael/relativity-living-light e exige permissions.pull=true, permissions.push=false, permissions.admin=false. PAT amplo/administrativo é recusado.
3. RLL_ENTROPY_RECIPIENT_X25519_PUBLIC_HEX precisa estar associado por verificação independente ao destinatário autorizado. Não existe ainda prova de que seja RapidTools.
4. RLL_ENTROPY_PRIVATE_ROOT deve ser um diretório absoluto privado FORA do checkout RLL. Arquivos de origem e destino devem ficar nessa raiz; saída preexistente ou qualquer fonte pública é recusada.
5. O processamento só ocorre após os gates. O payload completo é cifrado em memória para chave pública X25519 autenticada externamente: X25519 efêmero + HKDF-SHA256 + AES-256-GCM, AAD rll.joao_matheus.private.v1. Somente o envelope cifrado é persistido (modo 0600), e stdout registra apenas estado cifrado e checksum do ciphertext.
6. Nenhum segredo, PAT, imagem, matriz aberta ou hash de secret é publicado em logs, GitHub, comentários ou Actions. A criptografia fornece confidencialidade e integridade do conteúdo para o destinatário, mas NÃO autentica sozinha o autor.

Comando após provisionamento externo:
python3 tools/private_entropy/joao_matheus.py --input-private-image /private/root/folio.png --source-ref source-corpus@sha --out-encrypted /private/root/results/folio.enc.json

Instalar apenas dependências auditadas Pillow e cryptography no ambiente PRIVADO; nenhuma nova Actions de consumo de secrets é ativada neste PR. Um PAT NÃO deve ser colado em workflow_dispatch input ou argumento CLI. Para execução remota, exigir Environment protegido, revisão humana, executor identificado, chave e autorização por operação; habilitação posterior depende de autoridade e readback reais.

## Segurança e falsificadores

Sem chave correta ou PAT read-only = BLOCKED antes de ler a imagem. Sem recipient pinado = BLOCKED. Entrada >32 MiB, imagem >16 milhões de pixels, matriz irregular, caminho fora de root ou saída existente = BLOCKED. Violação de autenticidade AES-GCM = FAIL. Nenhum resultado assume que entropia alta signifique criptografia; nenhum resultado do Voynich prova modelo físico RLL.

Os testes locais, exclusivamente sintéticos, cobrem oito casos: distinção de entropia, duas ordens inversas, geometria inválida, secret ausente/incorreto, chave correta, PAT com privilege negativa, encrypt/decrypt e adulteração, arquivo não aberto antes do gate. Execução local PASS_SCOPED (8/8); CI e runtime autorizado real TOKEN_VAZIO.

## R3

F_ok: duas matrizes programáticas, key gate, PAT read-only gate, saída cifrada, testes locais e documentação.
F_gap: autoridade RapidTools/Conversation Check, custódia do recipient, instalação de dependências no executor, prova de execução com secret válido, imagens reais e reprodução independente ainda TOKEN_VAZIO.
F_next: identificar produtores concretos sem fornecer segredo no chat; verificar chave pública de destinatário e PAT estritamente read-only; executar canary privado, recibo com hash/ref e revisão antes de qualquer promoção.
Rollback: fechar a PR draft sem merge; main e credenciais não alterados.
