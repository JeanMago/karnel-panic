import pygame
from ecs.entity import Entity


class NullPointer(Entity):
    """Invisível/inerte até `reference` válido (paste/patch); depois persegue o alvo."""

    def __init__(self, x, y, target=None):
        super().__init__()
        self.target = target

        self.properties = {
            "tipo": "NullPointer",
            "state": "dangling",
            "health": 30,
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "speed": 22,
            "reference": None,
            "visible": False,
            "color": (255, 80, 80),
            "hostile": True,
        }

    def _is_resolved(self) -> bool:
        return self.properties.get("reference") is not None

    def update(self):
        if not self._is_resolved():
            self.properties["visible"] = False
            self.properties["state"] = "dangling"
            return

        self.properties["visible"] = True
        self.properties["state"] = "chasing"

        speed = self.properties.get("speed")
        if speed is None:
            speed = 0
        try:
            speed = float(speed)
        except (TypeError, ValueError):
            speed = 0

        if self.target and speed > 0:
            tx = self.target.properties.get("x", self.properties["x"])
            ty = self.target.properties.get("y", self.properties["y"])

            if self.properties["x"] < tx:
                self.properties["x"] += speed
            if self.properties["x"] > tx:
                self.properties["x"] -= speed
            if self.properties["y"] < ty:
                self.properties["y"] += speed
            if self.properties["y"] > ty:
                self.properties["y"] -= speed

    def render(self, screen):
        if not self.properties.get("visible"):
            return

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
