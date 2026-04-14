import pygame
from ecs.entity import Entity
from config import PLAYER_SPEED

class Player(Entity):
    def __init__(self, x, y):
        super().__init__()

        self.properties = {
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "speed": PLAYER_SPEED,
            "color": (0, 255, 0)
        }

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.properties["y"] -= self.properties["speed"]
        if keys[pygame.K_s]:
            self.properties["y"] += self.properties["speed"]
        if keys[pygame.K_a]:
            self.properties["x"] -= self.properties["speed"]
        if keys[pygame.K_d]:
            self.properties["x"] += self.properties["speed"]

    def render(self, screen):
        pygame.draw.rect(
            screen,
            self.properties["color"],
            (
                self.properties["x"],
                self.properties["y"],
                self.properties["w"],
                self.properties["h"]
            )
        )
