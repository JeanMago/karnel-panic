import pygame
import math
import random
from ecs.entity import Entity

class Boss(Entity):
    def __init__(self, x, y, name, health, color):
        super().__init__()
        self.properties = {
            "tipo": "BOSS",
            "name": name,
            "x": x,
            "y": y,
            "w": 120,
            "h": 120,
            "health": health,
            "max_health": health,
            "color": color,
            "collision": True,
            "hostile": True,
            "state": "active",
            "speed": 2,
            "stun_timer": 0,
            "last_hit_timer": 0,
            "vulnerability": 1.0 # Multiplicador de dano recebido
        }
        self._phase_timer = 0

    def is_dead(self):
        hp = self.properties.get("health", 0)
        return hp is not None and hp <= 0

    def take_damage(self, amount):
        """Método formal para reduzir vida com feedback visual."""
        if self.is_dead(): return
        vuln = self.properties.get("vulnerability", 1.0)
        damage = amount * vuln
        self.properties["health"] -= damage
        self.properties["last_hit_timer"] = 15 # frames de flash
        
        if self.properties["health"] <= 0:
            self.properties["health"] = 0
            self.properties["collision"] = False
            self.properties["hostile"] = False
            self.properties["state"] = "neutralized"
        return damage

    def draw_boss_bar(self, screen):
        sw = screen.get_width()
        bar_w = 500
        bar_h = 24
        x = sw // 2 - bar_w // 2
        y = 40
        
        hp = max(0, self.properties.get("health", 0))
        max_hp = self.properties.get("max_health", 100)
        pct = hp / max_hp
        
        # Fundo barra
        pygame.draw.rect(screen, (30, 0, 0), (x, y, bar_w, bar_h))
        # Vida barra
        pygame.draw.rect(screen, self.properties["color"], (x, y, int(bar_w * pct), bar_h))
        # Detalhe de brilho na vida
        if pct > 0:
            pygame.draw.rect(screen, (255, 255, 255, 100), (x, y, int(bar_w * pct), bar_h // 3), 0)
        # Borda
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        
        # Nome do Processo Crítico
        font = pygame.font.SysFont("monospace", 22, bold=True)
        txt = font.render(f"SYSTEM_CRITICAL: {self.properties['name']}", True, (255, 255, 255))
        screen.blit(txt, (x, y - 30))

    def _common_render(self, screen, shape_func):
        if self.is_dead(): return
        
        # Efeito de Flash ao tomar dano
        color = self.properties["color"]
        if self.properties["last_hit_timer"] > 0:
            color = (255, 255, 255)
            self.properties["last_hit_timer"] -= 1
            
        shape_func(color)
        self.draw_boss_bar(screen)

class NullMaster(Boss):
    """Boss da Fase 1: Fraco a injeções de memória (pasted values)."""
    def __init__(self, x, y):
        super().__init__(x, y, "NULL_MASTER.EXE", 250, (255, 60, 60))
        self.properties["speed"] = 4.0
        self._inverted = False

    def update(self, dt):
        if self.is_dead(): return
        
        # Nova Vulnerabilidade: Inversão de Cores
        c = self.properties.get("color", (255, 60, 60))
        if c[0] < 100 and not self._inverted:
            self._inverted = True
            self.take_damage(60)
            self.properties["stun_timer"] = 60
        elif c[0] > 100:
            self._inverted = False

        # Reação a atordoamento (speed=0)
        if self.properties.get("stun_timer", 0) > 0:
            self.properties["stun_timer"] -= 1 * dt
            self.properties["speed"] = 0.0
            if self.properties["stun_timer"] <= 0:
                self.properties["speed"] = 2.5
            return

        try:
            sp = float(self.properties.get("speed", 0.0))
        except: sp = 0.0

        if sp <= 0.1:
            self.properties["stun_timer"] = 120
            self.take_damage(40)
            return

        self._phase_timer += 0.02 * sp * dt
        self.properties["x"] += math.sin(self._phase_timer * 1.2) * (sp * 2) * dt
        self.properties["y"] += math.cos(self._phase_timer * 0.8) * (sp * 1) * dt

        if self.properties["health"] < 125 and random.random() < 0.01:
            self.properties["x"] += random.randint(-100, 100)
            self.properties["y"] += random.randint(-100, 100)

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            if self.properties.get("stun_timer", 0) > 0:
                color = (100, 100, 255) if (pygame.time.get_ticks() // 100) % 2 == 0 else color
            for i in range(3):
                off = i * 8
                pygame.draw.rect(screen, color, (x+off, y+off, w-off*2, h-off*2), 2)
            for _ in range(5):
                rx = x + random.randint(0, w)
                ry = y + random.randint(0, h)
                pygame.draw.rect(screen, (255, 255, 255), (rx, ry, 4, 4))
        self._common_render(screen, draw_shape)

class RecursiveOverlord(Boss):
    """Boss da Fase 2: Fraco a reduções de carga (load)."""
    def __init__(self, x, y):
        super().__init__(x, y, "OVERLORD_RECURSION", 400, (255, 140, 0))
        self.properties["load"] = 100.0
        self.properties["speed"] = 3.0
        self._anchor_x = x
        self._anchor_y = y
        self._reaction_cooldown = 0

    def update(self, dt):
        if self.is_dead(): return
        
        if self._reaction_cooldown > 0:
            self._reaction_cooldown -= 1 * dt

        try:
            current_load = float(self.properties.get("load", 100.0))
            sp = float(self.properties.get("speed", 0.0))
        except:
            current_load = 100.0
            sp = 0.0

        if sp > 15:
            self.take_damage(0.6 * dt)
            self.properties["color"] = (255, 255, 255) if (pygame.time.get_ticks() // 50) % 2 == 0 else (255, 50, 0)
        else:
            if self._reaction_cooldown > 0:
                self.properties["color"] = (255, 0, 0)
            else:
                self.properties["color"] = (255, 140, 0)

        self._phase_timer += 0.005 * sp * dt
        radius = 200 + math.sin(self._phase_timer * 0.5) * 100
        self.properties["x"] = self._anchor_x + math.cos(self._phase_timer) * radius
        self.properties["y"] = self._anchor_y + math.sin(self._phase_timer) * radius
        
        if current_load < 50.0 and self._reaction_cooldown <= 0:
            self.take_damage(80)
            self.properties["load"] = 150.0
            self.properties["speed"] = 8.0
            self._reaction_cooldown = 150
            return

        if self._reaction_cooldown <= 0:
            if current_load > 100.0:
                self.properties["load"] = current_load - 0.1 * dt
            elif current_load < 100.0:
                self.properties["load"] = current_load + 0.05 * dt
            
            if sp > 3.0 and sp < 15:
                self.properties["speed"] = max(3.0, sp - 0.02 * dt)

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            cx, cy = x + w//2, y + h//2
            try: load_factor = float(self.properties.get("load", 100.0)) / 100.0
            except: load_factor = 1.0
            current_w = w * max(0.5, min(2.0, load_factor))
            angle = pygame.time.get_ticks() * 0.01
            pts = []
            for i in range(16):
                a = angle + (i * math.pi / 8)
                r = (current_w // 2) if i % 2 == 0 else (current_w // 3)
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            pygame.draw.polygon(screen, color, pts)
            pygame.draw.polygon(screen, (255, 255, 255), pts, 2)
            for i in range(3):
                r = (w // 8) - i*4
                if r > 0:
                    pygame.draw.circle(screen, (0, 0, 0), (int(cx), int(cy)), r)
                    pygame.draw.circle(screen, color, (int(cx), int(cy)), r, 1)
        self._common_render(screen, draw_shape)

class PanicCore(Boss):
    """Boss da Fase 3: Vulnerável a Smart Patches e Identidade."""
    def __init__(self, x, y):
        super().__init__(x, y, "CORE_KERNEL_PANIC", 600, (200, 0, 255))
        self.properties["integrity_vulnerability"] = True
        self.properties["speed"] = 1.0
        self.properties["reference"] = "@kernel::core_root"

    def update(self, dt):
        if self.is_dead(): return
        
        ref = self.properties.get("reference")
        if ref and "@PID:0xCAFE" in str(ref):
            self.take_damage(200)
            self.properties["reference"] = "@kernel::core_root"
            self.properties["speed"] = 0.1
            return

        try: sp = float(self.properties.get("speed", 1.0))
        except: sp = 1.0
        self._phase_timer += 0.1 * sp * dt
        s = 130 + math.sin(self._phase_timer) * 40
        self.properties["w"] = s
        self.properties["h"] = s

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            for i in range(4):
                sw, sh = w - i*20, h - i*20
                if sw > 0 and sh > 0:
                    pygame.draw.ellipse(screen, color, (x + i*10, y + i*10, sw, sh), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(x+w//2), int(y+h//2)), int(w//8))
        self._common_render(screen, draw_shape)
