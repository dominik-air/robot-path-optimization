import pygame.freetype
import json
import constants
from typing import List
from entities import (
    Graph,
    Warehouse,
    Viewable,
    Robot,
    FPSCounter,
    VisibilityController,
)
from control import RobotController

pygame.init()


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    SCALE = 2
    SETTINGS = load_json("dimensions.json")

    MAP_LENGTH = SETTINGS["warehouse"]["length"] * SCALE
    MAP_WIDTH = SETTINGS["warehouse"]["width"] * SCALE

    ROWS = SETTINGS["warehouse"]["layout"]["rows"]
    COLS = SETTINGS["warehouse"]["layout"]["columns"]

    X_OFFSET = SETTINGS["warehouse"]["layout"]["x_offset"] * SCALE
    Y_OFFSET = SETTINGS["warehouse"]["layout"]["y_offset"] * SCALE
    X_SPACING = SETTINGS["warehouse"]["layout"]["x_spacing"] * SCALE
    Y_SPACING = SETTINGS["warehouse"]["layout"]["y_spacing"] * SCALE

    SHELF_LENGTH = SETTINGS["shelf"]["length"] * SCALE
    SHELF_WIDTH = SETTINGS["shelf"]["width"] * SCALE

    ROBOT_LENGTH = SETTINGS["robot"]["length"] * SCALE
    ROBOT_WIDTH = SETTINGS["robot"]["width"] * SCALE

    screen = pygame.display.set_mode([MAP_WIDTH, MAP_LENGTH])

    step_size = 1 * SCALE

    polygons = load_json("polygon.json")
    warehouse = Warehouse(polygons)
    graph_data = load_json("visibility_graph.json")

    nodes = graph_data["nodes"]
    edges = graph_data["edges"]

    visibility_graph = Graph(
        nodes=nodes,
        color=constants.BLUE_VERTEX,
        edges=edges,
        edge_color=constants.RED_ROBOT,
        radius=10,
    )

    robot = Robot(x=5 * SCALE, y=5 * SCALE, width=ROBOT_WIDTH, length=ROBOT_LENGTH)

    fps_counter = FPSCounter(x=int(MAP_WIDTH * 0.8), y=10)

    robot_controller = RobotController(robot, step_size)
    user_nodes = Graph(
        nodes=robot_controller.points, color=constants.GREEN_POINTER, radius=5
    )

    visible_objects: List[Viewable] = [robot, warehouse, user_nodes, fps_counter]
    visibility_controller = VisibilityController(visible_objects)

    i = 0
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # FIXME: the ruleset (the sim's structure overall) isn't defined
                #  in the most verbose way it could have been, but it works for now
                # f - run robot
                # n - add new point that the robot should visit
                # r - reset robot (also clears points)
                if event.key == ord("f"):
                    i = 0
                    robot_controller.push_new_instructions()
                if event.key == ord("n"):
                    robot_controller.add_point(pygame.mouse.get_pos())
                if event.key == ord("r"):
                    robot_controller.clear_points()
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

        if fps_counter.fps and i % (fps_counter.fps / 1000) == 0:
            robot_controller.move_robot()
        i += 1

        screen.fill(constants.WHITE)

        for obj in visible_objects:
            obj.draw(screen)
        pygame.display.flip()

    pygame.quit()
