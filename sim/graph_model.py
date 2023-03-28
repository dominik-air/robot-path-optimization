import networkx as nx
from typing import List
from sim.constants import Origin, COLOR_MAP
from sim.tsp import TSP_Solver, ortools_solver
from sim.types import Node
from sim.utils import load_graph_data_from_json
from sim.distance_metrics import DistanceMetric, manhattan_distance
from sim.shortest_path import ShortestPathAlgorithm, ShortestPathLengthAlgorithm


class GraphModel:
    def __init__(
        self,
        data_path: str,
        sp_alg: ShortestPathAlgorithm = nx.shortest_path,
        sp_length_alg: ShortestPathLengthAlgorithm = nx.shortest_path_length,
        tsp_solver: TSP_Solver = ortools_solver,
        distance_metric: DistanceMetric = manhattan_distance,
    ):
        self.graph = nx.Graph()
        graph_data = load_graph_data_from_json(data_path)
        self.graph.add_nodes_from(
            graph_data["nodes"], color=COLOR_MAP[Origin.BASE_NODE]
        )
        self.graph.add_edges_from(
            graph_data["edges"], color=COLOR_MAP[Origin.BASE_EDGE]
        )

        self.shortest_path = sp_alg
        self.shortest_path_length = sp_length_alg
        self.tsp_solver = tsp_solver
        self.distance_metric = distance_metric

    def insert_node(self, node: Node) -> None:
        nodes = [
            n
            for n, data in self.graph.nodes(data=True)
            if data["color"] != COLOR_MAP[Origin.USER_NODE]
        ]
        nearest = nodes[0]
        best_dist = self.distance_metric(node, nearest)
        for neighbour in nodes[1:]:
            distance = self.distance_metric(node, neighbour)
            if best_dist > distance:
                nearest = neighbour
                best_dist = distance
        self.graph.add_node(node, color=COLOR_MAP[Origin.USER_NODE])
        self.graph.add_edge(node, nearest, color=COLOR_MAP[Origin.SOLUTION_EDGE])

    def list_nodes_from(self, origin: Origin) -> List[Node]:
        nodes = []
        for node, data in self.graph.nodes(data=True):
            if data["color"] == COLOR_MAP[origin]:
                nodes.append(node)
        return nodes

    def reset(self) -> None:
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if data["color"] == COLOR_MAP[Origin.USER_NODE]:
                nodes_to_remove.append(node)
        self.graph.remove_nodes_from(nodes_to_remove)
        nx.set_node_attributes(
            self.graph, values=COLOR_MAP[Origin.BASE_NODE], name="color"
        )
        nx.set_edge_attributes(
            self.graph, values=COLOR_MAP[Origin.BASE_EDGE], name="color"
        )

    def create_distance_matrix(self) -> List[List[int]]:
        matrix = []
        nodes = self.list_nodes_from(origin=Origin.USER_NODE)
        for n1 in nodes:
            row = []
            for n2 in nodes:
                length = self.shortest_path_length(
                    self.graph, source=n1, target=n2, weight=self.distance_metric
                )
                row.append(length)
            matrix.append(row)
        return matrix

    def solve_tsp(self) -> list:
        nodes_to_visit = self.list_nodes_from(origin=Origin.USER_NODE)
        path = self.tsp_solver(self.create_distance_matrix())
        nodes_on_path = [nodes_to_visit[idx] for idx in path]

        optimal_route = []
        for n1, n2 in zip(nodes_on_path[:-1], nodes_on_path[1:]):
            optimal_route.extend(
                self.shortest_path(
                    self.graph, source=n1, target=n2, weight=self.distance_metric
                )[1:]
            )

        # color map significant nodes and edges in the optimal route
        for n1, n2 in zip(optimal_route[:-1], optimal_route[1:]):
            self.graph[n1][n2]["color"] = COLOR_MAP[Origin.SOLUTION_EDGE]
        self.graph.nodes[optimal_route[0]]["color"] = COLOR_MAP[
            Origin.SOLUTION_START_NODE
        ]
        self.graph.nodes[optimal_route[-1]]["color"] = COLOR_MAP[
            Origin.SOLUTION_END_NODE
        ]
        return optimal_route
