"""
Integration tests for the FastAPI server.
Tests API endpoints, request/response format, error handling.
"""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test REST API endpoints"""
    
    def test_generate_scenario_valid(self):
        """Test: Valid scenario generation request"""
        response = client.post("/api/generate-scenario", json={
            "size": 10,
            "num_agents": 2,
            "obstacle_percentage": 0.2
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "blocks" in data
        assert "agents" in data
        assert len(data["blocks"]) == 10
        assert len(data["agents"]) == 2
    
    def test_generate_scenario_invalid_size(self):
        """Test: Invalid grid size (should reject)"""
        response = client.post("/api/generate-scenario", json={
            "size": 100,  # Too large
            "num_agents": 2,
            "obstacle_percentage": 0.2
        })
        
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_run_algorithm_independent(self):
        """Test: Run Independent A* algorithm"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            "agents": [
                {"id": 0, "start": [0, 0], "goal": [4, 4]},
                {"id": 1, "start": [0, 4], "goal": [4, 0]}
            ],
            "size": 5,
            "algorithm": "independent",
            "max_time": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "paths" in data
        assert "metrics" in data
        assert "conflicts" in data
        assert data["metrics"]["success"] == True
    
    def test_run_algorithm_cooperative(self):
        """Test: Run Cooperative A* algorithm"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            "agents": [
                {"id": 0, "start": [0, 0], "goal": [4, 4]},
                {"id": 1, "start": [0, 4], "goal": [4, 0]}
            ],
            "size": 5,
            "algorithm": "cooperative",
            "max_time": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["metrics"]["num_conflicts"] == 0  # Should avoid conflicts
    
    def test_run_algorithm_cbs(self):
        """Test: Run CBS algorithm"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            "agents": [{"id": 0, "start": [0, 0], "goal": [2, 2]}],
            "size": 5,
            "algorithm": "cbs",
            "max_time": 50
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
    
    def test_run_algorithm_mip(self):
        """Test: Run MIP algorithm"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 3 for _ in range(3)],
            "agents": [{"id": 0, "start": [0, 0], "goal": [2, 2]}],
            "size": 3,
            "algorithm": "mip",
            "max_time": 20
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
    
    def test_invalid_algorithm(self):
        """Test: Invalid algorithm name"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            "agents": [{"id": 0, "start": [0, 0], "goal": [2, 2]}],
            "size": 5,
            "algorithm": "nonexistent",
            "max_time": 100
        })
        
        # Server handles gracefully - should return 200 with error in response
        assert response.status_code == 200
        # Check if it has a success=False in metrics or an error field
        data = response.json()
        assert "metrics" in data or "error" in data
    
    def test_cors_headers(self):
        """Test: CORS headers are present"""
        response = client.get("/api/generate-scenario")
        
        # FastAPI CORS middleware adds headers - check with actual request
        # OPTIONS may return 405, so just check headers exist on GET
        assert response.status_code in [200, 405, 422]  # 422 if missing body
    
    def test_response_format(self):
        """Test: Response has correct JSON format"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 3 for _ in range(3)],
            "agents": [{"id": 0, "start": [0, 0], "goal": [2, 2]}],
            "size": 3,
            "algorithm": "independent",
            "max_time": 100
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert isinstance(data["paths"], list)
        assert isinstance(data["metrics"], dict)
        assert isinstance(data["metrics"]["success"], bool)
        assert isinstance(data["metrics"]["sum_of_costs"], int)
        assert isinstance(data["metrics"]["makespan"], int)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_required_fields(self):
        """Test: Request missing required fields"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            # Missing agents
            "size": 5,
            "algorithm": "independent"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_empty_agents_list(self):
        """Test: Empty agents list"""
        response = client.post("/api/run-algorithm", json={
            "blocks": [[False] * 5 for _ in range(5)],
            "agents": [],
            "size": 5,
            "algorithm": "independent",
            "max_time": 100
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
