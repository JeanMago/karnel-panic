import pygame
import random
import math
from config import FPS

class TronGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.reset()

    def reset(self):
        # Usa dimensões dinâmicas da tela atual
        self.sw, self.sh = self.screen.get_width(), self.screen.get_height()
        
        # Jogador (Azul Neon)
        self.p1_pos = [self.sw // 4, self.sh // 2]
        self.p1_dir = [1, 0]
        self.p1_trail = [tuple(self.p1_pos)]
        self.p1_color = (0, 255, 255)
        
        # IA (Vermelho Crítico) - Agora mais inteligente
        self.p2_pos = [3 * self.sw // 4, self.sh // 2]
        self.p2_dir = [-1, 0]
        self.p2_trail = [tuple(self.p2_pos)]
        self.p2_color = (255, 50, 50)
        
        self.speed = 5
        self.running = True
        self.winner = None
        self.font = pygame.font.SysFont("monospace", 40, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 20)

    def _is_valid(self, pos, trail_list):
        """Checa se a posição é segura (dentro das bordas e fora das trilhas)."""
        if not (10 <= pos[0] <= self.sw - 10 and 10 <= pos[1] <= self.sh - 10):
            return False
        # Checa colisão com trilhas (aproximado por distância para performance)
        for trail in trail_list:
            for p in trail:
                dist_sq = (pos[0]-p[0])**2 + (pos[1]-p[1])**2
                if dist_sq < 16: # 4 pixels de raio
                    return False
        return True

    def _ai_think(self):
        """IA preditiva que tenta evitar colisões."""
        possible_dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]]
        # Evita virar 180 graus
        opp = [-self.p2_dir[0], -self.p2_dir[1]]
        possible_dirs = [d for d in possible_dirs if d != opp]

        # 1. Checa se a direção atual é perigosa
        future_pos = [self.p2_pos[0] + self.p2_dir[0] * self.speed * 2, 
                      self.p2_pos[1] + self.p2_dir[1] * self.speed * 2]
        
        needs_change = not self._is_valid(future_pos, [self.p1_trail, self.p2_trail])

        if needs_change or random.random() < 0.02:
            # Tenta encontrar a melhor direção
            best_dir = self.p2_dir
            max_dist = -1
            
            random.shuffle(possible_dirs) # Aleatoriedade para não ser mecânico demais
            for d in possible_dirs:
                # Projeta distância livre nessa direção
                free_dist = 0
                for step in range(1, 15):
                    test_p = [self.p2_pos[0] + d[0] * self.speed * step, 
                              self.p2_pos[1] + d[1] * self.speed * step]
                    if self._is_valid(test_p, [self.p1_trail, self.p2_trail]):
                        free_dist += 1
                    else:
                        break
                
                if free_dist > max_dist:
                    max_dist = free_dist
                    best_dir = d
            
            self.p2_dir = best_dir

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w and self.p1_dir != [0, 1]: self.p1_dir = [0, -1]
                    if event.key == pygame.K_s and self.p1_dir != [0, -1]: self.p1_dir = [0, 1]
                    if event.key == pygame.K_a and self.p1_dir != [1, 0]: self.p1_dir = [-1, 0]
                    if event.key == pygame.K_d and self.p1_dir != [-1, 0]: self.p1_dir = [1, 0]
                    if event.key == pygame.K_ESCAPE: self.running = False
                if event.type == pygame.VIDEORESIZE:
                    # Tron se adapta ao redimensionamento em tempo real
                    self.sw, self.sh = event.w, event.h

            self._ai_think()

            # Mover
            self.p1_pos[0] += self.p1_dir[0] * self.speed
            self.p1_pos[1] += self.p1_dir[1] * self.speed
            self.p2_pos[0] += self.p2_dir[0] * self.speed
            self.p2_pos[1] += self.p2_dir[1] * self.speed

            # Colisões exatas
            p1_rect = pygame.Rect(self.p1_pos[0], self.p1_pos[1], 4, 4)
            p2_rect = pygame.Rect(self.p2_pos[0], self.p2_pos[1], 4, 4)

            # Bordas
            if not (5 <= self.p1_pos[0] <= self.sw - 5 and 5 <= self.p1_pos[1] <= self.sh - 5):
                self.winner = "IA (Kernel)"
                self.running = False
            if not (5 <= self.p2_pos[0] <= self.sw - 5 and 5 <= self.p2_pos[1] <= self.sh - 5):
                self.winner = "SENTINELA"
                self.running = False

            # Trilhas (otimizado: checa apenas colisão com pontos para evitar muitos Rects)
            for part in self.p1_trail[:-5]:
                if p1_rect.collidepoint(part): self.winner = "IA (Kernel)"; self.running = False
                if p2_rect.collidepoint(part): self.winner = "SENTINELA"; self.running = False
            for part in self.p2_trail[:-5]:
                if p1_rect.collidepoint(part): self.winner = "IA (Kernel)"; self.running = False
                if p2_rect.collidepoint(part): self.winner = "SENTINELA"; self.running = False

            self.p1_trail.append(tuple(self.p1_pos))
            self.p2_trail.append(tuple(self.p2_pos))

            # Renderização Estilizada
            self.screen.fill((5, 5, 15))
            
            # Grid Dinâmico
            grid_size = 60
            for x in range(0, self.sw, grid_size):
                pygame.draw.line(self.screen, (20, 30, 60), (x, 0), (x, self.sh), 1)
            for y in range(0, self.sh, grid_size):
                pygame.draw.line(self.screen, (20, 30, 60), (0, y), (self.sw, y), 1)

            # Trilhas com brilho
            if len(self.p1_trail) > 1:
                pygame.draw.lines(self.screen, self.p1_color, False, self.p1_trail, 4)
            if len(self.p2_trail) > 1:
                pygame.draw.lines(self.screen, self.p2_color, False, self.p2_trail, 4)

            # Cabeças das motos
            pygame.draw.rect(self.screen, (255, 255, 255), p1_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), p2_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        if self.winner:
            self._show_end_screen()

    def _show_end_screen(self):
        overlay = pygame.Surface((self.sw, self.sh))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        txt = self.font.render(f"VENCEDOR: {self.winner}", True, (255, 255, 0))
        self.screen.blit(txt, (self.sw // 2 - txt.get_width() // 2, self.sh // 2 - 30))
        
        msg = self.font_small.render("PROTOCOLO FINALIZADO. RETORNANDO...", True, (0, 255, 150))
        self.screen.blit(msg, (self.sw // 2 - msg.get_width() // 2, self.sh // 2 + 40))
        
        pygame.display.flip()
        pygame.time.delay(2500)
