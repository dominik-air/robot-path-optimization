import pygame
import json
from .geometry import create_robot_moves

pygame.init()


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


class Robot:
    def __init__(self, x: int, y: int, width: int, length: int):
        self.rect = pygame.Rect(x, y, width, length)
        self.color = (255, 0, 0)
        self.enabled = False

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def move(self, x: int = 0, y: int = 0):
        self.rect.move_ip(x, y)

    def update(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


def draw_shelves() -> None:
    for row in range(ROWS):
        for col in range(COLS):
            x = X_OFFSET + col * (SHELF_WIDTH + X_SPACING)
            y = Y_OFFSET + row * (SHELF_LENGTH + Y_SPACING)
            rect = pygame.Rect(x, y, SHELF_WIDTH, SHELF_LENGTH)
            pygame.draw.rect(screen, (0, 0, 0), rect)


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


if __name__ == '__main__':

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
    FPS = 60

    robot = Robot(x=5*SCALE, y=5*SCALE, width=ROBOT_WIDTH, length=ROBOT_LENGTH)

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

        if robot.enabled:
            if j % FPS == 0:
                try_some_moves(robot, i, moves)
                i += 1
            j += 1

        screen.fill((255, 255, 255))

        for p in circles:
            pygame.draw.circle(screen, (0, 255, 0), p, 5)

        draw_shelves()
        robot.update(screen)
        pygame.display.flip()

    pygame.quit()
