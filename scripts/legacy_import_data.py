#!/usr/bin/env python3
"""
Importa dados reais de uma URL HTTPS pública explícita (JSON ou CSV) e salva em
um arquivo local definido pelo chamador.

Uso esperado no workflow guardado:
- entrada: URL pública fornecida manualmente;
- saída: `_audit/raw/data.json` como artifact temporário;
- sem commit automático de dados brutos.

Configuração:
- Usa REAL_DATA_URL (env) ou argumento --url;
- Opcional: REAL_DATA_API_KEY (env) para autorização Bearer;
- Opcional: REAL_DATA_MAX_BYTES (env) para limitar o tamanho baixado
  (padrão: 50 MiB).

Fronteira de claim:
este script materializa uma amostra/artefato de auditoria. Ele não valida RLL,
matéria escura, energia escura ou qualquer hipótese cosmológica.
"""

import argparse
import ipaddress
import json
import os
from pathlib import Path
import socket
import sys
from urllib.parse import urlparse

import pandas as pd
import requests

DEFAULT_MAX_BYTES = 50 * 1024 * 1024
BLOCKED_HOSTS = {"localhost", "localhost.localdomain"}


class ImportDataError(RuntimeError):
    """Erro operacional controlado para importação guardada."""


def parse_max_bytes() -> int:
    raw = os.environ.get("REAL_DATA_MAX_BYTES", str(DEFAULT_MAX_BYTES))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ImportDataError("REAL_DATA_MAX_BYTES deve ser inteiro") from exc
    if value <= 0:
        raise ImportDataError("REAL_DATA_MAX_BYTES deve ser positivo")
    return value


def _is_forbidden_ip(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return any(
        (
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_reserved,
            ip.is_multicast,
            ip.is_unspecified,
        )
    )


def _resolve_public_host(hostname: str) -> None:
    """Bloqueia localhost, IP literal privado e DNS que resolve para alvo local."""
    host = hostname.strip().rstrip(".").lower()
    if not host or host in BLOCKED_HOSTS or host.endswith(".local"):
        raise ImportDataError("URL deve apontar para host público, não local")

    try:
        if _is_forbidden_ip(host):
            raise ImportDataError("URL não pode apontar para IP privado/local/reservado")
        return
    except ValueError:
        pass

    try:
        resolved = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ImportDataError(f"Não foi possível resolver host da URL: {host}") from exc

    ips = {entry[4][0] for entry in resolved}
    if not ips:
        raise ImportDataError("Host da URL não retornou endereço IP")

    forbidden = [ip for ip in ips if _is_forbidden_ip(ip)]
    if forbidden:
        raise ImportDataError(
            "URL resolve para endereço privado/local/reservado: " + ", ".join(sorted(forbidden))
        )


def validate_public_https_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ImportDataError("URL deve usar HTTPS público explícito")
    if not parsed.hostname:
        raise ImportDataError("URL deve conter hostname")
    if parsed.username or parsed.password:
        raise ImportDataError("URL não deve conter credenciais embutidas")
    _resolve_public_host(parsed.hostname)
    return url


def fetch(url: str, api_key: str | None = None, max_bytes: int = DEFAULT_MAX_BYTES):
    validate_public_https_url(url)
    headers = {"Accept": "application/json, text/csv, text/plain;q=0.9, */*;q=0.1"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    with requests.get(url, headers=headers, timeout=30, stream=True) as resp:
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > max_bytes:
            raise ImportDataError(
                f"Arquivo remoto excede REAL_DATA_MAX_BYTES ({content_length} > {max_bytes})"
            )

        chunks: list[bytes] = []
        total = 0
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise ImportDataError(
                    f"Download excedeu REAL_DATA_MAX_BYTES ({total} > {max_bytes})"
                )
            chunks.append(chunk)

    payload = b"".join(chunks)
    text = payload.decode("utf-8-sig")
    return text, content_type, total


def save_json(obj, out_path):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)


def try_parse_text_as_json_or_csv(text, out_path):
    try:
        data = json.loads(text)
        save_json(data, out_path)
        return "json"
    except Exception:
        from io import StringIO

        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(StringIO(text))
        df.to_json(out, orient="records", force_ascii=False, indent=2)
        return "csv"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", help="URL HTTPS pública para baixar os dados", default=None)
    p.add_argument(
        "--out",
        help="Caminho do arquivo de saída (ex.: _audit/raw/data.json)",
        required=True,
    )
    args = p.parse_args()

    url = args.url or os.environ.get("REAL_DATA_URL")
    api_key = os.environ.get("REAL_DATA_API_KEY")

    if not url:
        print("ERRO: URL não fornecida via --url nem REAL_DATA_URL", file=sys.stderr)
        sys.exit(2)

    try:
        max_bytes = parse_max_bytes()
        text, content_type, total_bytes = fetch(url, api_key, max_bytes)
        out = args.out
        normalized = text.strip()
        if "application/json" in content_type or normalized.startswith(("{", "[")):
            try:
                data = json.loads(text)
                save_json(data, out)
                print(f"Dados JSON salvos em {out} ({total_bytes} bytes)")
            except Exception:
                parsed_as = try_parse_text_as_json_or_csv(text, out)
                print(f"Dados salvos por fallback {parsed_as} em {out} ({total_bytes} bytes)")
        else:
            parsed_as = try_parse_text_as_json_or_csv(text, out)
            print(f"Dados salvos como {parsed_as} em {out} ({total_bytes} bytes)")
    except (ImportDataError, requests.RequestException, UnicodeDecodeError, pd.errors.ParserError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
