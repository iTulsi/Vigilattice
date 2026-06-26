import type {
  BenchmarkAnalytics,
  BenchmarkBatch,
  EvaluationRun,
  RegressionBaseline,
  RegressionComparison,
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

async function optionalRequest<T>(path: string): Promise<T | null> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) return null;

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

  getRegressionBaseline: (agent: string) =>
    optionalRequest<RegressionBaseline>(
      `/regressions/baselines/${encodeURIComponent(agent)}`,
    ),

  setRegressionBaseline: (batchId: string) =>
    request<RegressionBaseline>(
      `/regressions/baselines/${encodeURIComponent(batchId)}`,
      { method: "POST" },
    ),

  compareBatch: (
    batchId: string,
    maxScoreDrop: number,
    maxPassRateDrop: number,
  ) => {
    const query = new URLSearchParams({
      max_score_drop: String(maxScoreDrop),
      max_pass_rate_drop: String(maxPassRateDrop),
    });

    return request<RegressionComparison>(
      `/regressions/compare/${encodeURIComponent(batchId)}?${query}`,
    );
  },

  exportRegressionUrl: (
    batchId: string,
    format: "json" | "csv",
    maxScoreDrop: number,
    maxPassRateDrop: number,
  ) => {
    const query = new URLSearchParams({
      format,
      max_score_drop: String(maxScoreDrop),
      max_pass_rate_drop: String(maxPassRateDrop),
    });

    return `${API_BASE}/regressions/compare/${encodeURIComponent(
      batchId,
    )}/export?${query}`;
  },
};
