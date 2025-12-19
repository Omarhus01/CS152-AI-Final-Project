# Multi-Agent Pathfinding (MAPF) Visualizer

A full-stack web application for visualizing and comparing Multi-Agent Pathfinding algorithms. Built with FastAPI (Python) backend and Vite + TypeScript frontend.



## About This Project

Multi-Agent Pathfinding (MAPF) finds collision-free paths for multiple agents simultaneously. Unlike single-agent pathfinding, **all agents must reach their goals without conflicts** (no two agents in same cell at same time, no edge crossing). This is an NP-hard problem.

### Implemented Algorithms

1. **Independent A*** - Fast, may show conflicts ⚡
2. **Cooperative A*** - Uses reservation table to avoid conflicts 🏃
3. **Conflict-Based Search (CBS)** - Optimal solution, exponential with agents 🐢
4. **Mixed Integer Programming (MIP)** - Provably optimal, very slow 🐌

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** or higher
- **Node.js 18** or higher  
- **npm** (comes with Node.js)

### Installation & Running

**1. Clone the repository:**
```bash
git clone https://github.com/Omarhus01/CS152-AI-Final-Project.git
cd CS152-AI-Final-Project
```

**2. Start the Backend (Terminal 1):**
```bash
cd backend
pip install -r requirements.txt
python server.py
# On macOS, you might need: python3 server.py
```
✅ Backend running at: `http://localhost:8000`

**3. Start the Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend running at: `http://localhost:5173`

**4. Open your browser:**
Navigate to `http://localhost:5173` and start visualizing!

---

## 🧪 Running Tests

All 23 tests passing! ✅

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v
```

**Test Coverage:**
- ✅ Algorithm correctness (Independent A*, Cooperative A*, CBS, MIP)
- ✅ Edge cases (blocked goals, agents at goal, large grids)
- ✅ API endpoints (generate scenario, run algorithms)
- ✅ Error handling (invalid inputs, missing fields)

---

## 🎮 How to Use

### Configuration Panel
1. **Grid Size:** 5-20 (recommended ≤15 for best performance)
2. **Number of Agents:** 1-10 (recommended ≤6)
3. **Obstacles:** 0-50% (recommended ≤30%)

### Single Algorithm Mode
1. Click **"Generate New Scenario"** to create a random grid
2. Select an algorithm from the dropdown
3. Adjust animation speed if desired
4. Click **"Run Algorithm"** to visualize the pathfinding

### Comparison Mode
1. Click **"Enable Comparison Mode"**
2. Select two different algorithms to compare
3. Click **"Run Both Algorithms"**
4. Watch them solve the same scenario side-by-side

### Understanding the Visualization
- 🟦 **Blue cells:** Obstacles
- 🟩 **Green circles:** Start positions (numbered by agent ID)
- 🎯 **Target icons:** Goal positions
- 🔴 **Red cells:** Conflicts (two agents in same cell)
- **Colored paths:** Each agent has a unique color trail

---

## 📊 Performance Recommendations

| Grid Size | Agents | Obstacles | Best Algorithms |
|-----------|--------|-----------|----------------|
| 5-10      | 2-4    | 10-20%    | All algorithms work well |
| 10-15     | 4-6    | 20-30%    | Avoid MIP (too slow) |
| 15-20     | 6-8    | 20-30%    | Independent A*, Cooperative A* only |
| >20       | >8     | >30%      | Not recommended (very slow) |

**Algorithm Performance:**
- **Independent A*:** Fastest, may have conflicts ⚡
- **Cooperative A*:** Fast, usually no conflicts 🏃
- **CBS:** Optimal, slow with many agents 🐢
- **MIP:** Optimal, very slow (grid ≤10 only) 🐌

---

## 🏗️ Project Structure

```
CS152-AI-Final-Project/
├── backend/
│   ├── algorithms/              # MAPF algorithm implementations
│   │   ├── independent_astar.py # Independent A* (fast, conflicts)
│   │   ├── cooperative_astar.py # Cooperative A* (reservation table)
│   │   ├── cbs.py              # Conflict-Based Search (optimal)
│   │   ├── mip_solver.py       # Mixed Integer Programming
│   │   └── space_time_astar.py # Core pathfinding with time dimension
│   ├── tests/                   # Comprehensive test suite (23 tests)
│   │   ├── test_algorithms.py  # Algorithm correctness tests
│   │   └── test_api.py         # API endpoint tests
│   ├── server.py               # FastAPI REST API server
│   ├── mapf_solver.py          # Main solver entry point
│   ├── utils.py                # Helper classes (Pair, Agent)
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── main.ts            # Main UI controller & visualization
│   │   ├── services/
│   │   │   └── mapfService.ts # API communication layer
│   │   ├── constants.ts       # UI constants, colors, defaults
│   │   ├── utils.ts           # Helper functions
│   │   └── style.css          # Responsive styling with Tailwind
│   ├── index.html             # Entry HTML file
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.ts         # Vite build configuration
│   └── tailwind.config.js     # Tailwind CSS configuration
│
└── README.md                   # This file
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.11+)
python --version

# If version is wrong, try python3
python3 --version

# Install dependencies
cd backend
pip install -r requirements.txt

# Run server
python server.py
```

### Frontend won't start
```bash
# Check Node.js version (need 18+)
node --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### "Failed to generate scenario" error
- ✅ Ensure backend is running on `http://localhost:8000`
- ✅ Check backend terminal for any errors
- ✅ Try with smaller parameters (grid 10, agents 2, obstacles 20%)
- ✅ Restart both frontend and backend

### Algorithms running very slowly
- Reduce grid size to 10 or less
- Reduce number of agents to 4 or less
- Avoid MIP solver for grids larger than 10
- Avoid CBS for more than 6 agents
- Lower obstacle percentage to 20%

### Port already in use
```bash
# Backend (port 8000)
# Find process: netstat -ano | findstr :8000
# Kill process: taskkill /PID <process_id> /F

# Frontend (port 5173)
# Vite will automatically try port 5174, 5175, etc.
```

---

## 📝 API Documentation

### Generate Scenario
```http
POST /api/generate-scenario
Content-Type: application/json

{
  "size": 10,
  "num_agents": 2,
  "obstacle_percentage": 0.2,
  "seed": null  // Optional: for reproducible scenarios
}
```

**Response:**
```json
{
  "blocks": [[false, false, ...], ...],
  "agents": [
    {"id": 0, "start": [0, 0], "goal": [9, 9]},
    {"id": 1, "start": [1, 1], "goal": [8, 8]}
  ]
}
```

### Run Algorithm
```http
POST /api/run-algorithm
Content-Type: application/json

{
  "blocks": [[false, false, ...], ...],
  "agents": [{"id": 0, "start": [0, 0], "goal": [9, 9]}],
  "size": 10,
  "algorithm": "cooperative",
  "max_time": 100,
  "priority_policy": "distance_first"  // Optional
}
```

**Available Algorithms:**
- `independent` - Independent A* (fast, may have conflicts)
- `cooperative` - Cooperative A* (reservation table)
- `cbs` - Conflict-Based Search (optimal)
- `mip` - Mixed Integer Programming (very slow, optimal)

**Response:**
```json
{
  "paths": [[[0,0], [1,0], [2,0], ...], ...],
  "exploration_orders": [...],
  "metrics": {
    "success": true,
    "time_taken_ms": 123.45,
    "explored_size": 500,
    "num_conflicts": 0,
    "sum_of_costs": 20,
    "makespan": 12
  },
  "conflicts": []
}
```

---

## 🤝 Contributing

This is a CS152 final project. Contributions, issues, and feature requests are welcome!

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is part of an academic assignment for CS152 - Artificial Intelligence.

---

## 👥 Authors

- **Omar Hussein** - [@Omarhus01](https://github.com/Omarhus01)

---

## 🙏 Acknowledgments

- CS152 course staff and instructors at Minerva University
- FastAPI framework for elegant Python APIs
- Vite.js for lightning-fast frontend development
- MAPF research community for algorithmic foundations
- PuLP library for linear programming support

---

## 📚 References

- **Multi-Agent Pathfinding:** Stern et al. (2019) - "Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks"
- **Conflict-Based Search:** Sharon et al. (2015) - "Conflict-based search for optimal multi-agent pathfinding"
- **Cooperative A*:** Silver (2005) - "Cooperative Pathfinding"

---

**Enjoy exploring Multi-Agent Pathfinding! 🚀**
