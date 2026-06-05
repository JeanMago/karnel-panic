import pygame
import math
from ecs.entity import Entity
from config import PLAYER_SPEED


class Player(Entity):
    def __init__(self, x, y):
        super().__init__()

        self.properties = {
            "tipo": "processo",
            "state": "running",
            "health": 100,
            "x": x,
            "y": y,
            "last_x": x,
            "last_y": y,
            "w": 40,
            "h": 40,
            "speed": PLAYER_SPEED,
            "token": "@PID:0xCAFE",
            "color": (0, 255, 0),
            "collision": True,
            "hostile": False,
            "invuln_timer": 0,
            "last_hit_timer": 0
        }

    def take_damage(self, amount):
        if self.properties["invuln_timer"] <= 0:
            self.properties["health"] -= amount
            self.properties["invuln_timer"] = 60 # ~1 segundo de i-frames
            self.properties["last_hit_timer"] = 15
            return True
        return False

    def update(self, dt):
        if self.properties["invuln_timer"] > 0:
            self.properties["invuln_timer"] -= 1 * dt
        if self.properties["last_hit_timer"] > 0:
            self.properties["last_hit_timer"] -= 1 * dt

        keys = pygame.key.get_pressed()
        spd = self.properties.get("speed")
        if spd is None:
            return
        try:
            spd = float(spd) * dt
        except (TypeError, ValueError):
            return

        self.properties["last_x"] = self.properties["x"]
        self.properties["last_y"] = self.properties["y"]

        if keys[pygame.K_w]:
            self.properties["y"] -= spd
        if keys[pygame.K_s]:
            self.properties["y"] += spd
        if keys[pygame.K_a]:
            self.properties["x"] -= spd
        if keys[pygame.K_d]:
            self.properties["x"] += spd

    def render(self, screen):
        x, y = self.properties["x"], self.properties["y"]
        w, h = self.properties["w"], self.properties["h"]
        
        # Feedback visual de dano / invulnerabilidade
        if self.properties["invuln_timer"] > 0 and (pygame.time.get_ticks() // 100) % 2 == 0:
            return # Efeito de piscar (flicker)

        color = self.properties["color"]
        if self.properties["last_hit_timer"] > 0:
            color = (255, 50, 50) # Flash vermelho ao ser atingido
        
        # Desenha o corpo em forma de diamante (Sentinela)
        points = [
            (x + w // 2, y),          # Topo
            (x + w, y + h // 2),      # Direita
            (x + w // 2, y + h),      # Baixo
            (x, y + h // 2)           # Esquerda
        ]
        
        # Brilho externo (aura)
        glow_rect = pygame.Rect(x-2, y-2, w+4, h+4)
        pygame.draw.rect(screen, (0, 40, 0), glow_rect, 0, 8)
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2) # Borda branca fina
        
        # Núcleo pulsante
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
        core_size = int(8 + pulse * 6)
        core_rect = pygame.Rect(
            x + w // 2 - core_size // 2,
            y + h // 2 - core_size // 2,
            core_size,
            core_size
        )
        pygame.draw.rect(screen, (200, 255, 200), core_rect)
        pygame.draw.rect(screen, (255, 255, 255), core_rect, 1)
