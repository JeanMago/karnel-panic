import pygame
import math
from ecs.entity import Entity


class InfiniteLoop(Entity):
    """Movimento cíclico em retângulo (perímetro fixo)."""

    def __init__(self, x, y, w_rect=220, h_rect=140, speed=2.5):
        super().__init__()
        self._base_x = x
        self._base_y = y
        self._w_rect = w_rect
        self._h_rect = h_rect
        self._perimeter = 2 * (w_rect + h_rect)
        self._s = 0.0

        self.properties = {
            "tipo": "InfiniteLoop",
            "state": "looping",
            "health": 40,
            "x": x,
            "y": y,
            "w": 36,
            "h": 36,
            "speed": speed,
            "color": (255, 180, 0),
            "collision": True,
            "hostile": True,
        }

    def _pos_from_t(self, t: float):
        t = t % self._perimeter
        w, h = self._w_rect, self._h_rect
        if t <= w:
            return t, 0.0
        t -= w
        if t <= h:
            return float(w), t
        t -= h
        if t <= w:
            return w - t, float(h)
        t -= w
        return 0.0, h - t

    def update(self, dt):
        sp = self.properties.get("speed")
        if sp is None:
            return
        try:
            sp = float(sp) * dt
        except (TypeError, ValueError):
            return
        if sp <= 0:
            return

        self._s += sp
        ox, oy = self._pos_from_t(self._s)
        self.properties["x"] = self._base_x + ox
        self.properties["y"] = self._base_y + oy

    def render(self, screen):
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        cx, cy = x + w // 2, y + h // 2
        
        angle = pygame.time.get_ticks() * 0.005
        points = []
        for i in range(8):
            a = angle + (i * math.pi / 4)
            r = (w // 2) if i % 2 == 0 else (w // 2.5)
            px = cx + math.cos(a) * r
            py = cy + math.sin(a) * r
            points.append((px, py))
            
        # Engrenagem externa
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)
        
        # Buraco central (vazio/preto)
        pygame.draw.circle(screen, (10, 10, 15), (int(cx), int(cy)), int(w // 5))
        pygame.draw.circle(screen, (255, 255, 255), (int(cx), int(cy)), int(w // 5), 1)
