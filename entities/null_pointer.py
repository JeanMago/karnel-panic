import pygame
from ecs.entity import Entity

class NullPointer(Entity):
    def __init__(self, x, y, target=None):
        super().__init__()

        self.target = target
        self.properties = {
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "speed": 2,
            "visible": True,
            "color": (255, 0, 0)
        }

    def update(self):
        # O NullPointer persegue o alvo (Player) se possuir velocidade
        speed = self.properties.get("speed", 0)
        if speed is None:
            speed = 0
            
        if self.target and speed > 0:
            tx = self.target.properties.get("x", self.properties["x"])
            ty = self.target.properties.get("y", self.properties["y"])
            
            if self.properties["x"] < tx: self.properties["x"] += speed
            if self.properties["x"] > tx: self.properties["x"] -= speed
            if self.properties["y"] < ty: self.properties["y"] += speed
            if self.properties["y"] > ty: self.properties["y"] -= speed

    def render(self, screen):
        if not self.properties["visible"]:
            return

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
