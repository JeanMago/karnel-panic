"""
Fases (/root, /bin, /lib reservados para expansão): cada nível monta entidades e metadados.
"""

import pygame
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ecs.entity import Entity
from entities.player import Player
from entities.null_pointer import NullPointer
from entities.infinite_loop import InfiniteLoop
from entities.stack_overflow import StackOverflow


@dataclass
class LevelInfo:
    id: int
    name: str
    path_hint: str


LEVELS = {
    1: LevelInfo(1, "The Heap", "/root/var/heap"),
    2: LevelInfo(2, "Stack Overflow", "/bin/stack"),
    3: LevelInfo(3, "Kernel Panic", "/lib/kernel"),
}


class Exit(Entity):
    """Entidade que permite concluir o nível quando ativo."""
    def __init__(self, x, y):
        super().__init__()
        self.properties = {
            "tipo": "TERMINAL_EXIT",
            "x": x,
            "y": y,
            "w": 50,
            "h": 60,
            "active": False,
            "color": (50, 50, 50),
            "hostile": False,
        }

    def update(self, dt):
        if self.properties.get("active"):
            self.properties["color"] = (0, 255, 200)
        else:
            self.properties["color"] = (50, 50, 50)

    def render(self, screen):
        pygame.draw.rect(screen, self.properties["color"], (self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]), 2)
        if self.properties.get("active"):
            # Efeito de brilho
            pygame.draw.rect(screen, (0, 100, 80), (self.properties["x"]+10, self.properties["y"]+10, 30, 40))

def build_level(level_id: int, sw: int, sh: int) -> Tuple[Player, List[Entity]]:
    """Retorna jogador e lista de entidades do nível."""
    player = Player(sw // 4, sh // 2)
    exit_node = Exit(sw - 80, sh // 2 - 30)
    entities: List[Entity] = [player, exit_node]

    if level_id == 1:
        entities.append(NullPointer(sw // 2, sh // 2, target=player))
    elif level_id == 2:
        entities.append(InfiniteLoop(sw // 2 - 40, sh // 3))
        entities.append(StackOverflow(sw // 2 + 100, sh * 2 // 3))
    else:
        entities.append(NullPointer(sw // 2, sh // 4, target=player))
        entities.append(InfiniteLoop(sw // 4, sh // 2))
        entities.append(StackOverflow(sw * 3 // 4, sh // 2))

    return player, entities


def get_level_info(level_id: int) -> Optional[LevelInfo]:
    return LEVELS.get(level_id)
