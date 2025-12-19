"""
Independent A* (Baseline)
Each agent plans independently ignoring others
Shows why coordination is needed (collisions occur)
"""
import time
from typing import Dict, Any, List
import sys
sys.path.append('..')
from utils import Agent
from .space_time_astar import space_time_astar

def independent_astar(
    agents: List[Agent],
    blocks: List[List[bool]],
    size: int,
    max_time: int = 100
) -> Dict[str, Any]:
    """
    Independent A* - each agent plans without coordination
    
    Args:
        agents: List of agents
        blocks: 2D grid of obstacles
        size: Grid size
        max_time: Maximum time horizon
    
    Returns:
        Dictionary with paths for all agents and metrics
    """
    start_time = time.time()
    
    all_paths = []
    all_exploration_orders = []
    total_nodes_expanded = 0
    total_path_length = 0
    max_makespan = 0
    conflicts = []
    
    # Plan for each agent independently
    for agent in agents:
        result = space_time_astar(agent, blocks, size, max_time)
        
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
                    "makespan": 0
                },
                "conflicts": []
            }
        
        all_paths.append(result["path"])
        all_exploration_orders.append(result["exploration_order"])
        total_nodes_expanded += result["metrics"]["nodes_expanded"]
        total_path_length += result["metrics"]["path_length"]
        max_makespan = max(max_makespan, result["metrics"]["makespan"])
    
    # Detect conflicts
    conflicts = detect_conflicts(all_paths)
    
    metrics = {
        "explored_size": total_nodes_expanded,
        "time_taken_ms": (time.time() - start_time) * 1000,
        "success": True,
        "num_conflicts": len(conflicts),
        "sum_of_costs": total_path_length,
        "makespan": max_makespan
    }
    
    return {
        "paths": all_paths,
        "exploration_orders": all_exploration_orders,
        "metrics": metrics,
        "conflicts": conflicts
    }

def detect_conflicts(paths: List[List[List[int]]]) -> List[Dict[str, Any]]:
    """
    Detect vertex and edge conflicts between agent paths
    
    Returns:
        List of conflict dictionaries
    """
    conflicts = []
    
    if not paths or len(paths) < 2:
        return conflicts
    
    # Find max time
    max_time = max(len(path) for path in paths)
    
    for t in range(max_time):
        # Vertex conflicts: two agents at same position at same time
        positions_at_t = {}
        for agent_id, path in enumerate(paths):
            if t < len(path):
                pos = tuple(path[t][:2])  # (x, y)
                if pos in positions_at_t:
                    conflicts.append({
                        "type": "vertex",
                        "agents": [positions_at_t[pos], agent_id],
                        "time": t,
                        "location": list(pos)
                    })
                else:
                    positions_at_t[pos] = agent_id
        
        # Edge conflicts: two agents swap positions
        if t > 0:
            for i in range(len(paths)):
                for j in range(i + 1, len(paths)):
                    if t < len(paths[i]) and t < len(paths[j]):
                        # Agent i: prev_i -> curr_i
                        prev_i = tuple(paths[i][t-1][:2])
                        curr_i = tuple(paths[i][t][:2])
                        
                        # Agent j: prev_j -> curr_j
                        prev_j = tuple(paths[j][t-1][:2])
                        curr_j = tuple(paths[j][t][:2])
                        
                        # Check for swap
                        if prev_i == curr_j and prev_j == curr_i:
                            conflicts.append({
                                "type": "edge",
                                "agents": [i, j],
                                "time": t,
                                "edge": [list(prev_i), list(curr_i)]
                            })
    
    return conflicts
