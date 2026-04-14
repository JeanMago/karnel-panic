import pygame

class Console:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 16)
        self.logs = []

    def log(self, text):
        self.logs.append(text)
        if len(self.logs) > 10:
            self.logs.pop(0)

    def draw(self, screen):
        y = 400
        for log in self.logs:
            txt = self.font.render(log, True, (0,255,255))
            screen.blit(txt, (20, y))
            y += 20
