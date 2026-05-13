import random
import pygame

class CorruptionSystem:
    def __init__(self):
        self.level = 0.0
        self.glitch_active = False
        self.glitch_offset = (0, 0)
        self.integrity_failure = False

    def increase(self, amount):
        self.level = min(1.0, self.level + amount)
        if self.level >= 1.0:
            self.integrity_failure = True

    def update_frame_glitch(self):
        """Chamado uma vez por frame no início do game loop."""
        self.glitch_active = False
        if self.level >= 0.15:
            # Chance de glitch aumenta com o nível
            chance = (self.level ** 2) * 0.4
            if random.random() < chance:
                self.glitch_active = True
                intensity = int(self.level * 20)
                self.glitch_offset = (
                    random.randint(-intensity, intensity),
                    random.randint(-intensity, intensity)
                )
            else:
                self.glitch_offset = (0, 0)

    def get_color_shift(self):
        if self.level < 0.1: return (0, 0, 0)
        # Retorna um deslocamento de cor RGB baseado no nível
        r = int(self.level * 150) if random.random() < 0.3 else 0
        g = int(self.level * 50) if random.random() < 0.1 else 0
        b = int(self.level * 200) if random.random() < 0.2 else 0
        return (r, g, b)

    def apply_world_effects(self, entities, player):
        """Aplica efeitos físicos/lógicos às entidades baseados na corrupção."""
        if self.level < 0.3:
            return

        for entity in entities:
            # Distorção de movimento em níveis altos
            if self.level > 0.6 and random.random() < (self.level * 0.05):
                if "x" in entity.properties and "y" in entity.properties:
                    entity.properties["x"] += random.randint(-2, 2)
                    entity.properties["y"] += random.randint(-2, 2)

            # Corrupção passiva: entidades próximas ao player aumentam corrupção
            if entity.debug_label() != "Player":
                ex, ey = entity.properties.get("x", 0), entity.properties.get("y", 0)
                px, py = player.properties.get("x", 0), player.properties.get("y", 0)
                dist_sq = (ex - px)**2 + (ey - py)**2
                if dist_sq < 2500: # 50 pixels
                    self.increase(0.0001)

    def get_glitch_text(self, text):
        """Corrompe strings aleatoriamente."""
        if self.level < 0.4 or random.random() > (self.level * 0.3):
            return text
        
        chars = list(text)
        glitch_chars = ["@", "#", "$", "%", "&", "*", "!", "?", "0", "1"]
        for i in range(len(chars)):
            if random.random() < (self.level * 0.1):
                chars[i] = random.choice(glitch_chars)
        return "".join(chars)
