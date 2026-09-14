#!/usr/bin/env python3
"""
Polymathic Concept Matrix Synthesis Engine (PCMSE) — RLL/RAFAELIA
Cross-domain knowledge orchestrator: formulas × biological metaphors × academic refs.

Architecture:
  1. Load equation/concept registry (rll_equation_registry.yml)
  2. Apply polymathic bridges (biological↔physical metaphors)
  3. Compute SHA-256 + BLAKE3 per concept node (deterministic)
  4. Build multi-dimensional knowledge matrix
  5. Generate hypothesis connections across domains
  6. Create mining queue ordered by evidence density
  7. Output JSON with ISO 8601 timestamps + hash chain (blockchain-style custody)

Design invariants (RLL policy):
  - No synthetic data; TOKEN_VAZIO for missing evidence
  - All hashes deterministic (sorted canonical JSON)
  - Hash chain: each node references previous_hash → tamper-evident sequence
  - Timestamps: ISO 8601 UTC, measured once at script start
  - Claim boundaries: every node has claim_boundary field
  - Structural validation only; metaphors illuminate but do not validate science
"""

import sys
import json
import hashlib
import argparse
import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import blake3 as _blake3_lib
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

# ── Blake3 helper ─────────────────────────────────────────────────────────────

def _blake3_hex(data: bytes) -> str:
    if HAS_BLAKE3:
        return _blake3_lib.blake3(data).hexdigest()
    return "TOKEN_VAZIO:blake3_not_installed"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(obj: dict) -> bytes:
    """Deterministic canonical JSON (sorted keys, no extra whitespace)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':')).encode('utf-8')


# ── Polymathic bridges (biological↔physical) ──────────────────────────────────
# Metaphors ILLUMINATE concepts but do NOT validate claims.
# Each bridge maps a biological phenomenon to a physical/mathematical analogue.

POLYMATHIC_BRIDGES = [
    {
        "id": "METAPHOR_TURTLE_TIMESCALE",
        "type": "METAPHOR",
        "name": "Tartaruga — longevidade, ritmo lento, estabilidade estrutural",
        "bio_mechanism": (
            "Telomere protection + low metabolic rate → low error accumulation; "
            "200+ year lifespan demonstrates genome fidelity over geological time."
        ),
        "physics_analogue": (
            "Low Lyapunov exponent λ → long predictability horizon; "
            "slow-roll inflation; adiabatic invariants in slowly varying systems."
        ),
        "rll_equation_ids": ["modal_response", "lyapunov_growth"],
        "domains": ["evolutionary_biology", "cosmology", "dynamical_systems"],
        "cross_domain_pattern": "slow_rate_high_resilience",
        "claim_boundary": "Metaphor only; no quantitative mapping established without dataset.",
        "doi_seeds": ["10.1073/pnas.1407158111"],
    },
    {
        "id": "METAPHOR_JELLYFISH_BOUNCE",
        "type": "METAPHOR",
        "name": "Água-viva imortal (Turritopsis dohrnii) — retrogênese cíclica",
        "bio_mechanism": (
            "Transdifferentiation: somatic cells revert to pluripotent state → full "
            "biological reset without apoptosis; cyclical rejuvenation."
        ),
        "physics_analogue": (
            "Cosmological bounce: T^7 cyclic attractor 42 slots; phase reset at "
            "attractor boundary; LQC (loop quantum cosmology) bouncing models."
        ),
        "rll_equation_ids": ["impulse_response", "toroidal_state_space"],
        "domains": ["biology", "cosmology", "cyclicity", "RLL"],
        "cross_domain_pattern": "cyclic_reset",
        "claim_boundary": "Metaphor only; cosmological bounce not established by RLL data.",
        "doi_seeds": ["10.1016/j.cub.2022.01.095"],
    },
    {
        "id": "METAPHOR_WHALESHARK_FILTER",
        "type": "METAPHOR",
        "name": "Tubarão-baleia — filtragem volumétrica de escala macroscópica",
        "bio_mechanism": (
            "Filter feeding via ram filtration: buccal volume selects plankton by "
            "physical size cutoff (mesh geometry). Scales from micro to macro."
        ),
        "physics_analogue": (
            "Power spectrum cutoff: P(k) suppressed for k > k_filter; "
            "large-scale structure formed by surviving modes; density contrast δ(x,z)."
        ),
        "rll_equation_ids": ["density_contrast", "cosmic_web_graph"],
        "domains": ["marine_biology", "cosmology", "large_scale_structure"],
        "cross_domain_pattern": "scale_selective_filtering",
        "claim_boundary": "Metaphor only; k_filter analogy not quantified.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_PLANKTON_QUANTUM",
        "type": "METAPHOR",
        "name": "Plâncton — agentes microscópicos formando macroestruturas",
        "bio_mechanism": (
            "Individual nano-organisms (1–200 μm) → collective blooms covering "
            "10^6 km² → primary production base of marine food web."
        ),
        "physics_analogue": (
            "Bottom-up structure formation: quantum fluctuations → CDM density seeds "
            "→ halos → filaments → cosmic web; δ(x,z) grows from δ~10^-5."
        ),
        "rll_equation_ids": ["density_contrast", "chi2"],
        "domains": ["marine_biology", "cosmology", "quantum_mechanics"],
        "cross_domain_pattern": "bottom_up_collective_emergence",
        "claim_boundary": "Metaphor only; no quantitative link between plankton and δ(x,z).",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_MANGROVE_BOUNDARY",
        "type": "METAPHOR",
        "name": "Manguezal — zona de transição, condições de contorno ecológicas",
        "bio_mechanism": (
            "Land-sea-freshwater interface: salinity gradient, tidal inundation, "
            "root filtration → boundary condition for nutrient cycling."
        ),
        "physics_analogue": (
            "Boundary conditions in PDEs: Cauchy problem on ∂Ω; "
            "observation equation maps src state at te to obs at t0 across interface."
        ),
        "rll_equation_ids": ["tidal_triggering", "observation_equation"],
        "domains": ["ecology", "geophysics", "mathematical_physics"],
        "cross_domain_pattern": "boundary_interface_conditions",
        "claim_boundary": "Metaphor only; boundary form not quantified for RLL observables.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_REEF_NETWORK",
        "type": "METAPHOR",
        "name": "Recife de coral — rede complexa, resiliência por biodiversidade",
        "bio_mechanism": (
            "Coral symbiosis (zooxanthellae + CaCO3 + fish diversity): redundancy "
            "at each trophic level gives scale-free robustness against disturbance."
        ),
        "physics_analogue": (
            "Scale-free network: degree distribution P(k) ~ k^-γ; hub nodes "
            "(massive halos in cosmic web) maintain connectivity under random failure; "
            "rafaelia_coherence φ = (1-H)C measures cohesion."
        ),
        "rll_equation_ids": ["cosmic_web_graph", "rafaelia_coherence"],
        "domains": ["marine_ecology", "network_science", "cosmology", "RafaelIA"],
        "cross_domain_pattern": "scale_free_resilience",
        "claim_boundary": "Metaphor only; degree distribution not fitted to RLL graph data.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_TIDE_MULTISCALE",
        "type": "METAPHOR",
        "name": "Marés barométricas — oscilações de múltiplas frequências (S4~6h, MT3~9h, S2~12h, ~16h, S1~24h)",
        "bio_mechanism": (
            "Barometric tidal spectrum: S4~6h (quarter-diurnal), MT3~9h (terdiurnal), "
            "S2~12h (semidiurnal), ~16h (ultradian stress cycle), S1~24h (diurnal solar); "
            "biological clocks synchronize to all these harmonics across kingdoms: "
            "cortisol ultradian (~9h), growth hormone (~16h), full circadian (~24h)."
        ),
        "physics_analogue": (
            "Modal response h(t) = Σ Ak exp(-γk t) cos(ωk t + φk): "
            "each tide component is one mode with distinct ωk; multi-scale oscillation drives "
            "tidal triggering ΔCFS = Δτ + μ′Δσn. Fisher information I_total aggregates "
            "constraints from all frequency bands simultaneously."
        ),
        "rll_equation_ids": ["modal_response", "tidal_triggering", "impulse_response", "fisher_information_total"],
        "domains": ["geophysics", "oceanography", "atmospheric_science", "biology", "chronobiology"],
        "cross_domain_pattern": "multi_frequency_oscillation",
        "claim_boundary": "Metaphor only; 9h/16h biological analogues to atmospheric tides not quantified in RLL.",
        "doi_seeds": ["10.1029/2018GL080421"],
    },
    {
        "id": "METAPHOR_CHERNOBYL_RECURSION",
        "type": "METAPHOR",
        "name": "Chernobyl — recursão positiva não controlada (cascade failure)",
        "bio_mechanism": (
            "Prompt criticality at 1986-04-26T01:23Z: positive void coefficient "
            "→ power spike 30,000× nominal → steam explosion; "
            "ecological recovery: forest regrowth, wildlife adaptation."
        ),
        "physics_analogue": (
            "Lyapunov λ >> 0: ||δx(t)|| grows exponentially; "
            "positive feedback loop collapses control → chaos onset; "
            "metaphor for divergent numerical simulations without adaptive step-size."
        ),
        "rll_equation_ids": ["lyapunov_growth", "tidal_triggering"],
        "domains": ["nuclear_physics", "dynamical_systems", "ecology", "catastrophe_theory"],
        "cross_domain_pattern": "uncontrolled_cascade",
        "claim_boundary": "Metaphor only; no quantitative Lyapunov fit to RLL models.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_NASA_CONTROLLED_CATALYSIS",
        "type": "METAPHOR",
        "name": "NASA — recursão controlada: catálise, inversão, retroalimentação estabilizadora",
        "bio_mechanism": (
            "Mission-critical engineering: fault-tree analysis, triple redundancy, "
            "controlled burn orbit insertion; inversion (retrograde firing) as "
            "mathematical inversion of trajectory."
        ),
        "physics_analogue": (
            "PID controller / LQR stabilization; χ² minimization as feedback: "
            "residual vector (d-m) drives parameter update toward convergence; "
            "rafaelia_coherence φ as goal function (maximize coherence)."
        ),
        "rll_equation_ids": ["impulse_response", "chi2", "rafaelia_coherence"],
        "domains": ["aerospace_engineering", "control_theory", "statistics", "RafaelIA"],
        "cross_domain_pattern": "controlled_stabilizing_feedback",
        "claim_boundary": "Metaphor only; PID analogue not formalized in RLL parameter space.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_RNA_INFORMATION_TRANSFER",
        "type": "METAPHOR",
        "name": "RNA mensageiro — transferência de informação entre domínios distintos",
        "bio_mechanism": (
            "mRNA: DNA transcription → ribosomal translation → protein; "
            "triplet codon = compressed symbol (4^3 = 64 symbols, 20 amino acids); "
            "error rate ~10^-4 per base → error correction via redundancy."
        ),
        "physics_analogue": (
            "Photon / gravitational wave as information carrier across causal boundary; "
            "observation equation: s_src → F_prop → s_obs; "
            "claim_state_entropy H_claim measures information loss in transfer."
        ),
        "rll_equation_ids": ["observation_equation", "claim_state_entropy"],
        "domains": ["molecular_biology", "information_theory", "cosmology", "RLL"],
        "cross_domain_pattern": "cross_domain_information_encoding",
        "claim_boundary": "Metaphor only; codon redundancy ≠ observational noise model.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_SEASLUG_HORIZONTAL",
        "type": "METAPHOR",
        "name": "Lesma do mar (Elysia chlorotica) — transferência horizontal de genes",
        "bio_mechanism": (
            "E. chlorotica integrates chloroplast-derived photosynthesis genes into "
            "animal genome; acquires function across kingdom boundary (animal ← plant)."
        ),
        "physics_analogue": (
            "Cross-domain axiom import: topology borrowed in physics → T^7 toroidal "
            "state space; graph theory borrowed in biology → network analysis of reefs; "
            "rafaelia_coherence φ measures degree of successful cross-domain absorption."
        ),
        "rll_equation_ids": ["rafaelia_coherence", "toroidal_state_space"],
        "domains": ["marine_biology", "evolutionary_biology", "mathematics", "RafaelIA"],
        "cross_domain_pattern": "horizontal_domain_transfer",
        "claim_boundary": "Metaphor only; HGT frequency not quantified in RafaelIA context.",
        "doi_seeds": ["10.1093/molbev/msq171"],
    },
    {
        "id": "METAPHOR_DNA_COMPRESSION",
        "type": "METAPHOR",
        "name": "DNA — máximo empilhamento de informação ao menor custo energético",
        "bio_mechanism": (
            "3×10^9 bp in 6 μm nucleus: ~0.34 nm/bp; histone spooling "
            "achieves 10,000× compaction; error rate ~10^-10 post-repair; "
            "metabolic cost ~70 ATP per bp replication."
        ),
        "physics_analogue": (
            "Bekenstein bound: S ≤ 2πRE/ℏc; "
            "claim_state_entropy H_max = log2(14) ≈ 3.81 bits at TOKEN_VAZIO → 0 at CLAIM_ALLOWED; "
            "tag14_entropy H_Tag14 as operational proxy for information compressibility."
        ),
        "rll_equation_ids": ["claim_state_entropy", "tag14_entropy"],
        "domains": ["molecular_biology", "information_theory", "physics", "RafaelIA"],
        "cross_domain_pattern": "maximum_compression_minimum_cost",
        "claim_boundary": "Metaphor only; Bekenstein bound not applied to DNA numerically here.",
        "doi_seeds": [],
    },
    {
        "id": "METAPHOR_METAMORPHOSIS_PHASE",
        "type": "METAPHOR",
        "name": "Metamorfose (holometabola) — transição de fase estrutural sem perda de informação",
        "bio_mechanism": (
            "Complete metamorphosis (egg→larva→pupa→imago): imaginal discs preserve "
            "structural information during radical morphological reorganization; "
            "information fidelity maintained across topological phase change."
        ),
        "physics_analogue": (
            "Topological phase transition: order parameter changes, symmetry breaks, "
            "bulk topology index (Chern number) preserved; "
            "T^7 attractor trajectory through phase space maintains φ_ethica continuity."
        ),
        "rll_equation_ids": ["toroidal_state_space", "lyapunov_growth", "impulse_response"],
        "domains": ["entomology", "topology", "quantum_physics", "RLL"],
        "cross_domain_pattern": "structure_preserving_phase_transition",
        "claim_boundary": "Metaphor only; topological invariant not computed for RLL attractors.",
        "doi_seeds": ["10.1242/jeb.174300"],
    },
    # ── NEW BRIDGES (2026-07-28) ──────────────────────────────────────────────
    # Covers: viruses/recursion/inversion, homeostasis/buffering,
    # kingdoms/mycorrhiza, neuroplasticity/cognitive, Lotka-Volterra/scarcity
    # Also links previously orphaned equations: aic, bic, v_info_vector,
    # fisher_information_total
    {
        "id": "METAPHOR_VIRUS_LATERAL_RECURSION",
        "type": "METAPHOR",
        "name": "Vírus — recursão lateral, hijack de replicação, inversão de informação",
        "bio_mechanism": (
            "Retroviruses (HIV, SARS-CoV-2): insert reverse-transcribed genome into host "
            "DNA → hijack replication machinery → produce viral copies; "
            "RNA→DNA inversion (reverse transcriptase) is biological recursion-inversion; "
            "horizontal transfer across kingdoms (phage transduction in bacteria→eukaryotes)."
        ),
        "physics_analogue": (
            "Cross-domain parameter injection: V_info vector encodes multi-dimensional "
            "state that can be 'inserted' into a new domain (like a retrovirus); "
            "T^7 toroidal attractor as host state space where injected information "
            "creates new fixed points; claim_state_entropy drops after successful integration."
        ),
        "rll_equation_ids": ["claim_state_entropy", "v_info_vector", "toroidal_state_space"],
        "domains": ["virology", "evolutionary_biology", "information_theory", "dynamical_systems", "RLL"],
        "cross_domain_pattern": "hijack_recursion_lateral_transfer",
        "claim_boundary": "Metaphor only; retroviral insertion ≠ literal parameter injection in RLL models.",
        "doi_seeds": ["10.1038/s41559-019-0948-2"],
    },
    {
        "id": "METAPHOR_HOMEOSTASIS_BUFFERING",
        "type": "METAPHOR",
        "name": "Homeostase — tamponamento nasal/pH, equilíbrio dos reinos por retroalimentação negativa",
        "bio_mechanism": (
            "Nasal/blood pH buffering: CO2 + H2O ⇌ H2CO3 ⇌ HCO3⁻ + H⁺ — bicarbonate "
            "buffer maintains pH 7.35–7.45 despite metabolic flux; "
            "negative feedback loop (Henderson-Hasselbalch equation) minimizes variance; "
            "kingdoms balance: predator/prey, producer/consumer ratios stay bounded."
        ),
        "physics_analogue": (
            "Lyapunov stable fixed point with λ < 0: perturbations decay exponentially; "
            "Fisher information I_total measures how precisely system can be tracked "
            "near equilibrium (Cramér-Rao bound); χ² residuals as measure of homeostatic "
            "deviation from expected model."
        ),
        "rll_equation_ids": ["lyapunov_growth", "fisher_information_total", "chi2"],
        "domains": ["physiology", "control_theory", "statistics", "dynamical_systems", "ecological_equilibrium"],
        "cross_domain_pattern": "homeostatic_feedback_equilibrium",
        "claim_boundary": "Metaphor only; Henderson-Hasselbalch not directly mapped to RLL Lyapunov spectrum.",
        "doi_seeds": ["10.1152/physrev.00023.2016"],
    },
    {
        "id": "METAPHOR_KINGDOMS_MYCORRHIZA",
        "type": "METAPHOR",
        "name": "Reinos + Micorriza (Wood Wide Web) — rede multi-reino de troca de recursos",
        "bio_mechanism": (
            "Mycorrhizal fungal networks connect plant roots across species: sugar↔phosphorus "
            "exchange, chemical warning signals, resource redistribution to shade-suppressed "
            "seedlings; 5 kingdoms (Animalia/Plantae/Fungi/Protista/Monera) in dynamic "
            "equilibrium via trophic cascades and mutualistic cycling."
        ),
        "physics_analogue": (
            "Cosmic web graph G_z = (V_z, E_z, W_z) as multi-kingdom network: nodes = "
            "halos/organisms, edges = filaments/hyphal links, weights = matter flux/nutrient flow; "
            "V_info multi-dimensional vector captures 14 observational dimensions like kingdoms "
            "capture multi-modal ecological axes; rafaelia_coherence φ measures network cohesion."
        ),
        "rll_equation_ids": ["cosmic_web_graph", "rafaelia_coherence", "v_info_vector"],
        "domains": ["mycology", "botany", "ecology", "network_science", "RafaelIA"],
        "cross_domain_pattern": "multi_kingdom_network_equilibrium",
        "claim_boundary": "Metaphor only; mycorrhizal topology not formally mapped to cosmic web metrics.",
        "doi_seeds": ["10.1038/nature02097"],
    },
    {
        "id": "METAPHOR_NEURAL_PLASTICITY",
        "type": "METAPHOR",
        "name": "Neuroplasticidade — poda sináptica, aprendizado de Hebb, consolidação HDC cognitiva",
        "bio_mechanism": (
            "Synaptic pruning: adolescent brain eliminates ~50% of synapses (AIC-like: "
            "minimum connections that explain behavior); Hebbian learning ('neurons that fire "
            "together wire together') = local evidence-driven weight update; "
            "memory consolidation during sleep: hippocampus→neocortex transfer = information "
            "compression from high-dimensional experience to compact engram."
        ),
        "physics_analogue": (
            "Model selection: AIC = χ² + 2k selects minimum-parameter model "
            "(penalizes complexity like pruning penalizes unused synapses); "
            "BIC = χ² + k ln(n) is stricter pruning criterion for large n; "
            "claim_state_entropy decreases as evidence accumulates (H_claim → 0); "
            "tag14_entropy H_Tag14 as proxy for cognitive information density per token."
        ),
        "rll_equation_ids": ["claim_state_entropy", "tag14_entropy", "aic", "bic"],
        "domains": ["neuroscience", "cognitive_science", "information_theory", "machine_learning", "RafaelIA"],
        "cross_domain_pattern": "adaptive_pruning_hypervector_consolidation",
        "claim_boundary": "Metaphor only; AIC/BIC model selection not formally equivalent to synaptic pruning.",
        "doi_seeds": ["10.1523/JNEUROSCI.3927-11.2012"],
    },
    {
        "id": "METAPHOR_LOTKA_VOLTERRA_SCARCITY",
        "type": "METAPHOR",
        "name": "Lotka-Volterra — dinâmica predador/presa, colapso por escassez alimentar",
        "bio_mechanism": (
            "Predator-prey oscillation: dN/dt = αN - βNP; dP/dt = δNP - γP; "
            "when food (N) is scarce, predator (P) collapses → prey recovers → "
            "oscillatory limit cycle or extinction; "
            "stability depends critically on initial conditions and reaction coefficients."
        ),
        "physics_analogue": (
            "Lyapunov exponent λ near separatrix: small perturbation → divergent trajectory; "
            "tidal triggering ΔCFS as threshold: stress accumulates until failure cascade; "
            "modal response captures oscillatory recovery after collapse; "
            "system near criticality = maximum sensitivity to initial conditions."
        ),
        "rll_equation_ids": ["lyapunov_growth", "tidal_triggering", "modal_response"],
        "domains": ["population_dynamics", "ecology", "dynamical_systems", "catastrophe_theory", "geophysics"],
        "cross_domain_pattern": "predator_prey_oscillation_collapse",
        "claim_boundary": "Metaphor only; Lotka-Volterra coefficients not fitted to RLL datasets.",
        "doi_seeds": ["10.1007/s12080-013-0201-7"],
    },
]


# ── Core synthesis engine ──────────────────────────────────────────────────────

def load_equation_registry(registry_path: Path) -> list:
    if not registry_path.exists():
        print(f"TOKEN_VAZIO: {registry_path} not found — returning empty registry",
              file=sys.stderr)
        return []
    with registry_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('equations', [])


def build_concept_node(node_id: str, node_type: str, name: str,
                       domains: list, claim_boundary: str,
                       extra: dict, timestamp: str, prev_hash: str) -> dict:
    """Build a single concept node and compute hashes."""
    node = {
        "id": node_id,
        "type": node_type,
        "name": name,
        "domains": sorted(domains),
        "claim_boundary": claim_boundary,
        "timestamp_utc": timestamp,
        "previous_hash": prev_hash,
        **extra,
    }
    canonical = _canonical_bytes(node)
    sha256 = _sha256_hex(canonical)
    blake3 = _blake3_hex(canonical)
    node["sha256"] = sha256
    node["blake3"] = blake3
    node["chain_hash"] = _sha256_hex((prev_hash + sha256).encode('utf-8'))
    return node


def score_concept(node: dict) -> float:
    """
    Mining queue score = evidence_density / (1 + TOKEN_VAZIO_count).
    Higher = should be mined first.
    """
    equation_ids = node.get("rll_equation_ids", []) or []
    doi_seeds = node.get("doi_seeds", []) or []
    linked_eqs = len(equation_ids)
    doi_count = len([d for d in doi_seeds if d])
    token_vazio = 1 if "TOKEN_VAZIO" in json.dumps(node) else 0
    domains = len(node.get("domains", []))
    return (linked_eqs * 2 + doi_count * 3 + domains) / (1 + token_vazio)


def build_hypothesis(bridge: dict, eq_map: dict) -> dict:
    """Generate a cross-domain hypothesis from a bridge + linked equations."""
    linked = [eq_map.get(eid, {}) for eid in bridge.get("rll_equation_ids", [])]
    linked_equations = [e.get("equation", "TOKEN_VAZIO") for e in linked if e]
    if not linked_equations:
        linked_equations = ["TOKEN_VAZIO:no_linked_equations"]

    hypothesis_text = (
        f"Hypothesis derived from polymathic bridge '{bridge['id']}': "
        f"The biological pattern '{bridge['cross_domain_pattern']}' "
        f"(from '{bridge['name']}') may correspond to a formal structure "
        f"in domains {bridge['domains']} via equations: {linked_equations}. "
        f"Claim boundary: {bridge['claim_boundary']}"
    )
    return {
        "hypothesis_id": f"HYP_{bridge['id']}",
        "bridge_id": bridge["id"],
        "pattern": bridge["cross_domain_pattern"],
        "linked_equations": linked_equations,
        "domains": bridge["domains"],
        "text": hypothesis_text,
        "status": "CANDIDATE",
        "evidence_state": "TOKEN_VAZIO",
        "next_gate": (
            "Quantify cross-domain mapping numerically with real RLL dataset; "
            "compute Pearson r or structural similarity index; report AIC delta."
        ),
    }


def build_knowledge_matrix(equation_nodes: list, bridge_nodes: list) -> dict:
    """Build domain × concept_type matrix with counts."""
    all_domains = set()
    for n in equation_nodes + bridge_nodes:
        all_domains.update(n.get("domains", []))
    domains = sorted(all_domains)

    matrix = {}
    for d in domains:
        eq_count = sum(1 for n in equation_nodes if d in n.get("domains", []))
        bridge_count = sum(1 for n in bridge_nodes if d in n.get("domains", []))
        matrix[d] = {
            "equations": eq_count,
            "metaphors": bridge_count,
            "total": eq_count + bridge_count,
        }
    return matrix


def main():
    parser = argparse.ArgumentParser(
        description="Polymathic Concept Matrix Synthesis Engine — RLL/RAFAELIA"
    )
    parser.add_argument(
        "--registry", default="rll_equation_registry.yml",
        help="Path to equation registry YAML (default: rll_equation_registry.yml)"
    )
    parser.add_argument(
        "--output-dir", default="results/concept_matrix",
        help="Output directory for JSON artifacts"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and compute hashes but do not write output files"
    )
    args = parser.parse_args()

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')
    run_date = timestamp[:10]

    repo_root = Path(__file__).resolve().parent.parent
    registry_path = repo_root / args.registry
    output_dir = repo_root / args.output_dir
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[PCMSE] timestamp: {timestamp}")
    print(f"[PCMSE] blake3: {'available' if HAS_BLAKE3 else 'TOKEN_VAZIO (pip install blake3)'}")
    print(f"[PCMSE] registry: {registry_path}")

    # ── 1. Load equations ─────────────────────────────────────────────────────
    raw_equations = load_equation_registry(registry_path)
    eq_map = {eq["id"]: eq for eq in raw_equations}
    print(f"[PCMSE] loaded {len(raw_equations)} equations from registry")

    # ── 2. Build equation nodes ───────────────────────────────────────────────
    prev_hash = "0" * 64
    equation_nodes = []
    for eq in raw_equations:
        extra = {
            "equation": eq.get("equation", "TOKEN_VAZIO"),
            "status": eq.get("status", "TOKEN_VAZIO"),
            "rll_equation_ids": [],
            "doi_seeds": [],
        }
        if "source_doc" in eq:
            extra["source_doc"] = eq["source_doc"]
        node = build_concept_node(
            node_id=f"FORMULA_{eq['id'].upper()}",
            node_type="FORMULA",
            name=eq.get("equation", eq["id"]),
            domains=eq.get("domain", []),
            claim_boundary=eq.get("claim_boundary", "No claim boundary declared."),
            extra=extra,
            timestamp=timestamp,
            prev_hash=prev_hash,
        )
        prev_hash = node["chain_hash"]
        equation_nodes.append(node)

    # ── 3. Build polymathic bridge nodes ──────────────────────────────────────
    bridge_nodes = []
    hypotheses = []
    for bridge in POLYMATHIC_BRIDGES:
        extra = {
            "bio_mechanism": bridge["bio_mechanism"],
            "physics_analogue": bridge["physics_analogue"],
            "rll_equation_ids": bridge["rll_equation_ids"],
            "cross_domain_pattern": bridge["cross_domain_pattern"],
            "doi_seeds": bridge.get("doi_seeds", []),
        }
        node = build_concept_node(
            node_id=bridge["id"],
            node_type="METAPHOR",
            name=bridge["name"],
            domains=bridge["domains"],
            claim_boundary=bridge["claim_boundary"],
            extra=extra,
            timestamp=timestamp,
            prev_hash=prev_hash,
        )
        prev_hash = node["chain_hash"]
        bridge_nodes.append(node)
        hypotheses.append(build_hypothesis(bridge, eq_map))

    all_nodes = equation_nodes + bridge_nodes
    print(f"[PCMSE] built {len(equation_nodes)} equation nodes, "
          f"{len(bridge_nodes)} metaphor bridges")
    print(f"[PCMSE] generated {len(hypotheses)} hypothesis candidates")

    # ── 4. Knowledge matrix ───────────────────────────────────────────────────
    matrix = build_knowledge_matrix(equation_nodes, bridge_nodes)

    # ── 5. Mining queue (ordered by evidence score descending) ────────────────
    scored = [(score_concept(n), n) for n in all_nodes]
    scored.sort(key=lambda x: x[0], reverse=True)
    mining_queue = [
        {
            "rank": i + 1,
            "id": n["id"],
            "type": n["type"],
            "score": round(s, 4),
            "domains": n["domains"],
            "sha256_prefix": n["sha256"][:16],
        }
        for i, (s, n) in enumerate(scored)
    ]

    # ── 6. Root hash over all nodes ───────────────────────────────────────────
    root_payload = json.dumps(
        [n["sha256"] for n in all_nodes], sort_keys=True, separators=(',', ':')
    ).encode('utf-8')
    root_sha256 = _sha256_hex(root_payload)
    root_blake3 = _blake3_hex(root_payload)

    # ── 7. Assemble output document ───────────────────────────────────────────
    output = {
        "schema": "rll.polymathic-concept-matrix.v1",
        "schema_version": "1.0.0",
        "timestamp_utc": timestamp,
        "run_date": run_date,
        "generator": "scripts/polymathic_concept_matrix.py",
        "blake3_available": HAS_BLAKE3,
        "claim_boundary": (
            "This matrix provides structural cross-domain mappings as METAPHORS and "
            "FORMULAS. No scientific superiority claim is established here. "
            "Metaphors illuminate but do not validate. Real-data validation is required "
            "for any quantitative claim. TOKEN_VAZIO marks missing evidence."
        ),
        "integrity": {
            "total_nodes": len(all_nodes),
            "equation_nodes": len(equation_nodes),
            "metaphor_nodes": len(bridge_nodes),
            "root_sha256": root_sha256,
            "root_blake3": root_blake3,
            "chain_terminal_hash": prev_hash,
        },
        "knowledge_matrix": matrix,
        "mining_queue": mining_queue,
        "hypotheses": hypotheses,
        "nodes": all_nodes,
    }

    output_json = json.dumps(output, indent=2, ensure_ascii=True)
    integrity = {
        "sha256": _sha256_hex(output_json.encode('utf-8')),
        "blake3": _blake3_hex(output_json.encode('utf-8')),
    }
    output["file_integrity"] = integrity

    if args.dry_run:
        print(f"[PCMSE] dry-run: {len(all_nodes)} nodes built, "
              f"root_sha256={root_sha256[:16]}... — no files written")
        print("[PCMSE] PASS")
        return 0

    # ── Write output ──────────────────────────────────────────────────────────
    out_file = output_dir / f"{run_date}_concept_matrix.json"
    final_json = json.dumps(output, indent=2, ensure_ascii=True)
    out_file.write_text(final_json, encoding='utf-8')

    # Recompute file integrity after final serialization
    file_sha256 = _sha256_hex(final_json.encode('utf-8'))
    file_blake3 = _blake3_hex(final_json.encode('utf-8'))

    manifest_file = output_dir / f"{run_date}_manifest.json"
    manifest = {
        "schema": "rll.concept-matrix-manifest.v1",
        "timestamp_utc": timestamp,
        "matrix_file": out_file.name,
        "sha256": file_sha256,
        "blake3": file_blake3,
        "stats": {
            "total_nodes": len(all_nodes),
            "equation_nodes": len(equation_nodes),
            "metaphor_nodes": len(bridge_nodes),
            "hypotheses": len(hypotheses),
            "domains_covered": len(matrix),
        },
    }
    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True), encoding='utf-8'
    )

    print(f"[PCMSE] wrote {out_file}")
    print(f"[PCMSE] wrote {manifest_file}")
    print(f"[PCMSE] sha256: {file_sha256}")
    print(f"[PCMSE] blake3: {file_blake3}")
    print(f"[PCMSE] domains covered: {sorted(matrix.keys())}")
    print(f"[PCMSE] top-5 mining queue:")
    for entry in mining_queue[:5]:
        print(f"  [{entry['rank']}] {entry['id']} (score={entry['score']}, "
              f"domains={entry['domains'][:2]}...)")
    print("[PCMSE] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
