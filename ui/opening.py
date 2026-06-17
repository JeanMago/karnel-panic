import pygame
import math
import random
from config import FPS, WIDTH, HEIGHT

def show_opening_crawl(game):
    """
    Exibe a sequência de abertura do jogo, incluindo logs de boot simulados e um alerta crítico.
    
    Funcionamento:
    1. Fase de Boot: Exibe uma série de mensagens de log como se o sistema estivesse inicializando.
       Usa um efeito de digitação (char por char) para cada linha.
    2. Alerta Crítico: Pisca uma tela vermelha com uma mensagem de intrusão para criar tensão.
    3. Confirmação: Mostra uma tela final pedindo ao jogador para confirmar o início ('Y').
    """
    screen = game.screen
    clock = game.clock
    
    # 1. FASE DE BOOT (Cinemática)
    # Lista de mensagens que simulam a inicialização de um Kernel
    boot_logs = [
        "> INITIALIZING KERNEL_LOADER...",
        "> CHECKING MEMORY INTEGRITY... [OK]",
        "> LOADING SECURITY_PROTOCOLS... [FAIL]",
        "> WARNING: UNKNOWN PROCESS DETECTED: 'Sentinel_Alpha.err'",
        "> SYSTEM CORRUPTION DETECTED AT 15.4%",
        "> URGENT: MANUAL INTERVENTION REQUIRED.",
        "> DEPLOYING SENTINEL.EXE..."
    ]
    
    font = pygame.font.SysFont("monospace", 18)
    lines_to_draw = []
    
    # Animação de logs surgindo gradualmente (efeito typewriter)
    for log in boot_logs:
        for i in range(len(log) + 1):
            screen.fill((5, 5, 10))
            # Redesenha as linhas que já foram completadas
            for idx, line in enumerate(lines_to_draw):
                txt = font.render(line, True, (0, 255, 0))
                screen.blit(txt, (40, 100 + idx * 25))
            
            # Desenha a linha atual sendo "digitada" com um cursor '_'
            current_txt = font.render(log[:i] + "_", True, (200, 255, 200))
            screen.blit(current_txt, (40, 100 + len(lines_to_draw) * 25))
            
            pygame.display.flip()
            pygame.time.delay(20)
            
            # Permite que o usuário feche o jogo ou interrompa a animação (se implementado)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: break
        lines_to_draw.append(log)
        pygame.time.delay(200)

    pygame.time.delay(1000)

    # 2. ALERTA CRÍTICO
    # Efeito visual de alerta piscante em vermelho
    alert_font = pygame.font.SysFont("monospace", 40, bold=True)
    for _ in range(3):
        screen.fill((50, 0, 0)) # Fundo vermelho escuro
        txt = alert_font.render("!!! INTRUSÃO DETECTADA !!!", True, (255, 255, 255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 20))
        pygame.display.flip()
        pygame.time.delay(200)
        screen.fill((5, 5, 10)) # Volta para o fundo escuro
        pygame.display.flip()
        pygame.time.delay(200)

    # 3. CONFIRMAÇÃO PARA COMEÇAR
    # Aguarda a entrada do jogador ('Y') para prosseguir para o jogo
    while True:
        screen.fill((5, 5, 10))
        # Grade de fundo sutil para estilo "cyber"
        for x in range(0, WIDTH, 50): pygame.draw.line(screen, (10, 20, 10), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50): pygame.draw.line(screen, (10, 20, 10), (0, y), (WIDTH, y))

        t1 = alert_font.render("INICIALIZAR KERNEL?", True, (0, 255, 255))
        t2 = font.render("O RIVAL 'SENTINEL_ALPHA' JÁ ESTÁ NO SISTEMA.", True, (200, 200, 200))
        t3 = alert_font.render("[ PRESSIONE 'Y' PARA CONFIRMAR ]", True, (255, 255, 0))
        
        # Efeito de pulso (transparência variável) no texto de confirmação
        alpha = 155 + math.sin(pygame.time.get_ticks() * 0.01) * 100
        t3.set_alpha(int(alpha))

        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//3))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 80))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y: return # Inicia o jogo
                if event.key == pygame.K_ESCAPE: return False # Volta ou cancela
        clock.tick(FPS)

