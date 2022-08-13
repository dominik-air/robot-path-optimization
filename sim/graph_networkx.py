import json
import networkx as nx


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main___":
    graph_data = load_json("visibility_graph_symbolic.json")

    nodes = graph_data["nodes"]
    edges = graph_data["edges"]

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    path = nx.shortest_path(G, source="A", target="O")
    print(path)
