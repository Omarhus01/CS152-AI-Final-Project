"""
Cooperative A* / Prioritized Planning with Reservation Table
Plan agents one-by-one, reserving space-time cells
"""
import time
from typing import Dict, Any, List, Set, Tuple
import sys
sys.path.append('..')
from utils import Agent, manhattan_distance
from .space_time_astar import space_time_astar

def cooperative_astar(
    agents: List[Agent],
    blocks: List[List[bool]],
    size: int,
    max_time: int = 100,
    priority_policy: str = "distance_first"
) -> Dict[str, Any]:
    """
    Cooperative A* with Reservation Table (Prioritized Planning)
    
    Args:
        agents: List of agents
        blocks: 2D grid of obstacles
        size: Grid size
        max_time: Maximum time horizon
        priority_policy: "distance_first", "id_order", or "random"
    
    Returns:
        Dictionary with paths for all agents and metrics
    """
    start_time = time.time()
    
    # Sort agents by priority policy
    sorted_agents = sort_agents_by_priority(agents, priority_policy)
    
    reservation_table: Set[Tuple[int, int, int]] = set()
    all_paths = []
    all_exploration_orders = []
    total_nodes_expanded = 0
    total_path_length = 0
    max_makespan = 0
    
    # Plan for each agent in priority order
    for agent in sorted_agents:
        result = space_time_astar(
            agent, 
            blocks, 
            size, 
            max_time,
            reservation_table=reservation_table
        )
        
        if result["path"] is None:
            # Agent failed to find path
            return {
                "paths": None,
                "exploration_orders": all_exploration_orders,
                "metrics": {
                    "explored_size": total_nodes_expanded,
                    "time_taken_ms": (time.time() - start_time) * 1000,
                    "success": False,
                    "num_conflicts": 0,
                    "sum_of_costs": 0,
                    "makespan": 0,
                    "priority_policy": priority_policy
                },
                "conflicts": []
            }
        
        # Add path to reservation table
        path = result["path"]
        for step in path:
            x, y, t = step
            reservation_table.add((x, y, t))
        
        # Also reserve goal position for all future times
        goal_pos = path[-1]
        for t in range(goal_pos[2] + 1, max_time):
            reservation_table.add((goal_pos[0], goal_pos[1], t))
        
        all_paths.append(path)
        all_exploration_orders.append(result["exploration_order"])
        total_nodes_expanded += result["metrics"]["nodes_expanded"]
        total_path_length += result["metrics"]["path_length"]
        max_makespan = max(max_makespan, result["metrics"]["makespan"])
    
    # Detect any remaining conflicts (should be 0)
    from .independent_astar import detect_conflicts
    conflicts = detect_conflicts(all_paths)
    
    metrics = {
        "explored_size": total_nodes_expanded,
        "time_taken_ms": (time.time() - start_time) * 1000,
        "success": True,
        "num_conflicts": len(conflicts),
        "sum_of_costs": total_path_length,
        "makespan": max_makespan,
        "priority_policy": priority_policy
    }
    
    return {
        "paths": all_paths,
        "exploration_orders": all_exploration_orders,
        "metrics": metrics,
        "conflicts": conflicts
    }

def sort_agents_by_priority(agents: List[Agent], policy: str) -> List[Agent]:
    """Sort agents based on priority policy"""
    if policy == "distance_first":
        # Agents with shorter Manhattan distance go first
        return sorted(agents, key=lambda a: manhattan_distance(a.start, a.goal))
    elif policy == "id_order":
        # Fixed ID order
        return sorted(agents, key=lambda a: a.id)
    elif policy == "random":
        import random
        shuffled = agents.copy()
        random.shuffle(shuffled)
        return shuffled
    else:
        return agents
