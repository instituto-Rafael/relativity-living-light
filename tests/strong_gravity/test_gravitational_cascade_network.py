import math

from data.pipelines.strong_gravity.gravitational_cascade_network import (
    C_M_S,
    CascadeNetwork,
    Edge,
    Node,
    branching_potential,
)


def test_single_seed_can_unlock_preloaded_domino_chain():
    nodes = [
        Node("A", threshold_j=1.0, reservoir_j=10.0),
        Node("B", threshold_j=2.0, reservoir_j=8.0),
        Node("C", threshold_j=2.0, reservoir_j=6.0),
        Node("D", threshold_j=2.0, reservoir_j=4.0),
    ]
    edges = [
        Edge("A", "B", distance_m=1.0, coupling=0.5),
        Edge("B", "C", distance_m=1.0, coupling=0.5),
        Edge("C", "D", distance_m=1.0, coupling=0.5),
    ]
    net = CascadeNetwork(nodes, edges, attenuation_scale_m=1000.0)
    result = net.run({"A": 1.0})

    assert [a.node_id for a in result.activations] == ["A", "B", "C", "D"]
    assert result.avalanche_size == 4
    assert result.max_depth == 3
    assert result.total_seed_j == 1.0
    # The output exceeds the seed only because each node already held a reservoir.
    assert result.total_released_j == 28.0


def test_subthreshold_network_does_not_fake_avalanche():
    nodes = [
        Node("A", threshold_j=1.0, reservoir_j=1.0),
        Node("B", threshold_j=10.0, reservoir_j=10.0),
    ]
    net = CascadeNetwork(
        nodes,
        [Edge("A", "B", distance_m=1.0, coupling=0.1)],
        attenuation_scale_m=1.0,
    )
    result = net.run({"A": 1.0})

    assert result.avalanche_size == 1
    assert result.activations[0].node_id == "A"
    assert result.total_released_j == 1.0


def test_causality_delay_is_never_superluminal():
    distance = 3.0e8
    nodes = [
        Node("A", threshold_j=1.0, reservoir_j=100.0),
        Node("B", threshold_j=1.0, reservoir_j=1.0),
    ]
    net = CascadeNetwork(
        nodes,
        [Edge("A", "B", distance_m=distance, coupling=1.0)],
        attenuation_scale_m=1.0e12,
        propagation_speed_m_s=C_M_S,
    )
    result = net.run({"A": 1.0})
    b = next(a for a in result.activations if a.node_id == "B")

    assert b.time_s >= distance / C_M_S
    assert math.isclose(b.time_s, distance / C_M_S, rel_tol=1e-12)


def test_dense_near_threshold_graph_has_larger_branching_potential():
    nodes = [
        Node("A", threshold_j=1.0, reservoir_j=10.0),
        Node("B", threshold_j=1.0, reservoir_j=1.0),
        Node("C", threshold_j=1.0, reservoir_j=1.0),
        Node("D", threshold_j=1.0, reservoir_j=1.0),
    ]
    dense = CascadeNetwork(
        nodes,
        [
            Edge("A", "B", 1.0, 0.30),
            Edge("A", "C", 1.0, 0.30),
            Edge("A", "D", 1.0, 0.30),
        ],
        attenuation_scale_m=1000.0,
    )
    sparse = CascadeNetwork(
        nodes,
        [Edge("A", "B", 1.0, 0.05)],
        attenuation_scale_m=1000.0,
    )

    assert branching_potential(dense)["A"] > branching_potential(sparse)["A"]


def test_outgoing_coupling_budget_blocks_energy_duplication():
    nodes = [
        Node("A", 1.0, 10.0),
        Node("B", 1.0, 1.0),
        Node("C", 1.0, 1.0),
    ]
    try:
        CascadeNetwork(
            nodes,
            [Edge("A", "B", 1.0, 0.7), Edge("A", "C", 1.0, 0.7)],
            attenuation_scale_m=1000.0,
        )
    except ValueError as exc:
        assert "coupling budget" in str(exc)
    else:
        raise AssertionError("fan-out must not duplicate released energy")


def test_duplicate_node_ids_are_rejected():
    try:
        CascadeNetwork(
            [Node("A", 1.0, 1.0), Node("A", 2.0, 2.0)],
            [],
            attenuation_scale_m=1.0,
        )
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate node ids must fail closed")


def test_input_guards_block_superluminal_or_unbounded_parameters():
    nodes = [Node("A", 1.0, 1.0)]
    try:
        CascadeNetwork(nodes, [], attenuation_scale_m=1.0, propagation_speed_m_s=C_M_S * 1.01)
    except ValueError as exc:
        assert "propagation speed" in str(exc)
    else:
        raise AssertionError("superluminal speed must be rejected")
