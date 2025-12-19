# Multi-Agent Pathfinding System
## CS152 Final Project - Artificial Intelligence

**Author:** Omar Huss  
**Course:** CS152 - Artificial Intelligence  
**Project:** Multi-Agent Navigation with Conflict Resolution

---

## Project Overview

This project implements and compares multiple algorithms for Multi-Agent Pathfinding (MAPF), a fundamental challenge in AI where multiple autonomous agents must navigate to their goals while avoiding collisions. The system demonstrates:

- **Space-Time A*** pathfinding in (x,y,t) state space
- **Cooperative A*** with priority-based planning and reservation tables
- **Conflict-Based Search (CBS)** for optimal multi-agent coordination
- **MIP/ILP solver** for small-scale optimal solutions
- **Prolog-based logic** for priority policies and conflict resolution rules

### Targeted Learning Outcomes
- **#search** - Space-time A*, CBS high-level search, heuristics
- **#ailogic** - Prolog rules for prioritization, conflict resolution, deadlock detection
- **#aicoding** - Modular implementation, testing, reproducibility

---

## Key Features

✓ **Enhanced Interactive GUI** with side-by-side comparison mode  
✓ **Multiple Algorithms** - Independent A*, Cooperative A*, CBS, MIP  
✓ **Manual Controls** - Adjustable obstacle density, agent count, grid size  
✓ **Dual-Grid Comparison** - Run different algorithms simultaneously  
✓ **Conflict Detection** - Vertex and edge collision detection  
✓ **Scenario Generator** - Open field, corridors, bottlenecks, intersections  
✓ **Prolog Integration** - Logic-based decision making  
✓ **Comprehensive Metrics** - SOC, makespan, conflicts, node expansions  

---

## Installation

### Requirements
- Python 3.8+
- SWI-Prolog (optional, for logic rules)

### Setup

```bash
# Clone the repository
git clone https://github.com/Omarhus01/CS152-AI-Final-Project.git
cd CS152-AI-Final-Project

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `numpy` - Array operations
- `pygame` - GUI and visualization
- `matplotlib` - Plotting (for analysis)
- `pulp` - MIP solver
- `pyswip` - Prolog interface (optional)

---

## Usage

### Interactive GUI

Run the main application with an interactive graphical interface:

```bash
python main.py
```

**GUI Controls:**
- Select algorithm (Independent A*, Cooperative A*, CBS)
- Choose predefined scenarios (Open Field, Corridor, Bottleneck)
- Play/Pause/Step through animations
- Toggle agent trails
- View real-time metrics

**Keyboard Shortcuts:**
- `SPACE` - Play/Pause
- `→` - Step forward
- `←` - Step backward
- `R` - Reset

### Command-Line Options

```bash
# Run with specific scenario
python main.py --scenario corridor --agents 6 --grid-size 20

# Run with reproducible seed
python main.py --scenario bottleneck --agents 8 --seed 42
```

### Algorithm Comparison

Run automated benchmarks comparing all algorithms:

```bash
# Compare algorithms on multiple scenarios
python compare.py --scenarios 5 --agents 4 6 8 --output results.json

# Run with specific parameters
python compare.py --scenarios 3 --agents 6 --grid-size 15 --seed 123
```

This generates:
- Console output with metrics
- JSON file with detailed results
- Comparison data for analysis

### Running Tests

```bash
# Run all unit tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_core
```

---

## Project Structure

```
CS152-AI-Final-Project/
├── src/
│   ├── core/
│   │   ├── grid.py              # Grid environment
│   │   ├── agent.py             # Agent representation
│   │   ├── conflict.py          # Conflict detection
│   │   └── reservation.py       # Reservation table
│   ├── algorithms/
│   │   ├── space_time_astar.py  # Space-Time A*
│   │   ├── independent.py       # Independent A* baseline
│   │   ├── cooperative.py       # Cooperative A*
│   │   ├── cbs.py               # Conflict-Based Search
│   │   └── mip_solver.py        # MIP/ILP solver
│   ├── logic/
│   │   └── prolog_rules.py      # Prolog logic integration
│   ├── gui/
│   │   └── mapf_gui.py          # Pygame GUI
│   └── scenarios/
│       └── generator.py         # Scenario generation
├── tests/
│   └── test_core.py             # Unit tests
├── main.py                      # Main GUI application
├── compare.py                   # Comparison runner
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

---

## Algorithms

### 1. Independent A* (Baseline)
Plans each agent independently using Space-Time A*, ignoring other agents. Shows why coordination is necessary by demonstrating conflicts.

### 2. Cooperative A* (Prioritized Planning)
Plans agents sequentially in priority order, using a reservation table to avoid conflicts with previously planned agents.

**Priority Policies:**
- Distance-first: Shortest paths planned first
- Constrained-first: Agents in narrow areas planned first
- Logic-based: Prolog rules determine ordering

### 3. Conflict-Based Search (CBS)
Optimal multi-agent planner using two-level search:
- **High-level**: Best-first search over constraint trees
- **Low-level**: Space-Time A* replanning for conflicting agents

### 4. MIP/ILP Solver (CS164 Integration)
Mixed-integer programming formulation for optimal solutions on small instances (≤8 agents). Used as benchmark for optimality gap analysis.

---

## Scenarios

### Open Field
Random obstacles with agents navigating across the grid. Tests general coordination under low conflict pressure.

### Corridor
Narrow horizontal corridor forcing agents to coordinate passing and yielding. High conflict potential.

### Bottleneck
Wall with small opening in the middle. Agents must queue and coordinate passage through chokepoint.

### Intersection
Perpendicular corridors meeting at a central point. Tests intersection coordination and deadlock avoidance.

---

## Metrics

The system tracks comprehensive metrics:

- **Success Rate** - Percentage of agents reaching goals
- **Sum of Costs (SOC)** - Total path lengths
- **Makespan** - Time until all agents reach goals
- **Conflicts** - Number of vertex and edge collisions
- **Node Expansions** - A* search effort
- **Runtime** - Algorithm execution time
- **Optimality Gap** - Difference from MIP optimal solution

---

## Example Results

```
Scenario: Corridor with 6 agents

Independent A*:
  Runtime: 0.023s
  SOC: 84
  Conflicts: 12
  Success: False

Cooperative A*:
  Runtime: 0.067s
  SOC: 96
  Conflicts: 0
  Success: True

CBS:
  Runtime: 0.234s
  SOC: 92
  Conflicts: 0
  Success: True
```

---

## Development

### Adding New Algorithms

1. Create a new file in `src/algorithms/`
2. Implement `plan(agents) -> (paths, metrics)` method
3. Add to GUI and comparison runner

### Adding New Scenarios

1. Add method to `ScenarioGenerator` class
2. Return `(GridMap, List[Agent])` tuple
3. Add button/option in GUI

---

## Report

The accompanying report (max 3 pages) covers:

1. **Problem Definition** - Multi-agent navigation with conflicts
2. **Solution Specification** - Algorithm descriptions and implementation
3. **Analysis** - Experimental results on test scenarios
4. **References** - Academic papers and resources
5. **Appendices** - Code, original proposal, HC/LO justification

---

## References

- Sharon, G., et al. (2015). "Conflict-Based Search For Optimal Multi-Agent Path Finding"
- Silver, D. (2005). "Cooperative Pathfinding"
- Hart, P., et al. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"

---

## License

This project is for educational purposes as part of CS152 coursework.

---

## Acknowledgments

**Professor:** Rohan Shekhar  
**Institution:** Minerva University  
**Course:** CS152 - Artificial Intelligence

---

## Contact

Omar Huss  
GitHub: [@Omarhus01](https://github.com/Omarhus01)
