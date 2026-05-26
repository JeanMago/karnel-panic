import pygame

from config import FPS, RESOLUTIONS
from persistence.storage import save_settings


def show_menu(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 60, bold=True)
    font_item = pygame.font.SysFont("monospace", 30)

    options = ["Iniciar Sistema", "Configurações", "Manual (Como Jogar)", "Sair"]
    selected_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Kernel.panic()", True, (0, 255, 0))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 4))

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
            text = f"> {option} <" if i == selected_idx else f"  {option}  "
            item_surf = font_item.render(text, True, color)
            screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        return "start"
                    if selected_idx == 1:
                        return "settings"
                    if selected_idx == 2:
                        return "tutorial"
                    if selected_idx == 3:
                        return "quit"
        clock.tick(FPS)


def show_settings(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_item = pygame.font.SysFont("monospace", 26)

    # State local para o menu
    res_idx = 0
    for i, res in enumerate(RESOLUTIONS):
        if res == (game.width, game.height):
            res_idx = i
            break
    
    limit_fps = game.limit_fps
    
    # 0: Resolução, 1: Limite FPS, 2: Salvar e Voltar
    menu_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 15, 20))

        title_surf = font_title.render("CONFIGURAÇÕES", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 60))

        # Opção 1: Resolução
        res_text = f"Resolução: < {RESOLUTIONS[res_idx][0]}x{RESOLUTIONS[res_idx][1]} >"
        res_col = (0, 255, 0) if menu_idx == 0 else (150, 150, 150)
        res_surf = font_item.render(res_text, True, res_col)
        screen.blit(res_surf, (sw // 2 - res_surf.get_width() // 2, 200))

        # Opção 2: FPS
        fps_status = "LIGADO (60)" if limit_fps else "DESLIGADO (ILIMITADO)"
        fps_text = f"Limite de FPS: {fps_status}"
        fps_col = (0, 255, 0) if menu_idx == 1 else (150, 150, 150)
        fps_surf = font_item.render(fps_text, True, fps_col)
        screen.blit(fps_surf, (sw // 2 - fps_surf.get_width() // 2, 280))

        # Opção 3: Salvar
        save_col = (0, 255, 0) if menu_idx == 2 else (150, 150, 150)
        save_surf = font_item.render("[ SALVAR E VOLTAR ]", True, save_col)
        screen.blit(save_surf, (sw // 2 - save_surf.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % 3
                elif event.key == pygame.K_LEFT:
                    if menu_idx == 0:
                        res_idx = (res_idx - 1) % len(RESOLUTIONS)
                elif event.key == pygame.K_RIGHT:
                    if menu_idx == 0:
                        res_idx = (res_idx + 1) % len(RESOLUTIONS)
                elif event.key == pygame.K_RETURN:
                    if menu_idx == 0:
                        # Enter na resolução também pode avançar
                        res_idx = (res_idx + 1) % len(RESOLUTIONS)
                    elif menu_idx == 1:
                        limit_fps = not limit_fps
                    elif menu_idx == 2:
                        # Aplicar e Salvar
                        new_w, new_h = RESOLUTIONS[res_idx]
                        old_w, old_h = game.width, game.height
                        
                        game.width = new_w
                        game.height = new_h
                        game.limit_fps = limit_fps
                        save_settings(new_w, new_h, limit_fps)
                        
                        # Se a resolução mudou, resetamos o subsistema de vídeo para evitar erro de renderer
                        if (new_w, new_h) != (old_w, old_h):
                            pygame.display.quit()
                            pygame.display.init()
                            game.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE | pygame.SCALED)
                            pygame.display.set_caption("Kernel.panic()")
                            # Atualiza a referência local da tela no menu
                            screen = game.screen
                        return
                elif event.key == pygame.K_ESCAPE:
                    return
        clock.tick(FPS)


def show_tutorial(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_text = pygame.font.SysFont("monospace", 18)

    tutorial_lines = [
        "--- MANUAL DE OPERAÇÃO DA DEBUGGER GUN ---",
        "",
        "SISTEMA: A Integridade do Kernel está comprometida.",
        "Corrupção aumenta ao usar ferramentas e ao contato com falhas.",
        "",
        "CONTROLES BÁSICOS:",
        "  [ W,A,S,D ] Movimentação de baixo nível",
        "  [ MOUSE ] Selecionar Objeto / Inspecionar Memória",
        "",
        "DEBUGGER GUN (CLIPBOARD):",
        "  [ TAB ] Alterna entre Slot A e B",
        "  [ X ] CUT (Recortar valor da propriedade)",
        "  [ V ] PASTE (Colar valor no alvo selecionado)",
        "  [ P ] SMART PATCH (Auto-reparo sugerido)",
        "",
        "PATCH POR CÓDIGO [ TECLA C ]:",
        "  Abre o console de injeção direta. Exemplos:",
        "  - speed = 10         (Atribuição)",
        "  - speed += 2         (Incremento)",
        "  - if speed == 0: speed = 5 (Condicional)",
        "",
        "SISTEMA DE CORRUPÇÃO:",
        "  - Quanto maior o nível, mais o sistema falha.",
        "  - Efeitos: Glitches visuais, instabilidade física.",
        "  - Se chegar a 100%, ocorre o KERNEL PANIC (Fim de Jogo).",
        "",
        "ESC — Voltar ao menu.",
    ]

    while True:
        sw = screen.get_width()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Manual do Sistema", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 40))

        for i, line in enumerate(tutorial_lines):
            color = (200, 200, 200)
            if line.startswith("  [") or line.startswith("  MOUSE"):
                color = (0, 255, 0)
            if "---" in line:
                color = (255, 255, 0)
            text_surf = font_text.render(line, True, color)
            screen.blit(text_surf, (40, 100 + i * 24))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    return True
        clock.tick(FPS)


def show_level_selection(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_item = pygame.font.SysFont("monospace", 26)

    levels = [
        "Fase 1: The Heap",
        "Fase 2: Stack / Loop",
        "Fase 3: Kernel Panic",
    ]
    selected_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Seleção de Sistema", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 6))

        for i, level in enumerate(levels):
            color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
            text = f"> {level} <" if i == selected_idx else f"  {level}  "
            item_surf = font_item.render(text, True, color)
            screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 - 40 + i * 48))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(levels)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(levels)
                elif event.key == pygame.K_RETURN:
                    return selected_idx + 1
                elif event.key == pygame.K_ESCAPE:
                    return None
        clock.tick(FPS)


def show_pause_menu(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 50, bold=True)
    font_item = pygame.font.SysFont("monospace", 30)

    options = ["Retomar Execução", "Voltar ao Menu Principal", "Salvar e Sair"]
    selected_idx = 0

    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.blit(overlay, (0, 0))

        title_surf = font_title.render("SISTEMA PAUSADO", True, (255, 100, 100))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 3))

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
            text = f"> {option} <" if i == selected_idx else f"  {option}  "
            item_surf = font_item.render(text, True, color)
            screen.blit(item_surf, (sw // 2 - item_surf.get_width() // 2, sh // 2 + i * 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        return "resume"
                    if selected_idx == 1:
                        return "menu"
                    if selected_idx == 2:
                        return "save_quit"
                elif event.key == pygame.K_ESCAPE:
                    return "resume"
        clock.tick(FPS)
