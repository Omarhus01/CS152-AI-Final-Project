"""
Space-Time A* Algorithm
State: (x, y, t) - position and time
Actions: move(N,E,S,W) or wait
Heuristic: Manhattan distance (admissible)
"""
import time
from typing import Dict, Any, List, Set, Tuple, Optional
from queue import PriorityQueue
from dataclasses import dataclass
import itertools
import sys
sys.path.append('..')
from utils import Pair, Agent, get_neighbors, manhattan_distance

@dataclass
class SpaceTimeState:
    pos: Pair
    time: int
    
    def __eq__(self, other):
        return self.pos == other.pos and self.time == other.time
    
    def __hash__(self):
        return hash((self.pos, self.time))
    
    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time
        return (self.pos.first, self.pos.second) < (other.pos.first, other.pos.second)

def space_time_astar(
    agent: Agent,
    blocks: List[List[bool]],
    size: int,
    max_time: int = 100,
    constraints: Optional[Set[Tuple[int, int, int]]] = None,
    reservation_table: Optional[Set[Tuple[int, int, int]]] = None
) -> Dict[str, Any]:
    """
    Space-Time A* for single agent
    
    Args:
        agent: Agent with start and goal
        blocks: 2D grid of obstacles
        size: Grid size
        max_time: Maximum time horizon
        constraints: Set of (x, y, t) forbidden states
        reservation_table: Set of (x, y, t) reserved by other agents
    
    Returns:
        Dictionary with path, exploration_order, and metrics
    """
    start_time = time.time()
    
    if constraints is None:
        constraints = set()
    if reservation_table is None:
        reservation_table = set()
    
    # Priority queue: (f_cost, counter, g_cost, state)
    pq = PriorityQueue()
    counter = itertools.count()
    start_state = SpaceTimeState(agent.start, 0)
    h_start = manhattan_distance(agent.start, agent.goal)
    pq.put((h_start, next(counter), 0, start_state))
    
    # Tracking
    visited: Set[SpaceTimeState] = set()
    parent: Dict[SpaceTimeState, Optional[SpaceTimeState]] = {start_state: None}
    g_cost: Dict[SpaceTimeState, int] = {start_state: 0}
    exploration_order = [[agent.start.first, agent.start.second, 0]]
    nodes_expanded = 0
    
    while not pq.empty():
        _, _, g, current = pq.get()
        
        if current in visited:
            continue
        
        visited.add(current)
        nodes_expanded += 1
        
        # Goal check
        if current.pos == agent.goal:
            # Reconstruct path
            path = []
            state = current
            while state is not None:
                path.insert(0, [state.pos.first, state.pos.second, state.time])
                state = parent[state]
            
            metrics = {
                "explored_size": len(visited),
                "nodes_expanded": nodes_expanded,
                "time_taken_ms": (time.time() - start_time) * 1000,
                "path_length": len(path) - 1,
                "makespan": current.time,
                "success": True
            }
            
            return {
                "path": path,
                "exploration_order": exploration_order,
                "metrics": metrics
            }
        
        # Time limit check
        if current.time >= max_time:
            continue
        
        # Generate successors: move or wait
        successors = []
        
        # Move actions
        for neighbor in get_neighbors(current.pos, blocks, size):
            next_state = SpaceTimeState(neighbor, current.time + 1)
            successors.append(next_state)
        
        # Wait action
        wait_state = SpaceTimeState(current.pos, current.time + 1)
        successors.append(wait_state)
        
        for next_state in successors:
            # Check constraints and reservations
            pos_tuple = (next_state.pos.first, next_state.pos.second, next_state.time)
            if pos_tuple in constraints or pos_tuple in reservation_table:
                continue
            
            if next_state in visited:
                continue
            
            new_g = g + 1
            
            if next_state not in g_cost or new_g < g_cost[next_state]:
                g_cost[next_state] = new_g
                h = manhattan_distance(next_state.pos, agent.goal)
                f = new_g + h
                
                pq.put((f, next(counter), new_g, next_state))
                parent[next_state] = current
                exploration_order.append([next_state.pos.first, next_state.pos.second, next_state.time])
    
    # No path found
    metrics = {
        "explored_size": len(visited),
        "nodes_expanded": nodes_expanded,
        "time_taken_ms": (time.time() - start_time) * 1000,
        "path_length": 0,
        "makespan": 0,
        "success": False
    }
    
    return {
        "path": None,
        "exploration_order": exploration_order,
        "metrics": metrics
    }
