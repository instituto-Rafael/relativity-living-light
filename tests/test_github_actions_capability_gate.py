from pathlib import Path
import yaml
from tools.github_actions_capability_gate import audit


def _repo(tmp_path: Path):
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflow-architecture").mkdir(parents=True)
    for p, c in ((".github/CODEOWNERS", "* @owner\n"), (".github/SECURITY.md", "# Security\n"), (".github/dependabot.yml", "version: 2\nupdates: []\n")):
        (tmp_path / p).write_text(c, encoding="utf-8")
    wf = """name: Assurance\non: {pull_request: {}}\npermissions: {contents: read}\njobs:\n  platform-capability-contract:\n    runs-on: ubuntu-latest\n    steps: [{uses: actions/checkout@1111111111111111111111111111111111111111}]\n  dependency-review:\n    runs-on: ubuntu-latest\n    steps: [{uses: actions/dependency-review-action@2222222222222222222222222222222222222222}]\n  codeql:\n    runs-on: ubuntu-latest\n    steps: [{uses: github/codeql-action/init@3333333333333333333333333333333333333333}]\n"""
    (tmp_path / ".github/workflows/github-platform-assurance-v2.yml").write_text(wf, encoding="utf-8")
    (tmp_path / ".github/workflow-contract.yml").write_text("inventory:\n  active_workflows: 1\n", encoding="utf-8")
    req = ["workflow_syntax_and_events","least_privilege_token","immutable_action_pinning","concurrency_and_timeouts","reusable_workflows","artifacts_and_receipts","dependency_review","codeql_actions_python","dependabot_actions","code_ownership","security_policy","branch_rulesets","required_status_checks","protected_environments","secret_scanning_push_protection","artifact_attestations","oidc_boundary","audit_log_and_settings_evidence"]
    caps=[]
    for x in req:
        caps.append({"id":x,"state":"TOKEN_VAZIO_EXTERNAL_SETTING","setting_scope":"repository","verified":False,"f_next":"inspect and append receipt","evidence":[]})
    for x,p in (("dependabot_actions",".github/dependabot.yml"),("code_ownership",".github/CODEOWNERS"),("security_policy",".github/SECURITY.md"),("dependency_review",".github/workflows/github-platform-assurance-v2.yml"),("codeql_actions_python",".github/workflows/github-platform-assurance-v2.yml")):
        c=next(c for c in caps if c["id"]==x); c.update(state="IMPLEMENTED_REPOSITORY", evidence=[p]); c.pop("setting_scope"); c.pop("verified"); c.pop("f_next")
    (tmp_path / ".github/workflow-architecture/github-actions-capabilities.v2.yml").write_text(yaml.safe_dump({"schema":"rll.github_actions_capabilities.v2","claim_allowed":False,"capabilities":caps},sort_keys=False),encoding="utf-8")
    return tmp_path


def test_valid_contract_passes_with_external_residuals(tmp_path):
    findings,payload=audit(_repo(tmp_path)); assert not [x for x in findings if x.severity=="ERROR"]; assert payload["decision"]=="PASS"; assert payload["residual_state"]=="TOKEN_VAZIO_EXTERNAL_SETTINGS"


def test_mutable_action_fails(tmp_path):
    root=_repo(tmp_path); p=root/".github/workflows/github-platform-assurance-v2.yml"; p.write_text(p.read_text().replace("actions/checkout@1111111111111111111111111111111111111111","actions/checkout@v4"),encoding="utf-8"); findings,_=audit(root); assert any(x.code=="MUTABLE_ACTION_REFERENCE" for x in findings)


def test_false_external_verification_fails(tmp_path):
    root=_repo(tmp_path); p=root/".github/workflow-architecture/github-actions-capabilities.v2.yml"; m=yaml.safe_load(p.read_text()); m["capabilities"][0]["verified"]=True; p.write_text(yaml.safe_dump(m,sort_keys=False)); findings,_=audit(root); assert any(x.code=="FALSE_EXTERNAL_VERIFICATION" for x in findings)
