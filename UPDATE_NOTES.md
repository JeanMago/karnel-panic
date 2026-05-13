# Changelog - Atualização do Kernel.panic()

## 🛠️ Debugger Gun & Injeção de Código
- **Patch por Código Expandido**: O terminal de patch (tecla `C`) agora suporta operações avançadas:
  - **Atribuição Direta**: `prop = valor`
  - **Operações Aritméticas**: `prop += valor` e `prop -= valor` (ex: `speed += 2`)
  - **Lógica Condicional**: Suporte inicial para `if` (ex: `if speed == 0: speed = 5`).
- **Feedback Visual**: Novo hint no editor de código para guiar o uso dos comandos.

## ☣️ Sistema de Corrupção 2.0 (Kernel Integrity)
- **Efeitos de Mundo**: A corrupção agora afeta fisicamente as entidades em níveis altos (jitter de posição e instabilidade de memória).
- **Propagação Passiva**: Estar próximo a processos corrompidos aumenta a taxa de corrupção do sistema.
- **Kernel Panic**: Implementada falha crítica de integridade. Se a corrupção atingir 100%, o sistema sofre um reboot forçado (reset do nível).
- **Glitches Visuais**: Novos efeitos de deslocamento de cor RGB e distorção de texto baseados no nível de falha.

## 🎵 Sistema de Áudio & Imersão
- **AudioManager**: Novo módulo centralizado para gerenciamento de trilhas sonoras.
- **Áudio Dinâmico**: O som agora reage à corrupção. Em níveis críticos, o volume sofre oscilações e glitches rítmicos.
- **Organização**: Estrutura de diretórios `assets/audio/` preparada para trilhas de menu e gameplay.

## 🐛 Correções e Estabilidade
- **Bug de Renderização**: Corrigido erro de tipo (`TypeError`) que ocorria ao calcular o brilho do fundo com o novo sistema de cores RGB.
- **Refatoração de Loop**: Delegação da lógica de efeitos para o `CorruptionSystem`, limpando o código principal do jogo.

## 📖 Manual do Sistema
- Tutorial atualizado no menu principal para incluir as novas mecânicas de Patch por Código e os perigos do nível de Corrupção.

---
*Gerado por Gemini CLI em 13 de Maio de 2026*
