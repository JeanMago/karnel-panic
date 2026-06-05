import math
import pygame
from ecs.entity import Entity


class StackOverflow(Entity):
    """
    Oscila horizontalmente (pilha “respirando”) e empilha fantasmas visuais.
    `stack_depth` limita quantas cópias podem aparecer.
    """

    def __init__(self, x, y, max_copies=4, spawn_interval_ms=900):
        super().__init__()
        self._anchor_x = x
        self._anchor_y = y
        self._max_copies = max_copies
        self._spawn_interval_ms = spawn_interval_ms
        self._last_spawn = 0
        self._phase = 0.0
        self.ghosts = []

        self.properties = {
            "tipo": "StackOverflow",
            "state": "pushing",
            "health": 50,
            "x": x,
            "y": y,
            "w": 34,
            "h": 34,
            "speed": 1.2,
            "stack_depth": 1,
            "color": (180, 80, 255),
            "collision": True,
            "hostile": True,
        }

    def update(self, dt):
        sp = self.properties.get("speed")
        if sp is None:
            return
        try:
            sp = float(sp)
        except (TypeError, ValueError):
            return
        if sp <= 0:
            return

        now = pygame.time.get_ticks()
        raw_d = self.properties.get("stack_depth", 1)
        if raw_d is None:
            depth = 1
            self.properties["stack_depth"] = 1
        else:
            try:
                depth = int(raw_d)
            except (TypeError, ValueError):
                depth = 1
        depth = max(1, min(self._max_copies + 1, depth))

        if (
            now - self._last_spawn >= self._spawn_interval_ms
            and len(self.ghosts) < depth - 1
        ):
            self._last_spawn = now
            off = 8 + len(self.ghosts) * 6
            self.ghosts.append({"ox": off, "oy": -off // 2, "a": 110})

        self._phase += 0.03 * sp * dt
        amp = 140
        self.properties["x"] = self._anchor_x + math.sin(self._phase) * amp
        self.properties["y"] = self._anchor_y

        for g in self.ghosts:
            g["ox"] = g.get("ox", 0) + math.sin(self._phase + 0.4) * 0.8 * dt

    def render(self, screen):
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        
        # Desenha a "Pilha" (base)
        for i in range(3):
            pygame.draw.rect(screen, color, (x, y + i * (h // 3), w, h // 3 - 1))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 1)

        # Renderizar fantasmas (camadas que transbordam)
        for g in self.ghosts:
            gx, gy = x + int(g["ox"]), y + int(g["oy"])
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((*color, g.get("a", 100)))
            screen.blit(s, (gx, gy))
            pygame.draw.rect(screen, (255, 255, 255, 50), (gx, gy, w, h), 1)
