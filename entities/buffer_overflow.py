import pygame
import random
import math
from ecs.entity import Entity

class BufferOverflow(Entity):
    """Se load > buffer_size, ele entra em overflow e ataca."""
    def __init__(self, x, y, target=None):
        super().__init__()
        self.target = target
        self.properties = {
            "tipo": "BufferOverflow",
            "state": "stable",
            "x": x,
            "y": y,
            "w": 50,
            "h": 50,
            "buffer_size": 100,
            "load": random.randint(40, 110), # Carga randômica (pode vir em overflow)
            "speed": 3.0, # Aumentado de 2.2
            "color": (255, 100, 0),
            "collision": True,
            "hostile": True
        }
        self._shake = 0

    def update(self, dt):
        raw_load = self.properties.get("load", 0)
        raw_size = self.properties.get("buffer_size", 1)
        raw_speed = self.properties.get("speed", 0)

        load = float(raw_load) if raw_load is not None else 0
        size = float(raw_size) if raw_size is not None else 1
        speed = float(raw_speed) if raw_speed is not None else 0
        
        if load > size:
            self.properties["state"] = "OVERFLOW"
            self.properties["color"] = (255, 0, 0)
            self.properties["hostile"] = True
            self._shake = (load - size) * 0.3
            
            # Persegue jogador quando em OVERFLOW
            if self.target and speed > 0:
                tx, ty = self.target.properties.get("x", 0), self.target.properties.get("y", 0)
                dx, dy = tx - self.properties["x"], ty - self.properties["y"]
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 5:
                    self.properties["x"] += (dx / dist) * speed * dt * 1.5 # Corre mais em overflow
                    self.properties["y"] += (dy / dist) * speed * dt * 1.5
            
            # Tremor visual/físico
            self.properties["x"] += random.uniform(-self._shake, self._shake) * dt
            self.properties["y"] += random.uniform(-self._shake, self._shake) * dt
        else:
            self.properties["state"] = "stable"
            self.properties["color"] = (255, 150, 0)
            self._shake = 0
            # Movimento lento e passivo (balanço suave)
            self.properties["x"] += math.sin(pygame.time.get_ticks() * 0.002) * speed * dt * 0.5

    def render(self, screen):
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        
        raw_load = self.properties.get("load", 0)
        raw_size = self.properties.get("buffer_size", 1)
        load = float(raw_load) if raw_load is not None else 0
        size = float(raw_size) if raw_size is not None else 1
        load_pct = min(1.0, load / max(1, size))

        # Estrutura externa (Recipiente)
        pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
        
        # Conteúdo interno (Líquido/Dados)
        content_h = int(h * load_pct)
        pygame.draw.rect(screen, color, (x, y + h - content_h, w, content_h))
        
        # Efeito de perigo se estiver em overflow
        if self.properties["state"] == "OVERFLOW":
            pygame.draw.rect(screen, (255, 255, 255), (x-2, y-2, w+4, h+4), 1)
            # Faixas de aviso
            for i in range(0, w, 10):
                pygame.draw.line(screen, (255, 255, 255), (x+i, y), (x+i+5, y+h), 1)

        # Barra de carga detalhada
        pygame.draw.rect(screen, (0, 0, 0), (x, y - 12, w, 6))
        pygame.draw.rect(screen, (255, 255, 0), (x, y - 12, int(w * load_pct), 6))
        pygame.draw.rect(screen, (255, 255, 255), (x, y - 12, w, 6), 1)
