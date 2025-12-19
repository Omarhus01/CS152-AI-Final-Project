"""
FastAPI Server for MAPF Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import random
from mapf_solver import (
    Pair, Agent,
    independent_astar, cooperative_astar, cbs, mip_solver
)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class GenerateScenarioRequest(BaseModel):
    size: int
    num_agents: int
    obstacle_percentage: float
    seed: Optional[int] = None

class GenerateScenarioResponse(BaseModel):
    blocks: List[List[bool]]
    agents: List[dict]  # {id, start: [x,y], goal: [x,y]}

class RunAlgorithmRequest(BaseModel):
    blocks: List[List[bool]]
    agents: List[dict]
    size: int
    algorithm: str
    max_time: Optional[int] = 100
    priority_policy: Optional[str] = "distance_first"

class RunAlgorithmResponse(BaseModel):
    paths: Optional[List[List[List[int]]]]
    exploration_orders: List[List[List[int]]]
    metrics: dict
    conflicts: List[dict]

@app.get("/")
async def root():
    return {"message": "MAPF Backend API", "status": "running"}

@app.post("/api/generate-scenario", response_model=GenerateScenarioResponse)
async def generate_scenario(request: GenerateScenarioRequest):
    """Generate random MAPF scenario"""
    if request.seed is not None:
        random.seed(request.seed)
    
    size = request.size
    num_agents = request.num_agents
    obstacle_pct = request.obstacle_percentage
    
    # Generate obstacles
    blocks = [[False for _ in range(size)] for _ in range(size)]
    num_obstacles = int(size * size * obstacle_pct)
    
    obstacle_positions = set()
    while len(obstacle_positions) < num_obstacles:
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        obstacle_positions.add((r, c))
    
    for r, c in obstacle_positions:
        blocks[r][c] = True
    
    # Generate agent start/goal positions
    free_cells = []
    for r in range(size):
        for c in range(size):
            if not blocks[r][c]:
                free_cells.append((r, c))
    
    if len(free_cells) < num_agents * 2:
        # Not enough space
        return GenerateScenarioResponse(
            blocks=blocks,
            agents=[]
        )
    
    random.shuffle(free_cells)
    agents = []
    
    for i in range(num_agents):
        start_r, start_c = free_cells[i * 2]
        goal_r, goal_c = free_cells[i * 2 + 1]
        
        agents.append({
            "id": i,
            "start": [start_r, start_c],
            "goal": [goal_r, goal_c]
        })
    
    return GenerateScenarioResponse(
        blocks=blocks,
        agents=agents
    )

@app.post("/api/run-algorithm", response_model=RunAlgorithmResponse)
async def run_algorithm(request: RunAlgorithmRequest):
    """Execute MAPF algorithm"""
    # Convert agent dicts to Agent objects
    agents = [
        Agent(
            id=a["id"],
            start=Pair(a["start"][0], a["start"][1]),
            goal=Pair(a["goal"][0], a["goal"][1])
        )
        for a in request.agents
    ]
    
    blocks = request.blocks
    size = request.size
    max_time = request.max_time
    
    print(f"\n=== Running {request.algorithm} ===")
    print(f"Agents: {len(agents)}, Size: {size}, Max time: {max_time}")
    for agent in agents:
        print(f"  Agent {agent.id}: ({agent.start.first},{agent.start.second}) -> ({agent.goal.first},{agent.goal.second})")
    
    # Run selected algorithm
    if request.algorithm == "independent":
        result = independent_astar(agents, blocks, size, max_time)
    elif request.algorithm == "cooperative":
        result = cooperative_astar(
            agents, blocks, size, max_time,
            priority_policy=request.priority_policy
        )
    elif request.algorithm == "cbs":
        result = cbs(agents, blocks, size, max_time)
    elif request.algorithm == "mip":
        # MIP needs much smaller time horizons to be tractable
        # Estimate: 2 * grid_size is usually enough for optimal path
        mip_time_limit = min(max_time, size * 3, 30)
        print(f"  MIP time limit: {mip_time_limit} (reduced from {max_time})")
        result = mip_solver(agents, blocks, size, mip_time_limit)
    else:
        return RunAlgorithmResponse(
            paths=None,
            exploration_orders=[],
            metrics={"error": f"Unknown algorithm: {request.algorithm}"},
            conflicts=[]
        )
    
    print(f"Result: paths={'Found' if result.get('paths') else 'None'}, success={result.get('metrics', {}).get('success')}")
    if result.get("paths"):
        print(f"  Paths length: {len(result['paths'])}")
    print(f"=== Done ===\n")
    
    return RunAlgorithmResponse(
        paths=result.get("paths"),
        exploration_orders=result.get("exploration_orders", []),
        metrics=result.get("metrics", {}),
        conflicts=result.get("conflicts", [])
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
