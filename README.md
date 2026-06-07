# Kernel.panic() 🖥️  
> **"Em um sistema quebrado, a lógica é sua única arma."**

**Kernel.panic()** é um jogo de ação tática e depuração técnica onde você assume o papel de um processo **Sentinel.exe** dentro de um sistema operacional em colapso. Esqueça as balas: aqui você luta manipulando variáveis, injetando dados e executando comandos de terminal em tempo real para restaurar a ordem binária antes que ocorra um Kernel Panic total.

---

## 🌌 A Crise do Sistema (Lore)
No ano de 2026, a Integridade do Núcleo foi comprometida. Bugs monstruosos tomaram conta do Heap, vazamentos de memória drenam os recursos vitais e processos mestres (Bosses) protegem setores corrompidos. Você foi instanciado com permissões de superusuário e a poderosa **Debugger Gun** para salvar o sistema de dentro para fora.

## 🛠️ Mecânicas de Jogo Únicas

### 🔦 Debugger Gun (A Arma de Depuração)
Diferente de qualquer arma tradicional, a Debugger Gun permite que você altere a realidade física dos inimigos:
- **[ X ] CUT (Recortar):** Extraia propriedades como `speed`, `load` ou `stack_depth` de uma entidade.
- **[ V ] PASTE (Colar):** Injete o valor roubado em outro alvo. Reduzir a velocidade de um Boss a zero causa um **Logical Stun**.
- **[ TAB ] Dual Clipboard:** Alterne entre os slots **A** e **B** para carregar múltiplos valores simultaneamente.
- **[ P ] SMART PATCH:** Uma IA de correção rápida que neutraliza erros comuns (como Buffer Overflows) sem gerar lixo de memória.

### ⌨️ Terminal de Código Direto [ Tecla C ]
Assuma o controle total enviando comandos de baixo nível para as entidades selecionadas:
- `purge`: A forma mais limpa de deletar um erro (reduz a corrupção do sistema).
- `chmod -x`: Remove a permissão de execução (hostilidade) do alvo, tornando-o inofensivo.
- `scan`: Revela variáveis vitais e HP oculto.
- `reboot`: Reinicia uma entidade para seus parâmetros de segurança originais.
- `if p == v: p2 = v2`: Execute lógica condicional simples diretamente no alvo.

### 📉 Sistema de Corrupção Dinâmico
Cada ação deixa um rastro. Usar métodos brutos como `kill` aumenta a **Corrupção**, gerando instabilidade física, glitches visuais e tornando o Kernel imprevisível. Priorize a **Execução Limpa** (Clean Execution) para estabilizar o mundo e ganhar bônus.

### 🗺️ Navegação Tática
- **Mundos Vasto:** Navegue por setores gigantescos mapeados em tempo real pelo **NAV_SYSTEM.MAP** (Mini-mapa).
- **Câmera Dinâmica:** O sistema de visão segue o seu processo por labirintos densos de endereços de memória.

---

## 👾 Guia de Ameaças (Inimigos)
- **NullPointer:** Invisível e letal. Requer uma injeção de `token` para se tornar visível.
- **Buffer Overflow:** Ataca quando sua carga excede sua capacidade. Aloque mais memória para estabilizá-lo.
- **RecursiveOverlord (Boss):** Um mestre da carga. Tente sabotar sua variável `load` ou force um superaquecimento via overclock (`speed = 20`).
- **PanicCore (Final Boss):** O coração do colapso. Vulnerável apenas a conflitos de identidade e patches lógicos massivos.

---

## 🎮 Controles e Atalhos
| Tecla | Ação |
| :--- | :--- |
| **W, A, S, D** | Movimentação de Processo |
| **MOUSE L/R** | Mirar Feixe / Selecionar Entidade |
| **TAB** | Alternar Slots de Clipboard (A/B) |
| **X / V** | CUT / PASTE (Consome os dados após o uso) |
| **P** | SMART PATCH (Ataque Lógico / Correção) |
| **C** | Abrir Terminal de Comando |
| **T** | Recortar `token` de si mesmo (Sentinel) |
| **F11** | Alternar Tela Cheia |
| **ESC** | Menu de Pausa / Configurações |

---

## 🚀 Instalação e Execução

### Pré-requisitos
- **Python 3.10+**
- **Pygame 2.0+** (`pip install pygame`)

### Executando o Jogo
1. Clone o repositório.
2. Navegue até a pasta raiz via terminal.
3. Execute:
   ```bash
   python main.py
   ```

## 🧠 Filosofia Técnica
**Kernel.panic()** é um projeto "Code-First". Todos os visuais, animações e mecânicas são gerados via scripts procedurais, sem o uso de assets externos de imagem, reforçando a estética de um sistema puramente computacional.

---
**Status do Sentinel:** OPERACIONAL  
**Integridade do Kernel:** INSTÁVEL  
**Boa depuração, Sentinela.**  
