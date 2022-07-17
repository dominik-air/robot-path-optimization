import pygame
import json
from geometry import create_robot_moves

pygame.init()


def load_json(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


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

step_size = 2 * SCALE
FPS = 60
screen = pygame.display.set_mode([MAP_WIDTH, MAP_LENGTH])


class Robot:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, ROBOT_WIDTH, ROBOT_LENGTH)
        self.color = (255, 0, 0)

    def move(self, x: int = 0, y: int = 0):
        self.rect.move_ip(x, y)

    def update(self):
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
    except IndexError:
        move = (0, 0)
    robot.move(*move)


def create_instruction_set(points) -> list:
    instructions = []
    for p1, p2 in zip(points[:-1], points[1:]):
        x_start, y_start = p1
        x_end, y_end = p2
        instructions += create_robot_moves(x_start, y_start, x_end, y_end, step_size)
    return instructions


if __name__ == '__main__':

    x_start = 5 * SCALE
    y_start = 5 * SCALE
    robot = Robot(x_start, y_start)
    x_end = 400
    y_end = 600
    points = [(x_start, y_start), (x_end, y_start), (x_end, y_end)]
    points += points[1::-1]
    moves = create_instruction_set(points)

    running = True
    i = 0
    j = 0
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    robot.move(x=-step_size)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    robot.move(x=step_size)
                if event.key == pygame.K_UP or event.key == ord('w'):
                    robot.move(y=-step_size)
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    robot.move(y=step_size)

        screen.fill((255, 255, 255))
        if j % FPS == 0:
            try_some_moves(robot, i, moves)
            i += 1
        j += 1
        draw_shelves()
        robot.update()
        pygame.display.flip()

    pygame.quit()
