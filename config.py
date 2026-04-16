import os

WIDTH = 800
HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5

# Layout HUD: faixa inferior só para o console (evita sobrepor o painel Debugger Gun)
CONSOLE_ZONE_HEIGHT = 132
DEBUGGER_GAP_ABOVE_CONSOLE = 10

_BASE = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(_BASE, "save", "game_state.json")