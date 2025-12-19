"""
MIP/ILP MAPF Solver (CS164 Integration)
Mixed-Integer Programming for optimal solutions
Time-expanded network with binary variables
"""
from typing import Dict, Any, List, Optional, Tuple
import time as time_module
import sys
sys.path.append('..')
from utils import Agent, Pair

try:
    from pulp import *
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

def mip_solver(
    agents: List[Agent],
    blocks: List[List[bool]],
    size: int,
    max_time: int = 50
) -> Dict[str, Any]:
    """
    MIP-based MAPF solver using PuLP
    
    Args:
        agents: List of agents
        blocks: 2D grid of obstacles
        size: Grid size
        max_time: Time horizon (keep small for feasibility)
    
    Returns:
        Dictionary with optimal paths and metrics
    """
    start_time_exec = time_module.time()
    
    if not PULP_AVAILABLE:
        return {
            "paths": None,
            "exploration_orders": [],
            "metrics": {
                "explored_size": 0,
                "time_taken_ms": 0,
                "success": False,
                "num_conflicts": 0,
                "sum_of_costs": 0,
                "makespan": 0,
                "error": "PuLP library not installed"
            },
            "conflicts": []
        }
    
    # Create MIP problem
    prob = LpProblem("MAPF_MIP", LpMinimize)
    
    # Decision variables: x[i][v][t] = 1 if agent i at position v at time t
    x = {}
    for i, agent in enumerate(agents):
        x[i] = {}
        for r in range(size):
            for c in range(size):
                if not blocks[r][c]:
                    v = (r, c)
                    x[i][v] = {}
                    for t in range(max_time + 1):
                        x[i][v][t] = LpVariable(f"x_{i}_{r}_{c}_{t}", cat='Binary')
    
    # Objective: minimize sum of costs (total timesteps)
    prob += lpSum([
        t * x[i][v][t]
        for i in range(len(agents))
        for v in x[i]
        for t in range(max_time + 1)
        if v == (agents[i].goal.first, agents[i].goal.second)
    ])
    
    # Constraints
    for i, agent in enumerate(agents):
        # Start position
        start_v = (agent.start.first, agent.start.second)
        if start_v in x[i]:
            prob += x[i][start_v][0] == 1
        
        # Each agent at exactly one position per timestep
        for t in range(max_time + 1):
            prob += lpSum([x[i][v][t] for v in x[i]]) == 1
        
        # Flow conservation
        for t in range(max_time):
            for v in x[i]:
                r, c = v
                neighbors = get_neighbors_mip(r, c, size, blocks)
                neighbors.append(v)  # Can stay at same position
                
                # If at v at time t, must come from neighbor at t-1
                prob += x[i][v][t + 1] <= lpSum([
                    x[i][u][t] for u in neighbors if u in x[i]
                ])
        
        # Goal reached and stayed
        goal_v = (agent.goal.first, agent.goal.second)
        if goal_v in x[i]:
            for t in range(1, max_time + 1):
                # Once at goal, stay there
                prob += x[i][goal_v][t] >= x[i][goal_v][t - 1]
    
    # Vertex collision constraints
    for t in range(max_time + 1):
        for r in range(size):
            for c in range(size):
                if not blocks[r][c]:
                    v = (r, c)
                    # At most one agent at position v at time t
                    prob += lpSum([
                        x[i][v][t] for i in range(len(agents)) if v in x[i]
                    ]) <= 1
    
    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))
    
    solve_time = (time_module.time() - start_time_exec) * 1000
    
    if LpStatus[prob.status] != 'Optimal':
        return {
            "paths": None,
            "exploration_orders": [],
            "metrics": {
                "explored_size": 0,
                "time_taken_ms": solve_time,
                "success": False,
                "num_conflicts": 0,
                "sum_of_costs": 0,
                "makespan": 0,
                "status": LpStatus[prob.status]
            },
            "conflicts": []
        }
    
    # Extract paths
    paths = []
    max_makespan = 0
    total_cost = 0
    
    for i, agent in enumerate(agents):
        path = []
        for t in range(max_time + 1):
            for v in x[i]:
                if value(x[i][v][t]) > 0.5:
                    r, c = v
                    path.append([r, c, t])
                    break
        
        paths.append(path)
        if path:
            max_makespan = max(max_makespan, path[-1][2])
            total_cost += len(path) - 1
    
    metrics = {
        "explored_size": len(agents) * size * size * max_time,  # MIP explores full space
        "time_taken_ms": solve_time,
        "success": True,
        "num_conflicts": 0,
        "sum_of_costs": total_cost,
        "makespan": max_makespan,
        "optimal": True
    }
    
    return {
        "paths": paths,
        "exploration_orders": [],
        "metrics": metrics,
        "conflicts": []
    }

def get_neighbors_mip(r: int, c: int, size: int, blocks: List[List[bool]]) -> List[Tuple[int, int]]:
    """Get valid neighbors for MIP"""
    neighbors = []
    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size and not blocks[nr][nc]:
            neighbors.append((nr, nc))
    return neighbors
