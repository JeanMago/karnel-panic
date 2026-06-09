import sys
import ctypes
from core.game import Game

# Habilitar DPI Awareness no Windows antes de inicializar o pygame
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

if __name__ == "__main__":
    game = Game()
    game.run()
    