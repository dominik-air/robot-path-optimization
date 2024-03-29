import pygame
import sim.constants
from sim.graph_model import GraphModel
from typing import Protocol, List


class Viewable(Protocol):
    def draw(self, surface: pygame.Surface) -> None:
        ...


class Warehouse:
    def __init__(self, polygons):
        self.polygons = polygons
        self.color = sim.constants.BLACK

    def draw(self, surface: pygame.Surface) -> None:
        for polygon in self.polygons:
            pygame.draw.polygon(surface, self.color, points=polygon)


class Graph:
    def __init__(self, model: GraphModel, radius: int):
        self.model = model
        self.radius = radius

    def draw(self, surface: pygame.Surface) -> None:
        for start, end, data in self.model.graph.edges(data=True):
            pygame.draw.line(surface, data["color"], start, end, width=4)
        for node, data in self.model.graph.nodes(data=True):
            pygame.draw.circle(surface, data["color"], center=node, radius=self.radius)


class FPSCounter:
    def __init__(self, x: int, y: int, clock: pygame.time.Clock):
        self.x = x
        self.y = y
        self.clock = clock
        self.font = pygame.freetype.SysFont("Arial", 20)

    @property
    def fps(self) -> int:
        return int(self.clock.get_fps())

    def draw(self, surface: pygame.Surface) -> None:
        self.font.render_to(
            surf=surface,
            dest=(self.x, self.y),
            text=f"FPS: {self.fps}",
            bgcolor=sim.constants.GREEN_POINTER,
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

    def draw(self, screen: pygame.Surface):
        for obj in self.visible_objects:
            obj.draw(screen)


class Robot:
    def __init__(self, x: int, y: int, width: int, length: int):
        self.rect = pygame.Rect(x, y, width, length)
        self.color = sim.constants.RED_ROBOT

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    def move(self, x: int, y: int) -> None:
        self.rect.move_ip(x, y)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
