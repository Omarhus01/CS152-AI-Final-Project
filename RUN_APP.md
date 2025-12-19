# MAPF Visualizer - Quick Start

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```

Backend runs at http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Usage

1. **Configure Scenario**: Use sliders to set grid size, number of agents, and obstacle percentage
2. **Generate Scenario**: Click "Generate New Scenario" to create a random MAPF problem
3. **Single Algorithm Mode**: 
   - Select algorithm from dropdown
   - Click "Run Algorithm"
   - Watch animation and view metrics
4. **Comparison Mode**:
   - Click "Enable Comparison Mode"
   - Select different algorithms for left and right grids
   - Click "Run Both Algorithms"
   - Compare performance side-by-side

## Algorithms

- **Independent A***: Baseline (shows conflicts)
- **Cooperative A***: Prioritized planning with reservation table
- **CBS**: Conflict-Based Search (optimal)
- **MIP**: Mixed-Integer Programming (optimal, small scenarios only)

## Features

- Interactive grid visualization
- Real-time animation
- Side-by-side algorithm comparison
- Performance metrics (SOC, makespan, conflicts, runtime)
- Adjustable animation speed
- Random scenario generation
