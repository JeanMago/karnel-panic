import pygame
import random
import math

from config import CONSOLE_ZONE_HEIGHT, DEBUGGER_GAP_ABOVE_CONSOLE


class HUD:
    """
    Classe responsável por desenhar a Interface de Usuário (HUD) durante o jogo.
    
    Elementos incluídos:
    - Barra de integridade (HP) e Corrupção.
    - Painel da Debugger Gun (informações de recorte/cola).
    - Minimapa tático.
    - Anel de seleção e feixe de mira.
    - Prompts de tutorial passo a passo.
    """

    def __init__(self):
        # Inicializa as fontes utilizadas no HUD
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_small = pygame.font.SysFont("consolas", 12)
        self.font_title = pygame.font.SysFont("consolas", 13, bold=True)
        self.font_header = pygame.font.SysFont("consolas", 16, bold=True)

    def _draw_cyber_rect(self, screen, rect, color, alpha=180, border_color=(0, 200, 200)):
        """
        Auxiliar para desenhar painéis com estilo futurista/cyber.
        Desenha um retângulo preenchido com transparência e bordas acentuadas nos cantos.
        """
        x, y, w, h = rect
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((*color, alpha))
        screen.blit(bg, (x, y))
        
        # Desenha a borda principal
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1)
        
        # Desenha detalhes brancos nos cantos para dar um aspecto tecnológico
        cl = 15 # comprimento do canto (corner length)
        # Superior Esquerdo
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x + cl, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y + cl), 2)
        # Superior Direito
        pygame.draw.line(screen, (255, 255, 255), (x + w, y), (x + w - cl, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + w, y), (x + w, y + cl), 2)
        # Inferior Esquerdo
        pygame.draw.line(screen, (255, 255, 255), (x, y + h), (x + cl, y + h), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y + h), (x, y + h - cl), 2)
        # Inferior Direito
        pygame.draw.line(screen, (255, 255, 255), (x + w, y + h), (x + w - cl, y + h), 2)
        pygame.draw.line(screen, (255, 255, 255), (x + w, y + h), (x + w, y + h - cl), 2)

    def draw_aim_link_with_camera(self, screen, player, selected, camera):
        """
        Desenha um feixe laser pulsante entre o jogador e a entidade selecionada.
        Utiliza as coordenadas transformadas pela câmera para precisão visual.
        """
        if not selected:
            return
        try:
            p_cam = camera.apply((player.properties["x"] + player.properties.get("w", 40)//2, 
                                 player.properties["y"] + player.properties.get("h", 40)//2))
            s_cam = camera.apply((selected.properties["x"] + selected.properties.get("w", 40)//2, 
                                 selected.properties["y"] + selected.properties.get("h", 40)//2))
        except:
            return
        
        # Efeito de pulso no feixe (transparência varia com o tempo)
        alpha = 50 + int(math.sin(pygame.time.get_ticks() * 0.01) * 30)
        color = (0, 255, 200, alpha)
        
        w, h = screen.get_width(), screen.get_height()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(surf, color, p_cam, s_cam, 2)
        screen.blit(surf, (0, 0))

    def draw_selection_ring_fixed(self, screen, cam_x, cam_y, w, h):
        """
        Desenha um retângulo de seleção em volta da entidade focada.
        O anel possui marcações nos cantos que piscam sutilmente.
        """
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
        """
        Desenha um mini-mapa tático no canto superior direito da tela.
        
        Funcionamento:
        - Mapeia as coordenadas do mundo (4000x3000) para o tamanho do painel do mapa (200x150).
        - Representa o jogador como um ponto verde.
        - Representa inimigos como pontos laranjas.
        - Representa o Boss como um ponto vermelho grande.
        - Representa a saída do nível com efeitos de pulso se estiver ativa.
        """
        sw, sh = screen.get_width(), screen.get_height()
        map_w, map_h = 200, 150
        padding = 15
        mx0 = sw - map_w - padding
        my0 = padding
        
        # Desenha o fundo do mapa
        self._draw_cyber_rect(screen, (mx0, my0, map_w, map_h), (5, 10, 15), alpha=160, border_color=(0, 150, 255))
        
        # Dimensões lógicas do mundo para cálculo de proporção
        WORLD_W, WORLD_H = 4000, 3000
        
        # Função para converter coord de mundo para coord de minimapa
        def to_map(wx, wy):
            rx = mx0 + (wx / WORLD_W) * map_w
            ry = my0 + (wy / WORLD_H) * map_h
            return int(rx), int(ry)

        # Itera sobre todas as entidades para desenhá-las no mapa
        for e in entities:
            # Pula obstáculos invisíveis ou bordas para manter o mapa limpo
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

        # Desenha o Player (Sempre por cima de tudo no mapa)
        px, py = player.properties.get("x", 0), player.properties.get("y", 0)
        pmx, pmy = to_map(px, py)
        pygame.draw.circle(screen, (0, 255, 100), (pmx, pmy), 4) # Ponto Verde
        # "Radar sweep" simbólico em volta do player
        pygame.draw.circle(screen, (0, 255, 100), (pmx, pmy), 10, 1)

        # Título do mapa
        label = self.font_small.render("NAV_SYSTEM.MAP", True, (0, 180, 255))
        screen.blit(label, (mx0, my0 + map_h + 5))

    def draw_tutorial_prompt(self, screen, step):
        """
        Exibe instruções na tela durante o nível de tutorial prático.
        Cada 'step' corresponde a uma instrução diferente guiando o jogador.
        """
        prompts = [
            "BEM-VINDO, SENTINELA. USE [ W, A, S, D ] PARA SE MOVER PELO KERNEL.",
            "ALVO DETECTADO. CLIQUE COM O MOUSE NO 'DUMMY_ALPHA' (VERMELHO) PARA SELECIONÁ-LO.",
            "EXCELENTE. AGORA PRESSIONE [ C ] PARA ABRIR O TERMINAL.",
            "DIGITE 'dump' E PRESSIONE [ENTER] PARA VER TODAS AS VARIÁVEIS DO ALVO.",
            "AGORA DIGITE 'scan' PARA UM RESUMO DE INTEGRIDADE (HP) E ESTADO.",
            "EXCELENTE. PRESSIONE [ X ] PARA RECORTAR (CUT) A VELOCIDADE DO ALVO.",
            "VALOR ARMAZENADO NO SLOT A. AGORA SELECIONE O 'DUMMY_BETA' (AMARELO).",
            "ALVO MUDADO. PRESSIONE [ V ] PARA COLAR (PASTE) A VELOCIDADE NO 'DUMMY_BETA'.",
            "MUITO BEM. ABRA O TERMINAL [ C ] NOVAMENTE COM O 'DUMMY_BETA' SELECIONADO.",
            "DIGITE 'chmod -x' NO TERMINAL E [ENTER] PARA REMOVER A PERMISSÃO DE ATAQUE.",
            "DUMMY_BETA NEUTRALIZADO. AGORA SELECIONE O 'DUMMY_GAMMA' (LARANJA).",
            "ESSE ERRO É UM BUFFER OVERFLOW. PRESSIONE [ P ] PARA UM SMART PATCH DE CORREÇÃO.",
            "ERRO CORRIGIDO! POR FIM, CLIQUE EM VOCÊ MESMO (SENTINELA) E ABRA O TERMINAL [ C ].",
            "DIGITE 'heal' PARA RESTAURAR SUA PRÓPRIA INTEGRIDADE E LIMPAR RASTROS.",
            "TUDO PRONTO! AGORA SELECIONE O 'DUMMY_ALPHA' NOVAMENTE.",
            "DIGITE 'purge' NO TERMINAL PARA APAGÁ-LO DE FORMA LIMPA E CONCLUIR.",
            "TREINAMENTO FINALIZADO. SIGA PARA A SAÍDA (CÍRCULO CIANO) PARA A MISSÃO REAL."
        ]
        
        if 0 <= step < len(prompts):
            sw, sh = screen.get_width(), screen.get_height()
            txt = prompts[step]
            
            # Painel central superior para o tutorial
            p_w = 700
            p_h = 50
            x = sw // 2 - p_w // 2
            y = 120
            
            self._draw_cyber_rect(screen, (x, y, p_w, p_h), (20, 30, 40), alpha=220, border_color=(0, 255, 200))
            
            # Texto pulsante para chamar a atenção
            alpha = 180 + int(math.sin(pygame.time.get_ticks() * 0.005) * 75)
            surf = self.font_header.render(txt, True, (255, 255, 255))
            surf.set_alpha(alpha)
            screen.blit(surf, (sw // 2 - surf.get_width() // 2, y + 15))

    def draw(self, screen, corruption, player, level_name: str, path_hint: str):
        """
        Desenha os elementos fixos do HUD: Nome da fase, HP e Barra de Corrupção.
        """
        sw = screen.get_width()
        
        # Painel Superior Esquerdo (Status do Sistema)
        panel_w = 400
        panel_h = 100
        self._draw_cyber_rect(screen, (10, 10, panel_w, panel_h), (10, 20, 30))
        
        x, y = 20, 20
        title = self.font_header.render(level_name.upper(), True, (0, 255, 255))
        screen.blit(title, (x, y))
        
        # Exibe o "caminho" do sistema (estético)
        hint = self.font_small.render(path_hint, True, (0, 150, 150))
        screen.blit(hint, (x, y + 20))

        # Barra de Integridade (HP do Jogador)
        hp = player.properties.get("health", 100)
        hp_pct = max(0.0, min(1.0, hp / 100.0))
        hp_bar_w = 150
        
        pygame.draw.rect(screen, (40, 0, 0), (x, y + 45, hp_bar_w, 12)) # Fundo barra
        pygame.draw.rect(screen, (0, 255, 100), (x, y + 45, int(hp_bar_w * hp_pct), 12)) # HP atual
        hp_label = self.font_small.render(f"INTEGRIDADE: {int(hp)}%", True, (150, 255, 200))
        screen.blit(hp_label, (x + hp_bar_w + 10, y + 43))

        # Barra de Corrupção (Instabilidade do Sistema)
        cp_pct = max(0.0, min(1.0, corruption.level))
        pygame.draw.rect(screen, (20, 20, 20), (x, y + 65, hp_bar_w, 12)) # Fundo barra
        pygame.draw.rect(screen, (255, 50, 80), (x, y + 65, int(hp_bar_w * cp_pct), 12)) # Corrupção atual
        cp_label = self.font_small.render(f"CORRUPÇÃO: {cp_pct*100:.1f}%", True, (255, 150, 150))
        screen.blit(cp_label, (x + hp_bar_w + 10, y + 63))

    def draw_debugger_gun_panel(
        self, screen, player, selected, debugger, peek_cut, peek_paste
    ):
        """
        Desenha o painel inferior esquerdo com as informações da Debugger Gun.
        
        Mostra:
        - Atalhos de teclado (Recorte/Cola/Patch/Terminal).
        - Status do Clipboard (Slot A e B).
        - Alvo selecionado no momento e o que pode ser feito com ele.
        """
        sw = screen.get_width()
        sh = screen.get_height()
        panel_w = 460
        panel_h = 180
        zh = min(CONSOLE_ZONE_HEIGHT, max(96, sh // 5))
        x0 = 10
        # Posicionamento dinâmico acima da zona do console
        y0 = sh - zh - DEBUGGER_GAP_ABOVE_CONSOLE - panel_h
        y0 = max(120, y0)

        self._draw_cyber_rect(screen, (x0, y0, panel_w, panel_h), (8, 12, 16), border_color=(0, 180, 140))

        title = self.font_header.render("DEBUGGER_GUN.EXE v2.0", True, (0, 255, 180))
        screen.blit(title, (x0 + 15, y0 + 12))

        # Lista de comandos disponíveis
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

        # Exibição do conteúdo dos slots A e B da área de transferência
        buf_y = y0 + 105
        for bline in debugger.buffer_status_lines():
            # Destaque em azul para o slot ativo (indicado por ►)
            col = (0, 220, 255) if bline.startswith("►") else (100, 150, 180)
            screen.blit(self.font_small.render(bline, True, col), (x0 + 15, buf_y))
            buf_y += 15

        # Informações sobre o alvo selecionado
        if selected:
            status_col = (100, 255, 150)
            target_name = selected.debug_label().upper()
            self.font_title.set_bold(True)
            tgt_surf = self.font_title.render(f"ACTIVE_TARGET: {target_name}", True, status_col)
            screen.blit(tgt_surf, (x0 + 15, buf_y + 5))
            
            # Mostra prévia do que será recortado ou colado
            cut_k = peek_cut or "NONE"
            pst = peek_paste or "NONE"
            hint = f"REQ: {cut_k} | DEST: {pst}"
            screen.blit(self.font_small.render(hint, True, (255, 255, 150)), (x0 + 15, buf_y + 22))
        else:
            warn = self.font_small.render(">> AGUARDANDO SELEÇÃO DE ALVO...", True, (255, 150, 0))
            screen.blit(warn, (x0 + 15, buf_y + 10))

    def draw_aim_link(self, screen, player, selected):
        """
        Versão estática do feixe de mira (sem câmera, usado se necessário).
        """
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
        """
        Versão estática do anel de seleção.
        """
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
