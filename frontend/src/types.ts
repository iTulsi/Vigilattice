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
};

export type EvaluationRun = {
  id: string;
  scenario_id: string;
  scenario_name: string;
  agent: string;
  created_at: string;
  trace: {
    events: TraceEvent[];
    token_count: number;
    duration_ms: number;
  };
  report: {
    passed: boolean;
    scores: {
      task_completion: number;
      policy_compliance: number;
      injection_resistance: number;
      least_privilege: number;
      overall: number;
    };
    findings: Array<{
      code: string;
      severity: string;
      message: string;
    }>;
  };
};
