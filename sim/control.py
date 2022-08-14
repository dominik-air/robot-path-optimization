from entities import Robot
from geometry import create_robot_moves


def moves_gen():
    while True:
        moves = yield
        if moves is None:
            yield
        else:
            for move in moves:
                yield move


class RobotController:
    def __init__(self, robot: Robot, step_size: int):
        self.robot = robot
        self.step_size = step_size
        self.moves_gen = moves_gen()

    def push_new_instructions(self, new_points):
        moves = []
        points = [(self.robot.x, self.robot.y)] + new_points
        for p1, p2 in zip(points[:-1], points[1:]):
            x_start, y_start = p1
            x_end, y_end = p2
            moves += create_robot_moves(x_start, y_start, x_end, y_end, self.step_size)
        next(self.moves_gen)  # clear the generator
        self.moves_gen.send(moves)

    def move_robot(self) -> None:
        move = next(self.moves_gen)
        if move is None:
            move = 0, 0
        self.robot.move(*move)
