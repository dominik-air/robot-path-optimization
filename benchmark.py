import json
import networkx as nx
from functools import partial
from sim.graph_model import GraphModel
from sim.distance_metrics import euclidean_distance
from solvers.convert import convert_distance_matrix_to_string, render_tsplib_file

a_star_shortest_path = partial(nx.astar_path, heuristic=euclidean_distance)
a_star_shortest_path_length = partial(
    nx.astar_path_length, heuristic=euclidean_distance
)

scenarios = [
    (3, 0, 0), (3, 2, 8), (3, 3, 8), (3, 4, 7),
    (4, 0, 3), (4, 2, 7), (4, 3, 1), (4, 4, 6),
    (5, 0, 1), (5, 1, 0), (5, 2, 5), (5, 4, 3),
    (6, 1, 4), (6, 2, 3), (6, 3, 2), (6, 4, 0)
]

for scenario in scenarios:
    gen, n, m = scenario
    graph_data_path = f"gen{gen}/visibility_graph-{n}-{m}.json"
    packages_path = f"gen{gen}/packages-{n}-{m}.json"
    name = f"custom-{gen}-{m}-{n}"

    model = GraphModel(
        data_path=graph_data_path,
        sp_alg=a_star_shortest_path,
        sp_length_alg=a_star_shortest_path_length,
        distance_metric=euclidean_distance
    )


    with open(packages_path) as f:
        nodes = json.load(f)["nodes"]

    for node in nodes:
        model.insert_node(tuple(node))

    matrix = model.create_distance_matrix()

    m = convert_distance_matrix_to_string(matrix)

    tsplib_file = render_tsplib_file(
        name=name, dimension=len(matrix), distance_matrix=m, output_dir="custom_tsplibs"
    )

    print(tsplib_file)
