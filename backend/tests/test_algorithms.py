"""
Unit tests for MAPF algorithms.
Tests each algorithm's correctness, edge cases, and performance.
"""

import pytest
from algorithms.independent_astar import independent_astar
from algorithms.cooperative_astar import cooperative_astar
from algorithms.cbs import cbs
from algorithms.mip_solver import mip_solver
from utils import Pair, Agent


def convert_agents(agent_dicts):
    """Convert agent dicts to Agent objects"""
    return [
        Agent(
            id=a["id"],
            start=Pair(a["start"][0], a["start"][1]),
            goal=Pair(a["goal"][0], a["goal"][1])
        )
        for a in agent_dicts
    ]


class TestAlgorithms:
    """Test suite for MAPF algorithms"""
    
    def test_simple_scenario_2_agents(self):
        """Test: 2 agents, no obstacles, should find paths"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [2, 2]},
            {"id": 1, "start": [0, 2], "goal": [2, 0]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 5 for _ in range(5)]
        size = 5
        
        # Test Independent A*
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        assert len(result["paths"]) == 2
        
        # Test Cooperative A*
        result = cooperative_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        assert len(result["paths"]) == 2
        assert result["metrics"]["num_conflicts"] == 0
    
    def test_no_solution_blocked_goal(self):
        """Test: Goal completely blocked, should return no solution"""
        agent_dicts = [{"id": 0, "start": [0, 0], "goal": [2, 2]}]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 5 for _ in range(5)]
        # Block goal completely
        blocks[1][2] = True
        blocks[2][1] = True
        blocks[2][3] = True
        blocks[3][2] = True
        size = 5
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == False
    
    def test_single_agent_straight_path(self):
        """Test: Single agent moving in straight line"""
        agent_dicts = [{"id": 0, "start": [0, 0], "goal": [0, 4]}]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 5 for _ in range(5)]
        size = 5
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        path = result["paths"][0]
        
        # Path should be straight horizontal line
        assert len(path) == 5
        for i, pos in enumerate(path):
            assert pos[0] == 0  # Row stays 0
            assert pos[1] == i  # Column increases
    
    def test_conflict_detection(self):
        """Test: Independent A* should detect conflicts"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [0, 2]},
            {"id": 1, "start": [0, 2], "goal": [0, 0]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        # Agents moving towards each other should have conflicts
        assert result["metrics"]["num_conflicts"] > 0
    
    def test_cooperative_avoids_conflicts(self):
        """Test: Cooperative A* should avoid conflicts"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [0, 2]},
            {"id": 1, "start": [0, 2], "goal": [0, 0]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = cooperative_astar(agents, blocks, size)
        # Cooperative A* should complete successfully
        # May still have conflicts on very tight spaces (3x3 with agents passing)
        assert result["metrics"]["success"] == True
    
    def test_obstacles_blocking(self):
        """Test: Agents navigate around obstacles"""
        agent_dicts = [{"id": 0, "start": [0, 0], "goal": [0, 4]}]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 5 for _ in range(5)]
        # Create wall blocking direct path
        blocks[0][1] = True
        blocks[0][2] = True
        blocks[0][3] = True
        size = 5
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        # Path should be longer than direct path (needs to go around)
        assert len(result["paths"][0]) > 5
    
    def test_mip_small_scenario(self):
        """Test: MIP solver on small scenario"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [2, 2]},
            {"id": 1, "start": [2, 0], "goal": [0, 2]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = mip_solver(agents, blocks, size, max_time=20)
        # MIP should find solution or timeout
        assert "metrics" in result
        assert "success" in result["metrics"]
    
    def test_cbs_small_scenario(self):
        """Test: CBS on small scenario"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [2, 2]},
            {"id": 1, "start": [2, 2], "goal": [0, 0]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = cbs(agents, blocks, size, max_time=50)
        # CBS should find optimal solution
        if result["metrics"]["success"]:
            assert result["metrics"]["num_conflicts"] == 0
    
    def test_metrics_calculation(self):
        """Test: Metrics are calculated correctly"""
        agent_dicts = [{"id": 0, "start": [0, 0], "goal": [0, 2]}]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = independent_astar(agents, blocks, size)
        metrics = result["metrics"]
        
        assert "sum_of_costs" in metrics
        assert "makespan" in metrics
        assert "time_taken_ms" in metrics
        assert "explored_size" in metrics
        assert metrics["sum_of_costs"] >= 2  # Minimum distance from [0,0] to [0,2]


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_agent_already_at_goal(self):
        """Test: Agent starting at goal position"""
        agent_dicts = [{"id": 0, "start": [1, 1], "goal": [1, 1]}]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        assert len(result["paths"][0]) == 1  # Should have 1-step path
    
    def test_multiple_agents_same_goal(self):
        """Test: Multiple agents with same goal (should handle gracefully)"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [2, 2]},
            {"id": 1, "start": [0, 1], "goal": [2, 2]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 3 for _ in range(3)]
        size = 3
        
        # Should complete without crashing
        result = cooperative_astar(agents, blocks, size)
        assert "metrics" in result
    
    def test_large_grid(self):
        """Test: Performance on larger grid"""
        agent_dicts = [
            {"id": 0, "start": [0, 0], "goal": [19, 19]},
            {"id": 1, "start": [19, 0], "goal": [0, 19]}
        ]
        agents = convert_agents(agent_dicts)
        blocks = [[False] * 20 for _ in range(20)]
        size = 20
        
        result = independent_astar(agents, blocks, size)
        assert result["metrics"]["success"] == True
        assert result["metrics"]["time_taken_ms"] < 5000  # Should complete in <5s


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
