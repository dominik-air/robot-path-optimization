from dataclasses import dataclass
from sim.entities import Robot
from sim.geometry import create_robot_moves

@dataclass
class InstructionSet:
    move: tuple[float, float]
    allignment_reference: tuple[int, int] | None


def create_instruction_sets(moves: list[tuple[float, float]], reference_point: tuple[int, int]) -> list[InstructionSet]:
    instruction_sets = []
    for move in moves[:-1]:
        instruction_sets.append(InstructionSet(move, allignment_reference=None))
    instruction_sets.append(InstructionSet(moves[-1], reference_point))
    return instruction_sets


class RobotController:
    def __init__(self, robot: Robot, step_size: int):
        self.robot: Robot = robot
        self.step_size: int = step_size
        self.instructions: list[InstructionSet] = []

    def push_new_instructions(self, new_points):
        points: list[tuple[int, int]] = [(self.robot.x, self.robot.y)] + new_points
        for p1, p2 in zip(points[:-1], points[1:]):
            x_start, y_start = p1
            x_end, y_end = p2
            moves = create_robot_moves(x_start, y_start, x_end, y_end, self.step_size)
            self.instructions.extend(create_instruction_sets(moves, p2))
    
    def correct_position(self, reference_point: tuple[int, int]) -> None:
        x, y = reference_point
        x -= self.robot.x
        y -= self.robot.y
        self.robot.move(x, y)

    def move_robot(self) -> None:
        try:
            instruction_set = self.instructions.pop(0)
            self.robot.move(*instruction_set.move)
            if instruction_set.allignment_reference is not None:
                self.correct_position(instruction_set.allignment_reference)
        except IndexError:
            pass

