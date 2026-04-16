import pygame

from config import CONSOLE_ZONE_HEIGHT, DEBUGGER_GAP_ABOVE_CONSOLE


class HUD:
    """Barra de corrupção, fase, Debugger Gun (painel) e destaque da seleção."""

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font_title = pygame.font.SysFont("consolas", 13, bold=True)

    def draw(self, screen, corruption, level_name: str, path_hint: str):
        sw = screen.get_width()
        bar_w = min(360, sw // 2)
        x, y = 12, 10

        title = self.font.render(level_name, True, (0, 255, 255))
        screen.blit(title, (x, y))
        hint = self.font_small.render(path_hint, True, (100, 180, 180))
        screen.blit(hint, (x, y + 22))

        pct = max(0.0, min(1.0, corruption.level))
        pygame.draw.rect(screen, (40, 40, 40), (x, y + 44, bar_w, 14))
        pygame.draw.rect(
            screen,
            (200, 60, 80),
            (x, y + 44, int(bar_w * pct), 14),
        )
        label = self.font_small.render(f"corrupção: {pct*100:.1f}%", True, (255, 200, 200))
        screen.blit(label, (x + bar_w + 8, y + 42))

    def draw_debugger_gun_panel(
        self, screen, player, selected, debugger, peek_cut, peek_paste
    ):
        """
        Explica a 'arma': não há sprite — o feixe parte do processo (você) para o alvo.
        Mostra buffer e qual propriedade CUT/PASTE afetam neste alvo.
        """
        sw = screen.get_width()
        sh = screen.get_height()
        panel_w = min(440, sw - 24)
        x0 = 12
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        panel_h = 168
        # Painel termina acima da faixa reservada ao console
        y0 = sh - zh - DEBUGGER_GAP_ABOVE_CONSOLE - panel_h
        y0 = max(72, y0)

        bg = pygame.Surface((panel_w, panel_h))
        bg.set_alpha(210)
        bg.fill((12, 18, 22))
        screen.blit(bg, (x0, y0))

        title = self.font_title.render("DEBUGGER GUN (feixe de depuração)", True, (0, 255, 160))
        screen.blit(title, (x0 + 8, y0 + 6))

        lines = [
            "1) Clique = mirar  |  painel direito = propriedades",
            "2) Dois clipboards A/B: [TAB] escolhe qual recebe CUT e manda PASTE",
            "[ I ] dump  [ X ] CUT speed  [ T ] CUT token (só você)  [ V ] PASTE  [ P ] PATCH",
            "Troca de velocidade: guarde cada speed num slot e cole nos alvos.",
        ]
        y = y0 + 26
        for line in lines:
            t = self.font_small.render(line, True, (190, 200, 210))
            screen.blit(t, (x0 + 8, y))
            y += 14

        buf_y = y0 + 84
        for bline in debugger.buffer_status_lines():
            col = (120, 220, 255) if bline.startswith("►") else (160, 200, 230)
            screen.blit(self.font_small.render(bline, True, col), (x0 + 8, buf_y))
            buf_y += 14

        if not selected:
            warn = self.font_small.render(
                "→ Sem alvo: clique num retângulo (você = verde)",
                True,
                (255, 200, 100),
            )
            screen.blit(warn, (x0 + 8, buf_y + 4))
            return

        tgt = f"alvo: {selected.debug_label()}"
        screen.blit(self.font_small.render(tgt, True, (180, 255, 200)), (x0 + 8, buf_y + 2))

        cut_k = peek_cut or "—"
        pst = peek_paste or "—"
        hint = f"[X] recorta: {cut_k}   |   [V] cola em: {pst}"
        screen.blit(self.font_small.render(hint, True, (220, 220, 160)), (x0 + 8, buf_y + 18))

    def draw_aim_link(self, screen, player, selected):
        """Feixe fraco contínuo: indica que a 'arma' está apontando para o alvo."""
        if not selected:
            return
        try:
            px = int(player.properties["x"] + player.properties.get("w", 40) // 2)
            py = int(player.properties["y"] + player.properties.get("h", 40) // 2)
            sx = int(selected.properties["x"] + selected.properties.get("w", 40) // 2)
            sy = int(selected.properties["y"] + selected.properties.get("h", 40) // 2)
        except (TypeError, ValueError):
            return
        w, h = screen.get_width(), screen.get_height()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(surf, (0, 220, 180, 55), (px, py), (sx, sy), 2)
        screen.blit(surf, (0, 0))

    def draw_selection_ring(self, screen, entity):
        if not entity:
            return
        try:
            ex = int(entity.properties.get("x", 0))
            ey = int(entity.properties.get("y", 0))
            ew = int(entity.properties.get("w", 40))
            eh = int(entity.properties.get("h", 40))
        except (TypeError, ValueError):
            return
        pad = 4
        rect = (ex - pad, ey - pad, ew + pad * 2, eh + pad * 2)
        pygame.draw.rect(screen, (0, 255, 120), rect, 2)
