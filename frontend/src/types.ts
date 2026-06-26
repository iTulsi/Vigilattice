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

export type ScenarioRegressionStatus =
  | "new_failure"
  | "recovered"
  | "unchanged_pass"
  | "unchanged_fail"
  | "missing"
  | "new_scenario";

export type RegressionBaseline = {
  id: string;
  agent: string;
  batch_id: string;
  created_at: string;
  batch: BenchmarkBatch;
};

export type RegressionThresholds = {
  max_score_drop: number;
  max_pass_rate_drop: number;
};

export type RegressionDeltas = {
  pass_rate: number;
  average_overall: number;
  average_policy: number;
  average_approval: number;
  critical_runs: number;
  error_runs: number;
};

export type ScenarioRegression = {
  scenario_id: string;
  scenario_name: string;
  status: ScenarioRegressionStatus;
  baseline_passed: boolean | null;
  candidate_passed: boolean | null;
  baseline_score: number | null;
  candidate_score: number | null;
  score_delta: number | null;
  baseline_risk: string | null;
  candidate_risk: string | null;
};

export type RegressionComparison = {
  baseline_id: string;
  baseline_batch_id: string;
  candidate_batch_id: string;
  agent: string;
  generated_at: string;
  thresholds: RegressionThresholds;
  deltas: RegressionDeltas;
  regressed: boolean;
  reasons: string[];
  newly_failing_scenarios: string[];
  recovered_scenarios: string[];
  missing_scenarios: string[];
  scenarios: ScenarioRegression[];
};
