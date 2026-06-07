import pygame
import random
import math
from ecs.entity import Entity

class MemoryBlock(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.properties = {
            "tipo": "AllocatedBlock",
            "x": x,
            "y": y,
            "w": 10,
            "h": 10,
            "visible": True,
            "color": (150, 150, 150),
            "hostile": True,
            "lifetime": 300 # frames
        }

    def update(self, dt):
        self.properties["lifetime"] -= 1 * dt
        if self.properties["lifetime"] <= 0:
            self.properties["visible"] = False

    def render(self, screen):
        if not self.properties["visible"]:
            return
        pygame.draw.rect(screen, self.properties["color"], (self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]))

class MemoryLeak(Entity):
    """Deixa um rastro de blocos que causam corrupção."""
    def __init__(self, x, y):
        super().__init__()
        self.properties = {
            "tipo": "MemoryLeak",
            "state": "leaking",
            "x": x,
            "y": y,
            "w": 45,
            "h": 45,
            "speed": 3,
            "leak_rate": 0.1, # chance por frame
            "color": (0, 255, 100),
            "collision": True,
            "hostile": True
        }
        self.spawned_blocks = [] # Lista de dicts: {x, y, life}
        self._dir = [1, 1]

    def update(self, dt):
        raw_sp = self.properties.get("speed", 0)
        sp = float(raw_sp) * dt if raw_sp is not None else 0
        
        # Normaliza direção para evitar velocidade diagonal extra
        dir_x, dir_y = self._dir
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist > 0:
            nx, ny = dir_x / dist, dir_y / dist
        else:
            nx, ny = 0, 0

        self.properties["x"] += nx * sp
        self.properties["y"] += ny * sp

        # Bouncing (Mundo 4000x3000)
        if self.properties["x"] < 0:
            self.properties["x"] = 0
            self._dir[0] *= -1
        elif self.properties["x"] > 3950:
            self.properties["x"] = 3950
            self._dir[0] *= -1

        if self.properties["y"] < 0:
            self.properties["y"] = 0
            self._dir[1] *= -1
        elif self.properties["y"] > 2950:
            self.properties["y"] = 2950
            self._dir[1] *= -1

        raw_rate = self.properties.get("leak_rate", 0)
        rate = float(raw_rate) if raw_rate is not None else 0
        
        if random.random() < rate * dt:
            self.spawned_blocks.append({
                "x": self.properties["x"] + 15,
                "y": self.properties["y"] + 15,
                "life": 100
            })

        for b in self.spawned_blocks:
            b["life"] -= 1 * dt
        
        self.spawned_blocks = [b for b in self.spawned_blocks if b["life"] > 0]

    def render(self, screen):
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        
        # Renderizar blocos (rastro de memória)
        for b in self.spawned_blocks:
            alpha = int(min(255, b["life"] * 2.5))
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            s.fill((0, 200, 50, alpha))
            screen.blit(s, (b["x"], b["y"]))
            pygame.draw.rect(screen, (255, 255, 255, alpha // 2), (b["x"], b["y"], 12, 12), 1)

        # Desenha a cabeça (Ponteiro)
        # Triângulo apontando na direção do movimento
        pts = [
            (x + w, y + h // 2), # Ponta
            (x, y),              # Topo trás
            (x + w // 4, y + h // 2), # Recuo centro
            (x, y + h),          # Baixo trás
        ]
        # Rotacionar baseado na direção seria ideal, mas fixo por enquanto para simplicidade
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, (255, 255, 255), pts, 2)
        
        # Brilho
        for _ in range(2):
            rx = x + random.randint(0, w)
            ry = y + random.randint(0, h)
            pygame.draw.rect(screen, (150, 255, 150), (rx, ry, 3, 3))
