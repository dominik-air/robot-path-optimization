import json
import networkx as nx
from typing import List, Tuple, Callable
from sim.constants import Origin, COLOR_MAP
from sim.solvers import TSP_Solver, ortools_solver


Node = Tuple[int, int]
ShortestPathAlgorithm = Callable[[nx.Graph, Node, Node], List[Node]]
ShortestPathLengthAlgorithm = Callable[[nx.Graph, Node, Node], int | float]


def make_tuples_out_of_child_elements(items: list) -> list:
    """Transforms a repeatedly nested list of lists into one with tuples on the lowest level."""
    new_list = []
    for item in items:
        try:
            content_type = item[0]
        except TypeError:
            return items
        if isinstance(content_type, list):
            new_list.append(make_tuples_out_of_child_elements(item))
        else:
            new_list.append(tuple(item))
    return new_list


def load_graph_data_from_json(filename: str) -> dict:
    with open(filename) as f:
        converted_data = {}
        for key, list_of_lists in json.load(f).items():
            converted_data[key] = make_tuples_out_of_child_elements(list_of_lists)
    return converted_data


def manhattan_distance(n1: Node, n2: Node, edge_attributes: dict = None) -> int:
    """Calculates the manhattan distance between two nodes.
    The edge_attributes argument is present to comply with the interface for callables in nx.shortest_path_length.
    """
    return abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])

class GraphModel:
    def __init__(self, data_path: str, 
                sp_alg: ShortestPathAlgorithm = nx.shortest_path, 
                sp_length_alg: ShortestPathLengthAlgorithm = nx.shortest_path_length,
                tsp_solver: TSP_Solver = ortools_solver):
        self.graph = nx.Graph()
        graph_data = load_graph_data_from_json(data_path)
        self.graph.add_nodes_from(graph_data["nodes"], color=COLOR_MAP[Origin.BASE_NODE])
        self.graph.add_edges_from(graph_data["edges"], color=COLOR_MAP[Origin.BASE_EDGE])

        self.shortest_path = sp_alg
        self.shortest_path_length = sp_length_alg
        self.tsp_solver = tsp_solver

    def insert_node(self, node: Node) -> None:
        nodes = [n for n, data in self.graph.nodes(data=True) if data["color"] != COLOR_MAP[Origin.USER_NODE]]
        nearest = nodes[0]
        best_dist = manhattan_distance(node, nearest)
        for neighbour in nodes[1:]:
            if best_dist > manhattan_distance(node, neighbour):
                nearest = neighbour
                best_dist = manhattan_distance(node, neighbour)
        self.graph.add_node(node, color=COLOR_MAP[Origin.USER_NODE])
        self.graph.add_edge(node, nearest, color=COLOR_MAP[Origin.SOLUTION_EDGE])

    def list_nodes_from(self, origin: Origin) -> List[Node]:
        nodes = []
        for node, data in self.graph.nodes(data=True):
            if data["color"] == COLOR_MAP[origin]:
                nodes.append(node)
        return nodes

    def reset(self):
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if data["color"] == COLOR_MAP[Origin.USER_NODE]:
                nodes_to_remove.append(node)
        self.graph.remove_nodes_from(nodes_to_remove)
        nx.set_node_attributes(self.graph, values=COLOR_MAP[Origin.BASE_NODE], name="color")
        nx.set_edge_attributes(self.graph, values=COLOR_MAP[Origin.BASE_EDGE], name="color")

    def create_distance_matrix(self) -> List[List[int]]:
        matrix = []
        nodes = self.list_nodes_from(origin=Origin.USER_NODE)
        for n1 in nodes:
            row = []
            for n2 in nodes:
                length = self.shortest_path_length(self.graph, source=n1, target=n2, weight=manhattan_distance)
                row.append(length)
            matrix.append(row)
        return matrix

    def solve_tsp(self) -> list:
        nodes_to_visit = self.list_nodes_from(origin=Origin.USER_NODE)
        path = self.tsp_solver(self.create_distance_matrix())
        nodes_on_path = [nodes_to_visit[idx] for idx in path]

        optimal_route = []
        for n1, n2 in zip(nodes_on_path[:-1], nodes_on_path[1:]):
            optimal_route.extend(self.shortest_path(self.graph, source=n1, target=n2, weight=manhattan_distance)[1:])

        # color map significant nodes and edges in the optimal route
        for n1, n2 in zip(optimal_route[:-1], optimal_route[1:]):
            self.graph[n1][n2]["color"] = COLOR_MAP[Origin.SOLUTION_EDGE]
        self.graph.nodes[optimal_route[0]]["color"] = COLOR_MAP[Origin.SOLUTION_START_NODE]
        self.graph.nodes[optimal_route[-1]]["color"] = COLOR_MAP[Origin.SOLUTION_END_NODE]
        return optimal_route


if __name__ == "__main__":
    model = GraphModel(data_path="../data/visibility_graph.json", sp_alg=nx.dijkstra_path)
    model.insert_node(node=(50, 30))
    model.insert_node(node=(50, 160))
    model.insert_node(node=(350, 180))
    model.insert_node(node=(80, 500))
    model.insert_node(node=(200, 550))
    model.insert_node(node=(480, 540))
    print(model.solve_tsp())
