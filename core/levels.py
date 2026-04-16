"""
Fases (/root, /bin, /lib reservados para expansão): cada nível monta entidades e metadados.
"""

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


def build_level(level_id: int, sw: int, sh: int) -> Tuple[Player, List[Entity]]:
    """Retorna jogador e lista de entidades do nível."""
    player = Player(sw // 4, sh // 2)
    entities: List[Entity] = [player]

    if level_id == 1:
        entities.append(NullPointer(sw * 3 // 4, sh // 2, target=player))
    elif level_id == 2:
        entities.append(InfiniteLoop(sw // 2 - 40, sh // 2 - 40))
        entities.append(StackOverflow(sw * 2 // 3, sh // 2))
    else:
        entities.append(NullPointer(sw * 3 // 4, sh // 3, target=player))
        entities.append(InfiniteLoop(sw // 3, sh * 2 // 3))
        entities.append(StackOverflow(sw // 2, sh // 2))

    return player, entities


def get_level_info(level_id: int) -> Optional[LevelInfo]:
    return LEVELS.get(level_id)
