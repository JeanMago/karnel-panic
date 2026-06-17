# 📑 Documentação Técnica: Kernel.panic()

## 1. Visão Geral do Projeto
**Kernel.panic()** é um jogo de ação top-down desenvolvido em Python utilizando a biblioteca Pygame. O jogo subverte as mecânicas tradicionais de combate, substituindo armas convencionais por ferramentas de depuração de software. O jogador assume o papel de um **Sentinel** encarregado de estabilizar um kernel de sistema operacional corrompido, enfrentando representações físicas de bugs e erros de runtime.

---

## 2. Arquitetura do Software

### 2.1. Paradigma de Entidades (Custom ECS)
O projeto utiliza um sistema de entidades altamente desacoplado:
- **`Entity` (Base)**: Cada entidade é um objeto leve cujo estado é definido por um dicionário `properties`.
- **Dinamismo**: Quase todos os comportamentos (velocidade, colisões, hostilidade, cores) são lidos das `properties` em tempo real, permitindo que ferramentas externas modifiquem o comportamento da entidade sem alterar sua classe.
- **Loop de Jogo**: Gerenciado pela classe `GameLoop`, que itera sobre as entidades para `update` e `render`.

### 2.2. O Sistema de Corrupção (`CorruptionSystem`)
Gerencia a integridade do sistema global:
- **Escalabilidade**: O nível de corrupção (0.0 a 1.0) aumenta conforme o jogador recebe dano ou utiliza hacks "agressivos".
- **Efeitos Visuais (Glitches)**: Implementa tremores de câmera, scanlines, inversão de cores e distorção de texto dinamicamente.
- **Impacto na Gameplay**: Em níveis altos, a corrupção causa "drift" de dados (entidades se movem sozinhas) e pode levar ao `INTEGRITY_FAILURE` (Game Over).

---

## 3. Mecânicas Centrais

### 3.1. Debugger Gun
A ferramenta primária do jogador, permitindo manipulação direta de memória:
- **CUT (X)**: Remove uma propriedade de uma entidade (ex: remove a velocidade de um inimigo).
- **PASTE (V)**: Injeta um valor armazenado em uma nova entidade ou em si mesmo.
- **SMART PATCH (P)**: Identifica automaticamente problemas comuns (ex: conserta um `BufferOverflow` redimensionando o buffer).
- **INSPECT**: Visualiza o dump completo de propriedades de qualquer processo selecionado.

### 3.2. Terminal de Patch (`CodeEditor`)
Permite a execução de comandos manuais no alvo selecionado:
- `chmod -x`: Torna processos hostis inofensivos.
- `purge`: Remove completamente a entidade da memória de forma segura.
- `if speed > 10: speed = 2`: Lógica condicional aplicada diretamente ao objeto.
- `hakai`: Comando de destruição total (God Mode).

---

## 4. Bestiário e Erros de Sistema

### 4.1. Inimigos Comuns
- **`NullPointer`**: Ataca se sua `reference` for nula. Pode ser neutralizado fornecendo uma referência válida.
- **`MemoryLeak`**: Cresce continuamente, consumindo espaço e aumentando a corrupção.
- **`InfiniteLoop`**: Move-se em velocidades extremas e padrões repetitivos.
- **`StackOverflow`**: Ataca através de recursão profunda (projéteis ou clones).
- **`Deadlock`**: Imobiliza o jogador ao contato, simulando espera de recursos.

### 4.2. Bosses (Processos Mestres)
- **NullMaster**: O mestre das referências vazias.
- **RecursiveOverlord**: Controla a pilha de execução do sistema.
- **PanicCore**: O núcleo da corrupção, capaz de distorcer a realidade do jogo.
- **FirewallDragon**: Protege as portas de saída com barreiras de dados.

---

## 5. Interface e Experiência do Usuário (UI/UX)
- **HUD**: Exibe HP, nível de corrupção e um minimapa em tempo real.
- **Console**: Um log persistente que informa todas as operações de baixo nível realizadas pelo jogador.
- **Inspector**: Uma janela lateral que detalha as variáveis internas da entidade em foco.

---

## 6. Estrutura de Níveis e Progressão
O jogo é dividido em setores lógicos do sistema operacional:
1. **Sandbox Tutorial** (`/mnt/sys/tutorial`)
2. **The Heap** (`/root/var/heap`)
3. **Stack Overflow** (`/bin/stack`)
4. **Kernel Panic** (`/lib/kernel`)
... seguindo até o nível 10 (**The Singularity**).

A progressão exige derrotar o Boss local para ativar o `TERMINAL_EXIT`, que permite a transmissão de dados para o próximo setor e recupera parte da integridade do sistema.

---

## 7. Configurações Técnicas
- **Resoluções Suportadas**: 1280x720, 1600x900, 1920x1080 (Proporção 16:9).
- **Persistência**: Estados salvos em `save/game_state.json`.
- **DPI Awareness**: Implementado para suporte a monitores de alta densidade no Windows.
- **FPS**: Limitado a 60 por padrão para estabilidade da física de dados.
