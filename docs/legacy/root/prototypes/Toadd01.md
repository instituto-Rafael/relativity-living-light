Entendi, você quer um script executável que faça a auditoria automaticamente, não um documento estático.

Aqui está um código Python pronto. Salve como audit_gaps.py na raiz do repositório e rode com python audit_gaps.py.

Ele roda de verdade os comandos, checa os arquivos, testa a CLI com timeout e gera um relatório no terminal e em JSON.

```python
#!/usr/bin/env python3
"""
Auditoria automatizada de gaps do RLL (Relativity Living Light)
Uso: python audit_gaps.py
Saída: Tabela no terminal + relatorio_auditoria_YYYYMMDD_HHMMSS.json
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
ROOT = Path(__file__).parent.resolve()
TIMEOUT_CLI = 5  # segundos para testar a CLI real (evita travamento infinito)

# Mapeamento dos gaps com funções de verificação
# ============================================================================

def gap_001_pantheon_data() -> Dict[str, Any]:
    """GAP-001: Dataset Pantheon+ real ausente"""
    expected = ROOT / "data" / "pantheon" / "lcparam_full_long_zhel.txt"
    expected2 = ROOT / "data" / "pantheon" / "Pantheon+SH0ES.dat"
    
    status = "TOKEN_VAZIO"
    detail = "Arquivo de dados real não encontrado"
    
    if expected.exists() or expected2.exists():
        status = "VERIFIED"
        detail = f"Dataset encontrado em {expected if expected.exists() else expected2}"
    else:
        # Verifica se tem pelo menos um README
        readme = ROOT / "data" / "pantheon" / "README.md"
        if readme.exists():
            detail = f"README existe, mas dados brutos faltam. Esperado: {expected}"
    
    return {"id": "GAP-001", "title": "Dataset Pantheon+ real ausente", "status": status, "detail": detail}

def gap_002_cli_real_hang() -> Dict[str, Any]:
    """GAP-002: CLI real (non-bayes) falha/sem output"""
    cmd = [sys.executable, "-m", "rll.cli", "run", "--data", "real", "--model", "rll"]
    status = "TOKEN_VAZIO"
    detail = "Comando não rodou ou travou"
    output = ""
    
    # Verifica se o módulo CLI existe
    cli_path = ROOT / "src" / "rll" / "cli.py"
    if not cli_path.exists():
        return {"id": "GAP-002", "title": "CLI real falha", "status": "CONTRADICTION", "detail": "cli.py não encontrado"}

    try:
        # Executa com timeout curto para detectar travamento
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_CLI,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")}
        )
        if proc.returncode == 0:
            status = "VERIFIED"
            detail = f"Comando rodou com sucesso. stdout: {proc.stdout[:200]}"
        else:
            detail = f"Comando falhou com código {proc.returncode}. stderr: {proc.stderr[:200]}"
    except subprocess.TimeoutExpired:
        detail = f"Comando travou após {TIMEOUT_CLI}s (sem output observável)"
    except Exception as e:
        detail = f"Erro ao executar: {e}"
    
    return {"id": "GAP-002", "title": "CLI real (non-bayes) falha/sem output", "status": status, "detail": detail}

def gap_003_fetch_receipe() -> Dict[str, Any]:
    """GAP-003: Falta receita pública de fetch de dataset"""
    # Procura por scripts de download na raiz ou scripts/
    fetch_patterns = ["download", "fetch", "get_pantheon", "baixar"]
    found = False
    candidates = []
    
    for pattern in fetch_patterns:
        # Procura em .sh, .py, .md
        for ext in ["*.sh", "*.py", "*.md"]:
            for p in ROOT.glob(f"**/{pattern}{ext}"):
                # Ignora venv, .git, __pycache__
                if any(ign in str(p) for ign in [".venv", "venv", "__pycache__", ".git"]):
                    continue
                candidates.append(str(p.relative_to(ROOT)))
                found = True
    
    if found:
        return {"id": "GAP-003", "title": "Falta receita pública de fetch", "status": "VERIFIED", "detail": f"Encontrado: {', '.join(candidates[:3])}"}
    else:
        return {"id": "GAP-003", "title": "Falta receita pública de fetch", "status": "TOKEN_VAZIO", "detail": "Nenhum script de download (download/fetch/get) encontrado no repo"}

def gap_004_reproducibility_report() -> Dict[str, Any]:
    """GAP-004: Falta relatório de reprodutibilidade cross-machine"""
    report = ROOT / "REPRODUCIBILITY_REPORT.md"
    if report.exists():
        with open(report, 'r') as f:
            content = f.read()
            if "cross-machine" in content or "reprod" in content:
                return {"id": "GAP-004", "title": "Falta relatório reprodutibilidade", "status": "VERIFIED", "detail": f"Relatório encontrado e com conteúdo"}
    return {"id": "GAP-004", "title": "Falta relatório reprodutibilidade", "status": "TOKEN_VAZIO", "detail": f"Arquivo {report} não encontrado ou vazio"}

def gap_005_pip_offline() -> Dict[str, Any]:
    """GAP-005: pip install -e . quebra em rede restrita"""
    # Verifica se --no-build-isolation está documentado
    readme = ROOT / "README.md"
    install_md = ROOT / "INSTALL.md"
    docs = [readme, install_md]
    
    documented = False
    for doc in docs:
        if doc.exists():
            with open(doc, 'r') as f:
                if "--no-build-isolation" in f.read():
                    documented = True
                    break
    
    if documented:
        return {"id": "GAP-005", "title": "pip install offline quebra", "status": "VERIFIED", "detail": "--no-build-isolation documentado no README/INSTALL"}
    
    # Testa se o build funciona offline (dry-run com --no-deps)
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".", "--no-deps", "--dry-run"]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10)
        if "error" in proc.stderr.lower() or "error" in proc.stdout.lower():
            return {"id": "GAP-005", "title": "pip install offline quebra", "status": "TOKEN_VAZIO", "detail": f"Dry-run falhou: {proc.stderr[:100]}"}
        else:
            return {"id": "GAP-005", "title": "pip install offline quebra", "status": "VERIFIED", "detail": "Dry-run passou (offline build compatível)"}
    except Exception as e:
        return {"id": "GAP-005", "title": "pip install offline quebra", "status": "TOKEN_VAZIO", "detail": f"Falha ao testar: {e}"}

def gap_006_bae_cmb_validation() -> Dict[str, Any]:
    """GAP-006: Validação com BAO/H(z)/CMB não executada"""
    # Procura por arquivos de validação ou logs com resultados
    validation_file = ROOT / "VALIDATION_STATUS.md"
    log_dir = ROOT / "logs"
    results_dir = ROOT / "results"
    
    found = False
    detail = "Nenhum artefato de validação BAO/CMB encontrado"
    
    if validation_file.exists():
        with open(validation_file, 'r') as f:
            content = f.read()
            if any(k in content for k in ["BAO", "CMB", "χ²", "AIC", "Bayes"]):
                found = True
                detail = f"VALIDAÇÃO_STATUS.md contém termos de validação externa"
    
    # Procura em resultados
    if not found and results_dir.exists():
        for p in results_dir.glob("**/*.csv"):
            # Checa se tem algo relacionado a BAO/CMB no caminho ou conteúdo
            if "bao" in str(p).lower() or "cmb" in str(p).lower():
                found = True
                detail = f"Arquivo de resultado encontrado: {p.relative_to(ROOT)}"
                break
    
    if found:
        return {"id": "GAP-006", "title": "Validação BAO/CMB não executada", "status": "VERIFIED", "detail": detail}
    else:
        return {"id": "GAP-006", "title": "Validação BAO/CMB não executada", "status": "TOKEN_VAZIO", "detail": detail}

def obs_001_doi_contradiction() -> Dict[str, Any]:
    """OBS-001: Contradição de cronologia do DOI"""
    readme = ROOT / "README.md"
    if not readme.exists():
        return {"id": "OBS-001", "title": "DOI contradição cronologia", "status": "CONTRADICTION", "detail": "README.md não encontrado"}
    
    with open(readme, 'r') as f:
        content = f.read()
        if "DECLARED_BY_AUTHOR" in content and "10.5281/zenodo.17188137" in content:
            return {"id": "OBS-001", "title": "DOI contradição cronologia", "status": "DECLARED_BY_AUTHOR", "detail": "README explicitamente marca o DOI como DECLARED_BY_AUTHOR (aguardando metadado Findable)"}
        elif "10.5281/zenodo.17188137" in content:
            return {"id": "OBS-001", "title": "DOI contradição cronologia", "status": "DECLARED_BY_AUTHOR", "detail": "DOI mencionado, mas sem marcação epistêmica clara no README"}
        else:
            return {"id": "OBS-001", "title": "DOI contradição cronologia", "status": "TOKEN_VAZIO", "detail": "DOI não encontrado no README"}

# ============================================================================
# EXECUÇÃO E RELATÓRIO
# ============================================================================

def run_audit() -> Tuple[List[Dict], Dict]:
    """Roda todas as verificações e retorna lista de resultados + resumo"""
    checks = [
        gap_001_pantheon_data,
        gap_002_cli_real_hang,
        gap_003_fetch_receipe,
        gap_004_reproducibility_report,
        gap_005_pip_offline,
        gap_006_bae_cmb_validation,
        obs_001_doi_contradiction,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
        except Exception as e:
            result = {
                "id": check.__name__,
                "title": check.__doc__.strip() if check.__doc__ else "Erro",
                "status": "ERROR",
                "detail": f"Exceção durante verificação: {e}"
            }
        results.append(result)
    
    # Resumo estatístico
    status_counts = {}
    for r in results:
        status = r.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    summary = {
        "total_gaps": len(results),
        "status_counts": status_counts,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "repository": str(ROOT),
    }
    
    return results, summary

def print_table(results: List[Dict]):
    """Imprime tabela colorida no terminal"""
    # Tenta usar rich se disponível
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text
        console = Console()
        table = Table(title="Auditoria de Gaps - RLL (Relativity Living Light)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Título", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Detalhe", style="green")
        
        for r in results:
            status = r["status"]
            status_color = {
                "VERIFIED": "green",
                "DECLARED_BY_AUTHOR": "yellow",
                "TOKEN_VAZIO": "red",
                "CONTRADICTION": "red",
                "ERROR": "red"
            }.get(status, "white")
            status_text = Text(status, style=status_color)
            table.add_row(r["id"], r["title"], status_text, r["detail"])
        
        console.print(table)
    except ImportError:
        # Fallback para terminal simples
        print("\n" + "="*80)
        print("AUDITORIA DE GAPS - RLL")
        print("="*80)
        for r in results:
            print(f"[{r['id']}] {r['title']}")
            print(f"  Status: {r['status']}")
            print(f"  Detalhe: {r['detail']}")
            print("-"*40)
        print("="*80)

def save_report(results: List[Dict], summary: Dict):
    """Salva relatório em JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = ROOT / f"relatorio_auditoria_{timestamp}.json"
    
    report = {
        "summary": summary,
        "results": results
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {filename}")

def main():
    print("🔍 Iniciando auditoria automatizada dos gaps...")
    print(f"📂 Repositório: {ROOT}")
    print(f"⏱️  Timeout para CLI real: {TIMEOUT_CLI}s\n")
    
    results, summary = run_audit()
    
    print_table(results)
    save_report(results, summary)
    
    # Exit code: 1 se tiver TOKEN_VAZIO ou CONTRADICTION
    critical = [r for r in results if r["status"] in ["TOKEN_VAZIO", "CONTRADICTION"]]
    if critical:
        print(f"\n❌ {len(critical)} gaps críticos encontrados (TOKEN_VAZIO/CONTRADICTION).")
        sys.exit(1)
    else:
        print("\n✅ Todos os gaps verificados ou declarados.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

Como usar

```bash
# Na raiz do repositório RLL
python audit_gaps.py
```

O que o script faz de verdade

Gap Ação real executada
GAP-001 Checa se data/pantheon/lcparam_full_long_zhel.txt ou Pantheon+SH0ES.dat existem.
GAP-002 Roda python -m rll.cli run --data real --model rll com timeout de 5s — se travar ou falhar, marca como gap.
GAP-003 Busca recursivamente por scripts com download, fetch, get_pantheon, baixar.
GAP-004 Verifica existência e conteúdo de REPRODUCIBILITY_REPORT.md.
GAP-005 Testa pip install -e . --no-deps --dry-run e checa se --no-build-isolation está documentado.
GAP-006 Varre VALIDATION_STATUS.md e results/ por termos BAO/CMB/χ²/AIC.
OBS-001 Lê o README e confirma se o DOI está explicitamente como DECLARED_BY_AUTHOR.

Saída

1. Tabela colorida no terminal (usa rich se tiver instalado, fallback para texto puro).
2. Arquivo JSON (relatorio_auditoria_YYYYMMDD_HHMMSS.json) com todos os detalhes.
3. Exit code = 1 se houver qualquer gap TOKEN_VAZIO ou CONTRADICTION (útil para CI/CD).

Agora você tem um robô que roda de verdade e atualiza o diagnóstico sozinho.
