import './style.css';
import {
  DEFAULT_SIZE,
  DEFAULT_AGENTS,
  DEFAULT_OBSTACLE_PCT,
  OBSTACLE_COLOR,
  EMPTY_CELL_COLOR,
  AGENT_COLORS,
  ANIMATION_DELAY,
} from './constants';
import { sleep } from './utils';
import {
  generateScenario,
  runAlgorithm,
  type Agent,
  type RunAlgorithmResponse,
} from './services/mapfService';

class MAPFApp {
  private size: number = DEFAULT_SIZE;
  private numAgents: number = DEFAULT_AGENTS;
  private obstaclePct: number = DEFAULT_OBSTACLE_PCT;
  private blocks: boolean[][] = [];
  private agents: Agent[] = [];
  
  // Comparison mode
  private comparisonMode: boolean = false;
  private leftAlgorithm: string = 'independent';
  private rightAlgorithm: string = 'cooperative';
  
  // Animation state
  private isAnimating: boolean = false;
  private animationSpeed: number = ANIMATION_DELAY;

  constructor() {
    this.setupUI();
    this.generateNewScenario();
  }

  private setupUI() {
    const app = document.getElementById('app')!;
    
    app.innerHTML = `
      <h1>Multi-Agent Pathfinding Visualizer</h1>
      
      <div class="card mb-4" style="background: #f0f9ff; border-left: 4px solid #3b82f6;">
        <h3 style="color: #1e40af; margin-bottom: 0.5rem;">📘 About This Project</h3>
        <p style="margin: 0; color: #1e3a8a;">
          Multi-Agent Pathfinding (MAPF) finds collision-free paths for multiple agents simultaneously. 
          Unlike single-agent pathfinding, <strong>all agents must reach their goals without conflicts</strong> 
          (no two agents in same cell at same time, no edge crossing). This is an NP-hard problem.
        </p>
      </div>
      
      <!-- Horizontal layout: Config on top, Grid below -->
      <div>
        
        <!-- TOP: Configuration Panel (Horizontal) -->
        <div class="card" style="padding: 2rem; margin-bottom: 2rem;">
          <h2 style="font-size: 2rem; margin-bottom: 1.5rem; font-weight: bold;">Configuration</h2>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
            <div>
              <label class="block mb-2 font-semibold" style="font-size: 1.2rem;">Grid Size: <span id="size-value">${this.size}</span></label>
              <input type="range" id="size-slider" class="slider" min="5" max="20" value="${this.size}" style="height: 8px;" />
            </div>
            
            <div>
              <label class="block mb-2 font-semibold" style="font-size: 1.2rem;">Number of Agents: <span id="agents-value">${this.numAgents}</span></label>
              <input type="range" id="agents-slider" class="slider" min="1" max="8" value="${this.numAgents}" style="height: 8px;" />
            </div>
            
            <div>
              <label class="block mb-2 font-semibold" style="font-size: 1.2rem;">Obstacles: <span id="obstacle-value">${Math.round(this.obstaclePct * 100)}%</span></label>
              <input type="range" id="obstacle-slider" class="slider" min="0" max="50" value="${this.obstaclePct * 100}" style="height: 8px;" />
            </div>
          </div>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
            <button id="generate-btn" class="btn btn-primary w-full" style="padding: 1rem; font-size: 1.2rem; font-weight: bold;">Generate New Scenario</button>
            <button id="comparison-toggle" class="btn btn-secondary w-full" style="padding: 1rem; font-size: 1.2rem; font-weight: bold;">Enable Comparison Mode</button>
          </div>
          
          <!-- Single Algorithm Config -->
          <div id="single-config">
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem; font-weight: bold;">Algorithm Settings</h3>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; align-items: end;">
              <div>
                <label class="block mb-2 font-semibold" style="font-size: 1.1rem;">Algorithm:</label>
                <select id="algorithm-select" class="w-full" style="padding: 0.75rem; font-size: 1.1rem;">
                  <option value="independent">Independent A*</option>
                  <option value="cooperative" selected>Cooperative A*</option>
                  <option value="cbs">CBS</option>
                  <option value="mip">MIP Solver</option>
                </select>
              </div>
              
              <div>
                <label class="block mb-2 font-semibold" style="font-size: 1.1rem;">Animation Speed: <span id="speed-value">Medium</span></label>
                <input type="range" id="speed-slider" class="slider" min="10" max="200" value="${200 - this.animationSpeed}" style="height: 8px;" />
              </div>
            </div>
            
            <div id="algorithm-info" class="mt-4 mb-4 p-4 rounded" style="background: #fef3c7; border-left: 4px solid #f59e0b;">
              <p class="mb-0" style="color: #92400e; line-height: 1.6; font-size: 1.05rem;">
                <strong style="font-size: 1.1rem;">💡 Recommended:</strong>
                <span id="algo-recommendation">Grid ≤15, Agents ≤6, Obstacles ≤30%</span>
              </p>
            </div>
            
            <button id="run-single-btn" class="btn btn-success w-full" style="padding: 1.2rem; font-size: 1.3rem; font-weight: bold;">Run Algorithm</button>
          </div>
          
          <!-- Comparison Algorithm Config -->
          <div id="comparison-config" class="hidden">
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem; font-weight: bold;">Algorithm Settings</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin-bottom: 1.5rem;">
              <div>
                <label class="block mb-2 font-semibold" style="font-size: 1.1rem;">Left Algorithm:</label>
                <select id="left-algorithm-select" class="w-full" style="padding: 0.75rem; font-size: 1.1rem;">
                  <option value="independent" selected>Independent A*</option>
                  <option value="cooperative">Cooperative A*</option>
                  <option value="cbs">CBS</option>
                  <option value="mip">MIP Solver</option>
                </select>
              </div>
              
              <div>
                <label class="block mb-2 font-semibold" style="font-size: 1.1rem;">Right Algorithm:</label>
                <select id="right-algorithm-select" class="w-full" style="padding: 0.75rem; font-size: 1.1rem;">
                  <option value="independent">Independent A*</option>
                  <option value="cooperative" selected>Cooperative A*</option>
                  <option value="cbs">CBS</option>
                  <option value="mip">MIP Solver</option>
                </select>
              </div>
              
              <div>
                <label class="block mb-2 font-semibold" style="font-size: 1.1rem;">Animation Speed: <span id="comparison-speed-value">Medium</span></label>
                <input type="range" id="comparison-speed-slider" class="slider" min="10" max="200" value="${200 - this.animationSpeed}" style="height: 8px;" />
              </div>
            </div>
            
            <div class="mt-4 mb-4 p-4 rounded" style="background: #fef3c7; border-left: 4px solid #f59e0b;">
              <p class="mb-0" style="color: #92400e; line-height: 1.6; font-size: 1.05rem;">
                <strong style="font-size: 1.1rem;">💡 Recommended:</strong> Grid ≤15, Agents ≤6, Obstacles ≤30% • Balanced speed and quality
              </p>
            </div>
            
            <button id="run-comparison-btn" class="btn btn-success w-full" style="padding: 1.2rem; font-size: 1.3rem; font-weight: bold;">Run Both Algorithms</button>
          </div>
        </div>
        
        <!-- BOTTOM: Grid Visualization (Full Width) -->
        <div>
          <div id="single-mode">
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
              <div class="card">
                <h2 style="font-size: 1.8rem; margin-bottom: 1rem;">Visualization</h2>
                <div id="single-grid-container" class="mt-4"></div>
              </div>
              <div>
                <div id="single-metrics"></div>
              </div>
            </div>
          </div>
          
          <div id="comparison-mode" class="hidden">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
              <div class="card">
                <h3 style="font-size: 1.5rem;">Left Grid</h3>
                <div id="left-grid-container"></div>
                <div id="left-metrics-sidebar" class="mt-4"></div>
              </div>
              
              <div class="card">
                <h3 style="font-size: 1.5rem;">Right Grid</h3>
                <div id="right-grid-container"></div>
                <div id="right-metrics-sidebar" class="mt-4"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    this.attachEventListeners();
  }

  private attachEventListeners() {
    // Sliders
    document.getElementById('size-slider')!.addEventListener('input', (e) => {
      this.size = parseInt((e.target as HTMLInputElement).value);
      document.getElementById('size-value')!.textContent = this.size.toString();
    });
    
    document.getElementById('agents-slider')!.addEventListener('input', (e) => {
      this.numAgents = parseInt((e.target as HTMLInputElement).value);
      document.getElementById('agents-value')!.textContent = this.numAgents.toString();
    });
    
    document.getElementById('obstacle-slider')!.addEventListener('input', (e) => {
      this.obstaclePct = parseInt((e.target as HTMLInputElement).value) / 100;
      document.getElementById('obstacle-value')!.textContent = Math.round(this.obstaclePct * 100) + '%';
    });
    
    document.getElementById('speed-slider')!.addEventListener('input', (e) => {
      const sliderValue = parseInt((e.target as HTMLInputElement).value);
      this.animationSpeed = 210 - sliderValue; // Invert: higher slider = faster (lower delay)
      
      // Update label
      const speedLabel = document.getElementById('speed-value')!;
      if (this.animationSpeed < 50) speedLabel.textContent = 'Very Fast';
      else if (this.animationSpeed < 100) speedLabel.textContent = 'Fast';
      else if (this.animationSpeed < 150) speedLabel.textContent = 'Medium';
      else speedLabel.textContent = 'Slow';
    });
    
    // Comparison speed slider
    document.getElementById('comparison-speed-slider')!.addEventListener('input', (e) => {
      const sliderValue = parseInt((e.target as HTMLInputElement).value);
      this.animationSpeed = 210 - sliderValue;
      
      const speedLabel = document.getElementById('comparison-speed-value')!;
      if (this.animationSpeed < 50) speedLabel.textContent = 'Very Fast';
      else if (this.animationSpeed < 100) speedLabel.textContent = 'Fast';
      else if (this.animationSpeed < 150) speedLabel.textContent = 'Medium';
      else speedLabel.textContent = 'Slow';
    });
    
    // Algorithm change handler
    document.getElementById('algorithm-select')!.addEventListener('change', (e) => {
      this.updateAlgorithmRecommendation((e.target as HTMLSelectElement).value);
    });
    
    // Initialize recommendation
    this.updateAlgorithmRecommendation('cooperative');
    
    // Buttons
    document.getElementById('generate-btn')!.addEventListener('click', () => {
      this.generateNewScenario();
    });
    
    document.getElementById('comparison-toggle')!.addEventListener('click', () => {
      this.toggleComparisonMode();
    });
    
    document.getElementById('run-single-btn')!.addEventListener('click', () => {
      this.runSingleAlgorithm();
    });
    
    document.getElementById('run-comparison-btn')!.addEventListener('click', () => {
      this.runComparison();
    });
    
    // Algorithm selects
    document.getElementById('left-algorithm-select')!.addEventListener('change', (e) => {
      this.leftAlgorithm = (e.target as HTMLSelectElement).value;
    });
    
    document.getElementById('right-algorithm-select')!.addEventListener('change', (e) => {
      this.rightAlgorithm = (e.target as HTMLSelectElement).value;
    });
  }

  private updateAlgorithmRecommendation(algorithm: string) {
    const recommendations: { [key: string]: string } = {
      'independent': 'Grid ≤20, Agents ≤8, Obstacles ≤40% • Fast, shows conflicts for analysis',
      'cooperative': 'Grid ≤15, Agents ≤6, Obstacles ≤30% • Balanced speed and quality',
      'cbs': 'Grid ≤12, Agents ≤4, Obstacles ≤25% • Slow but optimal, avoid large scenarios',
      'mip': 'Grid ≤10, Agents ≤3, Obstacles ≤20% • VERY SLOW, only for small problems'
    };
    
    const recommendationEl = document.getElementById('algo-recommendation');
    if (recommendationEl) {
      recommendationEl.textContent = recommendations[algorithm] || recommendations['cooperative'];
    }
  }

  private toggleComparisonMode() {
    this.comparisonMode = !this.comparisonMode;
    
    const singleMode = document.getElementById('single-mode')!;
    const comparisonModeDiv = document.getElementById('comparison-mode')!;
    const singleConfig = document.getElementById('single-config')!;
    const comparisonConfig = document.getElementById('comparison-config')!;
    const toggleBtn = document.getElementById('comparison-toggle')!;
    
    if (this.comparisonMode) {
      singleMode.classList.add('hidden');
      comparisonModeDiv.classList.remove('hidden');
      singleConfig.classList.add('hidden');
      comparisonConfig.classList.remove('hidden');
      toggleBtn.textContent = 'Disable Comparison Mode';
      toggleBtn.classList.remove('btn-secondary');
      toggleBtn.classList.add('btn-danger');
      this.renderGrid('left-grid-container');
      this.renderGrid('right-grid-container');
    } else {
      singleMode.classList.remove('hidden');
      comparisonModeDiv.classList.add('hidden');
      singleConfig.classList.remove('hidden');
      comparisonConfig.classList.add('hidden');
      toggleBtn.textContent = 'Enable Comparison Mode';
      toggleBtn.classList.remove('btn-danger');
      toggleBtn.classList.add('btn-secondary');
      this.renderGrid('single-grid-container');
    }
  }

  private async generateNewScenario() {
    try {
      const response = await generateScenario({
        size: this.size,
        num_agents: this.numAgents,
        obstacle_percentage: this.obstaclePct,
        seed: Date.now(),
      });
      
      this.blocks = response.blocks;
      this.agents = response.agents;
      
      if (this.comparisonMode) {
        this.renderGrid('left-grid-container');
        this.renderGrid('right-grid-container');
      } else {
        this.renderGrid('single-grid-container');
      }
      
      this.showAlert('New scenario generated!', 'success');
    } catch (error) {
      console.error('Error generating scenario:', error);
      this.showAlert('Failed to generate scenario', 'error');
    }
  }

  private renderGrid(containerId: string) {
    const container = document.getElementById(containerId)!;
    container.innerHTML = '';
    
    const gridDiv = document.createElement('div');
    gridDiv.className = 'grid-container';
    gridDiv.style.gridTemplateColumns = `repeat(${this.size}, 1fr)`;
    gridDiv.style.gridTemplateRows = `repeat(${this.size}, 1fr)`;
    gridDiv.style.maxHeight = '70vh';
    gridDiv.style.aspectRatio = '1';
    
    for (let r = 0; r < this.size; r++) {
      for (let c = 0; c < this.size; c++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.id = `${containerId}-cell-${r}-${c}`;
        
        if (this.blocks[r][c]) {
          cell.classList.add('obstacle');
          cell.style.backgroundColor = OBSTACLE_COLOR;
        } else {
          cell.style.backgroundColor = EMPTY_CELL_COLOR;
        }
        
        // Check if this is a start or goal for any agent
        for (const agent of this.agents) {
          if (agent.start[0] === r && agent.start[1] === c) {
            cell.style.backgroundColor = AGENT_COLORS[agent.id % AGENT_COLORS.length];
            const marker = document.createElement('div');
            marker.className = 'agent-marker';
            marker.style.backgroundColor = AGENT_COLORS[agent.id % AGENT_COLORS.length];
            marker.textContent = `S${agent.id}`;
            cell.appendChild(marker);
          }
          
          if (agent.goal[0] === r && agent.goal[1] === c) {
            cell.style.backgroundColor = AGENT_COLORS[agent.id % AGENT_COLORS.length];
            cell.style.opacity = '0.5';
            const marker = document.createElement('div');
            marker.className = 'agent-marker';
            marker.style.backgroundColor = AGENT_COLORS[agent.id % AGENT_COLORS.length];
            marker.textContent = `G${agent.id}`;
            cell.appendChild(marker);
          }
        }
        
        gridDiv.appendChild(cell);
      }
    }
    
    container.appendChild(gridDiv);
  }

  private async runSingleAlgorithm() {
    if (this.isAnimating) return;
    
    const algorithmSelect = document.getElementById('algorithm-select') as HTMLSelectElement;
    const algorithm = algorithmSelect.value;
    
    this.isAnimating = true;
    this.renderGrid('single-grid-container');
    
    try {
      const result = await runAlgorithm({
        blocks: this.blocks,
        agents: this.agents,
        size: this.size,
        algorithm: algorithm,
        max_time: 100,
      });
      
      console.log('Algorithm result:', result);
      
      if (result.paths && result.paths.length > 0) {
        await this.animatePaths(result.paths, 'single-grid-container', result.conflicts || []);
        this.displayMetrics(result, 'single-metrics');
        
        // Show conflict warning for Independent A*
        if (algorithm === 'independent' && result.conflicts && result.conflicts.length > 0) {
          this.showAlert(`Solution found with ${result.conflicts.length} conflicts! Red cells show collisions.`, 'info');
        } else {
          this.showAlert(`Solution found! SOC: ${result.metrics.sum_of_costs}`, 'success');
        }
      } else {
        this.displayMetrics(result, 'single-metrics');
        this.showAlert(`No solution found! Reason: ${result.metrics.success === false ? 'Path blocked or agents stuck' : 'Unknown'}`, 'error');
      }
    } catch (error) {
      console.error('Error running algorithm:', error);
      this.showAlert('Algorithm execution failed', 'error');
    }
    
    this.isAnimating = false;
  }

  private async runComparison() {
    if (this.isAnimating) return;
    
    this.isAnimating = true;
    this.renderGrid('left-grid-container');
    this.renderGrid('right-grid-container');
    
    try {
      // Run both algorithms
      const [leftResult, rightResult] = await Promise.all([
        runAlgorithm({
          blocks: this.blocks,
          agents: this.agents,
          size: this.size,
          algorithm: this.leftAlgorithm,
          max_time: 100,
        }),
        runAlgorithm({
          blocks: this.blocks,
          agents: this.agents,
          size: this.size,
          algorithm: this.rightAlgorithm,
          max_time: 100,
        }),
      ]);
      
      console.log('Left result:', leftResult);
      console.log('Right result:', rightResult);
      
      // Animate both simultaneously
      await Promise.all([
        leftResult.paths && leftResult.paths.length > 0 ? this.animatePaths(leftResult.paths, 'left-grid-container', leftResult.conflicts || []) : Promise.resolve(),
        rightResult.paths && rightResult.paths.length > 0 ? this.animatePaths(rightResult.paths, 'right-grid-container', rightResult.conflicts || []) : Promise.resolve(),
      ]);
      
      // Display metrics in sidebar
      this.displayMetrics(leftResult, 'left-metrics-sidebar', 'Left Algorithm');
      this.displayMetrics(rightResult, 'right-metrics-sidebar', 'Right Algorithm');
      
      if (leftResult.paths && rightResult.paths) {
        this.showAlert('Both solutions found!', 'success');
      } else if (!leftResult.paths && !rightResult.paths) {
        this.showAlert('Both algorithms failed to find solution', 'error');
      } else {
        this.showAlert('One algorithm found solution, one failed', 'info');
      }
      
    } catch (error) {
      console.error('Error running comparison:', error);
      this.showAlert('Comparison execution failed', 'error');
    }
    
    this.isAnimating = false;
  }

  private async animatePaths(paths: number[][][], containerId: string, conflicts: any[] = []) {
    const maxTime = Math.max(...paths.map(path => path.length));
    
    // Create conflict lookup by time for faster access
    const conflictsByTime = new Map<number, any[]>();
    conflicts.forEach(conflict => {
      if (!conflictsByTime.has(conflict.time)) {
        conflictsByTime.set(conflict.time, []);
      }
      conflictsByTime.get(conflict.time)!.push(conflict);
    });
    
    // Collect all conflict cells to highlight at the end
    const conflictCells = new Set<string>();
    conflicts.forEach(conflict => {
      if (conflict.type === 'vertex') {
        conflictCells.add(`${conflict.location[0]},${conflict.location[1]},${conflict.time}`);
      }
    });
    
    for (let t = 0; t < maxTime; t++) {
      for (let agentId = 0; agentId < paths.length; agentId++) {
        if (t < paths[agentId].length) {
          const [r, c] = paths[agentId][t];
          const cellId = `${containerId}-cell-${r}-${c}`;
          const cell = document.getElementById(cellId);
          
          if (cell && !cell.querySelector('.agent-marker')) {
            // Check if this cell is part of a conflict at this time
            const conflictKey = `${r},${c},${t}`;
            const hasConflict = conflictCells.has(conflictKey);
            
            // Highlight conflicts with red/warning color
            if (hasConflict) {
              cell.style.backgroundColor = '#ef4444'; // Red for conflict
              cell.style.border = '3px solid #dc2626';
              cell.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.6)';
              cell.setAttribute('data-conflict', 'true'); // Mark for later
            } else {
              cell.style.backgroundColor = AGENT_COLORS[agentId % AGENT_COLORS.length];
              cell.style.opacity = '0.7';
            }
          }
        }
      }
      await sleep(this.animationSpeed);
    }
    
    // After animation, re-highlight conflict cells
    conflicts.forEach(conflict => {
      if (conflict.type === 'vertex') {
        const [r, c] = conflict.location;
        const cellId = `${containerId}-cell-${r}-${c}`;
        const cell = document.getElementById(cellId);
        if (cell) {
          cell.style.backgroundColor = '#ef4444';
          cell.style.border = '3px solid #dc2626';
          cell.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.8)';
        }
      }
    });
  }

  private displayMetrics(result: RunAlgorithmResponse, containerId: string, title?: string) {
    const container = document.getElementById(containerId)!;
    
    const metrics = result.metrics;
    
    container.innerHTML = `
      ${title ? `<h3 class="mb-4" style="font-size: 1.5rem; color: #e5e7eb; font-weight: bold;">${title}</h3>` : '<h3 class="mb-4" style="font-size: 1.6rem; font-weight: bold;">Performance Metrics</h3>'}
      <div class="card" style="background: #1f2937; padding: 1.5rem;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">SUCCESS</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: ${metrics.success ? '#10b981' : '#ef4444'};">
              ${metrics.success ? 'Yes' : 'No'}
            </div>
          </div>
          
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">SUM OF COSTS</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #3b82f6;">${metrics.sum_of_costs}</div>
          </div>
          
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">MAKESPAN</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #a855f7;">${metrics.makespan}</div>
          </div>
          
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">CONFLICTS</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #f97316;">${metrics.num_conflicts || 0}</div>
          </div>
          
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">TIME (MS)</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #10b981;">${metrics.time_taken_ms.toFixed(2)}</div>
          </div>
          
          <div style="background: #374151; padding: 1.25rem; border-radius: 0.5rem;">
            <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 0.5rem; letter-spacing: 0.08em; font-weight: 700;">NODES EXPLORED</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #6366f1;">${metrics.explored_size}</div>
          </div>
        </div>
      </div>
      
      ${result.conflicts && result.conflicts.length > 0 ? `
        <div class="mt-3 p-3 rounded" style="background: #fee2e2; border-left: 3px solid #ef4444;">
          <h4 class="font-semibold mb-2" style="color: #991b1b; font-size: 0.9rem;">🚨 Conflicts Detected:</h4>
          <p class="text-xs mb-2" style="color: #7f1d1d;"><em>Note: Vertex conflicts (same cell, same time) are highlighted in red on grid.</em></p>
          <ul class="text-sm" style="color: #7f1d1d; max-height: 150px; overflow-y: auto;">
            ${result.conflicts.slice(0, 5).map((conflict: any) => {
              if (conflict.type === 'vertex') {
                return `<li>• <strong>Vertex conflict</strong> at time ${conflict.time}: Agents ${conflict.agents.join(' & ')} both at (${conflict.location.join(',')}) <span style="color: #ef4444;">●</span></li>`;
              } else {
                return `<li>• <strong>Edge conflict</strong> at time ${conflict.time}: Agents ${conflict.agents.join(' & ')} swapping</li>`;
              }
            }).join('')}
            ${result.conflicts.length > 5 ? `<li>• ... and ${result.conflicts.length - 5} more conflicts</li>` : ''}
          </ul>
        </div>
      ` : ''}
    `;
  }

  private showAlert(message: string, type: 'success' | 'error' | 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
      alert.remove();
    }, 3000);
  }
}

// Initialize app
new MAPFApp();
