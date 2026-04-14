import pygame

class Inspector:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 16)

    def draw(self, screen, entity):
        if not entity:
            return

        x = 750
        y = 20

        for key, value in entity.properties.items():
            text = self.font.render(f"{key}: {value}", True, (255,255,255))
            screen.blit(text, (x, y))
            y += 20
