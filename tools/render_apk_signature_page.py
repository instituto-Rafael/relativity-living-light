#!/usr/bin/env python3
"""Render a static GitHub Pages receipt for the latest signed RLL APK."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


TOKEN_VAZIO = "TOKEN_VAZIO_SIGNED_APK_RECEIPT"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render(receipt_path: Path | None) -> str:
    receipt = None
    if receipt_path and receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

    if receipt is None:
        body = f"""
        <p class="state empty">{TOKEN_VAZIO}</p>
        <p>Nenhum recibo verificável de APK assinado foi fornecido a esta publicação.</p>
        <p>Para fechar esta lacuna, o workflow Android Build precisa executar em <code>main</code>
        com os quatro secrets de assinatura configurados e concluir com sucesso.</p>
        """
        title = "Assinatura do APK — lacuna tipada"
    else:
        cert = receipt.get("certificate") or {}
        artifact = esc(receipt.get("artifact", "TOKEN_VAZIO"))
        artifact_sha = esc(receipt.get("artifact_sha256", "TOKEN_VAZIO"))
        cert_dn = esc(cert.get("dn", "TOKEN_VAZIO"))
        cert_sha = esc(cert.get("sha256", "TOKEN_VAZIO"))
        commit = esc(receipt.get("git_commit", "TOKEN_VAZIO"))
        run_id = esc(receipt.get("github_run_id", "TOKEN_VAZIO"))
        state = esc(receipt.get("state", "UNKNOWN"))
        body = f"""
        <p class="state verified">{state}</p>
        <dl>
          <dt>APK</dt><dd><code>{artifact}</code></dd>
          <dt>SHA-256 do APK</dt><dd><code>{artifact_sha}</code></dd>
          <dt>Certificado — DN</dt><dd><code>{cert_dn}</code></dd>
          <dt>SHA-256 do certificado</dt><dd><code>{cert_sha}</code></dd>
          <dt>Commit</dt><dd><code>{commit}</code></dd>
          <dt>GitHub Actions run</dt><dd><code>{run_id}</code></dd>
        </dl>
        <p class="scope">Escopo: integridade do artefato e identidade criptográfica do assinante.
        Este recibo não valida comportamento funcional, segurança integral ou claims científicos.</p>
        """
        title = "Assinatura verificável do APK"

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title} · Relativity Living Light</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    main {{ max-width: 58rem; margin: 3rem auto; padding: 0 1rem; }}
    h1 {{ line-height: 1.15; }}
    .state {{ display: inline-block; padding: .4rem .65rem; border-radius: .4rem; font-weight: 700; }}
    .verified {{ background: #0a7f3f; color: white; }}
    .empty {{ background: #8a4b00; color: white; }}
    dl {{ display: grid; grid-template-columns: minmax(10rem, 14rem) 1fr; gap: .8rem; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code {{ overflow-wrap: anywhere; }}
    .scope {{ border-left: .3rem solid #777; padding-left: 1rem; }}
  </style>
</head>
<body>
<main>
  <h1>{title}</h1>
  <p>Relativity Living Light · recibo público, gerado pelo pipeline.</p>
  {body}
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.receipt), encoding="utf-8")


if __name__ == "__main__":
    main()
