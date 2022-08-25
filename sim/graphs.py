import json
from enum import Enum
import networkx as nx
from typing import Dict, List, Tuple, Any
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sim.constants import Color

Node = Tuple[int, int]


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


def tsp_solver(matrix: List[List[int]]) -> List[int]:
    """Solves tsp problem defined with a cost matrix.
    Returns list of matrix's row indices that represents node order that forms an approx. minimal Hamiltonian cycle.
    Based on: https://developers.google.com/optimization/routing/tsp.
    """

    def extract_path(manager, routing, solution):
        index = routing.Start(0)
        optimal_route = []
        while not routing.IsEnd(index):
            optimal_route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        return optimal_route

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(matrix), 1, 0)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    return extract_path(manager, routing, solution)


class Origin(str, Enum):
    BASE_NODE = "base_node"
    USER_NODE = "user_node"
    BASE_EDGE = "base_edge"
    SOLUTION_EDGE = "solution_edge"
    SOLUTION_START_NODE = "solution_start_node"
    SOLUTION_END_NODE = "solution_end_node"


COLOR_MAP: Dict[Origin, Color] = {
    Origin.BASE_NODE: (219, 36, 20),
    Origin.BASE_EDGE: (17, 136, 120),
    Origin.USER_NODE: (38, 188, 222),
    Origin.SOLUTION_EDGE: (235, 195, 52),
    Origin.SOLUTION_START_NODE: (30, 140, 18),
    Origin.SOLUTION_END_NODE: (143, 14, 194),
}


class GraphModel:
    def __init__(self, data_path: str):
        self.graph = nx.Graph()
        graph_data = load_graph_data_from_json(data_path)
        self.graph.add_nodes_from(graph_data["nodes"], color=COLOR_MAP[Origin.BASE_NODE])
        self.graph.add_edges_from(graph_data["edges"], color=COLOR_MAP[Origin.BASE_EDGE])

    def insert_node(self, node: Node) -> None:
        nodes = list(self.graph.nodes().keys())
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
                length = nx.shortest_path_length(self.graph, source=n1, target=n2, weight=manhattan_distance)
                row.append(length)
            matrix.append(row)
        return matrix

    def solve_tsp(self) -> list:
        nodes_to_visit = self.list_nodes_from(origin=Origin.USER_NODE)
        path = tsp_solver(self.create_distance_matrix())
        nodes_on_path = [nodes_to_visit[idx] for idx in path]

        optimal_route = []
        for n1, n2 in zip(nodes_on_path[:-1], nodes_on_path[1:]):
            optimal_route.extend(nx.shortest_path(self.graph, source=n1, target=n2, weight=manhattan_distance)[1:])

        # color map significant nodes and edges in the optimal route
        for n1, n2 in zip(optimal_route[:-1], optimal_route[1:]):
            self.graph[n1][n2]["color"] = COLOR_MAP[Origin.SOLUTION_EDGE]
        self.graph.nodes[optimal_route[0]]["color"] = COLOR_MAP[Origin.SOLUTION_START_NODE]
        self.graph.nodes[optimal_route[-1]]["color"] = COLOR_MAP[Origin.SOLUTION_END_NODE]
        return optimal_route


if __name__ == "__main__":
    model = GraphModel(data_path="../data/visibility_graph.json")
    model.insert_node(node=(50, 30))
    model.insert_node(node=(50, 160))
    model.insert_node(node=(350, 180))
    model.insert_node(node=(80, 500))
    model.insert_node(node=(200, 550))
    model.insert_node(node=(480, 540))
    print(model.solve_tsp())
