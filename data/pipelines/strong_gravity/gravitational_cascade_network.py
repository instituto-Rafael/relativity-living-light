"""Causal threshold-cascade laboratory for RLL strong-gravity hypotheses.

This module is deliberately conservative. It implements a generic network of
pre-loaded reservoirs connected by finite-speed couplings. A perturbation can
unlock local stored energy when a threshold is crossed, which may in turn
trigger neighbours. This is the computational analogue of the user's
mousetrap/ping-pong-ball or domino picture.

It does *not* assert that the observed cosmic web undergoes such a chain
reaction. The scalar quantity used here is a reduced trigger variable, not a
new fundamental scalar field. Physical promotion requires a source model,
stress-energy map, coupling derivation, observations and falsification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import heapq
import math
from typing import Dict, Iterable, List, Mapping, Tuple


C_M_S = 299_792_458.0
_COUPLING_EPS = 1.0e-12


@dataclass(frozen=True)
class Node:
    """One potentially excitable element of a coarse-grained network.

    threshold_j
        Integrated incoming perturbation required to unlock the node.
    reservoir_j
        Local energy already stored in the node/system before the trigger.
    release_fraction
        Fraction of that reservoir exported into the cascade after activation.
    """

    node_id: str
    threshold_j: float
    reservoir_j: float
    release_fraction: float = 1.0

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must be non-empty")
        if self.threshold_j < 0.0 or self.reservoir_j < 0.0:
            raise ValueError("energies must be non-negative")
        if not 0.0 <= self.release_fraction <= 1.0:
            raise ValueError("release_fraction must be in [0, 1]")


@dataclass(frozen=True)
class Edge:
    """Finite-speed directed coupling between two nodes."""

    source: str
    target: str
    distance_m: float
    coupling: float

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError("self edges are not permitted")
        if self.distance_m < 0.0:
            raise ValueError("distance_m must be non-negative")
        if not 0.0 <= self.coupling <= 1.0:
            raise ValueError("coupling must be in [0, 1]")


@dataclass(order=True)
class _Pulse:
    arrival_s: float
    sequence: int
    target: str = field(compare=False)
    source: str = field(compare=False)
    energy_j: float = field(compare=False)
    depth: int = field(compare=False)


@dataclass(frozen=True)
class Activation:
    node_id: str
    time_s: float
    depth: int
    accumulated_trigger_j: float
    released_j: float


@dataclass(frozen=True)
class CascadeResult:
    activations: Tuple[Activation, ...]
    total_seed_j: float
    total_released_j: float
    max_depth: int
    duration_s: float
    active_fraction: float

    @property
    def avalanche_size(self) -> int:
        return len(self.activations)


class CascadeNetwork:
    """Discrete-event causal cascade with thresholded local reservoirs.

    Attenuation is intentionally a configurable *effective* law:

        A(d) = 1 / (1 + (d / d0)**alpha)

    It is finite at d=0 and can mimic different geometric/dissipative regimes.
    It must not be silently interpreted as a derived GR propagation law.

    ``coupling`` is an energy-allocation fraction. For every source node the
    outgoing fractions must sum to at most one, preventing graph fan-out from
    duplicating a local energy release.
    """

    def __init__(
        self,
        nodes: Iterable[Node],
        edges: Iterable[Edge],
        *,
        attenuation_scale_m: float,
        attenuation_exponent: float = 2.0,
        propagation_speed_m_s: float = C_M_S,
    ) -> None:
        node_list = list(nodes)
        self.nodes: Dict[str, Node] = {n.node_id: n for n in node_list}
        if not self.nodes:
            raise ValueError("network requires at least one node")
        if len(self.nodes) != len(node_list):
            raise ValueError("node_id values must be unique")
        if attenuation_scale_m <= 0.0:
            raise ValueError("attenuation_scale_m must be > 0")
        if attenuation_exponent < 0.0:
            raise ValueError("attenuation_exponent must be >= 0")
        if not 0.0 < propagation_speed_m_s <= C_M_S:
            raise ValueError("propagation speed must be in (0, c]")

        self.attenuation_scale_m = attenuation_scale_m
        self.attenuation_exponent = attenuation_exponent
        self.propagation_speed_m_s = propagation_speed_m_s
        self.outgoing: Dict[str, List[Edge]] = {key: [] for key in self.nodes}

        for edge in edges:
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError("edge endpoint absent from node set")
            self.outgoing[edge.source].append(edge)

        for source, source_edges in self.outgoing.items():
            coupling_budget = sum(edge.coupling for edge in source_edges)
            if coupling_budget > 1.0 + _COUPLING_EPS:
                raise ValueError(
                    f"outgoing coupling budget exceeds 1 for {source}: {coupling_budget}"
                )

    def attenuation(self, distance_m: float) -> float:
        x = distance_m / self.attenuation_scale_m
        return 1.0 / (1.0 + x ** self.attenuation_exponent)

    def run(self, seeds: Mapping[str, float]) -> CascadeResult:
        """Run one cascade.

        A seed is an externally supplied perturbation. Triggering a node does
        not create energy: it unlocks that node's pre-existing ``reservoir_j``.
        This distinction is the key conservation boundary in the mousetrap
        analogy.
        """

        if not seeds:
            raise ValueError("at least one seed is required")

        total_seed = 0.0
        accumulated = {node_id: 0.0 for node_id in self.nodes}
        activated: Dict[str, Activation] = {}
        queue: List[_Pulse] = []
        sequence = 0

        for node_id, energy_j in seeds.items():
            if node_id not in self.nodes:
                raise ValueError(f"unknown seed node: {node_id}")
            if energy_j < 0.0 or not math.isfinite(energy_j):
                raise ValueError("seed energies must be finite and non-negative")
            total_seed += energy_j
            heapq.heappush(queue, _Pulse(0.0, sequence, node_id, "EXTERNAL", energy_j, 0))
            sequence += 1

        while queue:
            pulse = heapq.heappop(queue)
            if pulse.target in activated:
                continue

            accumulated[pulse.target] += pulse.energy_j
            node = self.nodes[pulse.target]
            if accumulated[pulse.target] + 1e-15 < node.threshold_j:
                continue

            released = node.reservoir_j * node.release_fraction
            event = Activation(
                node_id=node.node_id,
                time_s=pulse.arrival_s,
                depth=pulse.depth,
                accumulated_trigger_j=accumulated[node.node_id],
                released_j=released,
            )
            activated[node.node_id] = event

            for edge in self.outgoing[node.node_id]:
                if edge.target in activated:
                    continue
                transmitted = released * edge.coupling * self.attenuation(edge.distance_m)
                if transmitted <= 0.0:
                    continue
                delay = edge.distance_m / self.propagation_speed_m_s
                heapq.heappush(
                    queue,
                    _Pulse(
                        pulse.arrival_s + delay,
                        sequence,
                        edge.target,
                        node.node_id,
                        transmitted,
                        pulse.depth + 1,
                    ),
                )
                sequence += 1

        ordered = tuple(sorted(activated.values(), key=lambda e: (e.time_s, e.node_id)))
        total_released = sum(event.released_j for event in ordered)
        max_depth = max((event.depth for event in ordered), default=0)
        duration = max((event.time_s for event in ordered), default=0.0)
        return CascadeResult(
            activations=ordered,
            total_seed_j=total_seed,
            total_released_j=total_released,
            max_depth=max_depth,
            duration_s=duration,
            active_fraction=len(ordered) / len(self.nodes),
        )


def branching_potential(network: CascadeNetwork) -> Dict[str, float]:
    """Return a dimensionless first-generation trigger potential for each node.

    For each outgoing edge this compares the pulse available from a full local
    release with the target threshold. Values > 1 are *not* proof of an
    avalanche; geometry, duplicate paths, timing and later generations matter.
    """

    out: Dict[str, float] = {}
    for source, edges in network.outgoing.items():
        released = network.nodes[source].reservoir_j * network.nodes[source].release_fraction
        score = 0.0
        for edge in edges:
            threshold = network.nodes[edge.target].threshold_j
            if threshold == 0.0:
                score += 1.0
                continue
            pulse = released * edge.coupling * network.attenuation(edge.distance_m)
            score += min(1.0, pulse / threshold)
        out[source] = score
    return out
