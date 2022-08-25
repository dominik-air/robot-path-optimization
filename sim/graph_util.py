def create_coordinates_matrix(scale=2):
    xs = [15 * scale]
    for i in range(1, 4):
        if i in [1, 3]:
            next_x = xs[-1] + 16 * scale + 40 * scale + 15 * scale
        else:
            next_x = xs[-1] + 16 * scale + 80 * scale
        xs.append(next_x)
    ys = [15 * scale]
    for j in range(1, 5):
        if j in [1, 4]:
            next_y = ys[-1] + (int(116 / 2) + 15) * scale
        else:
            next_y = ys[-1] + int(116 / 2) * scale + 30 * scale
        ys.append(next_y)

    coordinates = [(x, y) for y in ys for x in xs]

    return [coordinates[4 * i: 4 * i + 4] for i in range(5)]


def create_adjacency_list(matrix):
    adj_list = {}
    X = len(matrix)
    Y = len(matrix[0])
    for i in range(X):
        for j in range(Y):
            neighbors = []
            if i - 1 >= 0:
                neighbors.append(matrix[i - 1][j])
            if j - 1 >= 0 and i % 2 == 0:
                neighbors.append(matrix[i][j - 1])
            if i + 1 < X:
                neighbors.append(matrix[i + 1][j])
            if j + 1 < Y and i % 2 == 0:
                neighbors.append(matrix[i][j + 1])

            adj_list[matrix[i][j]] = neighbors
    return adj_list


if __name__ == "__main__":
    import json

    coordinates = create_coordinates_matrix()

    adj_list = create_adjacency_list(coordinates)
    nodes = list(adj_list.keys())

    edges = []
    for k in adj_list:
        for v in adj_list[k]:
            edges.append((k, v))
    edges = list(set(edges))

    data = {
        "nodes": nodes,
        "edges": edges,
    }

    with open("../data/visibility_graph.json", "w") as f:
        json.dump(data, f, indent=4)
