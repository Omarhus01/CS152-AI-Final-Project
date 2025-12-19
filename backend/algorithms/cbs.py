"""
Conflict-Based Search (CBS)
High-level search over constraints
Low-level replanning with Space-Time A*
"""
import time
from typing import Dict, Any, List, Set, Tuple, Optional
from queue import PriorityQueue
from dataclasses import dataclass, field
import sys
sys.path.append('..')
from utils import Agent
from .space_time_astar import space_time_astar
from .independent_astar import detect_conflicts

@dataclass
class CBSNode:
    """High-level CBS node"""
    constraints: Set[Tuple[int, int, int, int]]  # (agent_id, x, y, t)
    paths: List[List[List[int]]]
    cost: int  # Sum of costs
    
    def __lt__(self, other):
        return self.cost < other.cost

def cbs(
    agents: List[Agent],
    blocks: List[List[bool]],
    size: int,
    max_time: int = 100,
    max_iterations: int = 1000
) -> Dict[str, Any]:
    """
    Conflict-Based Search
    
    Args:
        agents: List of agents
        blocks: 2D grid of obstacles
        size: Grid size
        max_time: Maximum time horizon
        max_iterations: Maximum CBS iterations
    
    Returns:
        Dictionary with paths for all agents and metrics
    """
    start_time = time.time()
    
    # Initialize root node with independent planning
    root_paths = []
    total_cost = 0
    
    for agent in agents:
        result = space_time_astar(agent, blocks, size, max_time)
        if result["path"] is None:
            return {
                "paths": None,
                "exploration_orders": [],
                "metrics": {
                    "explored_size": 0,
                    "time_taken_ms": (time.time() - start_time) * 1000,
                    "success": False,
                    "num_conflicts": 0,
                    "sum_of_costs": 0,
                    "makespan": 0,
                    "cbs_iterations": 0
                },
                "conflicts": []
            }
        root_paths.append(result["path"])
        total_cost += result["metrics"]["path_length"]
    
    root_node = CBSNode(
        constraints=set(),
        paths=root_paths,
        cost=total_cost
    )
    
    # High-level search
    open_list = PriorityQueue()
    open_list.put((root_node.cost, id(root_node), root_node))
    
    iterations = 0
    nodes_expanded = 0
    
    while not open_list.empty() and iterations < max_iterations:
        iterations += 1
        _, _, current_node = open_list.get()
        nodes_expanded += 1
        
        # Detect conflicts
        conflicts = detect_conflicts(current_node.paths)
        
        if not conflicts:
            # Solution found!
            max_makespan = max(len(path) - 1 for path in current_node.paths)
            
            metrics = {
                "explored_size": nodes_expanded,
                "time_taken_ms": (time.time() - start_time) * 1000,
                "success": True,
                "num_conflicts": 0,
                "sum_of_costs": current_node.cost,
                "makespan": max_makespan,
                "cbs_iterations": iterations
            }
            
            return {
                "paths": current_node.paths,
                "exploration_orders": [],
                "metrics": metrics,
                "conflicts": []
            }
        
        # Pick first conflict
        conflict = conflicts[0]
        
        # Generate two child nodes
        if conflict["type"] == "vertex":
            agent_a, agent_b = conflict["agents"]
            t = conflict["time"]
            x, y = conflict["location"]
            
            # Child 1: constrain agent A
            child1_constraints = current_node.constraints.copy()
            child1_constraints.add((agent_a, x, y, t))
            child1 = create_child_node(
                agents, blocks, size, max_time,
                child1_constraints, current_node.paths, agent_a
            )
            if child1 is not None:
                open_list.put((child1.cost, id(child1), child1))
            
            # Child 2: constrain agent B
            child2_constraints = current_node.constraints.copy()
            child2_constraints.add((agent_b, x, y, t))
            child2 = create_child_node(
                agents, blocks, size, max_time,
                child2_constraints, current_node.paths, agent_b
            )
            if child2 is not None:
                open_list.put((child2.cost, id(child2), child2))
        
        elif conflict["type"] == "edge":
            # For edge conflicts, add vertex constraints at both positions
            agent_a, agent_b = conflict["agents"]
            t = conflict["time"]
            pos1, pos2 = conflict["edge"]
            x1, y1 = pos1
            x2, y2 = pos2
            
            # Child 1: constrain agent A from moving to pos2 at time t
            child1_constraints = current_node.constraints.copy()
            child1_constraints.add((agent_a, x2, y2, t))
            child1 = create_child_node(
                agents, blocks, size, max_time,
                child1_constraints, current_node.paths, agent_a
            )
            if child1 is not None:
                open_list.put((child1.cost, id(child1), child1))
            
            # Child 2: constrain agent B from moving to pos1 at time t
            child2_constraints = current_node.constraints.copy()
            child2_constraints.add((agent_b, x1, y1, t))
            child2 = create_child_node(
                agents, blocks, size, max_time,
                child2_constraints, current_node.paths, agent_b
            )
            if child2 is not None:
                open_list.put((child2.cost, id(child2), child2))
    
    # No solution found within iteration limit
    metrics = {
        "explored_size": nodes_expanded,
        "time_taken_ms": (time.time() - start_time) * 1000,
        "success": False,
        "num_conflicts": 0,
        "sum_of_costs": 0,
        "makespan": 0,
        "cbs_iterations": iterations
    }
    
    return {
        "paths": None,
        "exploration_orders": [],
        "metrics": metrics,
        "conflicts": []
    }

def create_child_node(
    agents: List[Agent],
    blocks: List[List[bool]],
    size: int,
    max_time: int,
    constraints: Set[Tuple[int, int, int, int]],
    parent_paths: List[List[List[int]]],
    replan_agent_id: int
) -> Optional[CBSNode]:
    """
    Create child CBS node by replanning one agent with new constraints
    """
    # Convert constraints for the specific agent
    agent_constraints = set()
    for agent_id, x, y, t in constraints:
        if agent_id == replan_agent_id:
            agent_constraints.add((x, y, t))
    
    # Replan this agent
    result = space_time_astar(
        agents[replan_agent_id],
        blocks,
        size,
        max_time,
        constraints=agent_constraints
    )
    
    if result["path"] is None:
        return None  # No valid path with these constraints
    
    # Create new paths list
    new_paths = parent_paths.copy()
    new_paths[replan_agent_id] = result["path"]
    
    # Calculate total cost
    total_cost = sum(len(path) - 1 for path in new_paths)
    
    return CBSNode(
        constraints=constraints,
        paths=new_paths,
        cost=total_cost
    )
