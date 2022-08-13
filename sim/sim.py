import pygame.freetype
import json
import constants
from typing import List
from geometry import create_robot_moves
from entities import (
    VisibilityGraph,
    Warehouse,
    Viewable,
    Robot,
    FPSCounter,
    VisibilityController,
)

pygame.init()


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


def try_some_moves(robot: Robot, i: int, moves: list):
    try:
        move = moves[i]
        robot.move(*move)
    except IndexError:
        return


def create_instruction_set(points, step_size) -> list:
    instructions = []
    for p1, p2 in zip(points[:-1], points[1:]):
        x_start, y_start = p1
        x_end, y_end = p2
        instructions += create_robot_moves(x_start, y_start, x_end, y_end, step_size)
    return instructions


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
    nodes = load_json("nodes.json")
    visibility_graph = VisibilityGraph(nodes, radius=10)

    robot = Robot(x=5 * SCALE, y=5 * SCALE, width=ROBOT_WIDTH, length=ROBOT_LENGTH)

    fps_counter = FPSCounter(x=int(MAP_WIDTH * 0.8), y=10)

    visible_objects: List[Viewable] = [robot, warehouse]
    controller = VisibilityController(visible_objects)

    points = [(robot.x, robot.y)]
    moves = []
    circles = []

    running = True
    i = 0
    j = 0
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
                    robot.enable()
                    i = 0
                    j = 0
                    moves = create_instruction_set(points, step_size)
                if event.key == ord("n") and not robot.enabled:
                    pos = pygame.mouse.get_pos()
                    circles.append(pos)
                    points.append(pos)
                if event.key == ord("r"):
                    robot.disable()
                    points = [(robot.x, robot.y)]
                    circles = []
                # Visibility Settings' keybinds
                mods = pygame.key.get_mods()
                if event.key == ord("q"):
                    if mods & pygame.KMOD_LSHIFT:
                        controller.show_object(fps_counter)
                    else:
                        controller.hide_object(fps_counter)
                if event.key == ord("w"):
                    if mods & pygame.KMOD_LSHIFT:
                        controller.show_object(visibility_graph)
                    else:
                        controller.hide_object(visibility_graph)
                if event.key == ord("e"):
                    if mods & pygame.KMOD_LSHIFT:
                        controller.show_object(warehouse)
                    else:
                        controller.hide_object(warehouse)
                if event.key == ord("t"):
                    if mods & pygame.KMOD_LSHIFT:
                        controller.show_object(robot)
                    else:
                        controller.hide_object(robot)

        if robot.enabled:
            if j % (fps_counter.fps / 1000) == 0:
                try_some_moves(robot, i, moves)
                i += 1
            j += 1

        screen.fill(constants.WHITE)

        for p in circles:
            pygame.draw.circle(screen, constants.GREEN_POINTER, p, 5)

        for obj in visible_objects:
            obj.draw(screen)
        pygame.display.flip()

    pygame.quit()
