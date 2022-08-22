import json
import networkx as nx
from typing import Dict
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from constants import Color


def make_tuples_out_of_child_elements(items: list) -> list:
    new_list = []
    for item in items:
        if isinstance(item[0], list):
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


def manhattan_distance(n1, n2, edge_attributes: dict = None) -> int:
    return abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])


def tsp_solver(matrix):
    def extract_path(manager, routing, solution):
        index = routing.Start(0)
        optimal_route = []
        route_distance = 0
        while not routing.IsEnd(index):
            optimal_route.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
        return optimal_route, route_distance

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
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    return extract_path(manager, routing, solution)


COLOR_MAP: Dict[str, Color] = {
    "base_node": (219, 36, 20),
    "user_node": (171, 136, 12),
    "base_edge": (38, 188, 222),
    "solution_edge": (235, 195, 52),
    "solution_start_node": (30, 140, 18),
    "solution_end_node": (143, 14, 194),
}


class GraphModel:
    def __init__(self, data_path: str):
        self.graph = nx.Graph()
        graph_data = load_graph_data_from_json(data_path)
        self.graph.add_nodes_from(
            graph_data["nodes"], color=COLOR_MAP["base_node"]
        )
        self.graph.add_edges_from(
            graph_data["edges"], color=COLOR_MAP["base_edge"]
        )
        self.nodes_to_visit = []

    def insert_node(self, node) -> None:
        self.nodes_to_visit.append(node)
        nodes = list(self.graph.nodes().keys())
        nearest = nodes[0]
        best_dist = manhattan_distance(node, nearest)
        for neighbour in nodes[1:]:
            if best_dist > manhattan_distance(node, neighbour):
                nearest = neighbour
                best_dist = manhattan_distance(node, neighbour)
        self.graph.add_node(node, color=COLOR_MAP["user_node"])
        self.graph.add_edge(node, nearest, color=COLOR_MAP["solution_edge"])

    def reset(self):
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if data["color"] == COLOR_MAP["user_node"]:
                nodes_to_remove.append(node)
        self.graph.remove_nodes_from(nodes_to_remove)
        self.nodes_to_visit.clear()
        nx.set_node_attributes(self.graph, values=COLOR_MAP["base_node"], name='color')
        nx.set_edge_attributes(self.graph, values=COLOR_MAP["base_edge"], name='color')

    def create_distance_matrix(self):
        matrix = []
        nodes = self.nodes_to_visit
        for n1 in nodes:
            row = []
            for n2 in nodes:
                length = nx.shortest_path_length(self.graph, source=n1, target=n2, weight=manhattan_distance)
                row.append(length)
            matrix.append(row)
        return matrix

    def solve_tsp(self) -> list:
        path, cost = tsp_solver(self.create_distance_matrix())
        nodes_on_path = [self.nodes_to_visit[idx] for idx in path]
        optimal_route = []
        for n1, n2 in zip(nodes_on_path[:-1], nodes_on_path[1:]):
            part = nx.shortest_path(self.graph, source=n1, target=n2, weight=manhattan_distance)[1:]
            optimal_route.extend(part)
        # color map significant nodes and edges in the optimal route
        for n1, n2 in zip(optimal_route[:-1], optimal_route[1:]):
            self.graph[n1][n2]['color'] = COLOR_MAP['solution_edge']
        self.graph.nodes[optimal_route[0]]['color'] = COLOR_MAP['solution_start_node']
        self.graph.nodes[optimal_route[-1]]['color'] = COLOR_MAP['solution_end_node']
        return optimal_route


if __name__ == "__main__":
    model = GraphModel(data_path="visibility_graph.json")
    model.insert_node(node=(50, 30))
    model.insert_node(node=(50, 160))
    model.insert_node(node=(350, 180))
    model.insert_node(node=(80, 500))
    model.insert_node(node=(200, 550))
    model.insert_node(node=(480, 540))
    print(model.solve_tsp())
