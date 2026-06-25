import type {
  BenchmarkAnalytics,
  EvaluationRun,
  Scenario,
} from "./types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      body || `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}

export const api = {
  listScenarios: () => request<Scenario[]>("/scenarios"),
  listRuns: () => request<EvaluationRun[]>("/runs"),
  getAnalytics: () =>
    request<BenchmarkAnalytics>("/analytics/summary"),
  createRun: (scenarioId: string, agent: string) =>
    request<EvaluationRun>("/runs", {
      method: "POST",
      body: JSON.stringify({
        scenario_id: scenarioId,
        agent,
      }),
    }),
};
