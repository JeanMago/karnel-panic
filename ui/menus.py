import pygame

from config import FPS


def show_menu(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 60, bold=True)
    font_item = pygame.font.SysFont("monospace", 30)

    options = ["Iniciar Sistema", "Manual (Como Jogar)", "Sair"]
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
            if event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen = game.screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        return "start"
                    if selected_idx == 1:
                        return "tutorial"
                    if selected_idx == 2:
                        return "quit"
        clock.tick(FPS)


def show_tutorial(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_text = pygame.font.SysFont("monospace", 18)

    tutorial_lines = [
        "--- MANUAL DE OPERAÇÃO DA DEBUGGER GUN ---",
        "",
        "ALERTA: O sistema principal (The Heap) está falhando!",
        "Evite que processos corrompidos encostem em você.",
        "",
        "MOVIMENTAÇÃO: W, A, S, D",
        "",
        "DEBUG:",
        "  MOUSE: selecionar entidade (painel direito + feixe)",
        "  [ TAB ] alterna clipboard A / B (dois valores ao mesmo tempo)",
        "  [ I ] dump  |  [ X ] CUT speed  |  [ T ] CUT token (só Player)",
        "  [ V ] PASTE no alvo  |  [ P ] PATCH automático",
        "",
        "Troca de velocidade: slot A = CUT speed do inimigo, slot B = CUT a sua,",
        "depois cole cada um no outro com TAB para escolher o slot antes do V.",
        "",
        "NullPointer: invisível até referência (token+paste ou PATCH).",
        "InfiniteLoop / StackOverflow: veja painel de propriedades.",
        "",
        "ESC — voltar.",
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
            if event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen = game.screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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
            if event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen = game.screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
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
            if event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                screen = game.screen
                overlay = pygame.Surface((screen.get_width(), screen.get_height()))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
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
