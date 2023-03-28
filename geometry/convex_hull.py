import sympy as smp
from typing import List
from enum import Enum, auto
from operator import attrgetter


def sort_lexicographically(points: List[smp.Point2D]) -> List[smp.Point2D]:
    """Returns points sorted by x and y coordinate."""
    return sorted(sorted(points, key=attrgetter("y")), key=attrgetter("x"))


class Colocation(Enum):
    RIGHT = auto()
    LEFT = auto()
    COLINEAR = auto()


def determine_point_colocation(
    p: smp.Point2D, q: smp.Point2D, r: smp.Point2D, eps: float = 0
) -> Colocation:
    """Determines whether r lies left or right of the directed line through two points p and q."""
    det = q.x * (r.y - p.y) + p.x * (q.y - r.y) + r.x * (p.y - q.y)
    if det > eps:
        return Colocation.LEFT
    elif det < eps:
        return Colocation.RIGHT
    else:
        return Colocation.COLINEAR


def convex_hull(points: List[smp.Point2D]) -> List[smp.Point2D]:
    p = sort_lexicographically(points)
    L_upper = [p[0], p[1]]
    for i in range(2, len(points)):
        L_upper.append(p[i])
        while (
            len(L_upper) > 2
            and determine_point_colocation(*L_upper[-3:]) != Colocation.RIGHT
        ):
            L_upper.remove(L_upper[-2])
    L_lower = [p[-1], p[-2]]
    for i in reversed(range(len(points) - 2)):
        L_lower.append(p[i])
        while (
            len(L_lower) > 2
            and determine_point_colocation(*L_lower[-3:]) != Colocation.RIGHT
        ):
            L_lower.remove(L_lower[-2])
    return L_upper + L_lower
