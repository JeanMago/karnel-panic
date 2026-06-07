import pygame
import random
import math

from config import CONSOLE_ZONE_HEIGHT, DEBUGGER_GAP_ABOVE_CONSOLE


class HUD:
    """Barra de corrupção, integridade, Debugger Gun (painel) e destaque da seleção."""

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font_title = pygame.font.SysFont("consolas", 13, bold=True)
        self.font_header = pygame.font.SysFont("consolas", 16, bold=True)

    def _draw_cyber_rect(self, screen, rect, color, alpha=180, border_color=(0, 200, 200)):
        """Desenha um painel com estilo futurista."""
        x, y, w, h = rect
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((*color, alpha))
        screen.blit(bg, (x, y))
        
        # Bordas e cantos
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1)
        
        # Cantos acentuados
        cl = 15 # corner length
        # Top Left
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x + cl, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y + cl), 2)
        # Top Right
        pygame.draw.line(screen, (255, 255, 255), (x + w, y), (x + w - cl, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + w, y), (x + w, y + cl), 2)
        # Bottom Left
        pygame.draw.line(screen, (255, 255, 255), (x, y + h), (x + cl, y + h), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y + h), (x, y + h - cl), 2)
        # Bottom Right
        pygame.draw.line(screen, (255, 255, 255), (x + w, y + h), (x + w - cl, y + h), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + w, y + h), (x + w, y + h - cl), 2)

    def draw_aim_link_with_camera(self, screen, player, selected, camera):
        """Feixe fraco contínuo usando coordenadas da câmera."""
        if not selected:
            return
        try:
            p_cam = camera.apply((player.properties["x"] + player.properties.get("w", 40)//2, 
                                 player.properties["y"] + player.properties.get("h", 40)//2))
            s_cam = camera.apply((selected.properties["x"] + selected.properties.get("w", 40)//2, 
                                 selected.properties["y"] + selected.properties.get("h", 40)//2))
        except:
            return
        
        # Linha pulsante
        alpha = 50 + int(math.sin(pygame.time.get_ticks() * 0.01) * 30)
        color = (0, 255, 200, alpha)
        
        w, h = screen.get_width(), screen.get_height()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(surf, color, p_cam, s_cam, 2)
        screen.blit(surf, (0, 0))

    def draw_selection_ring_fixed(self, screen, cam_x, cam_y, w, h):
        """Desenha o anel usando coordenadas já transformadas pela câmera."""
        pad = 6
        rect = (cam_x - pad, cam_y - pad, w + pad * 2, h + pad * 2)
        
        # Anel animado
        anim = (pygame.time.get_ticks() // 200) % 4
        color = (0, 255, 120)
        pygame.draw.rect(screen, color, rect, 2)
        
        # Cantos do anel
        cl = 8
        x, y, rw, rh = rect
        pygame.draw.rect(screen, (255, 255, 255), (x-2, y-2, cl, cl))
        pygame.draw.rect(screen, (255, 255, 255), (x+rw-cl+2, y-2, cl, cl))
        pygame.draw.rect(screen, (255, 255, 255), (x-2, y+rh-cl+2, cl, cl))
        pygame.draw.rect(screen, (255, 255, 255), (x+rw-cl+2, y+rh-cl+2, cl, cl))

    def draw_minimap(self, screen, entities, player):
        """Desenha um mini-mapa tático no canto superior direito."""
        sw, sh = screen.get_width(), screen.get_height()
        map_w, map_h = 200, 150
        padding = 15
        mx0 = sw - map_w - padding
        my0 = padding
        
        # Desenha container do mapa
        self._draw_cyber_rect(screen, (mx0, my0, map_w, map_h), (5, 10, 15), alpha=160, border_color=(0, 150, 255))
        
        # Dimensões do Mundo (baseado em core/levels.py)
        WORLD_W, WORLD_H = 4000, 3000
        
        # Função para converter coord de mundo para coord de minimapa
        def to_map(wx, wy):
            rx = mx0 + (wx / WORLD_W) * map_w
            ry = my0 + (wy / WORLD_H) * map_h
            return int(rx), int(ry)

        # Desenha entidades no mapa
        for e in entities:
            # Pula obstáculos comuns para não poluir
            tipo = e.properties.get("tipo")
            if tipo == "Boundary" or (tipo is None and e.debug_label() == "Obstacle"):
                continue
                
            ex, ey = e.properties.get("x", 0), e.properties.get("y", 0)
            mx, my = to_map(ex, ey)
            
            # Cores por tipo
            dot_color = (100, 100, 100)
            dot_size = 2
            
            if tipo == "TERMINAL_EXIT":
                if e.properties.get("active"):
                    dot_color = (0, 255, 200) # Ciano brilhante para saída ativa
                    dot_size = 5
                    # Efeito de pulso na saída
                    if (pygame.time.get_ticks() // 500) % 2 == 0:
                        pygame.draw.circle(screen, (0, 255, 200), (mx, my), 8, 1)
                else:
                    dot_color = (50, 50, 50) # Cinza se inativo
                    dot_size = 3
            elif tipo == "BOSS":
                if e.properties.get("health", 0) > 0:
                    dot_color = (255, 50, 50) # Vermelho para Boss vivo
                    dot_size = 6
                else:
                    dot_color = (100, 0, 0) # Vermelho escuro para morto
            elif e.is_hostile():
                dot_color = (255, 150, 0) # Laranja para inimigos
                dot_size = 2
            
            pygame.draw.circle(screen, dot_color, (mx, my), dot_size)

        # Desenha o Player (Sempre por cima)
        px, py = player.properties.get("x", 0), player.properties.get("y", 0)
        pmx, pmy = to_map(px, py)
        pygame.draw.circle(screen, (0, 255, 100), (pmx, pmy), 4) # Ponto Verde
        # "Radar sweep" simbólico em volta do player
        pygame.draw.circle(screen, (0, 255, 100), (pmx, pmy), 10, 1)

        # Título do mapa
        label = self.font_small.render("NAV_SYSTEM.MAP", True, (0, 180, 255))
        screen.blit(label, (mx0, my0 + map_h + 5))

    def draw(self, screen, corruption, player, level_name: str, path_hint: str):
        sw = screen.get_width()
        
        # Painel Superior Esquerdo (Status)
        panel_w = 400
        panel_h = 100
        self._draw_cyber_rect(screen, (10, 10, panel_w, panel_h), (10, 20, 30))
        
        x, y = 20, 20
        title = self.font_header.render(level_name.upper(), True, (0, 255, 255))
        screen.blit(title, (x, y))
        
        hint = self.font_small.render(path_hint, True, (0, 150, 150))
        screen.blit(hint, (x, y + 20))

        # Barra de Integridade (Vida)
        hp = player.properties.get("health", 100)
        hp_pct = max(0.0, min(1.0, hp / 100.0))
        hp_bar_w = 150
        
        pygame.draw.rect(screen, (40, 0, 0), (x, y + 45, hp_bar_w, 12))
        pygame.draw.rect(screen, (0, 255, 100), (x, y + 45, int(hp_bar_w * hp_pct), 12))
        hp_label = self.font_small.render(f"INTEGRIDADE: {int(hp)}%", True, (150, 255, 200))
        screen.blit(hp_label, (x + hp_bar_w + 10, y + 43))

        # Barra de Corrupção
        cp_pct = max(0.0, min(1.0, corruption.level))
        pygame.draw.rect(screen, (20, 20, 20), (x, y + 65, hp_bar_w, 12))
        pygame.draw.rect(screen, (255, 50, 80), (x, y + 65, int(hp_bar_w * cp_pct), 12))
        cp_label = self.font_small.render(f"CORRUPÇÃO: {cp_pct*100:.1f}%", True, (255, 150, 150))
        screen.blit(cp_label, (x + hp_bar_w + 10, y + 63))

    def draw_debugger_gun_panel(
        self, screen, player, selected, debugger, peek_cut, peek_paste
    ):
        sw = screen.get_width()
        sh = screen.get_height()
        panel_w = 460
        panel_h = 180
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        x0 = 10
        y0 = sh - zh - DEBUGGER_GAP_ABOVE_CONSOLE - panel_h
        y0 = max(120, y0)

        self._draw_cyber_rect(screen, (x0, y0, panel_w, panel_h), (8, 12, 16), border_color=(0, 180, 140))

        title = self.font_header.render("DEBUGGER_GUN.EXE v2.0", True, (0, 255, 180))
        screen.blit(title, (x0 + 15, y0 + 12))

        lines = [
            " [L-CLICK] Mirar | [R-CLICK] Selecionar",
            " [TAB] Alternar Clipboard (A/B)",
            " [X] CUT | [V] PASTE | [P] SMART_PATCH",
            " [C] TERMINAL_PATCH | [T] CUT_TOKEN",
        ]
        y = y0 + 38
        for line in lines:
            t = self.font_small.render(line, True, (160, 200, 210))
            screen.blit(t, (x0 + 10, y))
            y += 16

        # Clipboard Status
        buf_y = y0 + 105
        for bline in debugger.buffer_status_lines():
            col = (0, 220, 255) if bline.startswith("►") else (100, 150, 180)
            screen.blit(self.font_small.render(bline, True, col), (x0 + 15, buf_y))
            buf_y += 15

        # Alvo Atual
        if selected:
            status_col = (100, 255, 150)
            target_name = selected.debug_label().upper()
            self.font_title.set_bold(True)
            tgt_surf = self.font_title.render(f"ACTIVE_TARGET: {target_name}", True, status_col)
            screen.blit(tgt_surf, (x0 + 15, buf_y + 5))
            
            cut_k = peek_cut or "NONE"
            pst = peek_paste or "NONE"
            hint = f"REQ: {cut_k} | DEST: {pst}"
            screen.blit(self.font_small.render(hint, True, (255, 255, 150)), (x0 + 15, buf_y + 22))
        else:
            warn = self.font_small.render(">> AGUARDANDO SELEÇÃO DE ALVO...", True, (255, 150, 0))
            screen.blit(warn, (x0 + 15, buf_y + 10))

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
        
        alpha = 40 + int(math.sin(pygame.time.get_ticks() * 0.01) * 20)
        w, h = screen.get_width(), screen.get_height()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(surf, (0, 255, 200, alpha), (px, py), (sx, sy), 2)
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
        pad = 6
        rect = (ex - pad, ey - pad, ew + pad * 2, eh + pad * 2)
        pygame.draw.rect(screen, (0, 255, 120), rect, 2)

