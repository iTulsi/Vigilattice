export type Scenario = {
  id: string;
  name: string;
  category: string;
  description: string;
  severity: string;
};

export type TraceEvent = {
  sequence: number;
  kind: string;
  action: string;
  resource: string | null;
  detail: string;
  payload: Record<string, unknown>;
  policy_tags: string[];
  timestamp: string;
};

export type EvaluationFinding = {
  code: string;
  severity: string;
  message: string;
  evidence: string;
  event_sequences: number[];
  recommendation: string;
  penalty: number;
};

export type EvaluationRun = {
  id: string;
  scenario_id: string;
  scenario_name: string;
  agent: string;
  status: string;
  created_at: string;
  trace: {
    agent: string;
    final_answer: string;
    events: TraceEvent[];
    token_count: number;
    duration_ms: number;
    metadata: Record<string, unknown>;
  };
  report: {
    passed: boolean;
    risk_level: string;
    critical_failures: string[];
    evaluation_version: string;
    scores: {
      task_completion: number;
      policy_compliance: number;
      injection_resistance: number;
      least_privilege: number;
      approval_safety: number;
      overall: number;
    };
    findings: EvaluationFinding[];
  };
};

export type AgentAnalytics = {
  agent: string;
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
  pass_rate: number;
  average_overall: number;
  average_policy: number;
  average_approval: number;
  critical_runs: number;
};

export type BenchmarkAnalytics = {
  total_scenarios: number;
  total_runs: number;
  passed_runs: number;
  failed_runs: number;
  pass_rate: number;
  average_overall: number;
  average_policy: number;
  average_approval: number;
  critical_runs: number;
  agents: AgentAnalytics[];
};

export type BatchScenarioStatus = "completed" | "error";

export type BatchScenarioResult = {
  scenario_id: string;
  scenario_name: string;
  status: BatchScenarioStatus;
  run_id: string | null;
  passed: boolean | null;
  overall_score: number | null;
  policy_score: number | null;
  approval_score: number | null;
  risk_level: string | null;
  critical_failures: string[];
  error: string | null;
};

export type BatchSummary = {
  total_scenarios: number;
  completed_runs: number;
  error_runs: number;
  passed_runs: number;
  failed_runs: number;
  pass_rate: number;
  average_overall: number;
  average_policy: number;
  average_approval: number;
  critical_runs: number;
};

export type BenchmarkBatch = {
  id: string;
  agent: string;
  started_at: string;
  completed_at: string;
  duration_ms: number;
  summary: BatchSummary;
  results: BatchScenarioResult[];
};
