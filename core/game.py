import pygame

from config import WIDTH, HEIGHT, FPS
from core.loop import GameLoop
from core.corruption import CorruptionSystem
from core.levels import build_level, get_level_info

from mechanics.debugger_gun import DebuggerGun
from ui.inspector import Inspector
from ui.console import Console
from ui.hud import HUD
from ui import menus

from persistence.storage import load_state, save_state


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Kernel.panic()")

        self.clock = pygame.time.Clock()
        self.laser_color = (255, 255, 255)
        self.level_id = 1
        self.saved = load_state()
        self.reset_system(self.saved.get("level", 1))

    def reset_system(self, level_id: int):
        self.level_id = int(level_id)
        self.loop = GameLoop()
        self.corruption = CorruptionSystem()
        self.corruption.level = float(self.saved.get("corruption", 0.0))

        self.debugger = DebuggerGun(self.corruption)
        self.inspector = Inspector()
        self.console = Console()
        self.hud = HUD()

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
                self.corruption.increase(0.005)

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
        shift = self.corruption.get_color_shift()

        bg_color = min(255, 10 + shift)
        self.screen.fill((bg_color, 10, 15))

        grid_color = (0, max(50, 180 - shift), max(50, 200 - shift))
        if shift > 60:
            grid_color = (min(255, 100 + shift * 2), 0, 50)

        grid_size = 50
        offset = (pygame.time.get_ticks() // 50) % 5 if shift > 90 else 0

        for x in range(-offset, sw, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, sh), 1)
        for y in range(-offset, sh, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (sw, y), 1)

        self.loop.render(self.screen)

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

        pygame.display.flip()

    def run(self):
        while True:
            self.saved = load_state()
            self.reset_system(self.saved.get("level", 1))
            in_menu = True
            while in_menu:
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
                    self.reset_system(self.level_id)
                    self.console.log(f"Fase {self.level_id} montada.")
                    in_menu = False

            running = True

            while running:
                self.clock.tick(FPS)

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

                self.loop.update()
                self._clamp_entities()
                self._corruption_from_hostiles()
                self.render()
