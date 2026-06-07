"""
Fases (/root, /bin, /lib reservados para expansão): cada nível monta entidades e metadados.
"""

import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ecs.entity import Entity
from entities.player import Player
from entities.null_pointer import NullPointer
from entities.infinite_loop import InfiniteLoop
from entities.stack_overflow import StackOverflow
from entities.buffer_overflow import BufferOverflow
from entities.memory_leak import MemoryLeak
from entities.deadlock import Deadlock
from entities.rival_sentinel import RivalSentinel
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
    4: LevelInfo(4, "Deadlock Forest", "/sys/sync/mutex"),
    5: LevelInfo(5, "Registry Hive", "/root/etc/config"),
    6: LevelInfo(6, "Firewall Gate", "/net/filter/ip"),
    7: LevelInfo(7, "Cloud Sync", "/mnt/remote/cloud"),
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

def is_valid_spawn(x, y, w, h, entities: List[Entity], min_dist_to_player=300, player_pos=(0, 0)) -> bool:
    """Verifica se a posição de spawn não colide com obstáculos ou está muito perto do player."""
    spawn_rect = pygame.Rect(x, y, w, h)
    
    # Distância mínima do player para não morrer ao nascer
    dist_sq = (x - player_pos[0])**2 + (y - player_pos[1])**2
    if dist_sq < min_dist_to_player**2:
        return False

    for e in entities:
        if e.properties.get("collision"):
            ex, ey = e.properties["x"], e.properties["y"]
            ew, eh = e.properties["w"], e.properties["h"]
            if spawn_rect.colliderect(pygame.Rect(ex, ey, ew, eh)):
                return False
    return True

def build_level(level_id: int, sw: int, sh: int) -> Tuple[Player, List[Entity]]:
    """Cria áreas GIGANTES (ex: 4000x3000) com labirintos temáticos e spawns seguros."""
    entities: List[Entity] = []
    WORLD_W = 4000
    WORLD_H = 3000

    # Paredes de borda
    entities.append(Obstacle(0, -50, WORLD_W, 50, label="Boundary"))
    entities.append(Obstacle(0, WORLD_H, WORLD_W, 50, label="Boundary"))
    entities.append(Obstacle(-50, 0, 50, WORLD_H, label="Boundary"))
    entities.append(Obstacle(WORLD_W, 0, 50, WORLD_H, label="Boundary"))

    if level_id == 1:
        # THE HEAP: Blocos de memória em grade irregular (fragmentada)
        p_pos = (150, 150)
        player = Player(*p_pos)
        exit_node = Exit(WORLD_W - 200, WORLD_H - 200)
        
        # Grid de blocos "alocados"
        for gx in range(400, WORLD_W, 600):
            for gy in range(400, WORLD_H, 600):
                if random.random() < 0.7:
                    bw = random.randint(150, 400)
                    bh = random.randint(150, 400)
                    entities.append(Obstacle(gx, gy, bw, bh, color=(30, 30, 50)))
        
        # Boss
        bx, by = WORLD_W // 2 + 500, WORLD_H // 2 + 500
        entities.append(NullMaster(bx, by))
        
        # Inimigos comuns com checagem de spawn
        for _ in range(15):
            for _ in range(10): # Tentativas de spawn
                ex, ey = random.randint(500, WORLD_W-500), random.randint(500, WORLD_H-500)
                if is_valid_spawn(ex, ey, 40, 40, entities, player_pos=p_pos):
                    entities.append(NullPointer(ex, ey, target=player))
                    break
        
        for _ in range(10):
            for _ in range(10):
                ex, ey = random.randint(500, WORLD_W-500), random.randint(500, WORLD_H-500)
                if is_valid_spawn(ex, ey, 50, 50, entities, player_pos=p_pos):
                    entities.append(BufferOverflow(ex, ey, target=player))
                    break

    elif level_id == 2:
        # STACK OVERFLOW: Pilares verticais e corredores estreitos
        p_pos = (100, WORLD_H // 2)
        player = Player(*p_pos)
        exit_node = Exit(WORLD_W - 200, WORLD_H // 2)
        
        # "Stacks" verticais
        for x in range(600, WORLD_W - 400, 500):
            gap_y = random.randint(400, WORLD_H - 800)
            entities.append(Obstacle(x, 0, 100, gap_y, color=(60, 40, 70)))
            entities.append(Obstacle(x, gap_y + 400, 100, WORLD_H - gap_y - 400, color=(60, 40, 70)))

        # Boss
        entities.append(RecursiveOverlord(WORLD_W // 2, WORLD_H // 2))

        # Inimigos
        for _ in range(12):
            for _ in range(10):
                ex, ey = random.randint(500, WORLD_W-500), random.randint(200, WORLD_H-200)
                if is_valid_spawn(ex, ey, 36, 36, entities, player_pos=p_pos):
                    entities.append(InfiniteLoop(ex, ey))
                    break
        for _ in range(12):
            for _ in range(10):
                ex, ey = random.randint(500, WORLD_W-500), random.randint(200, WORLD_H-200)
                if is_valid_spawn(ex, ey, 34, 34, entities, player_pos=p_pos):
                    entities.append(StackOverflow(ex, ey))
                    break

    elif level_id == 3:
        # KERNEL PANIC: Fractal e caos radial
        p_pos = (2000, 1500)
        player = Player(*p_pos)
        exit_node = Exit(100, 100)
        
        # Boss e Rival
        entities.append(PanicCore(WORLD_W - 600, WORLD_H - 600))
        entities.append(RivalSentinel(WORLD_W // 2 - 500, WORLD_H // 2 - 500, target=player))

        # Labirinto radial/fracturado
        for i in range(8):
            angle = i * (3.1415 / 4)
            for dist in range(600, 2500, 400):
                ox = 2000 + pygame.math.Vector2(1, 0).rotate_rad(angle).x * dist
                oy = 1500 + pygame.math.Vector2(1, 0).rotate_rad(angle).y * dist
                if random.random() < 0.8:
                    entities.append(Obstacle(ox-50, oy-50, 150, 150, color=(80, 20, 20)))

        # Boss
        entities.append(PanicCore(WORLD_W - 600, WORLD_H - 600))

        # Mix de inimigos
        for _ in range(25):
            for _ in range(10):
                ex, ey = random.randint(200, WORLD_W-200), random.randint(200, WORLD_H-200)
                etype = random.choice([NullPointer, InfiniteLoop, StackOverflow, BufferOverflow, MemoryLeak])
                if is_valid_spawn(ex, ey, 45, 45, entities, player_pos=p_pos):
                    if etype in [NullPointer, BufferOverflow]: entities.append(etype(ex, ey, target=player))
                    else: entities.append(etype(ex, ey))
                    break

    elif level_id == 4:
        # DEADLOCK FOREST: Corredores densos com travas de recurso
        p_pos = (200, 200)
        player = Player(*p_pos)
        exit_node = Exit(WORLD_W - 200, WORLD_H - 200)
        entities.append(NullMaster(WORLD_W // 2, WORLD_H // 2))

        for _ in range(60):
            ox, oy = random.randint(400, WORLD_W-400), random.randint(400, WORLD_H-400)
            entities.append(Obstacle(ox, oy, 150, 150, color=(40, 60, 40)))

        for _ in range(20):
            ex, ey = random.randint(400, WORLD_W-400), random.randint(400, WORLD_H-400)
            if is_valid_spawn(ex, ey, 40, 40, entities, player_pos=p_pos):
                entities.append(Deadlock(ex, ey, target=player))

    elif level_id == 5:
        # REGISTRY HIVE: Labirinto ortogonal denso
        p_pos = (150, WORLD_H - 150)
        player = Player(*p_pos)
        exit_node = Exit(WORLD_W - 150, 150)
        entities.append(RecursiveOverlord(WORLD_W // 2, WORLD_H // 2))

        for x in range(300, WORLD_W, 400):
            for y in range(300, WORLD_H, 400):
                if random.random() < 0.8:
                    entities.append(Obstacle(x, y, 300, 40, color=(100, 100, 30)))
                    entities.append(Obstacle(x, y, 40, 300, color=(100, 100, 30)))

        for _ in range(30):
            ex, ey = random.randint(200, WORLD_W-200), random.randint(200, WORLD_H-200)
            etype = random.choice([StackOverflow, MemoryLeak, Deadlock])
            if is_valid_spawn(ex, ey, 40, 40, entities, player_pos=p_pos):
                if etype == Deadlock: entities.append(etype(ex, ey, target=player))
                else: entities.append(etype(ex, ey))

    elif level_id == 6:
        # FIREWALL GATE: Barreiras verticais longas
        p_pos = (100, 1500)
        player = Player(*p_pos)
        exit_node = Exit(WORLD_W - 100, 1500)
        entities.append(PanicCore(WORLD_W // 2, WORLD_H // 2))
        entities.append(RivalSentinel(WORLD_W // 2 + 300, WORLD_H // 2, target=player))

        for x in range(800, WORLD_W - 800, 800):
            entities.append(Obstacle(x, 0, 80, WORLD_H // 2 - 200, color=(200, 50, 50)))
            entities.append(Obstacle(x, WORLD_H // 2 + 200, 80, WORLD_H // 2 - 200, color=(200, 50, 50)))

        for _ in range(40):
            ex, ey = random.randint(200, WORLD_W-200), random.randint(200, WORLD_H-200)
            etype = random.choice([BufferOverflow, NullPointer, Deadlock])
            if is_valid_spawn(ex, ey, 50, 50, entities, player_pos=p_pos):
                entities.append(etype(ex, ey, target=player))

    else:
        # CLOUD SYNC: Final Boss Arena e caos total
        p_pos = (WORLD_W // 2, WORLD_H // 2)
        player = Player(*p_pos)
        exit_node = Exit(150, 150)
        entities.append(PanicCore(WORLD_W - 500, WORLD_H - 500))
        entities.append(RivalSentinel(500, 500, target=player))
        
        # Grande arena central
        for i in range(12):
            angle = i * (3.1415 * 2 / 12)
            ox = 2000 + math.cos(angle) * 800
            oy = 1500 + math.sin(angle) * 800
            entities.append(Obstacle(ox-40, oy-40, 80, 80, color=(50, 50, 150)))

        for _ in range(50):
            ex, ey = random.randint(200, WORLD_W-200), random.randint(200, WORLD_H-200)
            etype = random.choice([NullPointer, InfiniteLoop, StackOverflow, BufferOverflow, MemoryLeak, Deadlock])
            if is_valid_spawn(ex, ey, 40, 40, entities, player_pos=p_pos):
                if etype in [NullPointer, BufferOverflow, Deadlock]: entities.append(etype(ex, ey, target=player))
                else: entities.append(etype(ex, ey))
                break

    entities.insert(0, player)
    entities.append(exit_node)
    return player, entities

def get_level_info(level_id: int) -> Optional[LevelInfo]:
    return LEVELS.get(level_id)
