import pygame
import math
from config import FPS, WIDTH, HEIGHT

def show_opening_crawl(game):
    screen = game.screen
    clock = game.clock
    
    # Texto da história
    story_text = [
        "KERNEL.PANIC(2026)",
        "",
        "Episódio I",
        "A GRANDE CORRUPÇÃO",
        "",
        "O sistema está em colapso.",
        "Arquivos vitais foram perdidos",
        "no abismo do Heap.",
        "",
        "Como um processo sentinela,",
        "você deve navegar pelos",
        "setores corrompidos e",
        "restaurar a ordem binária.",
        "",
        "Armado com a DEBUGGER GUN,",
        "você tem o poder de",
        "reescrever a realidade.",
        "",
        "Mas cuidado: cada patch",
        "aplicado consome sua própria",
        "integridade...",
        "",
        "O Kernel espera.",
        "O tempo está acabando."
    ]

    font = pygame.font.SysFont("monospace", 32, bold=True)
    
    # Preparar superfícies de texto para renderização mais rápida
    text_surfaces = []
    for line in story_text:
        surf = font.render(line, True, (255, 220, 0)) # Amarelo clássico
        text_surfaces.append(surf)

    # Variáveis de animação
    scroll_y = float(HEIGHT)
    base_speed = 1.0
    
    running = True
    while running:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((0, 0, 0)) # Fundo preto profundo

        # Acelerar abertura ao segurar Espaço ou Clique
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        if keys[pygame.K_SPACE] or mouse_buttons[0]:
            scroll_speed = base_speed * 4.0
        else:
            scroll_speed = base_speed

        # Desenhar estrelas estáticas (simples)
        random_stars = [(int(sw * 0.1), int(sh * 0.2)), (int(sw * 0.8), int(sh * 0.5)), 
                        (int(sw * 0.4), int(sh * 0.8)), (int(sw * 0.7), int(sh * 0.1))]
        for star in random_stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 1)

        # Renderizar o texto com efeito de perspectiva (simulado)
        curr_y = scroll_y
        for i, surf in enumerate(text_surfaces):
            if -100 < curr_y < sh + 100:
                progresso = curr_y / sh
                escala = 0.4 + (max(0, progresso) * 0.6)
                if escala > 0:
                    scaled_w = int(surf.get_width() * escala)
                    scaled_h = int(surf.get_height() * escala)
                    if scaled_w > 0 and scaled_h > 0:
                        scaled_surf = pygame.transform.scale(surf, (scaled_w, scaled_h))
                        screen.blit(scaled_surf, (sw // 2 - scaled_w // 2, curr_y))
            curr_y += 50 * (0.4 + (max(0, curr_y/sh) * 0.6)) # Espaçamento também escalado

        scroll_y -= scroll_speed

        # Se todo o texto sumiu no topo, termina
        if curr_y < -50:
            running = False

        # Instrução na tela
        hint_font = pygame.font.SysFont("monospace", 14)
        hint_surf = hint_font.render("[ESPAÇO/CLIQUE] Acelerar  |  [ESC] Pular", True, (100, 100, 100))
        screen.blit(hint_surf, (sw - hint_surf.get_width() - 10, sh - 25))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        clock.tick(FPS)
