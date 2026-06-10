import pygame
import random
import math

from config import WIDTH, HEIGHT, FPS, LIMIT_FPS
from core.loop import GameLoop
from core.corruption import CorruptionSystem
from core.levels import build_level, get_level_info
from core.audio import AudioManager

from mechanics.debugger_gun import DebuggerGun
from ui.inspector import Inspector
from ui.console import Console
from ui.hud import HUD
from ui.code_editor import CodeEditor
from ui import menus
from ui.opening import show_opening_crawl
from mechanics.tron import TronGame

from persistence.storage import load_state, save_state, load_settings

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, pos):
        """Aplica o offset da câmera em uma posição (x, y)."""
        return (pos[0] + self.camera.x, pos[1] + self.camera.y)

    def update(self, target):
        """Faz a câmera seguir o alvo (player)."""
        x = -target.properties["x"] + int(self.width / 2)
        y = -target.properties["y"] + int(self.height / 2)
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Game:
    def __init__(self):
        pygame.init()
        settings = load_settings()
        self.width = settings.get("width", WIDTH)
        self.height = settings.get("height", HEIGHT)
        self.limit_fps = settings.get("limit_fps", LIMIT_FPS)

        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE | pygame.SCALED
        )
        pygame.display.set_caption("Kernel.panic()")

        self.clock = pygame.time.Clock()
        self.camera = Camera(WIDTH, HEIGHT)
        self.audio = AudioManager()
        self.laser_color = (255, 255, 255)
        self.level_id = 1
        self.is_fullscreen = False
        self.saved = load_state()
        self.reset_system(self.saved.get("level", 1))

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            # No pygame-ce, SCALED + FULLSCREEN funciona melhor com (0,0) ou a resolução interna
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.SCALED | pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.SCALED | pygame.RESIZABLE)

    def reset_system(self, level_id: int, carry_corruption: float = None):
        self.level_id = int(level_id)
        self.loop = GameLoop()
        
        if carry_corruption is not None:
            new_corruption = carry_corruption
        else:
            new_corruption = float(self.saved.get("corruption", 0.0))

        self.corruption = CorruptionSystem()
        self.corruption.level = new_corruption

        self.debugger = DebuggerGun(self.corruption)
        self.inspector = Inspector()
        self.console = Console()
        self.hud = HUD()
        self.code_editor = CodeEditor()

        sw, sh = self.screen.get_width(), self.screen.get_height()
        self.player, entities = build_level(self.level_id, sw, sh)
        for e in entities:
            self.loop.add_entity(e)

        self.selected = None
        self.laser_frames = 0
        self.tutorial_step = 0 if self.level_id == 0 else -1

    def _clamp_entities(self):
        # Em áreas gigantes, o clamp é opcional ou baseado no tamanho do mapa real.
        # Por agora, permitimos movimento livre.
        pass

    def _check_collision_with_obstacles(self, mover):
        mx, my = mover.properties["x"], mover.properties["y"]
        mw, mh = mover.properties["w"], mover.properties["h"]
        
        for other in self.loop.entities:
            if other is mover: continue
            if not other.properties.get("collision"): continue
            
            ox, oy = other.properties["x"], other.properties["y"]
            ow, oh = other.properties["w"], other.properties["h"]
            
            if mx < ox + ow and mx + mw > ox and my < oy + oh and my + mh > oy:
                return True
        return False

    def _corruption_from_hostiles(self):
        px, py = self.player.properties["x"], self.player.properties["y"]
        pw, ph = self.player.properties.get("w", 40), self.player.properties.get("h", 40)
        
        # HITBOX DE DANO: Ligeiramente MAIOR que o corpo físico (2px de folga)
        padding = 2
        p_damage_rect = pygame.Rect(px - padding, py - padding, pw + padding * 2, ph + padding * 2)

        for entity in self.loop.entities:
            if entity is self.player:
                continue
            
            for e_rect in entity.get_damage_rects():
                if p_damage_rect.colliderect(e_rect):
                    # 1. Aumento GRADUAL (por frame de contato)
                    self.corruption.increase(0.001) 
                    
                    # 2. Dano de IMPACTO (Saúde + Salto de Corrupção)
                    dmg = 15 # Aumentado de 10
                    corruption_bump = 0.05 # Aumentado de 0.03
                    
                    if entity.properties.get("tipo") == "BOSS":
                        dmg = 30 # Aumentado de 25
                        corruption_bump = 0.12 # Aumentado de 0.10
                    
                    if self.player.take_damage(dmg):
                        self.corruption.increase(corruption_bump)
                        self.console.log(f"DANO: -{dmg} HP | +{corruption_bump*100:.0f}% Corrupção")
                    break # Só aplica dano de uma hitbox por entidade por frame

    def select_entity(self, pos):
        # A posição do mouse (pos) está em Screen Space. 
        # Precisamos converter para World Space para colidir com as entidades.
        world_x = pos[0] - self.camera.camera.x
        world_y = pos[1] - self.camera.camera.y
        world_pos = (world_x, world_y)

        # Margem de tolerância para cliques (facilita selecionar entidades pequenas)
        margin = 10

        for entity in reversed(self.loop.entities):
            # Se for o player, a colisão deve ser exata para evitar selecioná-lo sem querer
            if entity.debug_label() == "Player":
                if entity.collide(world_pos):
                    self.selected = entity
                    self.console.log("INSPECT → Sentinel (Você)")
                    return
                continue

            # Para outras entidades, aplica a margem
            ex = entity.properties.get("x", 0)
            ey = entity.properties.get("y", 0)
            ew = entity.properties.get("w", 40)
            eh = entity.properties.get("h", 40)
            
            if (ex - margin <= world_x <= ex + ew + margin) and (ey - margin <= world_y <= ey + eh + margin):
                if self._has_line_of_sight(self.player, entity):
                    self.selected = entity
                    label = entity.debug_label()
                    tipo = entity.properties.get("tipo", "?")
                    st = entity.properties.get("state", "?")
                    self.console.log(f"INSPECT → {label} | {tipo} | {st}")
                else:
                    self.console.log("SINAL BLOQUEADO: Obstáculo detectado.")
                return

        # Se clicou no vazio, desseleciona
        if self.selected:
            self.selected = None
            self.console.log("DESSELECIONAR: Foco liberado.")

    def _has_line_of_sight(self, start_ent, end_entity):
        if start_ent is end_entity: return True
        
        x1, y1 = start_ent.properties["x"] + 20, start_ent.properties["y"] + 20
        x2, y2 = end_entity.properties["x"] + 20, end_entity.properties["y"] + 20
        
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: return True
        
        steps = int(dist / 10) 
        for i in range(1, steps):
            tx = x1 + (dx * i / steps)
            ty = y1 + (dy * i / steps)
            for other in self.loop.entities:
                if other is start_ent or other is end_entity: continue
                # Apenas obstáculos e inimigos sólidos bloqueiam a visão (ignora processos voláteis)
                if other.properties.get("collision") and other.properties.get("tipo") != "processo":
                    ox, oy = other.properties["x"], other.properties["y"]
                    ow, oh = other.properties["w"], other.properties["h"]
                    if ox <= tx <= ox + ow and oy <= ty <= oy + oh:
                        return False
        return True

    def handle_debug_keys(self, event):
        if self.code_editor.active:
            cmd = self.code_editor.handle_event(event)
            if cmd and self.selected:
                res = self.debugger.manual_patch(self.selected, cmd)
                self.console.log(res)
                if res == "SIGNAL: TRON_PROTOCOL_ACTIVATED":
                    self.code_editor.active = False
                    self.console.log("ACESSO À GRADE SECRETA...")
                    pygame.time.delay(1000)
                    tron = TronGame(self.screen, self.clock)
                    tron.run()
                    self.console.log("Protocolo Tron finalizado.")
                
                # Desseleciona apenas se o alvo foi purgado ou destruído
                if not self.selected.properties.get("visible", True) or (self.selected.properties.get("health", 1) or 1) <= 0:
                    self.selected = None
                
                self.code_editor.active = False # Fecha o editor automaticamente
            return

        if event.key == pygame.K_c:
            if self.selected:
                self.code_editor.toggle()
                self.console.log("Terminal de Patch: DIGITE comando (ex: speed=0)")
            else:
                self.console.log("Selecione um alvo primeiro para usar o Terminal [C]")
            return

        if event.key == pygame.K_TAB:
            slot = self.debugger.cycle_clip()
            self.console.log(f"Slot ativo: {'A' if slot == 0 else 'B'} (CUT / PASTE)")
            return

        if not self.selected:
            return

        if event.key == pygame.K_i:
            props = self.debugger.inspect(self.selected)
            self.console.log(f"dump: {props}")

        if event.key == pygame.K_t:
            if self.selected.debug_label() == "Player":
                if self.debugger.cut(self.selected, "token"):
                    self.console.log("CUT token → slot ativo (use no NullPointer com V)")
                else:
                    self.console.log("CUT token falhou")
            else:
                self.console.log("CUT token: só funciona no Player")
            self.laser_frames = 4
            self.laser_color = (255, 180, 80)
            return

        if event.key == pygame.K_x:
            ent = self.selected
            ok = False
            if self.debugger.cut(ent, self.debugger.peek_cut_key(ent)):
                self.console.log(f"CUT {self.debugger.peek_cut_key(ent)} → slot ativo")
                ok = True
            if not ok:
                self.console.log("CUT: sem propriedade válida neste alvo")
            self.laser_frames = 4
            self.laser_color = (255, 50, 50)
            return

        if event.key == pygame.K_v:
            dest = self.debugger.paste(self.selected)
            if dest:
                self.console.log(f"PASTE → {dest}")
                # Desseleciona apenas se o boss morreu na injeção
                if (self.selected.properties.get("health", 1) or 1) <= 0:
                    self.selected = None
            else:
                self.console.log("PASTE: buffer vazio ou destino inválido")
            self.laser_frames = 4
            self.laser_color = (50, 50, 255)
            return

        if event.key == pygame.K_p:
            what = self.debugger.smart_patch(self.selected)
            if what:
                self.console.log(f"PATCH aplicado em: {what}")
                if (self.selected.properties.get("health", 1) or 1) <= 0:
                    self.selected = None
            else:
                self.console.log("PATCH: nada a corrigir")
            self.laser_frames = 4
            self.laser_color = (50, 255, 50)

    def _update_tutorial(self):
        """Lógica de progressão do tutorial passo a passo."""
        if self.tutorial_step == -1: return

        if self.tutorial_step == 0:
            # Step 0: Move
            px, py = self.player.properties["x"], self.player.properties["y"]
            if abs(px - 200) > 50 or abs(py - 450) > 50:
                self.tutorial_step = 1

        elif self.tutorial_step == 1:
            # Step 1: Select DUMMY_ALPHA
            if self.selected and self.selected.properties.get("name") == "DUMMY_ALPHA":
                self.tutorial_step = 2

        elif self.tutorial_step == 2:
            # Step 2: Open Terminal
            if self.code_editor.active:
                self.tutorial_step = 3

        elif self.tutorial_step == 3:
            # Step 3: Run 'dump'
            if self.console.logs and "DUMP:" in self.console.logs[-1].upper():
                self.tutorial_step = 4

        elif self.tutorial_step == 4:
            # Step 4: Run 'scan'
            if self.console.logs and "SCAN:" in self.console.logs[-1].upper():
                self.tutorial_step = 5
        elif self.tutorial_step == 5:
            # Step 5: Cut speed
            # Garante que o terminal foi fechado antes de pedir o CUT
            if not self.code_editor.active:
                if self.debugger.buffers[0] is not None or self.debugger.buffers[1] is not None:
                    self.tutorial_step = 6

        elif self.tutorial_step == 6:
            # Step 6: Select DUMMY_BETA
            if self.selected and self.selected.properties.get("name") == "DUMMY_BETA":
                self.tutorial_step = 7

        elif self.tutorial_step == 7:
            # Step 7: Paste speed
            if self.selected and self.selected.properties.get("name") == "DUMMY_BETA":
                if (self.selected.properties.get("speed") or 0) > 0:
                    self.tutorial_step = 8

        elif self.tutorial_step == 8:
            # Step 8: Open Terminal on DUMMY_BETA
            if self.code_editor.active and self.selected and self.selected.properties.get("name") == "DUMMY_BETA":
                self.tutorial_step = 9

        elif self.tutorial_step == 9:
            # Step 9: chmod -x on DUMMY_BETA
            if self.selected and self.selected.properties.get("name") == "DUMMY_BETA":
                if not self.selected.properties.get("hostile", True):
                    self.tutorial_step = 10

        elif self.tutorial_step == 10:
            # Step 10: Select DUMMY_GAMMA (Terminar fechado)
            if not self.code_editor.active:
                if self.selected and self.selected.properties.get("name") == "DUMMY_GAMMA":
                    self.tutorial_step = 11

        elif self.tutorial_step == 11:
            # Step 11: Smart Patch on DUMMY_GAMMA
            if self.selected and self.selected.properties.get("name") == "DUMMY_GAMMA":
                if (self.selected.properties.get("buffer_size") or 0) > 100:
                    self.tutorial_step = 12

        elif self.tutorial_step == 12:
            # Step 12: Select self
            if self.selected and self.selected.debug_label() == "Player":
                self.player.properties["health"] = 45
                self.tutorial_step = 13

        elif self.tutorial_step == 13:
            # Step 13: heal yourself (Terminal)
            if self.player.properties.get("health", 0) >= 100:
                self.tutorial_step = 14

        elif self.tutorial_step == 14:
            # Step 14: Select DUMMY_ALPHA again
            if not self.code_editor.active:
                if self.selected and self.selected.properties.get("name") == "DUMMY_ALPHA":
                    self.tutorial_step = 15

        elif self.tutorial_step == 15:
            # Step 15: Purge DUMMY_ALPHA
            alpha_alive = False
            for e in self.loop.entities:
                if e.properties.get("name") == "DUMMY_ALPHA" and e.properties.get("visible", True):
                    alpha_alive = True
                    break
            if not alpha_alive:
                self.tutorial_step = 16
    def render(self):
        if self.tutorial_step != -1:
            self._update_tutorial()

        self.camera.update(self.player)
        sw, sh = self.screen.get_width(), self.screen.get_height()
        shift = self.corruption.get_color_shift()
        intensity = sum(shift) // 3

        bg_r = min(255, 10 + shift[0])
        bg_g = min(255, 10 + shift[1])
        bg_b = min(255, 15 + shift[2])
        self.screen.fill((bg_r, bg_g, bg_b))

        grid_color = (0, max(50, 180 - intensity), max(50, 200 - intensity))
        if intensity > 60:
            grid_color = (min(255, 100 + intensity * 2), 0, 50)

        grid_size = 50
        # Grid precisa acompanhar a câmera (infinito aparente)
        offset_x = self.camera.camera.x % grid_size
        offset_y = self.camera.camera.y % grid_size

        for x in range(int(offset_x) - grid_size, sw + grid_size, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, sh), 1)
        for y in range(int(offset_y) - grid_size, sh + grid_size, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (sw, y), 1)

        glitch_off = (0, 0)
        if self.corruption.glitch_active:
            glitch_off = self.corruption.glitch_offset

        # Renderizar entidades (com offset da câmera)
        for e in self.loop.entities:
            # Pula render de entidades "mortas" ou invisíveis
            if not e.should_render() or (e.properties.get("health", 1) is not None and e.properties.get("health", 1) <= 0):
                continue

            orig_x = e.properties.get("x", 0)
            orig_y = e.properties.get("y", 0)

            cam_pos = self.camera.apply((orig_x, orig_y))
            e.properties["x"] = cam_pos[0] + glitch_off[0]
            e.properties["y"] = cam_pos[1] + glitch_off[1]
            e.render(self.screen)

            e.properties["x"] = orig_x
            e.properties["y"] = orig_y

        # Feedback visual da Debugger Gun
        if self.selected:
            sx, sy = self.camera.apply((self.selected.properties["x"], self.selected.properties["y"]))
            self.hud.draw_selection_ring_fixed(self.screen, sx, sy, self.selected.properties.get("w", 40), self.selected.properties.get("h", 40))

        if self.laser_frames > 0 and self.selected:
            p_center = (self.player.properties["x"] + 20, self.player.properties["y"] + 20)
            s_center = (self.selected.properties["x"] + 20, self.selected.properties["y"] + 20)
            p_cam = self.camera.apply(p_center)
            s_cam = self.camera.apply(s_center)
            pygame.draw.line(self.screen, self.laser_color, p_cam, s_cam, 5)
            self.laser_frames -= 1

        info = get_level_info(self.level_id)
        name = info.name if info else f"Nível {self.level_id}"
        path = info.path_hint if info else "/"
        self.hud.draw(self.screen, self.corruption, self.player, name, path)

        # Chamada do Mini-mapa
        self.hud.draw_minimap(self.screen, self.loop.entities, self.player)

        peek_cut = self.debugger.peek_cut_key(self.selected) if self.selected else None
        peek_paste = self.debugger.peek_paste_destination(self.selected) if self.selected else None

        self.hud.draw_debugger_gun_panel(self.screen, self.player, self.selected, self.debugger, peek_cut, peek_paste)

        # Tutorial Prompt
        if self.tutorial_step != -1:
            self.hud.draw_tutorial_prompt(self.screen, self.tutorial_step)

        self.inspector.draw(self.screen, self.selected)
        self.console.draw(self.screen)
        self.code_editor.draw(self.screen)

        # Novos efeitos de corrupção dinâmicos
        self.corruption.draw_screen_glitches(self.screen)

        pygame.display.flip()
    def _check_objectives(self):
        exit_node = None
        boss_defeated = True
        boss_count = 0
        
        for e in self.loop.entities:
            if e.properties.get("tipo") == "TERMINAL_EXIT":
                exit_node = e
            elif e.properties.get("tipo") == "BOSS":
                boss_count += 1
                if e.properties.get("health", 0) > 0:
                    boss_defeated = False

        if exit_node:
            # Ativa a saída se todos os bosses foram derrotados (ou se não houver)
            is_active = boss_defeated and boss_count >= 0
            exit_node.properties["active"] = is_active
            
            px, py = self.player.properties["x"], self.player.properties["y"]
            pw, ph = self.player.properties.get("w", 40), self.player.properties.get("h", 40)
            ex, ey = exit_node.properties["x"], exit_node.properties["y"]
            ew, eh = exit_node.properties["w"], exit_node.properties["h"]
            
            # Se colidir com a saída ATIVA
            if is_active and px < ex + ew and px + pw > ex and py < ey + eh and py + ph > ey:
                self.console.log(">> CONEXÃO ESTABELECIDA. TRANSMITINDO DADOS...")
                pygame.time.delay(1200)
                
                recovery = 0.20 * (1.0 - self.corruption.level)
                self.corruption.level = max(0.0, self.corruption.level - recovery)
                self.console.log(f"REPARAÇÃO DO SETOR: -{recovery*100:.1f}% corrupção.")

                next_level = self.level_id + 1
                curr_max = int(self.saved.get("max_level", 1))
                new_max = max(curr_max, next_level)
                
                if self.level_id == 7:
                    self.console.log("!!! KERNEL TOTALMENTE REESTRUTURADO !!!")
                    pygame.time.delay(1000)
                    menus.show_ending(self)
                    next_level = 1
                
                curr_corruption = self.corruption.level
                save_state(curr_corruption, next_level, new_max)
                self.reset_system(next_level, carry_corruption=curr_corruption)

    def run(self):
        while True:
            self.saved = load_state()
            self.reset_system(self.saved.get("level", 1))
            in_menu = True
            while in_menu:
                self.audio.play_music("menu")
                action = menus.show_menu(self)
                if action == "quit":
                    pygame.quit()
                    return
                if action == "tutorial_level":
                    self.level_id = 0
                    self.reset_system(self.level_id, carry_corruption=0.0)
                    in_menu = False
                    continue

                if action == "tutorial":
                    if not menus.show_tutorial(self):
                        pygame.quit()
                        return
                    continue
                if action == "settings":
                    menus.show_settings(self)
                    continue
                if action == "start":
                    self.level_id = 1
                    self.reset_system(self.level_id, carry_corruption=0.0)
                    save_state(0.0, 1, 1)
                    if show_opening_crawl(self) is False:
                        continue # Volta ao menu se cancelar a confirmação
                    in_menu = False
                    continue
                
                if action == "select_level":
                    level = menus.show_level_selection(self)
                    if level is False:
                        pygame.quit()
                        return
                    if level is not None:
                        self.level_id = level
                        self.reset_system(self.level_id, carry_corruption=0.0)
                        self.console.log(f"Fase {self.level_id} montada.")
                        in_menu = False
                    continue

            running = True
            self.audio.play_music("level")

            while running:
                if self.limit_fps:
                    dt_ms = self.clock.tick(FPS)
                else:
                    dt_ms = self.clock.tick()
                
                dt = dt_ms * 60 / 1000.0

                self.corruption.update_frame_glitch()
                self.audio.update_volume(self.corruption.level)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.select_entity(event.pos)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F11:
                            self.toggle_fullscreen()
                        elif event.key == pygame.K_ESCAPE:
                            pause_action = menus.show_pause_menu(self)
                            if pause_action == "quit":
                                pygame.quit()
                                return
                            if pause_action == "menu":
                                running = False
                            elif pause_action == "save_quit":
                                curr_max = int(self.saved.get("max_level", 1))
                                save_state(self.corruption.level, self.level_id, curr_max)
                                pygame.quit()
                                return
                        else:
                            self.handle_debug_keys(event)

                if not running:
                    break

                if not self.code_editor.active:
                    # Salva posição anterior de todos para colisão
                    for e in self.loop.entities:
                        if "x" in e.properties and "y" in e.properties:
                            e.properties["last_x"] = e.properties["x"]
                            e.properties["last_y"] = e.properties["y"]

                    self.loop.update(dt)
                    self._apply_corruption_to_entities()
                    self._check_objectives()
                    
                    # Colisão e movimento para todas as entidades móveis
                    for e in self.loop.entities:
                        if e.properties.get("tipo") == "Boundary" or not e.properties.get("visible", True):
                            continue
                        
                        # Se for algo que se move (Player ou Inimigos), checa contra obstáculos
                        if e.properties.get("tipo") in ["processo", "NullPointer", "InfiniteLoop", "StackOverflow", "BufferOverflow", "MemoryLeak", "Deadlock", "Rival"]:
                            if self._check_collision_with_obstacles(e):
                                e.properties["x"] = e.properties.get("last_x", e.properties["x"])
                                e.properties["y"] = e.properties.get("last_y", e.properties["y"])
                                e.on_collision()
                    
                    self._corruption_from_hostiles()
                
                self.render()

    def _apply_corruption_to_entities(self):
        self.corruption.apply_world_effects(self.loop.entities, self.player)
        
        # Falha por corrupção OU falha por perda total de HP (Saúde)
        if self.corruption.integrity_failure or self.player.properties.get("health", 0) <= 0:
            msg = "!!! KERNEL PANIC: SISTEMA IRRECUPERÁVEL !!!"
            if self.player.properties.get("health", 0) <= 0:
                msg = "!!! CRITICAL FAILURE: PROCESS TERMINATED (0 HP) !!!"
            
            self.console.log(msg)
            self.render() 
            pygame.time.delay(2000)
            self.reset_system(self.level_id, carry_corruption=0.0)
            self.console.log("Kernel reiniciado. Estado anterior perdido.")
