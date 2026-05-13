import pygame

class CodeEditor:
    def __init__(self):
        self.active = False
        self.text = ""
        self.font = pygame.font.SysFont("consolas", 16)
        self.history = []

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.text = ""

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                cmd = self.text
                self.active = False
                return cmd
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                # Apenas caracteres básicos para simplicidade
                if event.unicode.isprintable():
                    self.text += event.unicode
        return None

    def draw(self, screen):
        if not self.active:
            return

        sw, sh = screen.get_width(), screen.get_height()
        # Painel centralizado
        w, h = 400, 40
        x, y = (sw - w) // 2, (sh - h) // 2
        
        # Fundo do editor
        pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h))
        pygame.draw.rect(screen, (0, 255, 150), (x, y, w, h), 2)
        
        prompt = self.font.render(f"> {self.text}_", True, (0, 255, 100))
        screen.blit(prompt, (x + 10, y + 10))
        
        hint = self.font.render("Ex: speed=10 | speed+=1 | if speed==0: speed=5", True, (100, 150, 100))
        screen.blit(hint, (x, y - 25))
