import json
import networkx as nx


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


def shortest_path(source: str, target: str) -> list:
    graph_data = load_json("visibility_graph.json")

    nodes = graph_data["nodes_symbols"]
    edges = graph_data["edges_symbols"]
    mapping = graph_data["mapping"]

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    path = nx.shortest_path(G, source, target)
    return [mapping[p] for p in path]
