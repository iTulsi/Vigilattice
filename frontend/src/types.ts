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
