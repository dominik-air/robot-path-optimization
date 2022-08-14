import json
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


def manhattan_distance(n1, n2) -> int:
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


class GraphModel:
    def __init__(self, data_path: str):
        self.data_path = data_path
        graph_data = load_json(data_path)
        self.nodes = graph_data["nodes_symbols"]
        self.edges = graph_data["edges_symbols"]
        self.mapping = graph_data["mapping"]
        self.nodes_to_visit = []

    @property
    def nodes_numeric(self):
        return [self.mapping[n] for n in self.nodes]

    @property
    def edges_numeric(self):
        return [(self.mapping[e[0]], self.mapping[e[1]]) for e in self.edges]

    def shortest_path(self, source: str, target: str) -> list:
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_edges_from(self.edges)

        path = nx.shortest_path(G, source, target)
        return [self.mapping[p] for p in path]

    def insert_node(self, node, node_symbol: str) -> None:
        self.nodes_to_visit.append(node_symbol)
        nodes = [self.mapping[n] for n in self.nodes]
        nearest = nodes[0]
        best_dist = manhattan_distance(node, nearest)
        for neighbour in nodes[1:]:
            if best_dist > manhattan_distance(node, neighbour):
                nearest = neighbour
                best_dist = manhattan_distance(node, neighbour)
        nearest_symbol = None
        for k, v in self.mapping.items():
            if v == nearest:
                nearest_symbol = k
                break
        self.nodes.append(node_symbol)
        self.edges.append((node_symbol, nearest_symbol))
        self.edges.append((nearest_symbol, node_symbol))
        self.mapping[node_symbol] = node

    def reset(self):
        graph_data = load_json(self.data_path)
        self.nodes = graph_data["nodes_symbols"]
        self.edges = graph_data["edges_symbols"]
        self.mapping = graph_data["mapping"]
        self.nodes_to_visit.clear()

    def create_distance_matrix(self):
        matrix = []
        nodes = [self.mapping[n] for n in self.nodes_to_visit]
        for n1 in nodes:
            row = []
            for n2 in nodes:
                row.append(manhattan_distance(n1, n2))
            matrix.append(row)
        return matrix

    def solve_tsp(self) -> list:
        path, cost = tsp_solver(self.create_distance_matrix())
        path = path[:-1]  # no need to go pack to the starting position
        path_symbols = [self.nodes_to_visit[idx] for idx in path]
        routes = [
            self.shortest_path(source=p1, target=p2)
            for p1, p2 in zip(path_symbols[:-1], path_symbols[1:])
        ]
        whole_route = [v for p in routes for v in p[1:]]
        return whole_route


if __name__ == "__main__":
    model = GraphModel(data_path="visibility_graph.json")
    model.insert_node(node=(50, 30), node_symbol="Robot")
    model.insert_node(node=(50, 160), node_symbol="P0")
    model.insert_node(node=(350, 180), node_symbol="P1")
    model.insert_node(node=(80, 500), node_symbol="P2")
    model.insert_node(node=(200, 550), node_symbol="P3")
    model.insert_node(node=(480, 540), node_symbol="P4")
    print(model.solve_tsp())
