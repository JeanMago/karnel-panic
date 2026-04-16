import pygame
from ecs.entity import Entity
from config import PLAYER_SPEED


class Player(Entity):
    def __init__(self, x, y):
        super().__init__()

        self.properties = {
            "tipo": "processo",
            "state": "running",
            "health": 100,
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "speed": PLAYER_SPEED,
            "token": "@PID:0xCAFE",
            "color": (0, 255, 0),
            "hostile": False,
        }

    def update(self):
        keys = pygame.key.get_pressed()
        spd = self.properties.get("speed")
        if spd is None:
            return
        try:
            spd = float(spd)
        except (TypeError, ValueError):
            return

        if keys[pygame.K_w]:
            self.properties["y"] -= spd
        if keys[pygame.K_s]:
            self.properties["y"] += spd
        if keys[pygame.K_a]:
            self.properties["x"] -= spd
        if keys[pygame.K_d]:
            self.properties["x"] += spd

    def render(self, screen):
        pygame.draw.rect(
            screen,
            self.properties["color"],
            (
                self.properties["x"],
                self.properties["y"],
                self.properties["w"],
                self.properties["h"],
            ),
        )
