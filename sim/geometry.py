import math
from sympy import Segment2D, Point2D


def split_segment(segment: Segment2D, step_size: int) -> list[Point2D]:
    """Splits the segment into equal parts and returns a list of points that match each part's starting point."""
    n = math.ceil(segment.length / step_size)
    move_vector = segment.direction / n
    movement = [segment.p1 + move_vector]
    for _ in range(n - 2):
        next_move = movement[-1] + move_vector
        movement.append(next_move)
    movement.append(segment.p2)
    return movement


def create_robot_instructions(points: list[Point2D], robot_starting_point: Point2D) -> list:
    """Transforms points into tuples of integer roundings of the given 2D coordinates."""
    points = [robot_starting_point] + points[::]  # list copy trick to avoid side effects
    instructions = []
    for p1, p2 in zip(points[:-1], points[1:]):
        difference = (p2 - p1).coordinates
        instructions.append((round(difference[0]), round(difference[1])))
    return instructions


def create_robot_moves(x_start: int, y_start: int, x_end: int, y_end: int, step_size: int) -> list:
    """Interface for external use of this module."""
    start = Point2D(x_start, y_start)
    end = Point2D(x_end, y_end)
    path = Segment2D(start, end)
    return create_robot_instructions(points=split_segment(path, step_size), robot_starting_point=start)
