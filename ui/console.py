import pygame

from config import CONSOLE_ZONE_HEIGHT


class Console:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 13)
        self.title_font = pygame.font.SysFont("consolas", 12, bold=True)
        self.logs = []
        self.max_lines = 7

    def log(self, text):
        self.logs.append(text)
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)

    def draw(self, screen):
        sh = screen.get_height()
        sw = screen.get_width()
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        top = sh - zh

        # Fundo só na faixa inferior (não cobre o painel de ajuda)
        bg = pygame.Surface((sw - 16, zh - 4))
        bg.set_alpha(200)
        bg.fill((8, 12, 18))
        screen.blit(bg, (8, top + 2))

        border_col = (0, 140, 160)
        pygame.draw.rect(screen, border_col, (8, top + 2, sw - 16, zh - 4), 1)

        title = self.title_font.render("CONSOLE (ações / dump)", True, (0, 200, 220))
        screen.blit(title, (16, top + 8))

        y = top + 28
        for log in self.logs:
            txt = self.font.render(log[:100], True, (160, 255, 255))
            screen.blit(txt, (16, y))
            y += 17
            if y > sh - 8:
                break
