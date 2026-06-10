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
            "speed": 3.0,
            "leak_rate": 0.15, # chance por frame
            "color": (0, 255, 100),
            "collision": True,
            "hostile": True
        }
        self.spawned_blocks = [] # Lista de dicts: {x, y, life}
        self._dir = [random.choice([-1, 1]), random.choice([-1, 1])]
        self._change_dir_timer = 0

    def update(self, dt):
        raw_sp = self.properties.get("speed", 0)
        sp = float(raw_sp) * dt if raw_sp is not None else 0
        
        # Mudar direção aleatoriamente de vez em quando
        self._change_dir_timer -= 1 * dt
        if self._change_dir_timer <= 0:
            angle = random.uniform(0, math.pi * 2)
            self._dir = [math.cos(angle), math.sin(angle)]
            self._change_dir_timer = random.randint(60, 180)

        # Normaliza direção para evitar velocidade diagonal extra
        dir_x, dir_y = self._dir
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist > 0:
            nx, ny = dir_x / dist, dir_y / dist
        else:
            nx, ny = 0, 0

        self.properties["x"] += nx * sp
        self.properties["y"] += ny * sp

        # Bouncing (Mundo 4000x3000) - Agora com margem maior e mudando _dir
        margin = 100
        hit_wall = False
        if self.properties["x"] < margin:
            self.properties["x"] = margin
            self._dir[0] = abs(self._dir[0])
            hit_wall = True
        elif self.properties["x"] > 4000 - margin - self.properties["w"]:
            self.properties["x"] = 4000 - margin - self.properties["w"]
            self._dir[0] = -abs(self._dir[0])
            hit_wall = True

        if self.properties["y"] < margin:
            self.properties["y"] = margin
            self._dir[1] = abs(self._dir[1])
            hit_wall = True
        elif self.properties["y"] > 3000 - margin - self.properties["h"]:
            self.properties["y"] = 3000 - margin - self.properties["h"]
            self._dir[1] = -abs(self._dir[1])
            hit_wall = True
        
        if hit_wall:
            self._change_dir_timer = random.randint(30, 90)

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

    def on_collision(self):
        """Inverte a direção ao bater em um obstáculo."""
        self._dir[0] *= -1
        self._dir[1] *= -1
        # Adiciona um pequeno desvio aleatório para não ficar preso
        self._dir[0] += random.uniform(-0.2, 0.2)
        self._dir[1] += random.uniform(-0.2, 0.2)
        self._change_dir_timer = random.randint(30, 60)

    def get_damage_rects(self):
        rects = super().get_damage_rects()
        for b in self.spawned_blocks:
            rects.append(pygame.Rect(b["x"], b["y"], 12, 12))
        return rects

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
