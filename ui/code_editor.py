import pygame

class CodeEditor:
    """
    Representa o editor de código/terminal interativo onde o jogador digita comandos.
    Ativado pela tecla [C] após selecionar um alvo.
    """
    def __init__(self):
        self.active = False # Indica se o editor está aberto e capturando teclado
        self.text = "" # Texto atual sendo digitado pelo usuário
        self.font = pygame.font.SysFont("consolas", 16)
        self.history = [] # Histórico de comandos (para expansão futura)

    def toggle(self):
        """Abre ou fecha o editor. Limpa o texto ao abrir."""
        self.active = not self.active
        if self.active:
            self.text = ""

    def handle_event(self, event):
        """
        Processa eventos de teclado para capturar o comando digitado.
        Retorna o comando quando 'Enter' é pressionado.
        """
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                cmd = self.text
                self.active = False # Fecha o editor ao enviar
                return cmd
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1] # Apaga o último caractere
            elif event.key == pygame.K_ESCAPE:
                self.active = False # Cancela e fecha o editor
            else:
                # Apenas captura caracteres imprimíveis (letras, números, símbolos básicos)
                if event.unicode.isprintable():
                    self.text += event.unicode
        return None

    def draw(self, screen):
        """Desenha a caixa de entrada de texto centralizada na tela."""
        if not self.active:
            return

        sw, sh = screen.get_width(), screen.get_height()
        # Define dimensões e posição do painel central
        w, h = 400, 40
        x, y = (sw - w) // 2, (sh - h) // 2
        
        # Fundo do editor preto com borda ciano/esmeralda
        pygame.draw.rect(screen, (0, 0, 0), (x, y, w, h))
        pygame.draw.rect(screen, (0, 255, 150), (x, y, w, h), 2)
        
        # Renderiza o prompt '> ' seguido do texto e um cursor '_'
        prompt = self.font.render(f"> {self.text}_", True, (0, 255, 100))
        screen.blit(prompt, (x + 10, y + 10))
        
        # Exibe exemplos de comandos acima da caixa para guiar o jogador
        hint = self.font.render("Ex: speed=10 | speed+=1 | if speed==0: speed=5", True, (100, 150, 100))
        screen.blit(hint, (x, y - 25))
