import pygame
import math
import random
from ecs.entity import Entity

class RivalSentinel(Entity):
    """
    O 'Anti-Sentinela'. Mimica as habilidades do player e tenta sabotá-lo.
    Possui uma Debugger Gun própria e IA de perseguição/sabotagem.
    """
    def __init__(self, x, y, target=None):
        super().__init__()
        self.target = target
        self.properties = {
            "tipo": "Rival",
            "name": "Sentinela_Alpha.err",
            "x": x,
            "y": y,
            "w": 40,
            "h": 40,
            "health": 150,
            "max_health": 150,
            "speed": 4.5,
            "color": (255, 0, 100),
            "collision": True,
            "hostile": True,
            "state": "ocioso",
            "last_hit_timer": 0
        }
        self._shoot_timer = 0
        self._strategy_timer = 0
        self._path_angle = random.uniform(0, math.pi * 2)

    def take_damage(self, amount):
        self.properties["health"] -= amount
        self.properties["last_hit_timer"] = 15
        if self.properties["health"] <= 0:
            self.properties["visible"] = False
            self.properties["hostile"] = False
            return True
        return False

    def update(self, dt):
        if not self.target or self.properties.get("health", 0) <= 0:
            return

        tx, ty = self.target.properties.get("x", 0), self.target.properties.get("y", 0)
        px, py = self.properties["x"], self.properties["y"]
        dx, dy = tx - px, ty - py
        dist = math.sqrt(dx**2 + dy**2)

        # IA de Movimento Dinâmica
        self._strategy_timer -= 1 * dt
        if self._strategy_timer <= 0:
            # Alterna entre circular o player, se afastar ou avançar agressivo
            self._mode = random.choice(["circle", "chase", "evade"])
            self._strategy_timer = random.randint(60, 180)

        speed = self.properties["speed"] * dt
        if dist > 0:
            if self._mode == "chase":
                # Avança direto
                self.properties["x"] += (dx / dist) * speed
                self.properties["y"] += (dy / dist) * speed
            elif self._mode == "circle":
                # Circunda o alvo
                self._path_angle += 0.05 * dt
                self.properties["x"] += (dx / dist) * speed * 0.5 + math.cos(self._path_angle) * speed
                self.properties["y"] += (dy / dist) * speed * 0.5 + math.sin(self._path_angle) * speed
            elif self._mode == "evade" and dist < 300:
                # Se afasta se estiver perto
                self.properties["x"] -= (dx / dist) * speed * 1.2
                self.properties["y"] -= (dy / dist) * speed * 1.2

        # Sabotagem (Ataque visual e corrupção)
        self._shoot_timer -= 1 * dt
        if self._shoot_timer <= 0 and dist < 500:
            self._shoot_timer = 120 # Ataca a cada 2 segs
            # Ativa um flash de laser falso que aumenta corrupção se acertar
            self.properties["state"] = "firing"
        else:
            self.properties["state"] = "idle"

    def render(self, screen):
        x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
        color = self.properties["color"]
        
        if self.properties["last_hit_timer"] > 0:
            color = (255, 255, 255)
            self.properties["last_hit_timer"] -= 1

        # Forma de diamante invertido
        points = [
            (x + w // 2, y + h),      # Baixo
            (x + w, y + h // 2),      # Direita
            (x + w // 2, y),          # Topo
            (x, y + h // 2)           # Esquerda
        ]
        
        # Aura de erro (Vermelho Escuro)
        pygame.draw.rect(screen, (60, 0, 20), (x-4, y-4, w+8, h+8), 0, 4)
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 1)
        
        # Núcleo "quebrado"
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            pygame.draw.line(screen, (0, 0, 0), (x, y), (x + w, y + h), 2)

        # Laser de Sabotagem
        if self.properties["state"] == "firing" and self.target:
            tx, ty = self.target.properties["x"] + 20, self.target.properties["y"] + 20
            pygame.draw.line(screen, (255, 0, 255), (x + 20, y + 20), (tx, ty), 2)
