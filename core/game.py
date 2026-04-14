import pygame
from config import WIDTH, HEIGHT, FPS
from core.loop import GameLoop
from core.corruption import CorruptionSystem

from entities.player import Player
from entities.null_pointer import NullPointer
from mechanics.debugger_gun import DebuggerGun
from ui.inspector import Inspector
from ui.console import Console

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kernel.panic()")

        self.clock = pygame.time.Clock()
        self.laser_color = (255, 255, 255)
        self.reset_system()

    def reset_system(self):
        self.loop = GameLoop()
        self.corruption = CorruptionSystem()
        self.debugger = DebuggerGun(self.corruption)

        self.inspector = Inspector()
        self.console = Console()

        sw, sh = self.screen.get_width(), self.screen.get_height()
        self.player = Player(sw // 4, sh // 2)
        self.enemy = NullPointer(sw * 3 // 4, sh // 2, self.player)

        self.loop.add_entity(self.player)
        self.loop.add_entity(self.enemy)

        self.selected = None
        self.laser_frames = 0

    def show_menu(self):
        font_title = pygame.font.SysFont("monospace", 60, bold=True)
        font_item = pygame.font.SysFont("monospace", 30)
        
        options = ["Iniciar Sistema", "Manual (Como Jogar)", "Sair"]
        selected_idx = 0
        
        while True:
            sw, sh = self.screen.get_width(), self.screen.get_height()
            self.screen.fill((10, 10, 15))
            
            title_surf = font_title.render("Kernel.panic()", True, (0, 255, 0))
            self.screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 4))
            
            for i, option in enumerate(options):
                color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
                text = f"> {option} <" if i == selected_idx else f"  {option}  "
                item_surf = font_item.render(text, True, color)
                self.screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 + i * 50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_idx = (selected_idx - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_idx = (selected_idx + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_idx == 0: return "start"
                        if selected_idx == 1: return "tutorial"
                        if selected_idx == 2: return "quit"
            self.clock.tick(FPS)

    def show_tutorial(self):
        font_title = pygame.font.SysFont("monospace", 40, bold=True)
        font_text = pygame.font.SysFont("monospace", 20)
        
        tutorial_lines = [
            "--- MANUAL DE OPERAÇÃO DA DEBUGGER GUN ---",
            "",
            "ALERTA: O sistema principal (The Heap) está falhando!",
            "Evite que os inimigos (NullPointers) encostem em você,",
            "ou o nível de corrupção aumentará até o Kernel Panic.",
            "",
            "MOVIMENTAÇÃO: Teclas W, A, S, D",
            "",
            "HACKEANDO A MEMÓRIA INIMIGA:",
            "1. Use o MOUSE (CLIQUE ESQUERDO) para focar em um alvo.",
            "2. Pressione as teclas abaixo para manipular o alvo:",
            "",
            " [ I ] INSPECIONAR : Exibe propriedades (variáveis) do alvo.",
            " [ X ] CUT         : Recorta (remove) a velocidade do alvo.",
            "                     (Dica: Use para paralisar NullPointers!)",
            " [ V ] PASTE       : Cola a velocidade recortada no alvo.",
            " [ P ] PATCH       : Aplica um patch de correção na memória.",
            "",
            "Pressione ESC para voltar."
        ]
        
        while True:
            sw = self.screen.get_width()
            self.screen.fill((10, 10, 15))
            
            title_surf = font_title.render("Manual do Sistema", True, (0, 255, 255))
            self.screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 50))
            
            for i, line in enumerate(tutorial_lines):
                color = (200, 200, 200) if not line.startswith(" [") else (0, 255, 0)
                if "---" in line: color = (255, 255, 0)
                text_surf = font_text.render(line, True, color)
                self.screen.blit(text_surf, (50, 120 + i * 30))
                
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return True
            self.clock.tick(FPS)

    def show_level_selection(self):
        font_title = pygame.font.SysFont("monospace", 40, bold=True)
        font_item = pygame.font.SysFont("monospace", 30)
        
        levels = ["Fase 1: The Heap", "Fase 2: Stack Overflow", "Fase 3: Kernel Panic"]
        selected_idx = 0
        
        while True:
            sw, sh = self.screen.get_width(), self.screen.get_height()
            self.screen.fill((10, 10, 15))
            
            title_surf = font_title.render("Seleção de Sistema", True, (0, 255, 255))
            self.screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 6))
            
            for i, level in enumerate(levels):
                color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
                text = f"> {level} <" if i == selected_idx else f"  {level}  "
                item_surf = font_item.render(text, True, color)
                self.screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 - 50 + i * 50))
                
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_idx = (selected_idx - 1) % len(levels)
                    elif event.key == pygame.K_DOWN:
                        selected_idx = (selected_idx + 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        return selected_idx + 1
                    elif event.key == pygame.K_ESCAPE:
                        return None
            self.clock.tick(FPS)

    def show_pause_menu(self):
        font_title = pygame.font.SysFont("monospace", 50, bold=True)
        font_item = pygame.font.SysFont("monospace", 30)
        
        options = ["Retomar Execução", "Voltar ao Menu Principal"]
        selected_idx = 0
        
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        
        while True:
            sw, sh = self.screen.get_width(), self.screen.get_height()
            self.screen.blit(overlay, (0, 0))
            
            title_surf = font_title.render("SISTEMA PAUSADO", True, (255, 100, 100))
            self.screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 3))
            
            for i, option in enumerate(options):
                color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
                text = f"> {option} <" if i == selected_idx else f"  {option}  "
                item_surf = font_item.render(text, True, color)
                self.screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 + i * 50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
                    overlay.set_alpha(200)
                    overlay.fill((0, 0, 0))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_idx = (selected_idx - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_idx = (selected_idx + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_idx == 0: return "resume"
                        if selected_idx == 1: return "menu"
                    elif event.key == pygame.K_ESCAPE:
                        return "resume"
            self.clock.tick(FPS)

    def run(self):
        while True:
            self.reset_system()
            in_menu = True
            while in_menu:
                action = self.show_menu()
                if action == "quit":
                    pygame.quit()
                    return
                elif action == "tutorial":
                    keep_playing = self.show_tutorial()
                    if not keep_playing:
                        pygame.quit()
                        return
                    continue  # Volta para o menu principal
                    
                level = self.show_level_selection()
                if level is False:
                    pygame.quit()
                    return
                elif level is not None:
                    self.console.log(f"Fase {level} carregada no sistema.")
                    in_menu = False

            running = True
    
            while running:
                self.clock.tick(FPS)
    
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.select_entity(event.pos)
    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pause_action = self.show_pause_menu()
                            if pause_action == "quit":
                                pygame.quit()
                                return
                            elif pause_action == "menu":
                                running = False
                        else:
                            self.handle_debug_keys(event)
                            
                if not running:
                    break
    
                self.loop.update()
                
                # Limita as entidades às bordas da tela (Responsividade)
                sw, sh = self.screen.get_width(), self.screen.get_height()
                for entity in self.loop.entities:
                    x, y = entity.properties.get("x"), entity.properties.get("y")
                    w, h = entity.properties.get("w", 0), entity.properties.get("h", 0)
                    if x is not None and y is not None:
                        entity.properties["x"] = max(0, min(x, sw - w))
                        entity.properties["y"] = max(0, min(y, sh - h))
                
                # Dano de corrupção caso o NullPointer toque o Player
                px, py = self.player.properties["x"], self.player.properties["y"]
                pw, ph = self.player.properties.get("w", 40), self.player.properties.get("h", 40)
                ex, ey = self.enemy.properties.get("x", 0), self.enemy.properties.get("y", 0)
                ew, eh = self.enemy.properties.get("w", 40), self.enemy.properties.get("h", 40)
                
                if px < ex + ew and px + pw > ex and py < ey + eh and py + ph > ey:
                    self.corruption.increase(0.005)
    
                self.render()

    def select_entity(self, pos):
        for entity in self.loop.entities:
            if entity.collide(pos):
                self.selected = entity
                self.console.log("Entidade selecionada")

    def handle_debug_keys(self, event):
        if not self.selected:
            return

        if event.key == pygame.K_i:
            props = self.debugger.inspect(self.selected)
            self.console.log(str(props))

        if event.key == pygame.K_x:
            self.debugger.cut(self.selected, "speed")
            self.console.log("CUT speed")
            self.laser_frames = 10
            self.laser_color = (255, 50, 50)  # Laser Vermelho para CUT

        if event.key == pygame.K_v:
            self.debugger.paste(self.selected, "speed")
            self.console.log("PASTE speed")
            self.laser_frames = 10
            self.laser_color = (50, 50, 255)  # Laser Azul para PASTE

        if event.key == pygame.K_p:
            self.debugger.patch(
                self.selected,
                "speed",
                lambda v: v is None or v < 1,
                5
            )
            self.console.log("PATCH aplicado")
            self.laser_frames = 10
            self.laser_color = (50, 255, 50)  # Laser Verde para PATCH

    def render(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        shift = self.corruption.get_color_shift()
        
        # O fundo escurece ou avermelha com a corrupção
        bg_color = min(255, 10 + shift)
        self.screen.fill((bg_color, 10, 15))
        
        # Cenário: Malha da Memória (The Heap Grid)
        # Começa ciano/verde, muda para vermelho/magenta em alta corrupção
        grid_color = (0, max(50, 180 - shift), max(50, 200 - shift))
        if shift > 60:
            grid_color = (min(255, 100 + shift * 2), 0, 50)
            
        grid_size = 50
        # Um leve efeito de tremedeira (glitch) quando a corrupção está altíssima
        offset = (pygame.time.get_ticks() // 50) % 5 if shift > 90 else 0
        
        # Desenha as linhas horizontais e verticais do chão
        for x in range(-offset, sw, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, sh), 1)
        for y in range(-offset, sh, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (sw, y), 1)

        self.loop.render(self.screen)

        # Efeito visual de tiro (Laser de Dados) da DebuggerGun
        if self.laser_frames > 0 and self.selected:
            px = self.player.properties["x"] + self.player.properties.get("w", 40) // 2
            py = self.player.properties["y"] + self.player.properties.get("h", 40) // 2
            sx = self.selected.properties["x"] + self.selected.properties.get("w", 40) // 2
            sy = self.selected.properties["y"] + self.selected.properties.get("h", 40) // 2
            
            pygame.draw.line(self.screen, self.laser_color, (px, py), (sx, sy), 5)
            self.laser_frames -= 1

        self.inspector.draw(self.screen, self.selected)
        self.console.draw(self.screen)

        pygame.display.flip()
