import pygame
import math
import random
from ecs.entity import Entity

class Deadlock(Entity):
    """Inimigo que trava o movimento do player se chegar muito perto."""
    def __init__(self, x, y, target=None):
        super().__init__()
        self.target = target
        self.properties = {
            "tipo": "Deadlock",
            "state": "waiting",
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "speed": 2.0,
            "color": (200, 200, 200),
            "collision": True,
            "hostile": True,
            "health": 60,
            "lock_range": 150
        }
        self._angle = 0

    def update(self, dt):
        if self.target:
            tx, ty = self.target.properties.get("x", 0), self.target.properties.get("y", 0)
            dx, dy = tx - self.properties["x"], ty - self.properties["y"]
            dist = math.sqrt(dx**2 + dy**2)
            
            # Se estiver longe, persegue devagar
            if dist > self.properties["lock_range"]:
                speed = self.properties["speed"] * dt
                self.properties["x"] += (dx / dist) * speed
                self.properties["y"] += (dy / dist) * speed
                self.properties["state"] = "chasing"
                self.properties["color"] = (180, 180, 180)
            else:
                # Se estiver perto, "trava" o player (efeito visual e redução de velocidade)
                self.properties["state"] = "LOCKING"
                self.properties["color"] = (255, 255, 0)
                # Drena um pouco de velocidade do player se não estiver corrigido
                if self.target.properties["speed"] > 1:
                    self.target.properties["speed"] -= 0.05 * dt

        self._angle += 0.1 * dt

    def render(self, screen):
        x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        
        # Desenha duas engrenagens intertravadas
        pygame.draw.rect(screen, color, (x, y, w, h), 2)
        pygame.draw.line(screen, color, (x, y), (x + w, y + h), 2)
        pygame.draw.line(screen, color, (x + w, y), (x, y + h), 2)
        
        if self.properties["state"] == "LOCKING":
            # Círculos de "trava"
            pygame.draw.circle(screen, (255, 255, 0), (int(x + w//2), int(y + h//2)), int(self.properties["lock_range"]), 1)
