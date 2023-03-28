from typing import Callable
from sim.types import Node

DistanceMetric = Callable[[Node, Node, dict | None], float | int]


def euclidean_distance(n1: Node, n2: Node, edge_attributes: dict = None) -> float:
    """Calculates the euclidean distance between two nodes.
    The edge_attributes argument is present to comply with the interface for callables in nx.shortest_path_length.
    """
    return ((n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2) ** 0.5


def manhattan_distance(n1: Node, n2: Node, edge_attributes: dict = None) -> int:
    """Calculates the manhattan distance between two nodes.
    The edge_attributes argument is present to comply with the interface for callables in nx.shortest_path_length.
    """
    return abs(n1[0] - n2[0]) + abs(n1[1] - n2[1])
