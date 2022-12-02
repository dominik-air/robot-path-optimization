from typing import Tuple, Dict
from enum import Enum
Color = Tuple[int, int, int]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE_VERTEX = (10, 10, 255)
RED_ROBOT = (255, 10, 10)
GREEN_POINTER = (10, 255, 10)

class Origin(str, Enum):
    BASE_NODE = "base_node"
    USER_NODE = "user_node"
    BASE_EDGE = "base_edge"
    SOLUTION_EDGE = "solution_edge"
    SOLUTION_START_NODE = "solution_start_node"
    SOLUTION_END_NODE = "solution_end_node"


COLOR_MAP: Dict[Origin, Color] = {
    Origin.BASE_NODE: (219, 36, 20),
    Origin.BASE_EDGE: (17, 136, 120),
    Origin.USER_NODE: (38, 188, 222),
    Origin.SOLUTION_EDGE: (235, 195, 52),
    Origin.SOLUTION_START_NODE: (30, 140, 18),
    Origin.SOLUTION_END_NODE: (143, 14, 194),
}
