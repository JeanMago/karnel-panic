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
        x = -target.properties["x"] + int(WIDTH / 2)
        y = -target.properties["y"] + int(HEIGHT / 2)
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
        self.saved = load_state()
        self.reset_system(self.saved.get("level", 1))

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

        for entity in self.loop.entities:
            if entity is self.player or not entity.is_hostile():
                continue
            if not entity.properties.get("visible", True):
                continue
            ex = entity.properties.get("x", 0)
            ey = entity.properties.get("y", 0)
            ew = entity.properties.get("w", 40)
            eh = entity.properties.get("h", 40)
            if px < ex + ew and px + pw > ex and py < ey + eh and py + ph > ey:
                self.corruption.increase(0.0005)

    def select_entity(self, pos):
        # A posição do mouse (pos) está em Screen Space. 
        # Precisamos converter para World Space para colidir com as entidades.
        world_x = pos[0] - self.camera.camera.x
        world_y = pos[1] - self.camera.camera.y
        world_pos = (world_x, world_y)

        for entity in reversed(self.loop.entities):
            if entity.collide(world_pos):
                if self._has_line_of_sight(self.player, entity):
                    self.selected = entity
                    label = entity.debug_label()
                    tipo = entity.properties.get("tipo", "?")
                    st = entity.properties.get("state", "?")
                    self.console.log(f"INSPECT → {label} | {tipo} | {st}")
                else:
                    self.console.log("SINAL BLOQUEADO: Obstáculo detectado.")
                return

    def _has_line_of_sight(self, start_ent, end_entity):
        if end_entity.properties.get("collision"): return True
        
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
                if other.properties.get("collision"):
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
            self.laser_frames = 10
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
            self.laser_frames = 10
            self.laser_color = (255, 50, 50)

        if event.key == pygame.K_v:
            dest = self.debugger.paste(self.selected)
            if dest:
                self.console.log(f"PASTE → {dest}")
            else:
                self.console.log("PASTE: buffer vazio ou destino inválido")
            self.laser_frames = 10
            self.laser_color = (50, 50, 255)

        if event.key == pygame.K_p:
            what = self.debugger.smart_patch(self.selected)
            if what:
                self.console.log(f"PATCH aplicado em: {what}")
            else:
                self.console.log("PATCH: nada a corrigir")
            self.laser_frames = 10
            self.laser_color = (50, 255, 50)

    def render(self):
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
        self.hud.draw(self.screen, self.corruption, name, path)

        peek_cut = self.debugger.peek_cut_key(self.selected) if self.selected else None
        peek_paste = self.debugger.peek_paste_destination(self.selected) if self.selected else None
        
        self.hud.draw_debugger_gun_panel(self.screen, self.player, self.selected, self.debugger, peek_cut, peek_paste)
        self.inspector.draw(self.screen, self.selected)
        self.console.draw(self.screen)
        self.code_editor.draw(self.screen)

        if self.corruption.level > 0.8 and self.corruption.glitch_active:
            inv = pygame.Surface((sw, sh))
            inv.fill((255, 255, 255))
            self.screen.blit(inv, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

        pygame.display.flip()

    def _check_objectives(self):
        exit_node = None
        boss_defeated = True # Se não houver boss, libera
        
        for e in self.loop.entities:
            if e.properties.get("tipo") == "TERMINAL_EXIT":
                exit_node = e
            elif e.properties.get("tipo") == "BOSS":
                if e.properties.get("health", 0) > 0:
                    boss_defeated = False

        if exit_node:
            exit_node.properties["active"] = boss_defeated
            
            px, py = self.player.properties["x"], self.player.properties["y"]
            pw, ph = self.player.properties.get("w", 40), self.player.properties.get("h", 40)
            ex, ey = exit_node.properties["x"], exit_node.properties["y"]
            ew, eh = exit_node.properties["w"], exit_node.properties["h"]
            
            if boss_defeated and px < ex + ew and px + pw > ex and py < ey + eh and py + ph > ey:
                self.console.log("BOSS DERROTADO. SISTEMA RESTAURADO.")
                pygame.time.delay(1000)
                
                recovery = 0.15 * (1.0 - self.corruption.level)
                self.corruption.level = max(0.0, self.corruption.level - recovery)
                self.console.log(f"REPARAÇÃO: -{recovery*100:.1f}% de corrupção.")

                next_level = self.level_id + 1
                curr_max = int(self.saved.get("max_level", 1))
                new_max = max(curr_max, next_level)
                
                if next_level > 3:
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
                    show_opening_crawl(self)
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
                            pygame.display.toggle_fullscreen()
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
                    self.loop.update(dt)
                    self._apply_corruption_to_entities()
                    self._check_objectives()
                    
                    # Colisão e movimento
                    if self._check_collision_with_obstacles(self.player):
                        self.player.properties["x"] = self.player.properties["last_x"]
                        self.player.properties["y"] = self.player.properties["last_y"]
                    
                    self._corruption_from_hostiles()
                
                self.render()

    def _apply_corruption_to_entities(self):
        self.corruption.apply_world_effects(self.loop.entities, self.player)
        if self.corruption.integrity_failure:
            self.console.log("!!! KERNEL PANIC: SISTEMA IRRECUPERÁVEL !!!")
            self.render() 
            pygame.time.delay(2000)
            self.reset_system(self.level_id, carry_corruption=0.0)
            self.console.log("Kernel reiniciado. Estado anterior perdido.")
