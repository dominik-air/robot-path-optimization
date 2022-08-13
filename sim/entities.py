import pygame
import constants
from typing import Protocol, List


class Viewable(Protocol):
    def draw(self, surface: pygame.Surface) -> None:
        ...


class Warehouse:
    def __init__(self, polygons):
        self.polygons = polygons
        self.color = constants.BLACK

    def draw(self, surface: pygame.Surface) -> None:
        for polygon in self.polygons:
            pygame.draw.polygon(surface, self.color, points=polygon)


class VisibilityGraph:
    def __init__(self, nodes, radius: int = 3):
        self.nodes = nodes
        self.color = constants.BLUE_VERTEX
        self.radius = radius

    def draw(self, surface: pygame.Surface) -> None:
        for node in self.nodes:
            pygame.draw.circle(surface, self.color, center=node, radius=self.radius)


class FPSCounter:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.clock = pygame.time.Clock()
        self.font = pygame.freetype.SysFont("Arial", 20)

    @property
    def fps(self) -> float:
        self.clock.tick()
        return self.clock.get_fps()

    def draw(self, surface: pygame.Surface):
        self.font.render_to(
            surf=surface,
            dest=(self.x, self.y),
            text=f"FPS: {self.fps}",
            bgcolor=constants.GREEN_POINTER,
        )


class VisibilityController:
    def __init__(self, objects: List[Viewable]):
        self.visible_objects = objects

    def show_object(self, x: Viewable) -> None:
        if x not in self.visible_objects:
            self.visible_objects.append(x)

    def hide_object(self, x: Viewable) -> None:
        if x in self.visible_objects:
            self.visible_objects.remove(x)


class Robot:
    def __init__(self, x: int, y: int, width: int, length: int):
        self.rect = pygame.Rect(x, y, width, length)
        self.color = constants.RED_ROBOT
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

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)
