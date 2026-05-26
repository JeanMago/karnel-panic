import os

# Configurações Iniciais (podem ser alteradas em tempo de execução)
WIDTH = 1280
HEIGHT = 720
FPS = 60
LIMIT_FPS = True

PLAYER_SPEED = 5

# Lista de resoluções suportadas (todas 16:9)
RESOLUTIONS = [
    (1280, 720),
    (1600, 900),
    (1920, 1080)
]

# Layout HUD
CONSOLE_ZONE_HEIGHT = 132
DEBUGGER_GAP_ABOVE_CONSOLE = 10

_BASE = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(_BASE, "save", "game_state.json")
CONFIG_PATH = os.path.join(_BASE, "save", "settings.json")