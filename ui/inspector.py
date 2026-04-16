import pygame

from config import CONSOLE_ZONE_HEIGHT


class Inspector:
    """Painel de propriedades ancorado à direita (responsivo)."""

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 15)
        self.title_font = pygame.font.SysFont("consolas", 16, bold=True)

    def draw(self, screen, entity):
        sw = screen.get_width()
        sh = screen.get_height()
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        y_max = sh - zh - 8
        panel_w = min(280, max(220, sw // 4))
        x0 = sw - panel_w - 12

        if not entity:
            label = self.title_font.render("Nenhuma entidade selecionada", True, (120, 120, 120))
            screen.blit(label, (x0, 16))
            return

        y = 12
        title = self.title_font.render(entity.debug_label(), True, (0, 255, 180))
        screen.blit(title, (x0, y))
        y += 26

        order = ("tipo", "state", "health", "speed", "reference", "stack_depth", "token")
        shown = set()
        for key in order:
            if key in entity.properties:
                shown.add(key)
                self._line(screen, x0, y, key, entity.properties[key])
                y += 20
                if y > y_max:
                    break

        for key, value in entity.properties.items():
            if key in shown:
                continue
            if key in ("color", "hostile"):
                continue
            self._line(screen, x0, y, key, value)
            y += 20
            if y > y_max:
                more = self.font.render("…", True, (180, 180, 180))
                screen.blit(more, (x0, y))
                break

    def _line(self, screen, x0, y, key, value):
        text = f"{key}: {value}"
        if len(text) > 42:
            text = text[:39] + "..."
        surf = self.font.render(text, True, (235, 235, 235))
        screen.blit(surf, (x0, y))
