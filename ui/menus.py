import pygame

from config import FPS, RESOLUTIONS
from persistence.storage import save_settings, load_state


def show_menu(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 60, bold=True)
    font_item = pygame.font.SysFont("monospace", 30)

    options = ["Novo Jogo", "Seleção de Fases", "Configurações", "Manual (Como Jogar)", "Sair"]
    selected_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Kernel.panic()", True, (0, 255, 0))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 5))

        option_rects = []
        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
            text = f"> {option} <" if i == selected_idx else f"  {option}  "
            item_surf = font_item.render(text, True, color)
            x = sw // 2 - item_surf.get_width() // 2
            y = sh // 2 - 50 + i * 50
            screen.blit(item_surf, (x, y))
            option_rects.append(pygame.Rect(x, y, item_surf.get_width(), item_surf.get_height()))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_idx = i

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(event.pos):
                            selected_idx = i
                            if i == 0: # Novo Jogo
                                if confirm_new_game(game): return "start"
                            if i == 1: return "select_level"
                            if i == 2: return "settings"
                            if i == 3: return "tutorial"
                            if i == 4: return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        if confirm_new_game(game): return "start"
                    if selected_idx == 1: return "select_level"
                    if selected_idx == 2: return "settings"
                    if selected_idx == 3: return "tutorial"
                    if selected_idx == 4: return "quit"
        clock.tick(FPS)

def confirm_new_game(game):
    """Tela de confirmação para não apagar o save sem querer."""
    screen = game.screen
    clock = game.clock
    font = pygame.font.SysFont("monospace", 24)
    
    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((20, 10, 10)) # Fundo avermelhado de alerta
        
        msg = font.render("INICIAR NOVO SISTEMA? O PROGRESSO ATUAL SERÁ PERDIDO.", True, (255, 255, 255))
        screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 3))
        
        # Opções: SIM ou NÃO
        opts = ["[S] SIM, REINICIAR", "[N] NÃO, VOLTAR"]
        for i, opt in enumerate(opts):
            col = (255, 100, 100) if i == 0 else (100, 255, 100)
            surf = font.render(opt, True, col)
            screen.blit(surf, (sw // 2 - surf.get_width() // 2, sh // 2 + i * 40))
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); import sys; sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: return True
                if event.key == pygame.K_n or event.key == pygame.K_ESCAPE: return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Simplificado: clique na metade de cima da tela confirma, baixo cancela
                if event.pos[1] > sh // 2: return False
                else: return True
        clock.tick(FPS)


def show_settings(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_item = pygame.font.SysFont("monospace", 26)

    res_idx = 0
    for i, res in enumerate(RESOLUTIONS):
        if res == (game.width, game.height):
            res_idx = i
            break
    
    limit_fps = game.limit_fps
    menu_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 15, 20))

        title_surf = font_title.render("CONFIGURAÇÕES", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 60))

        item_rects = []

        # Opção 1: Resolução
        res_text = f"Resolução: < {RESOLUTIONS[res_idx][0]}x{RESOLUTIONS[res_idx][1]} >"
        res_col = (0, 255, 0) if menu_idx == 0 else (150, 150, 150)
        res_surf = font_item.render(res_text, True, res_col)
        rx, ry = sw // 2 - res_surf.get_width() // 2, 200
        screen.blit(res_surf, (rx, ry))
        item_rects.append(pygame.Rect(rx, ry, res_surf.get_width(), res_surf.get_height()))

        # Opção 2: FPS
        fps_status = "LIGADO (60)" if limit_fps else "DESLIGADO (ILIMITADO)"
        fps_text = f"Limite de FPS: {fps_status}"
        fps_col = (0, 255, 0) if menu_idx == 1 else (150, 150, 150)
        fps_surf = font_item.render(fps_text, True, fps_col)
        fx, fy = sw // 2 - fps_surf.get_width() // 2, 280
        screen.blit(fps_surf, (fx, fy))
        item_rects.append(pygame.Rect(fx, fy, fps_surf.get_width(), fps_surf.get_height()))

        # Opção 3: Salvar
        save_col = (0, 255, 0) if menu_idx == 2 else (150, 150, 150)
        save_surf = font_item.render("[ SALVAR E VOLTAR ]", True, save_col)
        sx, sy = sw // 2 - save_surf.get_width() // 2, 400
        screen.blit(save_surf, (sx, sy))
        item_rects.append(pygame.Rect(sx, sy, save_surf.get_width(), save_surf.get_height()))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(event.pos):
                        menu_idx = i

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(item_rects):
                        if rect.collidepoint(event.pos):
                            menu_idx = i
                            if i == 0:
                                res_idx = (res_idx + 1) % len(RESOLUTIONS)
                            elif i == 1:
                                limit_fps = not limit_fps
                            elif i == 2:
                                # Salvar
                                new_w, new_h = RESOLUTIONS[res_idx]
                                old_w, old_h = game.width, game.height
                                game.width, game.height = new_w, new_h
                                game.limit_fps = limit_fps
                                save_settings(new_w, new_h, limit_fps)
                                if (new_w, new_h) != (old_w, old_h):
                                    pygame.display.quit()
                                    pygame.display.init()
                                    game.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE | pygame.SCALED)
                                    pygame.display.set_caption("Kernel.panic()")
                                    screen = game.screen
                                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    menu_idx = (menu_idx - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_idx = (menu_idx + 1) % 3
                elif event.key == pygame.K_LEFT:
                    if menu_idx == 0: res_idx = (res_idx - 1) % len(RESOLUTIONS)
                elif event.key == pygame.K_RIGHT:
                    if menu_idx == 0: res_idx = (res_idx + 1) % len(RESOLUTIONS)
                elif event.key == pygame.K_RETURN:
                    if menu_idx == 0: res_idx = (res_idx + 1) % len(RESOLUTIONS)
                    elif menu_idx == 1: limit_fps = not limit_fps
                    elif menu_idx == 2:
                        new_w, new_h = RESOLUTIONS[res_idx]
                        old_w, old_h = game.width, game.height
                        game.width, game.height = new_w, new_h
                        game.limit_fps = limit_fps
                        save_settings(new_w, new_h, limit_fps)
                        if (new_w, new_h) != (old_w, old_h):
                            pygame.display.quit()
                            pygame.display.init()
                            game.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE | pygame.SCALED)
                            pygame.display.set_caption("Kernel.panic()")
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
    font_small = pygame.font.SysFont("monospace", 14)

    pages = [
        # Página 1: O Básico
        [
            "--- CONTROLES: MOVIMENTAÇÃO E SELEÇÃO ---",
            "",
            "Você é um 'Sentinel.exe' encarregado de limpar o Kernel.",
            "O mundo é um labirinto de endereços de memória GIGANTE.",
            "",
            "MOVIMENTO E VISÃO:",
            "  [ W,A,S,D ] Mover pelo sistema.",
            "  [ MOUSE ] Clique em qualquer entidade para focar nela.",
            "  [ CÂMERA ] Ela segue você automaticamente pelo mapa.",
            "",
            "FERRAMENTA DE RECORTE (Debugger Gun):",
            "  [ X ] RECORTE: Copia o valor de uma variável (ex: speed).",
            "  [ V ] COLAR: Aplica o valor no alvo (ex: zerar speed do inimigo).",
            "  [ TAB ] Troca entre Slot A e B (você pode guardar 2 valores).",
            "  [ P ] SMART PATCH: Tenta uma correção automática rápida.",
            "",
            "DICA: Você pode recortar propriedades DE VOCÊ MESMO para usar!"
        ],
        # Página 2: Terminal de Código [C]
        [
            "--- TERMINAL DE CÓDIGO [ TECLA C ] ---",
            "",
            "Se o Recorte/Cola for limitado, use o Terminal para controle total.",
            "Primeiro SELECIONE um alvo com o mouse, depois pressione [C].",
            "",
            "COMANDOS DE ESTABILIZAÇÃO (RECOMENDADOS):",
            "  purge               (Purgar: Remove o erro e ESTABILIZA o sistema)",
            "  chmod -x            (Remove permissão de execução/ataque)",
            "  reboot              (Reinicia entidade para parâmetros seguros)",
            "  silence             (Suspende a hostilidade temporariamente)",
            "  heal                (Restaura integridade/HP em 100%)",
            "",
            "COMANDOS DE MANIPULAÇÃO:",
            "  kill                (Deleta o processo BRUTAMENTE - gera corrupção)",
            "  freeze / unfreeze   (Para ou solta o movimento completamente)",
            "  scan                (Exibe HP, Estado e Variáveis vitais)",
            "  optimize            (Aumenta velocidade em 50%)",
            "  teleport x y        (Move para coordenadas exatas)",
            "",
            "DICA: O comando 'purge' é a forma mais limpa de limpar o sistema."
        ],
        # Página 3: Execução Limpa vs Corrupção
        [
            "--- ESTRATÉGIA: EXECUÇÃO LIMPA ---",
            "",
            "Cada ação no Kernel deixa rastros. Entenda a diferença:",
            "",
            "1. MÉTODO BRUTO (Padrão):",
            "   Usar 'kill', 'teleport' ou sofrer danos aumenta a CORRUPÇÃO.",
            "   Isso causa glitches visuais e instabilidade física no mundo.",
            "",
            "2. EXECUÇÃO LIMPA (Recomendado):",
            "   Use 'purge' no terminal para apagar erros SEM deixar lixo.",
            "   Ações de correção (Smart Patch [P]) em inimigos específicos",
            "   REDUZEM a corrupção total do sistema.",
            "",
            "DICA: Operações em VOCÊ MESMO não geram corrupção.",
            "Ações 'limpas' (verde no manual) ajudam a manter o Kernel estável!"
        ],

        # Página 4: Guia de Erros (Inimigos)
        [
            "--- GUIA DE CAMPO: ELIMINANDO ERROS ---",
            "",
            "Cada erro tem uma falha lógica. Use para neutralizá-los LIMPO:",
            "",
            "1. NullPointer (Vermelho):",
            "   COMO VENCER: Ele é invisível. Recorte [T] o 'token' do Player",
            "   e cole [V] nele. Ele se revelará e parará de atacar.",
            "",
            "2. Buffer Overflow (Laranja):",
            "   COMO VENCER: O 'load' é maior que o 'buffer_size'. Use o",
            "   Smart Patch [P] para alocar mais memória e estabilizá-lo.",
            "",
            "3. Memory Leak (Verde):",
            "   COMO VENCER: Ele drena recursos. Use o Terminal [C] e digite",
            "   'leak_rate = 0' ou use o Smart Patch [P] para estancar o vazamento.",
            "",
            "4. Stack Overflow (Roxo):",
            "   COMO VENCER: Empilha processos. Use Smart Patch [P] para dar",
            "   'pop' na pilha até que ela esvazie.",
            "",
            "5. Infinite Loop (Amarelo):",
            "   COMO VENCER: Gira sem parar. Use o Terminal [C] para setar",
            "   'speed = 2' (reduzir velocidade) ou use Smart Patch [P]."
        ],
        # Página 5: Estratégia contra Bosses
        [
            "--- PROTOCOLO DE COMBATE: BOSSES ---",
            "",
            "Chefes são processos protegidos. 'Kill' e 'Purge' NÃO funcionam.",
            "Você deve esgotar o HP (Integridade) deles usando LÓGICA:",
            "",
            "A) LOGIC BURST [ TECLA P ]:",
            "   Envia um pulso de correção massiva. -50 HP por acerto.",
            "   Gera corrupção em Bosses comuns, mas é vital contra o Core.",
            "",
            "B) DATA INJECTION [ TECLA V ]:",
            "   Copie valores (ex: speed de 10) e cole neles.",
            "   A discrepância de dados causa -20 HP ou mais.",
            "",
            "C) SABOTAGEM DE TERMINAL [ TECLA C ]:",
            "   Mude variáveis em tempo real (ex: 'speed = 0').",
            "   Pode paralisar o Boss para você atacar com segurança.",
            "",
            "DICA: O comando 'scan' no terminal revela o HP atual do Boss."
        ],
        # Página 6: Setores do Kernel (Fases)
        [
            "--- MAPEAMENTO DOS SETORES (FASES) ---",
            "",
            "Cada setor é governado por um Processo Mestre (Boss).",
            "A Saída [TERMINAL_EXIT] só abre após derrotar o Boss local.",
            "",
            "SETOR 1-3 (NÚCLEO):",
            "   Ambientes simples para testar sua Debugger Gun.",
            "SETOR 4 (DEADLOCK FOREST):",
            "   Navegação difícil. Erros Deadlock drenam sua velocidade.",
            "SETOR 5-6 (INFRAESTRUTURA):",
            "   Fases complexas com defesas de rede e loops massivos.",
            "SETOR 7 (CLOUD SYNC):",
            "   A sincronização final. O Kernel está em colapso total.",
            "",
            "DICA: Derrotar o Boss do setor REDUZ sua corrupção atual!"
        ],
        # Página 7: Integridade e Morte
        [
            "--- INTEGRIDADE E KERNEL PANIC ---",
            "",
            "MANTENHA-SE OPERAÇÃO OU O SISTEMA IRÁ REINICIAR:",
            "",
            "HP (INTEGRIDADE):",
            "- Cair para 0 HP resulta em falha crítica do Sentinel.",
            "- Inimigos tiram 10 HP. Bosses tiram 25 HP.",
            "",
            "CORRUPÇÃO (INSTABILIDADE):",
            "- Atingir 100% de Corrupção causa um KERNEL PANIC.",
            "- O sistema se torna ilegível e reinicia o setor.",
            "",
            "RECUPERAÇÃO:",
            "- Use o comando 'heal' no terminal (em você mesmo) para 100% HP.",
            "- Use o comando 'purge' em inimigos comuns para reduzir corrupção.",
            "- Vença Bosses para uma limpeza profunda do Kernel."
        ],
        # Página 8: Vulnerabilidades Críticas (BOSSES)
        [
            "--- GUIA DE VULNERABILIDADES: BOSSES ---",
            "",
            "1. NULL_MASTER (Fase 1, 4):",
            "   - STUN LÓGICO: Sete 'speed = 0' no terminal.",
            "   - ERRO CROMÁTICO: Use o comando 'invert' no terminal.",
            "     A inversão de cores causa choque de renderização.",
            "",
            "2. RECURSIVE_OVERLORD (Fase 2, 5):",
            "   - SABOTAGEM DE CARGA: Reduza o 'load' para menos de 50.",
            "   - OVERCLOCK FATAL: Sete 'speed = 20' no terminal.",
            "     O excesso de ciclos causa superaquecimento e dano.",
            "",
            "3. CORE_KERNEL_PANIC (Fase 3, 6, 7):",
            "   - SMART PATCHING: Use o Patch [P] repetidamente.",
            "   - CONFLITO DE IDENTIDADE: Recorte [T] seu 'token' e cole",
            "     no núcleo [V]. Ele entrará em colapso de permissão.",
            "",
            "DICA: O manual mostra como vencer, mas sua habilidade define o sucesso!"
        ],
        # Página 9: Táticas de Elite (Resumo)
        [
            "--- RESUMO DE TÁTICAS DE ELITE ---",
            "",
            "COMO SER UM SENTINELA DE ELITE (0% CORRUPÇÃO):",
            "",
            "1. PRIORIZE O TERMINAL:",
            "   O comando 'purge' é seu melhor amigo. Use-o sempre.",
            "",
            "2. CHMOD -X É PODEROSO:",
            "   Não quer deletar? Tire a permissão de execução do inimigo.",
            "   Ele ficará inofensivo e o sistema continuará estável.",
            "",
            "3. USE O SCAN:",
            "   Sempre use 'scan' em novos alvos para ver quais variáveis",
            "   você pode manipular sem adivinhar.",
            "",
            "4. CUIDE DE VOCÊ:",
            "   Recortar de você mesmo (speed, token) nunca gera corrupção.",
            "",
            "SISTEMA PRONTO. SENTINEL.EXE EM EXECUÇÃO..."
        ]
    ]
    
    current_page = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        titles = [
            "1. Controles", 
            "2. Terminal", 
            "3. Execução Limpa",
            "4. Guia de Erros", 
            "5. Estratégia Boss",
            "6. Setores",
            "7. Objetivos",
            "8. Fraquezas Boss",
            "9. Táticas Elite"
        ]
        title_surf = font_title.render(titles[current_page], True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 40))

        # Desenhar conteúdo da página
        for i, line in enumerate(pages[current_page]):
            color = (200, 200, 200)
            if line.startswith("  [") or line.startswith("  MOUSE") or "SOLUÇÃO:" in line or "COMO VENCER:" in line:
                color = (0, 255, 0)
            if "---" in line or (line and line[0].isdigit()):
                color = (255, 255, 0)
            if "=" in line or "kill" in line or "freeze" in line or "teleport" in line or "LOGIC BURST" in line or "PATCH" in line:
                color = (0, 200, 255) # Cor de código/comando
                
            text_surf = font_text.render(line, True, color)
            screen.blit(text_surf, (40, 100 + i * 24))

        # Rodapé de navegação
        nav_text = f"Página {current_page + 1} de {len(pages)}  |  [<- / ->] Mudar Aba  |  [ESC] Voltar"
        nav_surf = font_small.render(nav_text, True, (100, 100, 100))
        screen.blit(nav_surf, (sw // 2 - nav_surf.get_width() // 2, sh - 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Clique para avançar
                    current_page = (current_page + 1) % len(pages)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key == pygame.K_LEFT:
                    current_page = (current_page - 1) % len(pages)
                elif event.key == pygame.K_RIGHT:
                    current_page = (current_page + 1) % len(pages)
                elif event.key == pygame.K_ESCAPE:
                    return True
        clock.tick(FPS)


def show_level_selection(game):
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_item = pygame.font.SysFont("monospace", 26)

    # Carrega o progresso salvo
    state = load_state()
    max_level = int(state.get("max_level", 1))

    levels = [
        "Fase 1: The Heap",
        "Fase 2: Stack Overflow",
        "Fase 3: Kernel Panic",
        "Fase 4: Deadlock Forest",
        "Fase 5: Registry Hive",
        "Fase 6: Firewall Gate",
        "Fase 7: Cloud Sync",
    ]
    selected_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Seleção de Sistema", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 6))

        level_rects = []
        for i, level in enumerate(levels):
            is_locked = (i + 1) > max_level
            
            if is_locked:
                color = (40, 40, 40)
                display_text = f"[ BLOQUEADO ]"
            else:
                color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
                display_text = f"> {level} <" if i == selected_idx else f"  {level}  "
            
            item_surf = font_item.render(display_text, True, color)
            x, y = sw // 2 - item_surf.get_width() // 2, sh // 2 - 40 + i * 48
            screen.blit(item_surf, (x, y))
            
            # Guardamos se está bloqueado junto com o retângulo
            rect = pygame.Rect(x, y, item_surf.get_width(), item_surf.get_height())
            level_rects.append((rect, is_locked))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEMOTION:
                for i, (rect, locked) in enumerate(level_rects):
                    if rect.collidepoint(event.pos) and not locked:
                        selected_idx = i

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, (rect, locked) in enumerate(level_rects):
                        if rect.collidepoint(event.pos) and not locked:
                            return i + 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    # Pula bloqueados ao subir
                    selected_idx = (selected_idx - 1) % len(levels)
                    while (selected_idx + 1) > max_level:
                        selected_idx = (selected_idx - 1) % len(levels)
                elif event.key == pygame.K_DOWN:
                    # Pula bloqueados ao descer
                    selected_idx = (selected_idx + 1) % len(levels)
                    if (selected_idx + 1) > max_level:
                        selected_idx = 0
                elif event.key == pygame.K_RETURN:
                    if (selected_idx + 1) <= max_level:
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

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        title_surf = font_title.render("SISTEMA PAUSADO", True, (255, 100, 100))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 3))

        option_rects = []
        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
            text = f"> {option} <" if i == selected_idx else f"  {option}  "
            item_surf = font_item.render(text, True, color)
            x, y = sw // 2 - item_surf.get_width() // 2, sh // 2 + i * 50
            screen.blit(item_surf, (x, y))
            option_rects.append(pygame.Rect(x, y, item_surf.get_width(), item_surf.get_height()))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_idx = i

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(event.pos):
                            if i == 0: return "resume"
                            if i == 1: return "menu"
                            if i == 2: return "save_quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    game.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0: return "resume"
                    if selected_idx == 1: return "menu"
                    if selected_idx == 2: return "save_quit"
                elif event.key == pygame.K_ESCAPE:
                    return "resume"
        clock.tick(FPS)
