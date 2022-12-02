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
from sim.graphs import GraphModel, manhattan_distance

pygame.init()

def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    SCALE = 2
    SETTINGS = load_json("data/dimensions.json")

    MAP_LENGTH = SETTINGS["warehouse"]["length"] * SCALE
    MAP_WIDTH = SETTINGS["warehouse"]["width"] * SCALE
    ROBOT_LENGTH = SETTINGS["robot"]["length"] * SCALE
    ROBOT_WIDTH = SETTINGS["robot"]["width"] * SCALE

    screen = pygame.display.set_mode([MAP_WIDTH, MAP_LENGTH])

    STEP_SIZE = 1 * SCALE

    polygons = load_json("data/polygon.json")
    warehouse = Warehouse(polygons)

    robot = Robot(x=5 * SCALE, y=5 * SCALE, width=ROBOT_WIDTH, length=ROBOT_LENGTH)

    a_star_shortest_path = partial(nx.astar_path, heuristic=manhattan_distance) 
    a_star_shortest_path_length = partial(nx.astar_path_length, heuristic=manhattan_distance) 

    model = GraphModel(data_path="data/visibility_graph.json",
                       sp_alg=a_star_shortest_path,
                       sp_length_alg=a_star_shortest_path_length)
    model.insert_node(node=(robot.x, robot.y))

    visibility_graph = Graph(
        model=model,
        radius=10
    )

    clock = pygame.time.Clock()
    fps_counter = FPSCounter(x=int(MAP_WIDTH * 0.8), y=10, clock=clock)

    robot_controller = RobotController(robot, STEP_SIZE)

    visible_objects: List[Viewable] = [warehouse, visibility_graph, robot, fps_counter]
    visibility_controller = VisibilityController(visible_objects)

    while running := True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # f - run robot controller
                # n - add new point that the robot should visit
                # r - clears points that the robot should visit
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
