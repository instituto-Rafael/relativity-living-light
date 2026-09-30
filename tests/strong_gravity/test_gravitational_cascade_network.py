import math

from data.pipelines.strong_gravity.gravitational_cascade_network import (
    C_M_S, CascadeNetwork, Edge, Node, branching_potential,
)


def test_single_seed_can_unlock_preloaded_domino_chain():
    nodes = [Node("A", 1.0, 10.0), Node("B", 2.0, 8.0), Node("C", 2.0, 6.0), Node("D", 2.0, 4.0)]
    edges = [Edge("A", "B", 1.0, 0.5), Edge("B", "C", 1.0, 0.5), Edge("C", "D", 1.0, 0.5)]
    result = CascadeNetwork(nodes, edges, attenuation_scale_m=1000.0).run({"A": 1.0})
    assert [a.node_id for a in result.activations] == ["A", "B", "C", "D"]
    assert result.avalanche_size == 4
    assert result.max_depth == 3
    assert result.total_seed_j == 1.0
    assert result.total_released_j == 28.0


def test_subthreshold_network_does_not_fake_avalanche():
    net = CascadeNetwork(
        [Node("A", 1.0, 1.0), Node("B", 10.0, 10.0)],
        [Edge("A", "B", 1.0, 0.1)], attenuation_scale_m=1.0,
    )
    result = net.run({"A": 1.0})
    assert result.avalanche_size == 1
    assert result.activations[0].node_id == "A"


def test_causality_delay_is_never_superluminal():
    distance = 3.0e8
    net = CascadeNetwork(
        [Node("A", 1.0, 100.0), Node("B", 1.0, 1.0)],
        [Edge("A", "B", distance, 1.0)], attenuation_scale_m=1.0e12,
        propagation_speed_m_s=C_M_S,
    )
    result = net.run({"A": 1.0})
    b = next(a for a in result.activations if a.node_id == "B")
    assert b.time_s >= distance / C_M_S
    assert math.isclose(b.time_s, distance / C_M_S, rel_tol=1e-12)


def test_dense_near_threshold_graph_has_larger_branching_potential():
    nodes = [Node("A", 1.0, 10.0), Node("B", 1.0, 1.0), Node("C", 1.0, 1.0), Node("D", 1.0, 1.0)]
    dense = CascadeNetwork(nodes, [Edge("A", "B", 1.0, 0.30), Edge("A", "C", 1.0, 0.30), Edge("A", "D", 1.0, 0.30)], attenuation_scale_m=1000.0)
    sparse = CascadeNetwork(nodes, [Edge("A", "B", 1.0, 0.05)], attenuation_scale_m=1000.0)
    assert branching_potential(dense)["A"] > branching_potential(sparse)["A"]


def test_outgoing_coupling_budget_blocks_energy_duplication():
    nodes = [Node("A", 1.0, 10.0), Node("B", 1.0, 1.0), Node("C", 1.0, 1.0)]
    try:
        CascadeNetwork(nodes, [Edge("A", "B", 1.0, 0.7), Edge("A", "C", 1.0, 0.7)], attenuation_scale_m=1000.0)
    except ValueError as exc:
        assert "coupling budget" in str(exc)
    else:
        raise AssertionError("fan-out must not duplicate released energy")


def test_duplicate_node_ids_are_rejected():
    try:
        CascadeNetwork([Node("A", 1.0, 1.0), Node("A", 2.0, 2.0)], [], attenuation_scale_m=1.0)
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate node ids must fail closed")


def test_input_guards_block_superluminal_parameters():
    try:
        CascadeNetwork([Node("A", 1.0, 1.0)], [], attenuation_scale_m=1.0, propagation_speed_m_s=C_M_S * 1.01)
    except ValueError as exc:
        assert "propagation speed" in str(exc)
    else:
        raise AssertionError("superluminal speed must be rejected")
