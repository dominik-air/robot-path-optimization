import random
import heapq
import math
import json
import numpy as np
import sympy as smp
import matplotlib.pyplot as plt
import pyvisgraph as vg
from copy import deepcopy
from typing import Callable
from functools import partial
from convex_hull import convex_hull


Coordinate = tuple[int, int]
Sampler = Callable[[], vg.Point]
ProximityEstimator = Callable[[vg.Point], int]
PointMerger = Callable[[list[vg.Point]], list[vg.Point]]


def point_to_coord(point: vg.Point | smp.Point2D) -> Coordinate:
    "Coordinates are meant to be in mm, but the generator operates on cm."
    x = abs(point.x - MAP_SIZE)
    y = abs(point.y - MAP_SIZE)
    return int(x * 10), int(y * 10)


def save_polygons_to_json(
    polygons: list[list[Coordinate]], save_file: str = "polygon.json"
):
    with open(save_file, "w") as f:
        json.dump(polygons, f, indent=4)


def save_graph_to_json(
    nodes: list[Coordinate],
    edges: list[tuple[Coordinate, Coordinate]],
    save_file: str = "visibility_graph.json",
) -> None:
    with open(save_file, "w") as f:
        data = {"nodes": nodes, "edges": edges}
        json.dump(data, f, indent=4)


def save_board_dimensions(
    length: int, width: int, save_file: str = "dimensions.json"
) -> None:
    with open(save_file, "w") as f:
        data = {
            "robot": {"length": 10, "width": 10},
            "warehouse": {"length": length, "width": width},
        }
        json.dump(data, f, indent=4)


def save_points_of_interest(points_of_interest, save_file: str) -> None:
    with open(save_file, "w") as f:
        data = {"nodes": points_of_interest}
        json.dump(data, f, indent=4)


def create_polygon(
    n_sides: int, center_x: int, center_y: int, radius: int
) -> list[smp.Point2D]:
    vertices = []
    for i in range(n_sides):
        angle = 2 * math.pi * i / n_sides
        x = center_x + radius * math.cos(angle) + random.randint(-1, 1)
        y = center_y + radius * math.sin(angle) + random.randint(-1, 1)
        vertices.append(smp.Point2D(x, y))
    return vertices


def plot_polygon(vertices: list[vg.Point | smp.Point2D]) -> None:
    xh = [p.x for p in vertices]
    yh = [p.y for p in vertices]
    plt.plot(xh, yh, "o-")


def plot_free_states(points: list[vg.Point | smp.Point2D]) -> None:
    xh = [p.x for p in points]
    yh = [p.y for p in points]
    plt.plot(xh, yh, "ro")


def plot_edges(
    edges: list[tuple[vg.Point | smp.Point2D, vg.Point | smp.Point2D]]
) -> None:
    for edge in edges:
        xs = [edge[0].x, edge[1].x]
        ys = [edge[0].y, edge[1].y]
        plt.plot(xs, ys, "b--")


def merge_points(points: list[vg.Point], radius: int) -> list[vg.Point]:
    merged_points = []
    for point in points:
        close_enough = False
        for merged_point in merged_points:
            dx = point.x - merged_point.x
            dy = point.y - merged_point.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= radius:
                close_enough = True
                break
        if not close_enough:
            merged_points.append(point)

    return merged_points


def distance_between_points(p1: vg.Point, p2: vg.Point) -> float:
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return (dx * dx + dy * dy) ** 0.5


def find_k_nearest_visible_points(
    point: vg.Point, points: list[vg.Point], k: int, graph: vg.VisGraph
) -> list[vg.Point]:
    heap = []
    for p in points:
        distance = distance_between_points(p, point)
        # if the distance is equal to the SP then it is a straight path
        # (nodes are visible from each other's POV)
        if abs(graph.shortest_path(point, p)[0] - distance) <= 0.1:
            heap.append((distance, p))
    return [p for _, p in heapq.nsmallest(k, heap)]


def base_proximity_estimator(
    point: vg.Point, center: vg.Point, sigma: int | float
) -> int:
    distance = distance_between_points(point, center)
    if distance <= sigma:
        return 5
    elif distance <= 2 * sigma:
        return 4
    else:
        return 3


def create_edges(
    points: list[vg.Point],
    graph: vg.VisGraph,
    proximity_estimator: ProximityEstimator,
) -> list[tuple[vg.Point, vg.Point]]:
    edges = []
    for point in points:
        neighbours = points[::]
        neighbours.remove(point)
        k = proximity_estimator(point)
        nearest = find_k_nearest_visible_points(point, neighbours, k=k, graph=graph)
        for p in nearest:
            if (point, p) in edges or (p, point) in edges:
                continue
            edges.append((p, point))
    return edges


def create_vectors(width: int, heigth: int, base_length: int = 10) -> list[smp.Point2D]:
    width += 1
    heigth += 1
    if width <= 2 and heigth <= 2:
        return [smp.Point2D(0, 0)]
    vectors = []
    for i in range(heigth):
        for j in range(width):
            if (i + j) % 2 != 0:
                continue
            vectors.append(smp.Point(i * base_length, j * base_length))
    return vectors


def calculate_centroid(points) -> smp.Point2D:
    sum_x = 0
    sum_y = 0
    for point in points:
        sum_x += point.x
        sum_y += point.y
    n = len(points)
    centroid_x = int(sum_x / n)
    centroid_y = int(sum_y / n)
    return smp.Point2D(centroid_x, centroid_y)


def smp_points_to_vg(points: list[smp.Point2D]) -> list[vg.Point]:
    return [vg.Point(p.x, p.y) for p in points]


def create_vg_polys(polygons: list[list[smp.Point2D]]) -> list[list[vg.Point]]:
    return [smp_points_to_vg(poly) for poly in polygons]


class Layout:
    def __init__(
        self, vectors: list[smp.Point2D], radius_estimator: ProximityEstimator
    ) -> None:
        self.vectors = vectors
        self.figure_id = hash(self)
        self._polygons: list[list[smp.Point2D]] = None
        self.radius_estimator = radius_estimator

    @property
    def polygons(self) -> list[list[smp.Point2D]]:
        if self._polygons is None:
            raise ValueError("There are no polygons in the layout.")
        return deepcopy(self._polygons)

    def create_polygons(
        self,
        min_vertices: int = 4,
        max_vertices: int = 8,
    ) -> None:

        self._clear_layout()

        polygons = []
        for vector in self.vectors:
            vertices = create_polygon(
                n_sides=random.randint(min_vertices, max_vertices),
                center_x=vector.x,
                center_y=vector.y,
                radius=self.radius_estimator(vector),
            )
            polygon = convex_hull(vertices)
            polygons.append(polygon)

            self._plot_polygon(polygon)
        self._polygons = polygons

    def _clear_layout(self) -> None:
        plt.figure(self.figure_id)
        plt.clf()
        self._polygons = None

    def _plot_polygon(self, polygon: list[smp.Point2D]) -> None:
        plt.figure(self.figure_id)
        plot_polygon(polygon)

    def show(self) -> None:
        plt.figure(self.figure_id)
        plt.show()

    def save(self, save_file: str) -> None:
        polys = [[point_to_coord(v) for v in poly] for poly in self.polygons]
        save_polygons_to_json(polys, save_file)


class VisibilityGraph:
    def __init__(
        self,
        polygons: list[list[vg.Point]],
        sampler: Sampler,
        proximity_estimator: ProximityEstimator,
        point_merger: PointMerger,
    ) -> None:
        self.polygons = polygons

        self.sampler = sampler
        self.proximity_estimator = proximity_estimator
        self.point_merger = point_merger

        self.vis_graph = vg.VisGraph()
        self.figure_id = hash(self)

        self.vis_graph.build(deepcopy(self.polygons))

        self._nodes = None
        self._edges = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise ValueError("The visibility graph has no nodes.")
        return self._nodes

    @property
    def edges(self):
        if self._edges is None:
            raise ValueError("The visibility graph has no edges.")
        return self._edges

    def create_graph(self, sample_size: int, retries: int = 5) -> None:
        self._clear_visibility_graph()
        if retries <= 0:
            raise ValueError("There are no retries left.")

        self._create_nodes(sample_size)
        try:
            self._create_edges()
        except KeyError:
            print("Generated visibility graph is disconnected.")
            print("Retrying...")
            retries -= 1
            self.create_graph(sample_size, retries)

        self._plot_edges()
        self._plot_nodes()

    def _create_nodes(self, sample_size: int) -> None:
        samples = []
        for _ in range(sample_size):
            free_state = None
            p = None
            while free_state != -1 or p in samples:
                p = self.sampler()
                free_state = self.vis_graph.point_in_polygon(p)
            samples.append(p)
        self._nodes = self.point_merger(samples)

    def _create_edges(self) -> None:
        self._edges = create_edges(self.nodes, self.vis_graph, self.proximity_estimator)

    def _clear_visibility_graph(self) -> None:
        plt.figure(self.figure_id)
        plt.clf()
        self._nodes = None
        self._edges = None

    def _plot_polygons(self) -> None:
        plt.figure(self.figure_id)
        for polygon in self.polygons:
            plot_polygon(polygon)

    def _plot_edges(self) -> None:
        plt.figure(self.figure_id)
        plot_edges(self._edges)

    def _plot_nodes(self) -> None:
        plt.figure(self.figure_id)
        plot_free_states(self._nodes)

    def show(self) -> None:
        plt.figure(self.figure_id)
        self._plot_polygons()
        plt.show()
    
    def save_figure(self, save_file: str) -> None:
        plt.figure(self.figure_id)
        self._plot_polygons()
        plt.savefig(save_file, format='png')

    def save(self, save_file: str) -> None:
        nodes = [point_to_coord(p) for p in self._nodes]
        edges = [(point_to_coord(e[0]), point_to_coord(e[1])) for e in self._edges]
        save_graph_to_json(nodes, edges, save_file)


def generate_layout_with_graph(
    sigma: int,
    n_samples: int,
    vector_width: int,
    vector_heigth: int,
    save_directory: str,
    n_layouts: int,
    m_graphs: int
):
    vectors = create_vectors(vector_width, vector_heigth, base_length=8)
    mu = calculate_centroid(vectors)

    def sample_point() -> vg.Point:
        x = int(np.random.normal(loc=mu.x, scale=sigma))
        y = int(np.random.normal(loc=mu.y, scale=sigma))
        return vg.Point(x, y)
    
    for nth_layout in range(n_layouts):
        layout = Layout(
            vectors,
            radius_estimator=partial(
                base_proximity_estimator, center=vg.Point(mu.x, mu.y), sigma=sigma
            ),
        )
        layout.create_polygons()

        for mth_graph in range(m_graphs):
            graph = VisibilityGraph(
                polygons=create_vg_polys(layout.polygons),
                sampler=sample_point,
                proximity_estimator=partial(
                    base_proximity_estimator, center=vg.Point(mu.x, mu.y), sigma=sigma
                ),
                point_merger=partial(merge_points, radius=math.ceil(math.sqrt(sigma))),
            )

            try:
                graph.create_graph(sample_size=n_samples, retries=10)
            except ValueError:
                continue

            points_of_interest = smp_points_to_vg(vectors)
            plt.figure(graph.figure_id)
            plot_free_states(points_of_interest)

            graph.save_figure(f"{save_directory}/fig-{nth_layout}-{mth_graph}.png")
            plt.close(graph.figure_id)

            layout.save(save_file=f"{save_directory}/polygon-{nth_layout}-{mth_graph}.json")
            graph.save(save_file=f"{save_directory}/visibility_graph-{nth_layout}-{mth_graph}.json")
            poi = [point_to_coord(p) for p in points_of_interest]
            save_points_of_interest(poi, save_file=f"{save_directory}/packages-{nth_layout}-{mth_graph}.json")
        
        plt.close(layout.figure_id)

if __name__ == "__main__":
    v_sizes = [3, 4, 5, 6]
    map_sizes = [50, 60, 65, 70]
    sigmas = [5, 8, 11, 14]
    for v, ms, s in zip(v_sizes, map_sizes, sigmas):
        MAP_SIZE = ms
        dir_name = f"gen{v}"
        import os
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        generate_layout_with_graph(
            sigma=s,
            n_samples=1000,
            vector_heigth=v,
            vector_width=v,
            save_directory=dir_name,
            n_layouts=5,
            m_graphs=10
        )
