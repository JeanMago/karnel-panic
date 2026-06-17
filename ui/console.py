import pygame

from config import CONSOLE_ZONE_HEIGHT


class Console:
    """
    Representa o console de logs inferior, onde as ações realizadas 
    (como 'CUT', 'PASTE', 'SMART PATCH') são registradas para o jogador.
    """
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 13)
        self.title_font = pygame.font.SysFont("consolas", 12, bold=True)
        self.logs = [] # Lista de mensagens registradas
        self.max_lines = 7 # Limite de linhas visíveis no console

    def log(self, text):
        """Adiciona uma nova mensagem ao console e remove a mais antiga se exceder o limite."""
        self.logs.append(text)
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)

    def draw(self, screen):
        """Desenha o painel do console na parte inferior da tela."""
        sh = screen.get_height()
        sw = screen.get_width()
        # Calcula a altura da zona do console proporcionalmente à tela
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        top = sh - zh

        # Desenha o fundo semi-transparente do console
        bg = pygame.Surface((sw - 16, zh - 4))
        bg.set_alpha(200)
        bg.fill((8, 12, 18))
        screen.blit(bg, (8, top + 2))

        # Borda azulada
        border_col = (0, 140, 160)
        pygame.draw.rect(screen, border_col, (8, top + 2, sw - 16, zh - 4), 1)

        title = self.title_font.render("CONSOLE (ações / dump)", True, (0, 200, 220))
        screen.blit(title, (16, top + 8))

        # Desenha cada linha de log
        y = top + 28
        for log in self.logs:
            # Limita o texto a 100 caracteres para não vazar do painel
            txt = self.font.render(log[:100], True, (160, 255, 255))
            screen.blit(txt, (16, y))
            y += 17
            if y > sh - 8:
                break
