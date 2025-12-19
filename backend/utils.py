from dataclasses import dataclass
from typing import List, Any, Tuple
import math

@dataclass
class Pair:
    first: int
    second: int
    
    def __eq__(self, other):
        return self.first == other.first and self.second == other.second
    
    def __hash__(self):
        return hash((self.first, self.second))

@dataclass
class Agent:
    id: int
    start: Pair
    goal: Pair
    
    def __hash__(self):
        return hash(self.id)

class PriorityQueueItem:
    def __init__(self, priority: float, item: Any):
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        return self.priority < other.priority

def make_2d_array(size: int, default_value: Any) -> List[List[Any]]:
    return [[default_value for _ in range(size)] for _ in range(size)]

def is_safe(x: int, y: int, size: int, blocks: List[List[bool]]) -> bool:
    return 0 <= x < size and 0 <= y < size and not blocks[x][y]

def get_neighbors(pos: Pair, blocks: List[List[bool]], size: int) -> List[Pair]:
    """Get valid neighboring cells (4-directional movement)"""
    neighbors = []
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
    
    for dx, dy in directions:
        x = pos.first + dx
        y = pos.second + dy
        if is_safe(x, y, size, blocks):
            neighbors.append(Pair(x, y))
    
    return neighbors

def manhattan_distance(a: Pair, b: Pair) -> int:
    """Manhattan distance heuristic"""
    return abs(a.first - b.first) + abs(a.second - b.second)

def euclidean_distance(a: Pair, b: Pair) -> float:
    """Euclidean distance heuristic"""
    dx = a.first - b.first
    dy = a.second - b.second
    return math.sqrt(dx * dx + dy * dy)

# Direction constants
DX_4D = [0, 1, 0, -1]
DY_4D = [1, 0, -1, 0]
