// API URL for local development
export const API_URL = 'http://localhost:8000';

export interface Agent {
  id: number;
  start: [number, number];
  goal: [number, number];
}

export interface GenerateScenarioRequest {
  size: number;
  num_agents: number;
  obstacle_percentage: number;
  seed?: number;
}

export interface GenerateScenarioResponse {
  blocks: boolean[][];
  agents: Agent[];
}

export interface RunAlgorithmRequest {
  blocks: boolean[][];
  agents: Agent[];
  size: number;
  algorithm: string;
  max_time?: number;
  priority_policy?: string;
}

export interface RunAlgorithmResponse {
  paths: number[][][] | null;
  exploration_orders: number[][][];
  metrics: {
    explored_size: number;
    time_taken_ms: number;
    success: boolean;
    num_conflicts: number;
    sum_of_costs: number;
    makespan: number;
    [key: string]: any;
  };
  conflicts: any[];
}

export async function generateScenario(
  request: GenerateScenarioRequest
): Promise<GenerateScenarioResponse> {
  const response = await fetch(`${API_URL}/api/generate-scenario`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

export async function runAlgorithm(
  request: RunAlgorithmRequest
): Promise<RunAlgorithmResponse> {
  const response = await fetch(`${API_URL}/api/run-algorithm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
