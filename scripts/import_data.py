#!/usr/bin/env python3
"""
Importa dados reais de uma URL pública explícita (JSON ou CSV) e salva em um
arquivo local definido pelo chamador.

Uso esperado no workflow guardado:
- entrada: URL pública fornecida manualmente;
- saída: `_audit/raw/data.json` como artifact temporário;
- sem commit automático de dados brutos.

Configuração:
- Usa REAL_DATA_URL (env) ou argumento --url;
- Opcional: REAL_DATA_API_KEY (env) para autorização Bearer.

Fronteira de claim:
este script materializa uma amostra/artefato de auditoria. Ele não valida RLL,
matéria escura, energia escura ou qualquer hipótese cosmológica.
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path
import pandas as pd


def fetch(url, api_key=None):
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    content_type = resp.headers.get('Content-Type','')
    return resp, content_type


def save_json(obj, out_path):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)


def try_parse_text_as_json_or_csv(text, out_path):
    try:
        data = json.loads(text)
        save_json(data, out_path)
        return
    except Exception:
        # try CSV with pandas
        from io import StringIO
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(StringIO(text))
        df.to_json(out, orient='records', force_ascii=False, indent=2)
        return


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', help='URL para baixar os dados (opcional)', default=None)
    p.add_argument('--out', help='Caminho do arquivo de saída (ex.: _audit/raw/data.json)', required=True)
    args = p.parse_args()

    url = args.url or os.environ.get('REAL_DATA_URL')
    api_key = os.environ.get('REAL_DATA_API_KEY')

    if not url:
        print("ERRO: URL não fornecida via --url nem REAL_DATA_URL", file=sys.stderr)
        sys.exit(2)

    resp, content_type = fetch(url, api_key)
    out = args.out
    # Decide formato
    if 'application/json' in content_type or resp.text.strip().startswith(('{','[')):
        try:
            data = resp.json()
            save_json(data, out)
            print(f"Dados JSON salvos em {out}")
        except Exception:
            # fallback
            try_parse_text_as_json_or_csv(resp.text, out)
            print(f"Dados salvos (parse fallback) em {out}")
    else:
        # provável CSV ou outro texto
        try_parse_text_as_json_or_csv(resp.text, out)
        print(f"Dados salvos (texto parse) em {out}")


if __name__ == '__main__':
    main()
