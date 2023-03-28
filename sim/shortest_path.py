import networkx as nx
from typing import Callable, List
from sim.types import Node

# use shortest path algorithms from networkx or such that align with the protocols below
ShortestPathAlgorithm = Callable[[nx.Graph, Node, Node], List[Node]]
ShortestPathLengthAlgorithm = Callable[[nx.Graph, Node, Node], int | float]
