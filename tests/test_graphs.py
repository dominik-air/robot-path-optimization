import pytest
from sim.graphs import make_tuples_out_of_child_elements, manhattan_distance, GraphModel, Origin, COLOR_MAP

make_tuples_out_of_child_elements_test_sets = [
    ([[[1, 2], [3, 4]], [[5, 6], [8, 9]]], [[(1, 2), (3, 4)], [(5, 6), (8, 9)]]),
    ([[1, 2], [3, 4]], [(1, 2), (3, 4)]),
    ([1, 2], [1, 2]),
]


@pytest.mark.parametrize("input_list, expected_list", make_tuples_out_of_child_elements_test_sets)
def test_make_tuples_out_of_child_elements(input_list, expected_list):
    test_list = make_tuples_out_of_child_elements(input_list)
    assert test_list == expected_list


manhattan_distance_test_sets = [[(20, 20), (30, 40), 30], [(-20, 20), (30, -40), 110], [(-20, -20), (-30, -40), 30]]


@pytest.mark.parametrize("n1, n2, expected_distance", manhattan_distance_test_sets)
def test_manhattan_distance(n1, n2, expected_distance):
    actual_distance = manhattan_distance(n1, n2)
    assert actual_distance == expected_distance


test_model = GraphModel(data_path="tests/data/graph.json")
insert_node_test_sets = [(test_model, (5, 4), ((5, 4), (6, 5))), (test_model, (2, 3), ((2, 3), (2, 1)))]


@pytest.mark.parametrize("graph_model, node, expected_edge", insert_node_test_sets)
def test_insert_node(graph_model, node, expected_edge):
    graph_model.insert_node(node)
    assert graph_model.graph.has_edge(*expected_edge) is True


test_model = GraphModel(data_path="tests/data/graph.json")
list_nodes_from_test_sets = [(test_model, (3, 3), Origin.BASE_NODE, 5), (test_model, (3, 3), Origin.USER_NODE, 1)]


@pytest.mark.parametrize("graph_model, node, origin, expected_nodes_num", list_nodes_from_test_sets)
def test_list_nodes_from(graph_model, node, origin, expected_nodes_num):
    graph_model.insert_node(node)
    assert len(graph_model.list_nodes_from(origin)) == expected_nodes_num


test_model = GraphModel(data_path="tests/data/graph.json")
list_nodes_from_after_reset_test_sets = [
    (test_model, (3, 3), Origin.BASE_NODE, 5),
    (test_model, (3, 3), Origin.USER_NODE, 0),
]


@pytest.mark.parametrize("graph_model, node, origin, expected_nodes_num", list_nodes_from_after_reset_test_sets)
def test_list_nodes_from_after_reset(graph_model, node, origin, expected_nodes_num):
    graph_model.insert_node(node)
    graph_model.reset()
    assert len(graph_model.list_nodes_from(origin)) == expected_nodes_num


def test_create_cost_matrix():
    test_model = GraphModel(data_path="tests/data/graph.json")
    for node in test_model.graph.nodes():
        test_model.graph.nodes[node]['color'] = COLOR_MAP[Origin.USER_NODE]
    expected_distance_matrix = [[0, 4, 8, 10, 6], [4, 0, 4, 8, 10], [8, 4, 0, 4, 8], [10, 8, 4, 0, 4], [6, 10, 8, 4, 0]]
    assert test_model.create_distance_matrix() == expected_distance_matrix
