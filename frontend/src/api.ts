import type {
  BenchmarkAnalytics,
  BenchmarkBatch,
  EvaluationRun,
  Scenario,
} from "./types";

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  headers.set("Content-Type", "application/json");

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    let message = body || `Request failed with status ${response.status}`;

    try {
      const parsed = JSON.parse(body) as { detail?: string };
      if (parsed.detail) message = parsed.detail;
    } catch {
      // Preserve the plain-text response when the body is not JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  listScenarios: () => request<Scenario[]>("/scenarios"),
  listRuns: () => request<EvaluationRun[]>("/runs"),
  getAnalytics: () => request<BenchmarkAnalytics>("/analytics/summary"),

  createRun: (scenarioId: string, agent: string) =>
    request<EvaluationRun>("/runs", {
      method: "POST",
      body: JSON.stringify({
        scenario_id: scenarioId,
        agent,
      }),
    }),

  listBatches: () => request<BenchmarkBatch[]>("/batches"),

  createBatch: (agent: string, scenarioIds?: string[]) =>
    request<BenchmarkBatch>("/batches", {
      method: "POST",
      body: JSON.stringify({
        agent,
        ...(scenarioIds ? { scenario_ids: scenarioIds } : {}),
      }),
    }),

  exportBatchUrl: (batchId: string, format: "json" | "csv") =>
    `${API_BASE}/batches/${encodeURIComponent(batchId)}/export?format=${format}`,
};
