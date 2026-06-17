import pygame
import math
import sys

from config import FPS, RESOLUTIONS
from persistence.storage import save_settings, load_state

# --- FUNÇÕES AUXILIARES DE OTIMIZAÇÃO ---

def _render_menu_options(screen, options, selected_idx, font, y_start, spacing=50):
    """
    Desenha uma lista de opções centralizadas e retorna seus retângulos de colisão.
    """
    sw = screen.get_width()
    rects = []
    for i, option in enumerate(options):
        # Destaque visual para o item selecionado
        is_selected = (i == selected_idx)
        color = (0, 255, 0) if is_selected else (100, 100, 100)
        text = f"> {option} <" if is_selected else f"  {option}  "
        
        surf = font.render(text, True, color)
        x = sw // 2 - surf.get_width() // 2
        y = y_start + i * spacing
        screen.blit(surf, (x, y))
        
        # Armazena o retângulo para detecção de mouse
        rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))
    return rects

def _process_menu_events(events, selected_idx, num_options, rects):
    """
    Trata eventos comuns de navegação (teclado e mouse hover).
    Retorna o novo índice selecionado e um booleano indicando se houve confirmação.
    """
    new_idx = selected_idx
    confirmed = False

    for event in events:
        if event.type == pygame.QUIT:
            return new_idx, "quit"
        
        # Navegação por teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                new_idx = (new_idx - 1) % num_options
            elif event.key == pygame.K_DOWN:
                new_idx = (new_idx + 1) % num_options
            elif event.key == pygame.K_RETURN:
                confirmed = True
        
        # Interação por mouse
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(rects):
                if rect.collidepoint(event.pos):
                    new_idx = i
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(rects):
                if rect.collidepoint(event.pos):
                    new_idx = i
                    confirmed = True
            
    return new_idx, confirmed

# --- TELAS DE MENU ---

def show_menu(game):
    """Exibe o menu principal do jogo otimizado."""
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 60, bold=True)
    font_item = pygame.font.SysFont("monospace", 30)

    options = ["Novo Jogo", "Seleção de Fases", "Tutorial Prático", "Manual do Sistema", "Configurações", "Sair"]
    selected_idx = 0
    rects = []

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Kernel.panic()", True, (0, 255, 0))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 5))

        # Renderização otimizada
        rects = _render_menu_options(screen, options, selected_idx, font_item, sh // 2 - 80)

        pygame.display.flip()

        # Processamento de eventos centralizado
        events = pygame.event.get()
        # Tratamento especial para F11 (Fullscreen) que é global
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                game.toggle_fullscreen()

        selected_idx, action = _process_menu_events(events, selected_idx, len(options), rects)

        if action == "quit": return "quit"
        if action is True: # Confirmado
            if selected_idx == 0:
                if confirm_new_game(game): return "start"
            if selected_idx == 1: return "select_level"
            if selected_idx == 2: return "tutorial_level"
            if selected_idx == 3: return "tutorial"
            if selected_idx == 4: return "settings"
            if selected_idx == 5: return "quit"

        clock.tick(FPS)

def confirm_new_game(game):
    """Tela de confirmação otimizada."""
    screen = game.screen
    clock = game.clock
    font = pygame.font.SysFont("monospace", 24)
    
    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((20, 10, 10))
        
        msg = font.render("INICIAR NOVO SISTEMA? O PROGRESSO ATUAL SERÁ PERDIDO.", True, (255, 255, 255))
        screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 3))
        
        options = ["SIM, REINICIAR", "NÃO, VOLTAR"]
        rects = []
        for i, opt in enumerate(options):
            col = (255, 100, 100) if i == 0 else (100, 255, 100)
            prefix = "[S] " if i == 0 else "[N] "
            surf = font.render(prefix + opt, True, col)
            x, y = sw // 2 - surf.get_width() // 2, sh // 2 + i * 40
            screen.blit(surf, (x, y))
            rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: return True
                if event.key == pygame.K_n or event.key == pygame.K_ESCAPE: return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rects[0].collidepoint(event.pos): return True
                if rects[1].collidepoint(event.pos): return False
        clock.tick(FPS)


def show_settings(game):
    """Tela de configurações otimizada."""
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

        # Opções dinâmicas
        fps_status = "LIGADO (60)" if limit_fps else "DESLIGADO (ILIMITADO)"
        options = [
            f"Resolução: < {RESOLUTIONS[res_idx][0]}x{RESOLUTIONS[res_idx][1]} >",
            f"Limite de FPS: {fps_status}",
            "[ SALVAR E VOLTAR ]"
        ]
        
        rects = _render_menu_options(screen, options, menu_idx, font_item, 200, spacing=80)
        pygame.display.flip()

        events = pygame.event.get()
        menu_idx, action = _process_menu_events(events, menu_idx, len(options), rects)

        if action == "quit": pygame.quit(); sys.exit()

        # Lógica específica para LEFT/RIGHT na resolução
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return
                if menu_idx == 0:
                    if event.key == pygame.K_LEFT: res_idx = (res_idx - 1) % len(RESOLUTIONS)
                    if event.key == pygame.K_RIGHT: res_idx = (res_idx + 1) % len(RESOLUTIONS)

        if action is True:
            if menu_idx == 0:
                res_idx = (res_idx + 1) % len(RESOLUTIONS)
            elif menu_idx == 1:
                limit_fps = not limit_fps
            elif menu_idx == 2:
                # Salvar e aplicar
                new_w, new_h = RESOLUTIONS[res_idx]
                game.width, game.height = new_w, new_h
                game.limit_fps = limit_fps
                save_settings(new_w, new_h, limit_fps)
                pygame.display.quit()
                pygame.display.init()
                game.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE | pygame.SCALED)
                pygame.display.set_caption("Kernel.panic()")
                return
        clock.tick(FPS)


def show_level_selection(game):
    """Seleção de níveis otimizada com bloqueio funcional."""
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_item = pygame.font.SysFont("monospace", 26)

    # Recarrega o estado para garantir que vemos o progresso mais recente
    state = load_state()
    max_level = int(state.get("max_level", 1))

    levels = [f"Fase {i+1}: {name}" for i, name in enumerate([
        "The Heap", "Stack Overflow", "Kernel Panic", "Deadlock Forest", 
        "Registry Hive", "Firewall Gate", "Cloud Sync", "Network Abyss", 
        "Mainframe Core", "Singularity"
    ])]
    selected_idx = 0

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render("Seleção de Sistema", True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, sh // 6))

        # Renderização manual para tratar o estado de bloqueio visualmente
        rects = []
        for i, level in enumerate(levels):
            is_locked = (i + 1) > max_level
            if is_locked:
                color = (40, 40, 40)
                display_text = "[ BLOQUEADO ]"
            else:
                color = (0, 255, 0) if i == selected_idx else (100, 100, 100)
                display_text = f"> {level} <" if i == selected_idx else f"  {level}  "
            
            surf = font_item.render(display_text, True, color)
            x, y = sw // 2 - surf.get_width() // 2, sh // 2 - 40 + i * 48
            screen.blit(surf, (x, y))
            rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))

        pygame.display.flip()

        events = pygame.event.get()
        # Tratamento de eventos customizado para respeitar o max_level
        for event in events:
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11: game.toggle_fullscreen()
                if event.key == pygame.K_ESCAPE: return None
                if event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(levels)
                    while (selected_idx + 1) > max_level:
                        selected_idx = (selected_idx - 1) % len(levels)
                if event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(levels)
                    if (selected_idx + 1) > max_level: selected_idx = 0
                if event.key == pygame.K_RETURN:
                    if (selected_idx + 1) <= max_level: return selected_idx + 1

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos) and (i + 1) <= max_level:
                        selected_idx = i

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos) and (i + 1) <= max_level:
                        return i + 1
            
        clock.tick(FPS)


def show_pause_menu(game):
    """Menu de pausa otimizado."""
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

        rects = _render_menu_options(screen, options, selected_idx, font_item, sh // 2)

        pygame.display.flip()

        events = pygame.event.get()
        selected_idx, action = _process_menu_events(events, selected_idx, len(options), rects)

        if action == "quit": return "quit"
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "resume"

        if action is True:
            if selected_idx == 0: return "resume"
            if selected_idx == 1: return "menu"
            if selected_idx == 2: return "save_quit"

        clock.tick(FPS)


def show_tutorial(game):
    """Mantido funcional, pois é mais uma galeria de imagens/texto que um menu de opções."""
    screen = game.screen
    clock = game.clock
    font_title = pygame.font.SysFont("monospace", 40, bold=True)
    font_text = pygame.font.SysFont("monospace", 18)
    font_small = pygame.font.SysFont("monospace", 14)

    pages = [
        [
            "--- CONTROLES: MOVIMENTAÇÃO E SELEÇÃO ---", "",
            "Você é um 'Sentinel.exe' encarregado de limpar o Kernel.",
            "O mundo é um labirinto de endereços de memória GIGANTE.", "",
            "MOVIMENTO E VISÃO:",
            "  [ W,A,S,D ] Mover pelo sistema.",
            "  [ MOUSE ] Clique em qualquer entidade para focar nela.",
            "  [ CÂMERA ] Ela segue você automaticamente pelo mapa.", "",
            "FERRAMENTA DE RECORTE (Debugger Gun):",
            "  [ X ] RECORTE: Copia o valor de uma variável (ex: speed).",
            "  [ V ] COLAR: Aplica o valor no alvo (ex: zerar speed do inimigo).",
            "  [ TAB ] Troca entre Slot A e B (você pode guardar 2 valores).",
            "  [ P ] SMART PATCH: Tenta uma correção automática rápida.", "",
            "DICA: Você pode recortar propriedades DE VOCÊ MESMO para usar!"
        ],
        [
            "--- TERMINAL DE CÓDIGO [ TECLA C ] ---", "",
            "Se o Recorte/Cola for limitado, use o Terminal para controle total.",
            "Primeiro SELECIONE um alvo com o mouse, depois pressione [C].", "",
            "COMANDOS DE ESTABILIZAÇÃO (RECOMENDADOS):",
            "  purge               (Purgar: Remove o erro e ESTABILIZA o sistema)",
            "  chmod -x            (Remove permissão de execução/ataque)",
            "  reboot              (Reinicia entidade para parâmetros seguros)",
            "  silence             (Suspende a hostilidade temporariamente)",
            "  heal                (Restaura integridade/HP em 100%)", "",
            "COMANDOS DE MANIPULAÇÃO:",
            "  kill                (Deleta o processo BRUTAMENTE - gera corrupção)",
            "  freeze / unfreeze   (Para ou solta o movimento completamente)",
            "  scan                (Exibe HP, Estado e Variáveis vitais)",
            "  optimize            (Aumenta velocidade em 50%)",
            "  teleport x y        (Move para coordenadas exatas)", "",
            "DICA: O comando 'purge' é a forma mais limpa de limpar o sistema."
        ],
        [
            "--- ESTRATÉGIA: EXECUÇÃO LIMPA ---", "",
            "Cada ação no Kernel deixa rastros. Entenda a diferença:", "",
            "1. MÉTODO BRUTO (Padrão):",
            "   Usar 'kill', 'teleport' ou sofrer danos aumenta a CORRUPÇÃO.",
            "   Isso causa glitches visuais e instabilidade física no mundo.", "",
            "2. EXECUÇÃO LIMPA (Recomendado):",
            "   Use 'purge' no terminal para apagar erros SEM deixar lixo.",
            "   Ações de correção (Smart Patch [P]) em inimigos específicos",
            "   REDUZEM a corrupção total do sistema.", "",
            "DICA: Operações em VOCÊ MESMO não geram corrupção.",
            "Ações 'limpas' (verde no manual) ajudam a manter o Kernel estável!"
        ],
        [
            "--- GUIA DE CAMPO: ELIMINANDO ERROS ---", "",
            "Cada erro tem uma falha lógica. Use para neutralizá-los LIMPO:", "",
            "1. NullPointer (Vermelho):",
            "   COMO VENCER: Ele é invisível. Recorte [T] o 'token' do Player",
            "   e cole [V] nele. Ele se revelará e parará de atacar.", "",
            "2. Buffer Overflow (Laranja):",
            "   COMO VENCER: O 'load' é maior que o 'buffer_size'. Use o",
            "   Smart Patch [P] para alocar mais memória e estabilizá-lo.", "",
            "3. Memory Leak (Verde):",
            "   COMO VENCER: Ele drena recursos. Use o Terminal [C] e digite",
            "   'leak_rate = 0' ou use o Smart Patch [P] para estancar o vazamento.", "",
            "4. Stack Overflow (Roxo):",
            "   COMO VENCER: Empilha processos. Use Smart Patch [P] para dar",
            "   'pop' na pilha até que ela esvazie.", "",
            "5. Infinite Loop (Amarelo):",
            "   COMO VENCER: Gira sem parar. Use o Terminal [C] para setar",
            "   'speed = 2' (reduzir velocidade) ou use Smart Patch [P]."
        ],
        [
            "--- PROTOCOLO DE COMBATE: BOSSES ---", "",
            "Chefes são processos protegidos. 'Kill' e 'Purge' NÃO funcionam.",
            "Você deve esgotar o HP (Integridade) deles usando LÓGICA:", "",
            "A) LOGIC BURST [ TECLA P ]:",
            "   Envia um pulso de correção massiva. -50 HP por acerto.",
            "   Gera corrupção em Bosses comuns, mas é vital contra o Core.", "",
            "B) DATA INJECTION [ TECLA V ]:",
            "   Copie valores (ex: speed de 10) e cole neles.",
            "   A discrepância de dados causa -20 HP ou mais.", "",
            "C) SABOTAGEM DE TERMINAL [ TECLA C ]:",
            "   Mude variáveis em tempo real (ex: 'speed = 0').",
            "   Pode paralisar o Boss para você atacar com segurança.", "",
            "DICA: O comando 'scan' no terminal revela o HP atual do Boss."
        ],
        [
            "--- MAPEAMENTO DOS SETORES (FASES) ---", "",
            "Cada setor é governado por um Processo Mestre (Boss).",
            "A Saída [TERMINAL_EXIT] só abre após derrotar o Boss local.", "",
            "SETOR 1-3 (NÚCLEO):",
            "   Ambientes simples para testar sua Debugger Gun.",
            "SETOR 4 (DEADLOCK FOREST):",
            "   Navegação difícil. Erros Deadlock drenam sua velocidade.",
            "SETOR 5-6 (INFRAESTRUTURA):",
            "   Fases complexas com defesas de rede e loops massivos.",
            "SETOR 7 (CLOUD SYNC):",
            "   A sincronização final. O Kernel está em colapso total.", "",
            "DICA: Derrotar o Boss do setor REDUZ sua corrupção atual!"
        ],
        [
            "--- INTEGRIDADE E KERNEL PANIC ---", "",
            "MANTENHA-SE OPERAÇÃO OU O SISTEMA IRÁ REINICIAR:", "",
            "HP (INTEGRIDADE):",
            "- Cair para 0 HP resulta em falha crítica do Sentinel.",
            "- Inimigos tiram 10 HP. Bosses tiram 25 HP.", "",
            "CORRUPÇÃO (INSTABILIDADE):",
            "- Atingir 100% de Corrupção causa um KERNEL PANIC.",
            "- O sistema se torna ilegível e reinicia o setor.", "",
            "RECUPERAÇÃO:",
            "- Use o comando 'heal' no terminal (em você mesmo) para 100% HP.",
            "- Use o comando 'purge' em inimigos comuns para reduzir corrupção.",
            "- Vença Bosses para uma limpeza profunda do Kernel."
        ],
        [
            "--- GUIA DE VULNERABILIDADES: BOSSES ---", "",
            "1. NULL_MASTER (Setor 1):",
            "   - STUN LÓGICO: Sete 'speed = 0' no terminal.",
            "   - ERRO CROMÁTICO: Use o comando 'invert' no terminal.",
            "     A inversão de cores causa choque de renderização.", "",
            "2. RECURSIVE_OVERLORD (Setor 2):",
            "   - SABOTAGEM DE CARGA: Reduza o 'load' para menos de 50.",
            "   - OVERCLOCK FATAL: Sete 'speed = 20' no terminal.",
            "     O excesso de ciclos causa superaquecimento e dano.", "",
            "3. CORE_KERNEL_PANIC (Setor 3):",
            "   - SMART PATCHING: Use o Patch [P] repetidamente.",
            "   - CONFLITO DE IDENTIDADE: Recorte [T] seu 'token' e cole",
            "     no núcleo [V]. Ele entrará em colapso de permissão."
        ],
        [
            "--- GUIA DE VULNERABILIDADES: BOSSES II ---", "",
            "4. MUTEX_MASTER (Setor 4):",
            "   - LIBERAÇÃO DE LOCK: Use 'lock_state = UNLOCKED'.",
            "     Isso remove o escudo e causa dano massivo de sincronia.", "",
            "5. REGISTRY_TYRANT (Setor 5):",
            "   - REVOGAÇÃO DE ACESSO: Sete 'access_level = USER'.",
            "   - PURGE DE REGISTRO: Mude 'registry_key' para 'NULL'.",
            "     Sem chaves válidas, o tirano perde o controle do banco.", "",
            "6. FIREWALL_DRAGON (Setor 6):",
            "   - BRECHA DE PORTA: Sete 'port_status = OPEN'.",
            "   - SPOOFING DE IP: Mude 'ip_source' para seu próprio IP.",
            "     O Firewall entra em conflito e desativa as defesas."
        ],
        [
            "--- ALERTA: SENTINELA_ALPHA.ERR ---", "",
            "O RIVAL APARECE EM MOMENTOS CRÍTICOS (SETOR 7):", "",
            "DIFERENCIAL:",
            "- Ele possui sua própria Debugger Gun.",
            "- Pode copiar seus atributos e usá-los contra você.", "",
            "COMO VENCER:",
            "- Use 'scan' para ver o que ele copiou de você.",
            "- O comando 'hakai' é a única forma de apagá-lo totalmente,",
            "  mas exige precisão e foco total no terminal.", "",
            "DICA: O manual mostra como vencer, mas sua habilidade define o sucesso!"
        ],
        [
            "--- RESUMO DE TÁTICAS DE ELITE ---", "",
            "COMO SER UM SENTINELA DE ELITE (0% CORRUPÇÃO):", "",
            "1. PRIORIZE O TERMINAL:",
            "   O comando 'purge' é seu melhor amigo. Use-o sempre.", "",
            "2. CHMOD -X É PODEROSO:",
            "   Não quer deletar? Tire a permissão de execução do inimigo.",
            "   Ele ficará inofensivo e o sistema continuará estável.", "",
            "3. USE O SCAN:",
            "   Sempre use 'scan' em novos alvos para ver quais variáveis",
            "   você pode manipular sem adivinhar.", "",
            "4. CUIDE DE VOCÊ:",
            "   Recortar de você mesmo (speed, token) nunca gera corrupção.", "",
            "SISTEMA PRONTO. SENTINEL.EXE EM EXECUÇÃO..."
        ]
    ]
    
    current_page = 0
    titles = [
        "1. Controles", "2. Terminal", "3. Execução Limpa", "4. Guia de Erros", 
        "5. Estratégia Boss", "6. Setores", "7. Objetivos", "8. Fraquezas Boss",
        "9. Fraquezas Boss II", "10. O Rival", "11. Táticas Elite"
    ]

    while True:
        sw, sh = screen.get_width(), screen.get_height()
        screen.fill((10, 10, 15))

        title_surf = font_title.render(titles[current_page], True, (0, 255, 255))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 40))

        for i, line in enumerate(pages[current_page]):
            color = (200, 200, 200)
            if line.startswith("  [") or line.startswith("  MOUSE") or "VENCER" in line: color = (0, 255, 0)
            if "---" in line or (line and line[0].isdigit()): color = (255, 255, 0)
            if "=" in line or "kill" in line or "PATCH" in line: color = (0, 200, 255)
            text_surf = font_text.render(line, True, color)
            screen.blit(text_surf, (40, 100 + i * 24))

        nav_text = f"Página {current_page + 1} de {len(pages)}  |  [<- / ->] Mudar Aba  |  [ESC] Voltar"
        nav_surf = font_small.render(nav_text, True, (100, 100, 100))
        screen.blit(nav_surf, (sw // 2 - nav_surf.get_width() // 2, sh - 40))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                current_page = (current_page + 1) % len(pages)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: current_page = (current_page - 1) % len(pages)
                elif event.key == pygame.K_RIGHT: current_page = (current_page + 1) % len(pages)
                elif event.key == pygame.K_ESCAPE: return True
        clock.tick(FPS)


def show_ending(game):
    """Tela final otimizada em logs e scroll."""
    screen = game.screen
    clock = game.clock
    sw, sh = screen.get_width(), screen.get_height()
    
    font_title = pygame.font.SysFont("monospace", 60, bold=True)
    font_text = pygame.font.SysFont("monospace", 24)
    font_logs = pygame.font.SysFont("monospace", 18)

    game.audio.play_music("menu")

    success_logs = [
        "> TERMINATING RIVAL_SENTINEL.ERR...", "> FLUSHING CORRUPTED CACHE...",
        "> REBUILDING KERNEL_INDEX... [OK]", "> RESTORING SECURITY_PROTOCOLS... [OK]",
        "> SYSTEM INTEGRITY: 100.0%", "> STATUS: SECURE.", "> GOODBYE, OPERATOR."
    ]
    
    lines_to_draw = []
    for log in success_logs:
        for i in range(len(log) + 1):
            screen.fill((5, 10, 5))
            for idx, line in enumerate(lines_to_draw):
                txt = font_logs.render(line, True, (0, 255, 100))
                screen.blit(txt, (40, 100 + idx * 25))
            screen.blit(font_logs.render(log[:i] + "_", True, (200, 255, 200)), (40, 100 + len(lines_to_draw) * 25))
            pygame.display.flip()
            pygame.time.delay(20)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        lines_to_draw.append(log)
        pygame.time.delay(200)

    credits = [
        "SISTEMA REESTRUTURADO COM SUCESSO", "---------------------------------",
        "Você purificou o Kernel do colapso iminente.",
        "A corrupção foi contida e a paz binária restaurada.", "",
        "CRÉDITOS:", "Desenvolvimento: Jean k. de Moura, Nicolas Castro, Henrique Froeder, ÍGOR PASLAUSKI",
        "Arte: Glitch_Generator v2.0", "Música: 8-bit Chaos Engine", "",
        "Obrigado por jogar!", "", "Pressione [ESCAPE] para retornar."
    ]

    y_scroll = sh
    while True:
        screen.fill((5, 10, 5))
        # Grid visual
        for x in range(0, sw, 50): pygame.draw.line(screen, (10, 30, 10), (x, 0), (x, sh))
        for y in range(0, sh, 50): pygame.draw.line(screen, (10, 30, 10), (0, y), (sw, y))

        title_surf = font_title.render("KERNEL.RESTORED", True, (0, 255, 100))
        title_surf.set_alpha(int(155 + math.sin(pygame.time.get_ticks() * 0.005) * 100))
        screen.blit(title_surf, (sw // 2 - title_surf.get_width() // 2, 50))

        for i, line in enumerate(credits):
            surf = font_text.render(line, True, (200, 255, 200))
            screen.blit(surf, (sw // 2 - surf.get_width() // 2, y_scroll + i * 40))

        y_scroll -= 1
        if y_scroll < -len(credits) * 40 - 100: y_scroll = sh // 2 + 100

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN): return
        clock.tick(FPS)
