"""
Fases (/root, /bin, /lib reservados para expansão): cada nível monta entidades e metadados.
"""

import pygame
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ecs.entity import Entity
from entities.player import Player
from entities.null_pointer import NullPointer
from entities.infinite_loop import InfiniteLoop
from entities.stack_overflow import StackOverflow
from entities.buffer_overflow import BufferOverflow
from entities.memory_leak import MemoryLeak
from entities.bosses import NullMaster, RecursiveOverlord, PanicCore


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

class Obstacle(Entity):
    """Parede ou bloco de dados que impede a passagem."""
    def __init__(self, x, y, w, h, color=(40, 40, 60), label="CorruptedData"):
        super().__init__()
        self.properties = {
            "tipo": label,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "color": color,
            "collision": True,
            "hostile": False
        }

    def render(self, screen):
        pygame.draw.rect(screen, self.properties["color"], (self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]))
        pygame.draw.rect(screen, (100, 100, 255), (self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]), 1)
        
        if random.random() < 0.01:
            gx = self.properties["x"] + random.randint(0, self.properties["w"])
            pygame.draw.line(screen, (255, 255, 255), (gx, self.properties["y"]), (gx, self.properties["y"] + self.properties["h"]))

class Exit(Entity):
    """Entidade que permite concluir o nível quando ativo."""
    def __init__(self, x, y):
        super().__init__()
        self.properties = {
            "tipo": "TERMINAL_EXIT",
            "x": x,
            "y": y,
            "w": 80,
            "h": 100,
            "active": False,
            "color": (50, 50, 50),
            "hostile": False
        }

    def update(self, dt):
        if self.properties.get("active"):
            self.properties["color"] = (0, 255, 200)
        else:
            self.properties["color"] = (50, 50, 50)

    def render(self, screen):
        x, y, w, h = self.properties["x"], self.properties["y"], self.properties["w"], self.properties["h"]
        pygame.draw.rect(screen, self.properties["color"], (x, y, w, h), 2)
        if self.properties.get("active"):
            pygame.draw.rect(screen, (0, 100, 80), (x+10, y+10, w-20, h-20))
            for i in range(3):
                off = (pygame.time.get_ticks() // 100 + i*10) % 30
                pygame.draw.rect(screen, (0, 255, 200), (x+10+off//2, y+10+off//2, w-20-off, h-20-off), 1)

def build_level(level_id: int, sw: int, sh: int) -> Tuple[Player, List[Entity]]:
    """Cria áreas GIGANTES (ex: 4000x3000) com labirintos e um Boss final."""
    entities: List[Entity] = []
    WORLD_W = 4000
    WORLD_H = 3000

    if level_id == 1:
        player = Player(100, 100)
        exit_node = Exit(WORLD_W - 200, WORLD_H - 200)
        boss = NullMaster(WORLD_W // 2, WORLD_H // 2)
        entities.append(boss)
        
        # Obstáculos aleatórios
        for _ in range(30):
            ox = random.randint(500, WORLD_W - 500)
            oy = random.randint(500, WORLD_H - 500)
            entities.append(Obstacle(ox, oy, 200, 40))

    elif level_id == 2:
        player = Player(100, 100)
        exit_node = Exit(WORLD_W - 200, WORLD_H - 200)
        boss = RecursiveOverlord(WORLD_W // 2, WORLD_H // 2)
        entities.append(boss)

        for i in range(1, 4):
            entities.append(Obstacle(i * 1000, 0, 50, WORLD_H - 800))
            entities.append(Obstacle(i * 1000, 800, 50, WORLD_H))

    else:
        player = Player(WORLD_W // 2, WORLD_H // 2)
        exit_node = Exit(100, 100)
        boss = PanicCore(WORLD_W - 500, WORLD_H - 500)
        entities.append(boss)
        
        for i in range(50):
            angle = i * (3.1415 * 2 / 50)
            dist = 600 + (i % 2) * 400
            ox = 2000 + pygame.math.Vector2(1, 0).rotate_rad(angle).x * dist
            oy = 1500 + pygame.math.Vector2(1, 0).rotate_rad(angle).y * dist
            entities.append(Obstacle(ox, oy, 100, 100, color=(100, 20, 20)))

    entities.insert(0, player)
    entities.append(exit_node)
    return player, entities

def get_level_info(level_id: int) -> Optional[LevelInfo]:
    return LEVELS.get(level_id)
