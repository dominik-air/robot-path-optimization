from sim.entities import Robot
from sim.geometry import create_robot_moves


class RobotController:
    def __init__(self, robot: Robot, step_size: int):
        self.robot = robot
        self.step_size = step_size
        self.instructions = []

    def push_new_instructions(self, new_points):
        moves = []
        points = [(self.robot.x, self.robot.y)] + new_points
        for p1, p2 in zip(points[:-1], points[1:]):
            x_start, y_start = p1
            x_end, y_end = p2
            moves += create_robot_moves(x_start, y_start, x_end, y_end, self.step_size)
        self.instructions.extend(moves)

    def move_robot(self) -> None:
        try:
            move = self.instructions.pop(0)
        except IndexError:
            move = 0, 0
        self.robot.move(*move)
