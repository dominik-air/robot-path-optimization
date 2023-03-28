import jinja2


def convert_distance_matrix_to_string(distance_matrix: list[list[int]]) -> str:
    s = " "
    for row in distance_matrix:
        s += " ".join([str(int(w)) for w in row])
        s += "\n "
    s = s[:-1]
    return s


def render_tsplib_file(
    name: str, dimension: int, distance_matrix: str, output_dir: str
) -> str:
    file_loader = jinja2.FileSystemLoader("templates")
    jinja_env = jinja2.Environment(loader=file_loader)

    template = jinja_env.get_template("tsplib_template.tsp.j2")

    output = template.render(
        name=name,
        comment=f"Custom {dimension}-dimension TSP problem.",
        dimension=dimension,
        distance_matrix=distance_matrix,
    )

    output_file = f"{output_dir}/{name}.tsp"

    with open(output_file, "w") as f:
        f.write(output)

    return output_file
