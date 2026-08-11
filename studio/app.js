"use strict";

const STATUS = Object.freeze({
  PASS: { label: "Verificado", badge: "badge-pass", dot: "var(--success)" },
  FAIL: { label: "Não passou", badge: "badge-fail", dot: "var(--danger)" },
  BLOCKED: { label: "Bloqueado", badge: "badge-blocked", dot: "var(--blocked)" },
  OBSERVED: { label: "Observado", badge: "badge-limited", dot: "var(--warn)" },
  OBSERVED_LIMITED: { label: "Evidência parcial", badge: "badge-limited", dot: "var(--warn)" },
  TOKEN_VAZIO: { label: "Ainda não comprovado", badge: "badge-empty", dot: "var(--unknown)" },
  NOT_MEASURED: { label: "Não executado", badge: "badge-not-measured", dot: "var(--unknown)" },
  UNAVAILABLE: { label: "Indisponível", badge: "badge-not-measured", dot: "var(--unknown)" },
  INVALIDATED: { label: "Invalidado", badge: "badge-fail", dot: "var(--danger)" }
});

const VIEW_META = Object.freeze({
  home: ["Visão operacional", "Início"],
  experiment: ["Contrato interoperável", "Experimento"],
  results: ["Leitura científica", "Resultados"],
  evidence: ["Rastreabilidade", "Evidências"],
  library: ["Fontes vinculadas", "Biblioteca"]
});

const SAMPLE = Object.freeze({
  schema_version: "rll-experiment-manifest/1.0.0",
  manifest_id: "RLL-STUDIO-DEMO-20260808",
  manifest_state: "OBSERVED_LIMITED",
  demo: true,
  experiment: {
    id: "rll-cpl-coherence-demo",
    name: "RLL × ΛCDM — leitura de coerência",
    created_at: "2026-08-08T00:00:00Z",
    mode: "scientific-review",
    model: "RLL density family",
    comparator: "ΛCDM",
    dataset: { name: "DESI DR2 + Pantheon+", version: "referência demonstrativa", hash: "TOKEN_VAZIO" },
    parameters: { z_t: 1.164, w_t: 0.405, w0: -0.946549844, wa: 0.401622855 }
  },
  execution: {
    state: "OBSERVED_LIMITED",
    method: "coherence audit",
    environment: "repository evidence",
    commit: "TOKEN_VAZIO",
    duration_ms: null,
    receipt: "TOKEN_VAZIO"
  },
  claim: {
    allowed: false,
    state: "BLOCKED",
    reason: "Demonstração de UX: resultados parciais não autorizam promoção física/cosmológica completa."
  },
  summary: "A interface separa resultado, evidência e autoridade. O usuário entende primeiro o que foi observado; detalhes técnicos permanecem acessíveis sem serem escondidos.",
  results: {
    narrative: "O exemplo apresenta parâmetros e fronteiras de claim sem converter evidência parcial em validação física.",
    metrics: [
      { label: "w₀", value: "−0,9465", detail: "mapeamento local" },
      { label: "wₐ", value: "+0,4016", detail: "reconstrução conservada" },
      { label: "Background", value: "PASS", detail: "fenomenologia" },
      { label: "Claim", value: "BLOCKED", detail: "fail-closed" }
    ],
    parameters: [
      { name: "w₀", value: -0.946549844, uncertainty68: "TOKEN_VAZIO", state: "OBSERVED_LIMITED" },
      { name: "wₐ", value: 0.401622855, uncertainty68: "TOKEN_VAZIO", state: "OBSERVED_LIMITED" },
      { name: "zₜ", value: 1.164, uncertainty68: "TOKEN_VAZIO", state: "OBSERVED" },
      { name: "wₜ", value: 0.405, uncertainty68: "TOKEN_VAZIO", state: "OBSERVED" }
    ],
    comparison: {
      label: "Indicador visual demonstrativo — não é Bayes factor",
      entries: [
        { name: "RLL", score: 72, display: "parcial" },
        { name: "ΛCDM", score: 100, display: "baseline" }
      ],
      caption: "A barra é apenas um componente de demonstração da interface. Nenhuma superioridade estatística é inferida deste exemplo."
    }
  },
  evidence: [
    { id: "background", title: "Background fenomenológico", state: "PASS", summary: "Formulação de background executável/inspecionável.", source: "repository", test: "check_rll_background", receipt: "repository audit", limitation: "PASS de background não valida a teoria física completa.", next_gate: "inferência conjunta governada" },
    { id: "continuity", title: "Conservação com pressão documentada", state: "FAIL", summary: "O residual de continuidade não fecha durante a transição variável.", source: "math audit", test: "symbolic identity", receipt: "science audit", limitation: "A formulação documentada não representa fluido separadamente conservado neste regime.", next_gate: "usar reconstrução conservada ou modelo de interação explícito" },
    { id: "reconstruction", title: "Reconstrução conservada", state: "OBSERVED_LIMITED", summary: "Reconstrução diagnóstica disponível, com escopo deliberadamente limitado.", source: "science audit", test: "regression", receipt: "repository evidence", limitation: "Diagnóstico não equivale a EFT físico completo.", next_gate: "perturbações + estabilidade" },
    { id: "perturbations", title: "Perturbações RLL exatas", state: "TOKEN_VAZIO", summary: "Ainda não há evidência suficiente para promover este eixo.", source: "TOKEN_VAZIO", test: "NOT_MEASURED", receipt: "TOKEN_VAZIO", limitation: "Sem este gate, claims de crescimento/estrutura permanecem limitados.", next_gate: "implementar e confrontar CLASS/CAMB" },
    { id: "eft", title: "EFT físico completo", state: "BLOCKED", summary: "Dependências científicas anteriores ainda não estão fechadas.", source: "claim gate", test: "dependency gate", receipt: "BLOCKED", limitation: "Bloqueio é um estado válido, não falha de interface.", next_gate: "fechar continuidade, perturbações e estabilidade" },
    { id: "replication", title: "Replicação externa independente", state: "NOT_MEASURED", summary: "Nenhuma replicação externa é assumida.", source: "external authority", test: "NOT_MEASURED", receipt: "TOKEN_VAZIO", limitation: "CI interna não substitui reprodução independente.", next_gate: "pacote reprodutível + executor externo" }
  ],
  interoperability: [
    { name: "JSON", state: "PASS", detail: "manifest canônico" },
    { name: "CLI", state: "OBSERVED_LIMITED", detail: "adapter pendente" },
    { name: "Jupyter", state: "OBSERVED_LIMITED", detail: "Python disponível" },
    { name: "CI", state: "PASS", detail: "gates existentes" },
    { name: "CLASS/CAMB", state: "OBSERVED_LIMITED", detail: "comparação parcial" },
    { name: "Drive/GitHub", state: "PASS", detail: "proveniência" }
  ],
  library: [
    { type: "modelo", title: "RLL density family", description: "Família fenomenológica de densidade usada na leitura demonstrativa.", ref: "docs/science" },
    { type: "baseline", title: "ΛCDM", description: "Modelo de referência para comparações governadas.", ref: "scientific baseline" },
    { type: "dataset", title: "DESI DR2", description: "Fonte observacional moderna vinculada à trilha de auditoria.", ref: "data/real" },
    { type: "dataset", title: "Pantheon+", description: "Supernovas usadas em rotas de validação cosmológica.", ref: "data/real" },
    { type: "evidência", title: "Science audit", description: "Documento/receipt que limita explicitamente o que pode ser alegado.", ref: "docs/science" },
    { type: "governança", title: "Claim gate", description: "Autoridade é produzida pelo pipeline de evidência, nunca pela UI.", ref: "claim_allowed=false" }
  ]
});

let currentManifest = structuredCloneSafe(SAMPLE);
let selectedEvidenceId = null;

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function structuredCloneSafe(value) {
  return typeof structuredClone === "function" ? structuredClone(value) : JSON.parse(JSON.stringify(value));
}

function text(value, fallback = "—") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function statusMeta(state) {
  return STATUS[state] || { label: text(state, "Desconhecido"), badge: "badge-not-measured", dot: "var(--unknown)" };
}

function setBadge(element, state, overrideLabel) {
  const meta = statusMeta(state);
  element.className = `badge ${meta.badge}`;
  element.textContent = overrideLabel || meta.label;
}

function showNotice(message, type = "success") {
  const el = $("#notice");
  el.hidden = false;
  el.className = `notice is-${type}`;
  el.textContent = message;
  window.clearTimeout(showNotice.timer);
  showNotice.timer = window.setTimeout(() => { el.hidden = true; }, 5000);
}

function validateManifest(candidate) {
  const errors = [];
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) errors.push("manifest deve ser um objeto JSON");
  if (candidate?.schema_version !== "rll-experiment-manifest/1.0.0") errors.push("schema_version incompatível");
  if (!candidate?.manifest_id) errors.push("manifest_id ausente");
  if (!candidate?.experiment?.id) errors.push("experiment.id ausente");
  if (!candidate?.experiment?.model) errors.push("experiment.model ausente");
  if (candidate?.claim?.allowed !== false) errors.push("claim.allowed deve ser false; a UI não possui autoridade de promoção");
  if (!candidate?.claim?.state) errors.push("claim.state ausente");
  if (!Array.isArray(candidate?.evidence)) errors.push("evidence deve ser uma lista");
  for (const item of candidate?.evidence || []) {
    if (!item.id || !item.title || !item.state) errors.push("cada evidência exige id, title e state");
    if (!STATUS[item.state]) errors.push(`estado de evidência não reconhecido: ${text(item.state)}`);
  }
  return errors;
}

function navigate(view) {
  if (!VIEW_META[view]) return;
  $$(".nav-item").forEach(button => {
    const active = button.dataset.view === view;
    button.classList.toggle("is-active", active);
    if (active) button.setAttribute("aria-current", "page"); else button.removeAttribute("aria-current");
  });
  $$(".view").forEach(panel => panel.classList.toggle("is-active", panel.dataset.viewPanel === view));
  $("#contextEyebrow").textContent = VIEW_META[view][0];
  $("#contextTitle").textContent = VIEW_META[view][1];
  $("#main").focus({ preventScroll: true });
  $(".sidebar").classList.remove("is-open");
  $("#mobileMenu").setAttribute("aria-expanded", "false");
}

function renderDefinitionList(root, entries) {
  root.replaceChildren();
  entries.forEach(([label, value]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = text(value);
    root.append(dt, dd);
  });
}

function renderHome(m) {
  $("#summaryText").textContent = text(m.summary, "Nenhum resumo disponível.");
  const claimState = m.claim?.allowed === true ? "PASS" : text(m.claim?.state, "BLOCKED");
  setBadge($("#claimBadge"), claimState, m.claim?.allowed === true ? "Autorizado" : "Bloqueado");
  $("#claimReason").textContent = text(m.claim?.reason, "Sem justificativa de claim no manifest.");
  $("#sideClaim").textContent = m.claim?.allowed === true ? "Autorizado" : "Bloqueado";
  $("#sideStatusDot").style.background = statusMeta(claimState).dot;
  $("#sideStatusDot").style.boxShadow = `0 0 0 4px color-mix(in srgb, ${statusMeta(claimState).dot} 18%, transparent)`;

  $("#metricModel").textContent = text(m.experiment?.model);
  $("#metricComparator").textContent = `vs ${text(m.experiment?.comparator, "sem comparador")}`;
  $("#metricDataset").textContent = text(m.experiment?.dataset?.name);
  $("#metricDatasetVersion").textContent = text(m.experiment?.dataset?.version, "versão não declarada");
  $("#metricRun").textContent = statusMeta(m.execution?.state).label;
  $("#metricRunTime").textContent = m.execution?.duration_ms == null ? text(m.execution?.method, "tempo não medido") : `${m.execution.duration_ms} ms`;
  $("#metricEvidence").textContent = statusMeta(m.manifest_state).label;
  $("#metricEvidenceDetail").textContent = `${(m.evidence || []).length} eixos explícitos`;
}

function renderExperiment(m) {
  setBadge($("#experimentStateBadge"), m.manifest_state);
  renderDefinitionList($("#experimentIdentity"), [
    ["ID", m.experiment?.id],
    ["Nome", m.experiment?.name],
    ["Modelo", m.experiment?.model],
    ["Comparador", m.experiment?.comparator],
    ["Dataset", m.experiment?.dataset?.name],
    ["Versão", m.experiment?.dataset?.version],
    ["Hash", m.experiment?.dataset?.hash],
    ["Método", m.execution?.method],
    ["Ambiente", m.execution?.environment],
    ["Commit", m.execution?.commit]
  ]);

  const parameterList = $("#parameterList");
  parameterList.replaceChildren();
  const params = m.experiment?.parameters || {};
  Object.entries(params).forEach(([key, value]) => {
    const row = document.createElement("div"); row.className = "parameter-row";
    const label = document.createElement("span"); label.textContent = key;
    const code = document.createElement("code"); code.textContent = text(value);
    row.append(label, code); parameterList.append(row);
  });
  if (!Object.keys(params).length) parameterList.textContent = "Nenhum parâmetro declarado.";

  const interop = $("#interopGrid"); interop.replaceChildren();
  (m.interoperability || []).forEach(item => {
    const card = document.createElement("div"); card.className = "interop-item";
    const strong = document.createElement("strong"); strong.textContent = item.name;
    const small = document.createElement("small"); small.textContent = `${statusMeta(item.state).label} · ${text(item.detail)}`;
    card.append(strong, small); interop.append(card);
  });
}

function renderResults(m) {
  $("#resultNarrative").textContent = text(m.results?.narrative, "Nenhum resultado declarado.");
  const metrics = $("#resultMetrics"); metrics.replaceChildren();
  (m.results?.metrics || []).forEach(item => {
    const card = document.createElement("article"); card.className = "metric-card";
    const label = document.createElement("span"); label.textContent = text(item.label);
    const strong = document.createElement("strong"); strong.textContent = text(item.value);
    const small = document.createElement("small"); small.textContent = text(item.detail);
    card.append(label, strong, small); metrics.append(card);
  });

  const tbody = $("#parameterResults"); tbody.replaceChildren();
  (m.results?.parameters || []).forEach(item => {
    const tr = document.createElement("tr");
    [item.name, item.value, item.uncertainty68].forEach(value => {
      const td = document.createElement("td"); td.textContent = text(value); tr.append(td);
    });
    const tdState = document.createElement("td"); const badge = document.createElement("span");
    setBadge(badge, item.state); tdState.append(badge); tr.append(tdState); tbody.append(tr);
  });

  $("#comparisonLabel").textContent = text(m.results?.comparison?.label);
  $("#comparisonCaption").textContent = text(m.results?.comparison?.caption, "");
  const bars = $("#comparisonBars"); bars.replaceChildren();
  const entries = m.results?.comparison?.entries || [];
  const max = Math.max(1, ...entries.map(item => Number(item.score) || 0));
  entries.forEach(item => {
    const row = document.createElement("div"); row.className = "bar-row";
    const name = document.createElement("strong"); name.textContent = text(item.name);
    const track = document.createElement("div"); track.className = "bar-track"; track.setAttribute("aria-label", `${text(item.name)}: ${text(item.display)}`);
    const fill = document.createElement("div"); fill.className = "bar-fill"; fill.style.width = `${Math.max(0, Math.min(100, (Number(item.score) || 0) / max * 100))}%`;
    const value = document.createElement("span"); value.textContent = text(item.display, item.score);
    track.append(fill); row.append(name, track, value); bars.append(row);
  });
}

function renderEvidence(m) {
  const filter = $("#evidenceFilter").value;
  const list = $("#evidenceList"); list.replaceChildren();
  const items = (m.evidence || []).filter(item => filter === "ALL" || item.state === filter);
  items.forEach(item => {
    const row = document.createElement("button"); row.type = "button"; row.className = "evidence-row"; row.dataset.evidenceId = item.id;
    if (item.id === selectedEvidenceId) row.classList.add("is-selected");
    const content = document.createElement("div"); const title = document.createElement("strong"); const summary = document.createElement("small");
    title.textContent = item.title; summary.textContent = text(item.summary); content.append(title, summary);
    const badge = document.createElement("span"); setBadge(badge, item.state);
    row.append(content, badge); row.addEventListener("click", () => selectEvidence(item.id)); list.append(row);
  });
  if (!items.length) list.textContent = "Nenhuma evidência corresponde ao filtro.";

  if (!selectedEvidenceId && items.length) selectEvidence(items[0].id, false);
  else if (selectedEvidenceId) {
    const exists = (m.evidence || []).some(item => item.id === selectedEvidenceId);
    if (!exists) selectedEvidenceId = null;
    renderEvidenceDetail((m.evidence || []).find(item => item.id === selectedEvidenceId));
  }
}

function selectEvidence(id, rerenderList = true) {
  selectedEvidenceId = id;
  const item = (currentManifest.evidence || []).find(entry => entry.id === id);
  renderEvidenceDetail(item);
  if (rerenderList) renderEvidence(currentManifest);
}

function renderEvidenceDetail(item) {
  if (!item) {
    $("#evidenceDetailTitle").textContent = "Selecione uma evidência";
    $("#evidenceDetailSummary").textContent = "O detalhe aparece aqui sem poluir a visão principal.";
    $("#evidenceDetail").replaceChildren();
    return;
  }
  $("#evidenceDetailTitle").textContent = item.title;
  $("#evidenceDetailSummary").textContent = text(item.summary);
  renderDefinitionList($("#evidenceDetail"), [
    ["Estado", statusMeta(item.state).label],
    ["Fonte", item.source],
    ["Teste", item.test],
    ["Receipt", item.receipt],
    ["Limitação", item.limitation],
    ["Próximo gate", item.next_gate]
  ]);
}

function renderLibrary(m) {
  const grid = $("#libraryGrid"); grid.replaceChildren();
  (m.library || []).forEach(item => {
    const card = document.createElement("article"); card.className = "library-card";
    const type = document.createElement("span"); type.className = "type"; type.textContent = text(item.type);
    const title = document.createElement("h3"); title.textContent = text(item.title);
    const description = document.createElement("p"); description.textContent = text(item.description);
    const ref = document.createElement("code"); ref.textContent = text(item.ref);
    card.append(type, title, description, ref); grid.append(card);
  });
}

function renderAll() {
  renderHome(currentManifest);
  renderExperiment(currentManifest);
  renderResults(currentManifest);
  renderEvidence(currentManifest);
  renderLibrary(currentManifest);
  $("#footerManifest").textContent = `manifest: ${text(currentManifest.manifest_id)}`;
}

function createBlankManifest() {
  const now = new Date().toISOString();
  return {
    schema_version: "rll-experiment-manifest/1.0.0",
    manifest_id: `RLL-DRAFT-${now.replace(/[^0-9]/g, "").slice(0, 14)}`,
    manifest_state: "NOT_MEASURED",
    experiment: {
      id: "new-experiment",
      name: "Novo experimento RLL",
      created_at: now,
      mode: "draft",
      model: "TOKEN_VAZIO",
      comparator: "ΛCDM",
      dataset: { name: "TOKEN_VAZIO", version: "TOKEN_VAZIO", hash: "TOKEN_VAZIO" },
      parameters: {}
    },
    execution: { state: "NOT_MEASURED", method: "TOKEN_VAZIO", environment: "TOKEN_VAZIO", commit: "TOKEN_VAZIO", duration_ms: null, receipt: "TOKEN_VAZIO" },
    claim: { allowed: false, state: "BLOCKED", reason: "Novo experimento nasce fail-closed até evidência explícita ser produzida." },
    summary: "Configure dados, modelo e método; execute fora da camada de apresentação; depois importe o manifest/receipt produzido pelo pipeline.",
    results: { narrative: "Ainda não executado.", metrics: [], parameters: [], comparison: { label: "Não medido", entries: [], caption: "" } },
    evidence: [
      { id: "execution", title: "Execução científica", state: "NOT_MEASURED", summary: "Execução ainda não registrada.", source: "TOKEN_VAZIO", test: "NOT_MEASURED", receipt: "TOKEN_VAZIO", limitation: "Sem execução não há claim.", next_gate: "executar pipeline governado" }
    ],
    interoperability: [
      { name: "JSON", state: "PASS", detail: "manifest v1" },
      { name: "CLI", state: "TOKEN_VAZIO", detail: "adapter não declarado" },
      { name: "Jupyter", state: "TOKEN_VAZIO", detail: "adapter não declarado" },
      { name: "CI", state: "TOKEN_VAZIO", detail: "receipt não importado" }
    ],
    library: []
  };
}

async function importManifest(file) {
  try {
    if (!file || file.size > 5 * 1024 * 1024) throw new Error("arquivo ausente ou maior que 5 MiB");
    const parsed = JSON.parse(await file.text());
    const errors = validateManifest(parsed);
    if (errors.length) throw new Error(errors.join("; "));
    currentManifest = parsed;
    selectedEvidenceId = null;
    renderAll(); navigate("home");
    showNotice(`Manifest ${text(parsed.manifest_id)} carregado com validação mínima fail-closed.`, "success");
  } catch (error) {
    showNotice(`Manifest rejeitado: ${error.message}`, "error");
  }
}

function exportManifest() {
  const json = JSON.stringify(currentManifest, null, 2) + "\n";
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = `${text(currentManifest.manifest_id, "rll-manifest")}.json`;
  document.body.append(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
}

function bindEvents() {
  $$(".nav-item").forEach(button => button.addEventListener("click", () => navigate(button.dataset.view)));
  $$('[data-go]').forEach(button => button.addEventListener("click", () => navigate(button.dataset.go)));
  $("#mobileMenu").addEventListener("click", () => {
    const side = $(".sidebar"); const open = side.classList.toggle("is-open");
    $("#mobileMenu").setAttribute("aria-expanded", String(open));
  });
  $("#manifestInput").addEventListener("change", event => importManifest(event.target.files?.[0]));
  $("#exportManifest").addEventListener("click", exportManifest);
  $("#newExperiment").addEventListener("click", () => {
    currentManifest = createBlankManifest(); selectedEvidenceId = null; renderAll(); navigate("experiment");
    showNotice("Novo manifest criado em estado NOT_MEASURED/BLOCKED. Exporte-o para integrar ao pipeline.", "success");
  });
  $("#evidenceFilter").addEventListener("change", () => { selectedEvidenceId = null; renderEvidence(currentManifest); });
  $("#copyParameters").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(currentManifest.experiment?.parameters || {}, null, 2));
      showNotice("Parâmetros copiados.", "success");
    } catch (_) { showNotice("Clipboard indisponível neste contexto; use Exportar.", "error"); }
  });
  $("#themeToggle").addEventListener("click", () => {
    const root = document.documentElement;
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    root.dataset.theme = next; localStorage.setItem("rll-studio-theme", next);
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      $(".sidebar").classList.remove("is-open");
      $("#mobileMenu").setAttribute("aria-expanded", "false");
    }
  });
}

function initTheme() {
  const saved = localStorage.getItem("rll-studio-theme");
  if (saved === "dark" || saved === "light") document.documentElement.dataset.theme = saved;
}

initTheme();
bindEvents();
renderAll();
