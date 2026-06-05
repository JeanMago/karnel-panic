import pygame
import math
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
            "speed": 3.5,
            "reference": None,
            "visible": False,
            "color": (255, 80, 80),
            "collision": False, # Começa sem colisão física
            "hostile": False,   # Começa inofensivo
        }

    def _is_resolved(self) -> bool:
        return self.properties.get("reference") is not None

    def update(self, dt):
        if not self._is_resolved():
            self.properties["visible"] = False
            self.properties["state"] = "dangling"
            self.properties["collision"] = False
            self.properties["hostile"] = False
            return

        self.properties["visible"] = True
        self.properties["state"] = "chasing"
        self.properties["collision"] = True
        self.properties["hostile"] = True

        speed = self.properties.get("speed")
        if speed is None: speed = 0
        try:
            speed = float(speed) * dt
        except (TypeError, ValueError):
            speed = 0

        if self.target and speed > 0:
            tx = self.target.properties.get("x", self.properties["x"])
            ty = self.target.properties.get("y", self.properties["y"])
            
            dx = tx - self.properties["x"]
            dy = ty - self.properties["y"]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 2: # Evita jitter ao chegar muito perto
                # Normaliza o movimento para evitar velocidade diagonal extra
                self.properties["x"] += (dx / dist) * speed
                self.properties["y"] += (dy / dist) * speed

    def render(self, screen):
        import random
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        color = self.properties["color"]

        if not self._is_resolved():
            # Fragmento instável (Dangling)
            for _ in range(12):
                rx = x + random.randint(-5, w)
                ry = y + random.randint(-5, h)
                rw = random.randint(2, 8)
                rh = random.randint(2, 8)
                # Cores de "erro"
                c = random.choice([(40, 0, 0), (80, 20, 20), (20, 20, 20)])
                pygame.draw.rect(screen, c, (rx, ry, rw, rh))
            return

        # Fragmento Perseguidor (Resolved)
        # Corpo central fragmentado
        for i in range(5):
            off_x = math.sin(pygame.time.get_ticks() * 0.02 + i) * 3
            off_y = math.cos(pygame.time.get_ticks() * 0.02 + i) * 3
            pygame.draw.rect(screen, color, (x + off_x, y + off_y, w, h), 1)
        
        # Partículas de rastro
        for _ in range(4):
            px = x + random.randint(0, w)
            py = y + random.randint(0, h)
            pygame.draw.rect(screen, (255, 0, 0), (px, py, 4, 4))
