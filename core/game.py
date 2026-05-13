import pygame
import random

from config import WIDTH, HEIGHT, FPS
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

from persistence.storage import load_state, save_state


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kernel.panic()")

        self.clock = pygame.time.Clock()
        self.audio = AudioManager()
        self.laser_color = (255, 255, 255)
        self.level_id = 1
        self.saved = load_state()
        self.reset_system(self.saved.get("level", 1))

    def reset_system(self, level_id: int, carry_corruption: float = None):
        self.level_id = int(level_id)
        self.loop = GameLoop()
        
        # Determinar nível de corrupção
        if carry_corruption is not None:
            new_corruption = carry_corruption
        else:
            # Se não houver carry, tentamos usar o salvo, mas apenas se carry_corruption não foi passado
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
        sw, sh = self.screen.get_width(), self.screen.get_height()
        for entity in self.loop.entities:
            x, y = entity.properties.get("x"), entity.properties.get("y")
            w, h = entity.properties.get("w", 0), entity.properties.get("h", 0)
            if x is not None and y is not None:
                entity.properties["x"] = max(0, min(x, sw - w))
                entity.properties["y"] = max(0, min(y, sh - h))

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
                self.corruption.increase(0.001)

    def select_entity(self, pos):
        for entity in reversed(self.loop.entities):
            if entity.collide(pos):
                self.selected = entity
                label = entity.debug_label()
                tipo = entity.properties.get("tipo", "?")
                st = entity.properties.get("state", "?")
                self.console.log(f"INSPECT → {label} | {tipo} | {st}")
                return

    def handle_debug_keys(self, event):
        if self.code_editor.active:
            cmd = self.code_editor.handle_event(event)
            if cmd and self.selected:
                res = self.debugger.manual_patch(self.selected, cmd)
                self.console.log(res)
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
            if self.debugger.cut(ent, "speed"):
                self.console.log("CUT speed → slot ativo")
                ok = True
            elif ent.debug_label() != "Player" and self.debugger.cut(ent, "stack_depth"):
                self.console.log("CUT stack_depth → slot ativo")
                ok = True
            if not ok:
                self.console.log("CUT: sem speed (ou stack_depth em inimigo)")
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
        sw, sh = self.screen.get_width(), self.screen.get_height()
        shift = self.corruption.get_color_shift() # (R, G, B)
        intensity = sum(shift) // 3

        # Efeito de corrupção no fundo
        bg_r = min(255, 10 + shift[0])
        bg_g = min(255, 10 + shift[1])
        bg_b = min(255, 15 + shift[2])
        self.screen.fill((bg_r, bg_g, bg_b))

        grid_color = (0, max(50, 180 - intensity), max(50, 200 - intensity))
        if intensity > 60:
            grid_color = (min(255, 100 + intensity * 2), 0, 50)

        grid_size = 50
        offset_grid = (pygame.time.get_ticks() // 50) % 5 if intensity > 90 else 0

        for x in range(-offset_grid, sw, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, sh), 1)
        for y in range(-offset_grid, sh, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (sw, y), 1)

        # Aplicar Glitch de Deslocamento Global sem criar nova Surface
        draw_target = self.screen
        glitch_off = (0, 0)
        if self.corruption.glitch_active:
            glitch_off = self.corruption.glitch_offset
            # Desenha tudo com um pequeno offset na tela principal
            # (Simplificado: apenas movemos o ponto de renderização das entidades)

        # Renderizar entidades (passando offset se necessário)
        for e in self.loop.entities:
            # Salvamos posição original para aplicar offset temporário
            orig_x = e.properties.get("x", 0)
            orig_y = e.properties.get("y", 0)
            e.properties["x"] = orig_x + glitch_off[0]
            e.properties["y"] = orig_y + glitch_off[1]
            e.render(self.screen)
            e.properties["x"] = orig_x
            e.properties["y"] = orig_y

        self.hud.draw_aim_link(self.screen, self.player, self.selected)

        if self.selected:
            self.hud.draw_selection_ring(self.screen, self.selected)

        if self.laser_frames > 0 and self.selected:
            px = self.player.properties["x"] + self.player.properties.get("w", 40) // 2
            py = self.player.properties["y"] + self.player.properties.get("h", 40) // 2
            sx = self.selected.properties["x"] + self.selected.properties.get("w", 40) // 2
            sy = self.selected.properties["y"] + self.selected.properties.get("h", 40) // 2

            pygame.draw.line(self.screen, self.laser_color, (px, py), (sx, sy), 5)
            self.laser_frames -= 1

        info = get_level_info(self.level_id)
        name = info.name if info else f"Nível {self.level_id}"
        path = info.path_hint if info else "/"
        self.hud.draw(self.screen, self.corruption, name, path)

        peek_cut = (
            self.debugger.peek_cut_key(self.selected) if self.selected else None
        )
        peek_paste = (
            self.debugger.peek_paste_destination(self.selected)
            if self.selected
            else None
        )
        self.hud.draw_debugger_gun_panel(
            self.screen,
            self.player,
            self.selected,
            self.debugger,
            peek_cut,
            peek_paste,
        )

        self.inspector.draw(self.screen, self.selected)
        self.console.draw(self.screen)
        self.code_editor.draw(self.screen)

        # Efeito de Inversão de Cores Esporádico (Nativo, sem numpy)
        if self.corruption.level > 0.8 and self.corruption.glitch_active:
            inv = pygame.Surface((sw, sh))
            inv.fill((255, 255, 255))
            self.screen.blit(inv, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

        pygame.display.flip()

    def _apply_corruption_to_entities(self):
        # Agora delegamos os efeitos ao sistema de corrupção melhorado
        self.corruption.apply_world_effects(self.loop.entities, self.player)

        # Checa se o sistema entrou em colapso total
        if self.corruption.integrity_failure:
            self.console.log("!!! KERNEL PANIC: SISTEMA IRRECUPERÁVEL !!!")
            self.render() # Garante que a mensagem apareça
            pygame.time.delay(2000)
            # Reseta o nível atual
            self.reset_system(self.level_id, carry_corruption=0.0)
            self.console.log("Kernel reiniciado. Estado anterior perdido.")

    def _check_objectives(self):
        exit_node = None
        hostiles_patched = True
        
        for e in self.loop.entities:
            if e.properties.get("tipo") == "TERMINAL_EXIT":
                exit_node = e
            elif e.debug_label() == "NullPointer":
                if e.properties.get("reference") is None:
                    hostiles_patched = False
            elif e.debug_label() == "InfiniteLoop":
                sp = e.properties.get("speed", 1)
                if sp is not None and sp > 0:
                    hostiles_patched = False
            elif e.debug_label() == "StackOverflow":
                depth = e.properties.get("stack_depth", 1)
                if depth is not None and depth > 1:
                    hostiles_patched = False

        if exit_node:
            exit_node.properties["active"] = hostiles_patched
            
            # Checar colisão com saída ativa
            px, py = self.player.properties["x"], self.player.properties["y"]
            pw, ph = self.player.properties.get("w", 40), self.player.properties.get("h", 40)
            ex, ey = exit_node.properties["x"], exit_node.properties["y"]
            ew, eh = exit_node.properties["w"], exit_node.properties["h"]
            
            if hostiles_patched and px < ex + ew and px + pw > ex and py < ey + eh and py + ph > ey:
                self.console.log("SISTEMA RESTAURADO. AVANÇANDO...")
                pygame.time.delay(1000)
                next_level = self.level_id + 1
                if next_level > 3:
                    next_level = 1
                curr_corruption = self.corruption.level
                save_state(curr_corruption, next_level)
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

                level = menus.show_level_selection(self)
                if level is False:
                    pygame.quit()
                    return
                if level is not None:
                    self.level_id = level
                    self.reset_system(self.level_id, carry_corruption=0.0)
                    self.console.log(f"Fase {self.level_id} montada.")
                    in_menu = False

            running = True
            self.audio.play_music("level")

            while running:
                self.clock.tick(FPS)
                self.corruption.update_frame_glitch()
                self.audio.update_volume(self.corruption.level)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode(
                            (event.w, event.h), pygame.RESIZABLE
                        )
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.select_entity(event.pos)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pause_action = menus.show_pause_menu(self)
                            if pause_action == "quit":
                                pygame.quit()
                                return
                            if pause_action == "menu":
                                running = False
                            elif pause_action == "save_quit":
                                save_state(self.corruption.level, self.level_id)
                                pygame.quit()
                                return
                        else:
                            self.handle_debug_keys(event)

                if not running:
                    break

                if not self.code_editor.active:
                    self.loop.update()
                    self._apply_corruption_to_entities()
                    self._check_objectives()
                    self._clamp_entities()
                    self._corruption_from_hostiles()
                
                self.render()
