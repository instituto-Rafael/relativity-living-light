# RLL — Reconciliação de linhagens lab + integration (candidata V1)

Estado: **CANDIDATE_ONLY / IMPLEMENTED_UNTESTED** · claim_allowed=false · publication_effect=NONE.
Data do registro: 2026-11-16. Escopo: preservar histórico divergente **sem modificar** branches protegidas ou promover alegação científica.

## Âncoras verificadas (refs do GitHub)

- `rll/lab` @ `c0e3e500b4c584a584e6c92e54e0f15dbb2839c1`; tree `89ef5a345f05411495546021af2a522722ade5d1`.
- `rll/integration` @ `63c0cf749ed52c554aaa69b5cd0766c82e9b4b4a`; tree `fe5f45c43b8008a5f82e259218ad424a9f55e427`.
- `main` @ `ac833cb1278ffde951e602dd70df4c11bcda6ac0` (referência; **não** é destino desta operação).
- `rll/release` @ `2cb3e3e88677ea9ac1f263377114b539db7bc47f` (não promover).
- Ancestral comum lab/integration observado: `be9a2d91287a979f9a770561c5c11861529106e2`.

## Motivo técnico

A comparação `rll/integration...rll/lab` no snapshot mostra 14 commits exclusivos de lab e um commit exclusivo de integration (merge #1222). A diferença de árvore ficou concentrada em:

1. `tools/validate_rll_credential_authority.py` — scanner de credenciais com reconhecimento de sintaxes de acesso.
2. `tests/test_rll_credential_authority.py` — testes negativos da mesma fronteira.

O commit de merge #1222 integra ancestralidade prévia sem necessariamente adicionar diferença de conteúdo. **Conservar os dois pais** incorpora essa linhagem na candidata, usando a árvore atual de lab como baseline para não regredir os dois arquivos, mais este manifesto aditivo.

## Topologia e autoridade

`work/* -> rll/lab -> rll/integration -> rll/release -> main`.
Esta branch é **candidata de trabalho**, não promoção. Não há força de push, exclusão, rebase da origem nem auto-merge. Não reaplicar mudanças já incorporadas por PRs #1222, #1228 ou #1229.

## Gates e falsificadores (antes de PR/merge)

1. Ler pais do commit candidato: primeiro `lab@` acima, segundo `integration@` acima. Se não houver os dois: BLOCKED_PARENT.
2. Comparar árvore da candidata com `lab@`: diferença permitida **somente** neste manifesto. Se alterar código, testes, YAML, dados ou outros arquivos: BLOCKED_TREE_REGRESSION.
3. Verificar que os dois arquivos citados na candidata têm os **mesmos blobs** de `lab@`: se não, BLOCKED_BLOB_PARITY.
4. Revalidar HEADs de lab/integration: caso tenham avançado, snapshot é histórico e requer sucessor e nova comparação, não atualização silenciosa.
5. Executar testes de credenciais, gate de maturidade, verificações YAML, Actions e checks exatos quando houver PR autorizado; ausência de CI é TOKEN_VAZIO_CI.
6. Para promover, seguir arestas oficiais, review e receipts. Nenhuma alteração em `rll/release` ou `main` por este registro.

## Reconstrução / rollback

Recuperar por `lab@c0e3e500` e `integration@63c0cf74`; o commit de convergência preserva ambos como pais. Em caso de falha, **não** atualizar nenhuma branch original, marcar a candidata HOLD e criar registro sucessor. Não apagar linhas históricas.

R3 = <F_ok: linhagens e árvores observadas; F_gap: CI e promoção não executadas; F_next: verificar readback, comparação e checks exatos antes de qualquer promoção>.
