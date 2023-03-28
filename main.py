import json
import networkx as nx
from typing import List
from functools import partial

import pygame.freetype

import sim.constants as constants
from sim.entities import (
    Graph,
    Warehouse,
    Viewable,
    Robot,
    FPSCounter,
    VisibilityController,
)
from sim.control import RobotController
from sim.graph_model import GraphModel, manhattan_distance

pygame.init()

SCALE = 2
BASE_NODE_RADIUS = 5
BASE_STEP_SIZE = 1
DIMENSIONS_SETTINGS_PATH = "gen/dimensions.json"
LAYOUT_DATA_PATH = "gen/polygon.json"
GRAPH_DATA_PATH = "gen/visibility_graph.json"


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    settings = load_json(DIMENSIONS_SETTINGS_PATH)

    map_length = settings["warehouse"]["length"] * SCALE
    map_width = settings["warehouse"]["width"] * SCALE
    screen = pygame.display.set_mode([map_width, map_length])

    polygons = load_json(LAYOUT_DATA_PATH)
    warehouse = Warehouse(polygons)

    robot_length = settings["robot"]["length"] * SCALE
    robot_width = settings["robot"]["width"] * SCALE
    robot = Robot(x=5 * SCALE, y=5 * SCALE, width=robot_width, length=robot_length)

    a_star_shortest_path = partial(nx.astar_path, heuristic=manhattan_distance)
    a_star_shortest_path_length = partial(
        nx.astar_path_length, heuristic=manhattan_distance
    )

    model = GraphModel(
        data_path=GRAPH_DATA_PATH,
        sp_alg=a_star_shortest_path,
        sp_length_alg=a_star_shortest_path_length,
    )
    model.insert_node(node=(robot.x, robot.y))

    node_radius = BASE_NODE_RADIUS * SCALE
    visibility_graph = Graph(model=model, radius=node_radius)

    clock = pygame.time.Clock()
    fps_counter = FPSCounter(x=int(map_width * 0.8), y=10, clock=clock)

    step_size = BASE_STEP_SIZE * SCALE
    robot_controller = RobotController(robot, step_size)

    visible_objects: List[Viewable] = [warehouse, visibility_graph, robot, fps_counter]
    visibility_controller = VisibilityController(visible_objects)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # f - run robot controller
                # n - add new point that the robot should visit
                # r - clears all points
                if event.key == ord("f") and not robot_controller.instructions:
                    robot_controller.push_new_instructions(model.solve_tsp())
                if event.key == ord("n"):
                    user_node = pygame.mouse.get_pos()
                    model.insert_node(node=user_node)
                if event.key == ord("r"):
                    model.reset()
                    model.insert_node(node=(robot.x, robot.y))
                # Visibility Settings' keybinds
                mods = pygame.key.get_mods()
                if event.key == ord("q"):
                    if mods & pygame.KMOD_LSHIFT:
                        visibility_controller.show_object(fps_counter)
                    else:
                        visibility_controller.hide_object(fps_counter)
                if event.key == ord("w"):
                    if mods & pygame.KMOD_LSHIFT:
                        visibility_controller.show_object(visibility_graph)
                    else:
                        visibility_controller.hide_object(visibility_graph)
                if event.key == ord("e"):
                    if mods & pygame.KMOD_LSHIFT:
                        visibility_controller.show_object(warehouse)
                    else:
                        visibility_controller.hide_object(warehouse)
                if event.key == ord("t"):
                    if mods & pygame.KMOD_LSHIFT:
                        visibility_controller.show_object(robot)
                    else:
                        visibility_controller.hide_object(robot)

        clock.tick(60)
        robot_controller.move_robot()
        screen.fill(constants.WHITE)
        visibility_controller.draw(screen)
        pygame.display.flip()

    pygame.quit()
