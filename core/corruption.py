import random
import pygame

class CorruptionSystem:
    def __init__(self):
        self.level = 0.0
        self.glitch_active = False
        self.glitch_offset = (0, 0)
        self.integrity_failure = False
        self.scanline_glitch = False
        self.inversion_active = False
        
        # Para suavizar a cintilação de cores
        self.current_color_shift = [0, 0, 0]
        self.target_color_shift = [0, 0, 0]
        self._color_timer = 0

    def increase(self, amount):
        self.level = min(1.0, self.level + amount)
        if self.level >= 1.0:
            self.integrity_failure = True

    def update_frame_glitch(self):
        """Chamado uma vez por frame no início do game loop."""
        self.glitch_active = False
        self.scanline_glitch = False
        self.inversion_active = False
        
        if self.level >= 0.15:
            # Restaurando intensidade do tremor original
            shake_chance = (self.level ** 2) * 0.4
            if random.random() < shake_chance:
                self.glitch_active = True
                intensity = int(self.level * 15)
                self.glitch_offset = (
                    random.randint(-intensity, intensity),
                    random.randint(-intensity, intensity)
                )
            
            # Restaurando intensidade das Scanlines originais
            if self.level > 0.4 and random.random() < (self.level * 0.2):
                self.scanline_glitch = True
                
            # Inversão de cores (Flash de luz agressivo) - Mantido sutil/raro
            if self.level > 0.85 and random.random() < 0.01:
                self.inversion_active = True

        # Suavização do Color Shift (Reduz a cintilação de luz sem tirar o efeito)
        self._color_timer -= 1
        if self._color_timer <= 0:
            # Define um novo alvo de cor a cada ~20-60 frames
            self._color_timer = random.randint(20, 60)
            if self.level > 0.1:
                r = int(self.level * 120) if random.random() < 0.3 else 0
                g = int(self.level * 30) if random.random() < 0.1 else 0
                b = int(self.level * 150) if random.random() < 0.2 else 0
                self.target_color_shift = [r, g, b]
            else:
                self.target_color_shift = [0, 0, 0]

        # Interpolação simples para evitar pulos de cor
        for i in range(3):
            diff = self.target_color_shift[i] - self.current_color_shift[i]
            if abs(diff) > 1:
                self.current_color_shift[i] += diff * 0.1
            else:
                self.current_color_shift[i] = self.target_color_shift[i]

    def get_color_shift(self):
        return tuple(map(int, self.current_color_shift))

    def apply_world_effects(self, entities, player):
        """Aplica efeitos físicos/lógicos às entidades baseados na corrupção."""
        if self.level < 0.3:
            return

        for entity in entities:
            # Distorção de movimento em níveis altos
            if self.level > 0.5 and random.random() < (self.level * 0.03):
                if "x" in entity.properties and "y" in entity.properties:
                    # Drift de dados
                    entity.properties["x"] += random.uniform(-1, 1) * self.level * 5
                    entity.properties["y"] += random.uniform(-1, 1) * self.level * 5

            # Corrupção passiva: entidades próximas ao player aumentam corrupção
            if entity.debug_label() != "Player":
                ex, ey = entity.properties.get("x", 0), entity.properties.get("y", 0)
                px, py = player.properties.get("x", 0), player.properties.get("y", 0)
                dist_sq = (ex - px)**2 + (ey - py)**2
                if dist_sq < 3600: # ~60 pixels
                    # Proximidade drena integridade gradualmente
                    self.increase(0.00015 * self.level)

    def draw_screen_glitches(self, screen):
        """Aplica efeitos de pós-processamento de baixo custo diretamente na screen."""
        if self.scanline_glitch:
            sw, sh = screen.get_width(), screen.get_height()
            for _ in range(int(self.level * 5)):
                y = random.randint(0, sh)
                h = random.randint(2, 10)
                off = random.randint(-20, 20)
                # Pega uma fatia da tela e desenha deslocada
                slice_rect = pygame.Rect(0, y, sw, h)
                try:
                    sub = screen.subsurface(slice_rect).copy()
                    screen.blit(sub, (off, y))
                except:
                    pass

        if self.inversion_active:
            # Efeito de flash negativo
            inv = pygame.Surface(screen.get_size())
            inv.fill((255, 255, 255))
            screen.blit(inv, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

    def get_glitch_text(self, text):
        """Corrompe strings aleatoriamente."""
        if self.level < 0.3 or random.random() > (self.level * 0.4):
            return text
        
        chars = list(text)
        glitch_chars = ["@", "#", "$", "%", "&", "*", "!", "?", "0", "1", "X", "▒", "░"]
        for i in range(len(chars)):
            if random.random() < (self.level * 0.15):
                chars[i] = random.choice(glitch_chars)
        return "".join(chars)
