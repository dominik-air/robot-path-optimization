import json
import pygame.freetype
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
from graphs import GraphModel

pygame.init()


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


if __name__ == "__main__":
    # FIXME: the old settings file is out of date - needs some love
    SCALE = 2
    SETTINGS = load_json("dimensions.json")

    MAP_LENGTH = SETTINGS["warehouse"]["length"] * SCALE
    MAP_WIDTH = SETTINGS["warehouse"]["width"] * SCALE
    ROBOT_LENGTH = SETTINGS["robot"]["length"] * SCALE
    ROBOT_WIDTH = SETTINGS["robot"]["width"] * SCALE

    screen = pygame.display.set_mode([MAP_WIDTH, MAP_LENGTH])

    step_size = 1 * SCALE

    polygons = load_json("polygon.json")
    warehouse = Warehouse(polygons)

    robot = Robot(x=5 * SCALE, y=5 * SCALE, width=ROBOT_WIDTH, length=ROBOT_LENGTH)

    model = GraphModel(data_path="visibility_graph.json")
    model.insert_node(node=(robot.x, robot.y))

    visibility_graph = Graph(
        model=model,
        radius=10
    )

    clock = pygame.time.Clock()
    fps_counter = FPSCounter(x=int(MAP_WIDTH * 0.8), y=10, clock=clock)

    robot_controller = RobotController(robot, step_size)

    visible_objects: List[Viewable] = [warehouse, visibility_graph, robot, fps_counter]
    visibility_controller = VisibilityController(visible_objects)

    while running := True:

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

        for obj in visible_objects:
            obj.draw(screen)
        pygame.display.flip()

    pygame.quit()
