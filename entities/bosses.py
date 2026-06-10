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
        self._dash_cooldown = 0

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
            return
        
        self.properties["speed"] = 4.0 if self.properties["health"] > 125 else 6.0

        # Movimento Senoidal + Dash Aleatório
        self._phase_timer += 0.02 * self.properties["speed"] * dt
        self.properties["x"] += math.sin(self._phase_timer * 1.2) * self.properties["speed"] * dt
        self.properties["y"] += math.cos(self._phase_timer * 0.8) * self.properties["speed"] * dt

        if self._dash_cooldown > 0:
            self._dash_cooldown -= 1 * dt
        elif random.random() < 0.02:
            # "Glitch Dash"
            self.properties["x"] += random.randint(-150, 150)
            self.properties["y"] += random.randint(-150, 150)
            self._dash_cooldown = 60

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            if self.properties.get("stun_timer", 0) > 0:
                color = (100, 100, 255) if (pygame.time.get_ticks() // 100) % 2 == 0 else color
            
            # Efeito de rastro/ghosting se estiver rápido
            if self.properties["health"] < 125:
                for i in range(1, 4):
                    pygame.draw.rect(screen, (*color, 50), (x - i*10, y - i*10, w, h), 1)

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
        self._angle = 0

    def update(self, dt):
        if self.is_dead(): return
        
        if self._reaction_cooldown > 0:
            self._reaction_cooldown -= 1 * dt

        try:
            current_load = float(self.properties.get("load", 100.0))
            sp = float(self.properties.get("speed", 3.0))
        except:
            current_load = 100.0
            sp = 3.0

        # Movimento em espiral agressiva
        self._angle += 0.02 * sp * dt
        radius = 200 + math.sin(self._angle * 0.5) * 150
        target_x = self._anchor_x + math.cos(self._angle) * radius
        target_y = self._anchor_y + math.sin(self._angle) * radius
        
        # Suaviza movimento para a posição alvo
        self.properties["x"] += (target_x - self.properties["x"]) * 0.1 * dt
        self.properties["y"] += (target_y - self.properties["y"]) * 0.1 * dt
        
        if sp > 15:
            self.take_damage(0.6 * dt)
            self.properties["color"] = (255, 255, 255) if (pygame.time.get_ticks() // 50) % 2 == 0 else (255, 50, 0)
        
        if current_load < 50.0 and self._reaction_cooldown <= 0:
            self.take_damage(80)
            self.properties["load"] = 180.0
            self.properties["speed"] = 10.0
            self._reaction_cooldown = 180
            return

        if self._reaction_cooldown <= 0:
            # Recuperação natural de carga
            if current_load > 100.0: self.properties["load"] -= 0.1 * dt
            elif current_load < 100.0: self.properties["load"] += 0.05 * dt
            
            # Frenesi se estiver com pouca vida
            if self.properties["health"] < 150:
                self.properties["speed"] = max(sp, 6.0)

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
        self.properties["speed"] = 1.5
        self.properties["reference"] = "@kernel::core_root"
        self._fragments = [] # Partículas decorativas/ataque

    def update(self, dt):
        if self.is_dead(): return
        
        ref = self.properties.get("reference")
        if ref and "@PID:0xCAFE" in str(ref):
            self.take_damage(200)
            self.properties["reference"] = "@kernel::core_root"
            self.properties["speed"] = 0.2
            return

        try: sp = float(self.properties.get("speed", 1.5))
        except: sp = 1.5
        
        # Pulsação e movimento errático
        self._phase_timer += 0.1 * sp * dt
        s = 130 + math.sin(self._phase_timer) * 40
        self.properties["w"] = s
        self.properties["h"] = s
        
        self.properties["x"] += math.sin(self._phase_timer * 0.5) * 4 * dt
        self.properties["y"] += math.cos(self._phase_timer * 0.3) * 4 * dt

        # Gera fragmentos
        if random.random() < 0.1:
            self._fragments.append({
                "x": self.properties["x"] + self.properties["w"] // 2,
                "y": self.properties["y"] + self.properties["h"] // 2,
                "vx": random.uniform(-5, 5),
                "vy": random.uniform(-5, 5),
                "life": 40
            })
        
        for f in self._fragments[:]:
            f["x"] += f["vx"] * dt
            f["y"] += f["vy"] * dt
            f["life"] -= 1 * dt
            if f["life"] <= 0: self._fragments.remove(f)

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            # Desenha fragmentos
            for f in self._fragments:
                pygame.draw.circle(screen, color, (int(f["x"]), int(f["y"])), 3)
            
            for i in range(4):
                sw, sh = w - i*20, h - i*20
                if sw > 0 and sh > 0:
                    alpha = 255 - i*50
                    s = pygame.Surface((sw, sh), pygame.SRCALPHA)
                    pygame.draw.ellipse(s, (*color, alpha), (0, 0, sw, sh), 2)
                    screen.blit(s, (x + i*10, y + i*10))
            pygame.draw.circle(screen, (255, 255, 255), (int(x+w//2), int(y+h//2)), int(w//8))
        self._common_render(screen, draw_shape)

class MutexMaster(Boss):
    """Boss da Fase 4: Sincronização e Travas. Vulnerável a scan e liberação de lock."""
    def __init__(self, x, y):
        super().__init__(x, y, "MUTEX_MASTER_SYNC", 450, (0, 150, 255))
        self.properties["lock_state"] = "LOCKED"
        self.properties["resource"] = "CPU_CYCLES"
        self.properties["speed"] = 1.5
        self._reaction_cooldown = 0
        self._shield_angle = 0

    def update(self, dt):
        if self.is_dead(): return
        
        if self._reaction_cooldown > 0:
            self._reaction_cooldown -= 1 * dt

        state = self.properties.get("lock_state", "LOCKED")
        if state == "UNLOCKED" and self._reaction_cooldown <= 0:
            self.take_damage(120)
            self.properties["lock_state"] = "LOCKED"
            self.properties["speed"] = 5.0 # Fica agressivo após ser destravado
            self._reaction_cooldown = 150
            return

        if self._reaction_cooldown <= 0:
            self.properties["speed"] = 2.0 + (1.0 - (self.properties["health"] / self.properties["max_health"]))
            
        sp = float(self.properties.get("speed", 1.5))
        self._phase_timer += 0.01 * sp * dt
        self._shield_angle += 0.05 * dt
        
        # Movimento em '8' mais amplo
        self.properties["x"] += math.cos(self._phase_timer) * 6 * dt
        self.properties["y"] += math.sin(self._phase_timer * 2) * 4 * dt

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            cx, cy = x + w//2, y + h//2
            
            # Escudo de travamento rotativo
            if self.properties.get("lock_state") == "LOCKED":
                for i in range(4):
                    a = self._shield_angle + i * (math.pi / 2)
                    sx = cx + math.cos(a) * 80
                    sy = cy + math.sin(a) * 80
                    pygame.draw.rect(screen, (0, 255, 255), (sx-10, sy-10, 20, 20), 2)
            
            # Desenha um cadeado estilizado
            pygame.draw.rect(screen, color, (x + 20, y + 40, w - 40, h - 40))
            pygame.draw.rect(screen, (255, 255, 255), (x + 20, y + 40, w - 40, h - 40), 2)
            # Arco do cadeado
            arc_rect = pygame.Rect(x + 30, y + 10, w - 60, 60)
            pygame.draw.arc(screen, color, arc_rect, 0, math.pi, 5)
            # Olho/Buraco da chave
            pygame.draw.circle(screen, (0, 0, 0), (int(cx), int(cy + 10)), 8)
        self._common_render(screen, draw_shape)

class RegistryTyrant(Boss):
    """Boss da Fase 5: Manipulação de dados e chaves de registro. Vulnerável a 'purge' e scan."""
    def __init__(self, x, y):
        super().__init__(x, y, "REGISTRY_TYRANT_DB", 500, (200, 200, 50))
        self.properties["registry_key"] = "HKEY_LOCAL_MACHINE\\SYSTEM"
        self.properties["access_level"] = "ADMIN"
        self._anchor_x = x
        self._anchor_y = y
        self._target_pos = (x, y)
        self._move_timer = 0

    def update(self, dt):
        if self.is_dead(): return
        
        # Se o nível de acesso for rebaixado, toma dano massivo
        access = self.properties.get("access_level", "ADMIN")
        if access != "ADMIN":
            self.take_damage(120)
            self.properties["access_level"] = "ADMIN"
            self._move_timer = 0 # Força novo movimento
            return

        # Se a chave for alterada para algo inválido
        key = self.properties.get("registry_key", "")
        if "HKEY" not in str(key):
            self.take_damage(60)
            self.properties["registry_key"] = "HKEY_LOCAL_MACHINE\\SYSTEM"
            return

        # Movimento tipo "Query" (Grid-aligned e rápido)
        self._move_timer -= 1 * dt
        if self._move_timer <= 0:
            grid_x = random.randint(-2, 2) * 200
            grid_y = random.randint(-2, 2) * 200
            self._target_pos = (self._anchor_x + grid_x, self._anchor_y + grid_y)
            self._move_timer = random.randint(30, 90)

        # Interpolação para a posição alvo
        self.properties["x"] += (self._target_pos[0] - self.properties["x"]) * 0.15 * dt
        self.properties["y"] += (self._target_pos[1] - self.properties["y"]) * 0.15 * dt

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            # Desenha uma colmeia/grade de dados
            for i in range(3):
                for j in range(3):
                    bx, by = x + i * (w // 3), y + j * (h // 3)
                    # Efeito de scan na grade
                    alpha = 100 + math.sin(pygame.time.get_ticks() * 0.01 + i + j) * 100
                    pygame.draw.rect(screen, (*color, int(alpha)), (bx + 5, by + 5, w // 3 - 10, h // 3 - 10), 2)
                    if random.random() < 0.1:
                        pygame.draw.rect(screen, (255, 255, 255, 50), (bx + 8, by + 8, w // 3 - 16, h // 3 - 16))
        self._common_render(screen, draw_shape)

class FirewallDragon(Boss):
    """Boss da Fase 6: Defesa de rede e pacotes. Vulnerável a injeção de pacotes (PASTE) e Scan."""
    def __init__(self, x, y):
        super().__init__(x, y, "FIREWALL_DRAGON_NET", 550, (50, 200, 50))
        self.properties["port_status"] = "FILTERED"
        self.properties["ip_source"] = "127.0.0.1"
        self._trail = [] # Para efeito de "corpo" de dragão/serpente
        self._angle = 0

    def update(self, dt):
        if self.is_dead(): return
        
        # Se a porta for aberta
        status = self.properties.get("port_status", "FILTERED")
        if status == "OPEN":
            self.take_damage(150)
            self.properties["port_status"] = "FILTERED"
            return

        # Se o IP for alterado
        ip = self.properties.get("ip_source", "127.0.0.1")
        if ip != "127.0.0.1":
            self.take_damage(40)
            self.properties["ip_source"] = "127.0.0.1"

        # Movimento "Data Flow" (serpente fluida)
        sp = 5.0 + (1.0 - self.properties["health"] / self.properties["max_health"]) * 5.0
        self._angle += 0.05 * dt
        self.properties["x"] += math.cos(self._angle) * sp * dt
        self.properties["y"] += math.sin(self._angle * 0.4) * (sp * 1.5) * dt
        
        # Atualiza rastro com interpolação
        self._trail.insert(0, (self.properties["x"], self.properties["y"]))
        if len(self._trail) > 20:
            self._trail.pop()

    def render(self, screen):
        def draw_shape(color):
            x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
            # Desenha o corpo do rastro
            for i, (tx, ty) in enumerate(self._trail):
                if i == 0: continue
                alpha = max(0, 255 - (i * 12))
                scale = 1.0 - (i / len(self._trail)) * 0.5
                s_w, s_h = w * scale, h * scale
                
                # Efeito de pulso nos segmentos
                seg_color = color if (pygame.time.get_ticks() // 100 + i) % 5 != 0 else (200, 255, 200)
                
                s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
                pygame.draw.rect(s, (*seg_color, alpha), (0, 0, s_w, s_h), 2)
                screen.blit(s, (tx + (w - s_w)//2, ty + (h - s_h)//2))
            
            # Cabeça mais robusta
            pygame.draw.rect(screen, color, (x, y, w, h), 3)
            # Olhos de pacotes binários
            eye_color = (255, 255, 255) if (pygame.time.get_ticks() // 200) % 2 == 0 else (0, 255, 0)
            pygame.draw.rect(screen, eye_color, (x + 20, y + 30, 20, 20))
            pygame.draw.rect(screen, eye_color, (x + w - 40, y + 30, 20, 20))
        self._common_render(screen, draw_shape)
