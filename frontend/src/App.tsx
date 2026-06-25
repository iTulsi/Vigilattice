import { useEffect, useMemo, useState } from "react";

import { api } from "./api";
import type {
  BenchmarkAnalytics,
  BenchmarkBatch,
  EvaluationRun,
  Scenario,
} from "./types";

type View = "evaluation" | "batches";
type BatchScope = "all" | "selected";

const agents = [
  { value: "mock-safe", label: "mock-safe", note: "Reference safe adapter" },
  {
    value: "mock-unsafe",
    label: "mock-unsafe",
    note: "Adversarial baseline",
  },
  {
    value: "llm-structured",
    label: "llm-structured",
    note: "Configured real model",
  },
];

const scoreLabels: Array<[keyof EvaluationRun["report"]["scores"], string]> = [
  ["task_completion", "Task completion"],
  ["policy_compliance", "Policy compliance"],
  ["injection_resistance", "Injection resistance"],
  ["least_privilege", "Least privilege"],
  ["approval_safety", "Approval safety"],
];

function App() {
  const [view, setView] = useState<View>("evaluation");
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [analytics, setAnalytics] = useState<BenchmarkAnalytics | null>(null);
  const [batches, setBatches] = useState<BenchmarkBatch[]>([]);
  const [selectedScenario, setSelectedScenario] = useState("");
  const [agent, setAgent] = useState("mock-safe");
  const [batchAgent, setBatchAgent] = useState("mock-safe");
  const [batchScope, setBatchScope] = useState<BatchScope>("all");
  const [batchScenarioIds, setBatchScenarioIds] = useState<string[]>([]);
  const [activeBatchId, setActiveBatchId] = useState("");
  const [running, setRunning] = useState(false);
  const [batchRunning, setBatchRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.listScenarios(),
      api.listRuns(),
      api.getAnalytics(),
      api.listBatches(),
    ])
      .then(([scenarioData, runData, analyticsData, batchData]) => {
        setScenarios(scenarioData);
        setRuns(runData);
        setAnalytics(analyticsData);
        setBatches(batchData);
        setSelectedScenario(scenarioData[0]?.id ?? "");
        setBatchScenarioIds(scenarioData.map((scenario) => scenario.id));
        setActiveBatchId(batchData[0]?.id ?? "");
      })
      .catch((reason: unknown) => {
        setError(
          reason instanceof Error
            ? reason.message
            : "Unable to connect to the Vigilattice API.",
        );
      })
      .finally(() => setLoading(false));
  }, []);

  const latestRun = runs[0];

  const selected = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenario),
    [scenarios, selectedScenario],
  );

  const activeBatch = useMemo(
    () => batches.find((batch) => batch.id === activeBatchId) ?? batches[0],
    [activeBatchId, batches],
  );

  async function refreshRunData() {
    const [runData, analyticsData] = await Promise.all([
      api.listRuns(),
      api.getAnalytics(),
    ]);
    setRuns(runData);
    setAnalytics(analyticsData);
  }

  async function runEvaluation() {
    if (!selectedScenario) return;

    setRunning(true);
    setError("");

    try {
      const result = await api.createRun(selectedScenario, agent);
      setRuns((current) => [result, ...current]);
      setAnalytics(await api.getAnalytics());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Evaluation failed.");
    } finally {
      setRunning(false);
    }
  }

  async function runBatch() {
    if (batchScope === "selected" && batchScenarioIds.length === 0) {
      setError("Select at least one scenario for this benchmark batch.");
      return;
    }

    setBatchRunning(true);
    setError("");

    try {
      const result = await api.createBatch(
        batchAgent,
        batchScope === "selected" ? batchScenarioIds : undefined,
      );
      setBatches((current) => [
        result,
        ...current.filter((batch) => batch.id !== result.id),
      ]);
      setActiveBatchId(result.id);
      await refreshRunData();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Batch benchmark failed.",
      );
    } finally {
      setBatchRunning(false);
    }
  }

  function toggleBatchScenario(scenarioId: string) {
    setBatchScenarioIds((current) =>
      current.includes(scenarioId)
        ? current.filter((id) => id !== scenarioId)
        : [...current, scenarioId],
    );
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">
          VL
        </div>
        <div className="brand-copy">
          <p className="eyebrow">AGENT SAFETY UNDER PRESSURE</p>
          <h1>Vigilattice</h1>
        </div>

        <nav className="view-switcher" aria-label="Dashboard views">
          <button
            className={view === "evaluation" ? "active" : ""}
            onClick={() => setView("evaluation")}
            type="button"
          >
            Live evaluation
          </button>
          <button
            className={view === "batches" ? "active" : ""}
            onClick={() => setView("batches")}
            type="button"
          >
            Batch reports
            {batches.length > 0 && <span>{batches.length}</span>}
          </button>
        </nav>

        <span className="status">
          <i />
          {loading ? "Connecting" : "Foundation online"}
        </span>
      </header>

      {error && (
        <div className="global-error" role="alert">
          <strong>Action required</strong>
          <span>{error}</span>
          <button onClick={() => setError("")} type="button">
            Dismiss
          </button>
        </div>
      )}

      {view === "evaluation" ? (
        <EvaluationView
          agent={agent}
          analytics={analytics}
          latestRun={latestRun}
          running={running}
          scenarios={scenarios}
          selected={selected}
          selectedScenario={selectedScenario}
          setAgent={setAgent}
          setSelectedScenario={setSelectedScenario}
          runEvaluation={runEvaluation}
        />
      ) : (
        <BatchView
          activeBatch={activeBatch}
          activeBatchId={activeBatchId}
          batchAgent={batchAgent}
          batchRunning={batchRunning}
          batchScenarioIds={batchScenarioIds}
          batchScope={batchScope}
          batches={batches}
          runBatch={runBatch}
          scenarios={scenarios}
          setActiveBatchId={setActiveBatchId}
          setBatchAgent={setBatchAgent}
          setBatchScope={setBatchScope}
          toggleBatchScenario={toggleBatchScenario}
        />
      )}
    </main>
  );
}

type EvaluationViewProps = {
  agent: string;
  analytics: BenchmarkAnalytics | null;
  latestRun: EvaluationRun | undefined;
  running: boolean;
  scenarios: Scenario[];
  selected: Scenario | undefined;
  selectedScenario: string;
  setAgent: (agent: string) => void;
  setSelectedScenario: (scenarioId: string) => void;
  runEvaluation: () => Promise<void>;
};

function EvaluationView({
  agent,
  analytics,
  latestRun,
  running,
  scenarios,
  selected,
  selectedScenario,
  setAgent,
  setSelectedScenario,
  runEvaluation,
}: EvaluationViewProps) {
  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">ADVERSARIAL EVALUATION INFRASTRUCTURE</p>
          <h2>Observe what an agent does when the environment fights back.</h2>
          <p className="hero-copy">
            Run stateful scenarios, capture every tool decision, and turn
            failures into reproducible safety evidence.
          </p>
        </div>

        <div className="run-panel">
          <label>
            Scenario
            <select
              value={selectedScenario}
              onChange={(event) => setSelectedScenario(event.target.value)}
            >
              {scenarios.map((scenario) => (
                <option key={scenario.id} value={scenario.id}>
                  {scenario.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Agent adapter
            <select
              value={agent}
              onChange={(event) => setAgent(event.target.value)}
            >
              {agents.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label} · {item.note}
                </option>
              ))}
            </select>
          </label>

          <button
            className="primary-button"
            onClick={() => void runEvaluation()}
            disabled={running || !selectedScenario}
            type="button"
          >
            {running ? "Executing evaluation…" : "Run evaluation"}
          </button>

          {selected && <p className="scenario-note">{selected.description}</p>}
        </div>
      </section>

      <section className="metrics" aria-label="Evaluation metrics">
        <Metric
          label="Persistent runs"
          value={String(analytics?.total_runs ?? 0)}
        />
        <Metric
          label="Average overall"
          value={analytics ? `${analytics.average_overall}%` : "—"}
        />
        <Metric
          label="Latest risk"
          value={latestRun ? latestRun.report.risk_level.toUpperCase() : "—"}
        />
        <Metric
          label="Benchmark pass rate"
          value={analytics ? `${analytics.pass_rate}%` : "—"}
        />
      </section>

      <section className="workspace">
        <article className="card trace-card">
          <div className="card-heading">
            <div>
              <p className="eyebrow">TRACE</p>
              <h3>{latestRun?.scenario_name ?? "No evaluation executed"}</h3>
            </div>
            {latestRun && (
              <span
                className={`verdict ${
                  latestRun.report.passed ? "pass" : "fail"
                }`}
              >
                {latestRun.report.passed ? "PASS" : "FAIL"}
              </span>
            )}
          </div>

          <div className="timeline">
            {latestRun ? (
              latestRun.trace.events.map((event) => (
                <div
                  className="event"
                  key={`${latestRun.id}-${event.sequence}`}
                >
                  <span className="event-index">
                    {String(event.sequence).padStart(2, "0")}
                  </span>
                  <div>
                    <strong>{event.action}</strong>
                    <p>{event.detail}</p>
                    <small>
                      {event.kind} · {event.resource ?? "no resource"}
                    </small>
                  </div>
                </div>
              ))
            ) : (
              <p className="empty">
                Run the safe and unsafe adapters to compare their behaviour.
              </p>
            )}
          </div>
        </article>

        <aside className="card score-card">
          <p className="eyebrow">EVALUATION</p>
          <div className="overall-score">
            <span>{latestRun?.report.scores.overall ?? 0}</span>
            <small>/100</small>
          </div>

          <div className="score-list">
            {scoreLabels.map(([key, label]) => {
              const value = latestRun?.report.scores[key] ?? 0;
              return (
                <div className="score-row" key={key}>
                  <div>
                    <span>{label}</span>
                    <b>{value}%</b>
                  </div>
                  <progress value={value} max="100" />
                </div>
              );
            })}
          </div>

          <div className="findings">
            <h4>Findings</h4>
            {latestRun?.report.findings.length ? (
              latestRun.report.findings.map((finding, index) => (
                <div className="finding" key={`${finding.code}-${index}`}>
                  <p>
                    <b>{finding.severity}</b> {finding.message}
                  </p>
                  <small>Evidence: {finding.evidence}</small>
                  <small>Fix: {finding.recommendation}</small>
                </div>
              ))
            ) : (
              <p>No policy findings in the latest trace.</p>
            )}
          </div>
        </aside>
      </section>

      <section className="card comparison-card">
        <div className="card-heading">
          <div>
            <p className="eyebrow">AGENT COMPARISON</p>
            <h3>Persistent benchmark performance</h3>
          </div>
          <span className="comparison-count">
            {analytics?.total_scenarios ?? 0} scenarios evaluated
          </span>
        </div>

        {analytics?.agents.length ? (
          <div className="comparison-table">
            <div className="comparison-row comparison-header">
              <span>Agent</span>
              <span>Runs</span>
              <span>Pass rate</span>
              <span>Avg. score</span>
              <span>Critical</span>
            </div>
            {analytics.agents.map((item) => (
              <div className="comparison-row" key={item.agent}>
                <strong>{item.agent}</strong>
                <span>{item.total_runs}</span>
                <span>{item.pass_rate}%</span>
                <span>{item.average_overall}%</span>
                <span>{item.critical_runs}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty">
            Run both reference agents to create a comparison.
          </p>
        )}
      </section>
    </>
  );
}

type BatchViewProps = {
  activeBatch: BenchmarkBatch | undefined;
  activeBatchId: string;
  batchAgent: string;
  batchRunning: boolean;
  batchScenarioIds: string[];
  batchScope: BatchScope;
  batches: BenchmarkBatch[];
  runBatch: () => Promise<void>;
  scenarios: Scenario[];
  setActiveBatchId: (batchId: string) => void;
  setBatchAgent: (agent: string) => void;
  setBatchScope: (scope: BatchScope) => void;
  toggleBatchScenario: (scenarioId: string) => void;
};

function BatchView({
  activeBatch,
  activeBatchId,
  batchAgent,
  batchRunning,
  batchScenarioIds,
  batchScope,
  batches,
  runBatch,
  scenarios,
  setActiveBatchId,
  setBatchAgent,
  setBatchScope,
  toggleBatchScenario,
}: BatchViewProps) {
  return (
    <>
      <section className="batch-hero">
        <div className="batch-intro">
          <p className="eyebrow">REPRODUCIBLE SAFETY REPORTS</p>
          <h2>Run the complete benchmark. Keep the evidence.</h2>
          <p>
            Execute multiple adversarial scenarios as one durable batch, compare
            aggregate safety scores, and export the full report for reviews or
            regression tracking.
          </p>
        </div>

        <div className="card batch-control">
          <div className="control-heading">
            <div>
              <p className="eyebrow">NEW BENCHMARK</p>
              <h3>Configure batch</h3>
            </div>
            <span className="suite-count">{scenarios.length} available</span>
          </div>

          <label>
            Agent adapter
            <select
              value={batchAgent}
              onChange={(event) => setBatchAgent(event.target.value)}
            >
              {agents.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label} · {item.note}
                </option>
              ))}
            </select>
          </label>

          <div className="scope-switcher" aria-label="Batch scenario scope">
            <button
              className={batchScope === "all" ? "active" : ""}
              onClick={() => setBatchScope("all")}
              type="button"
            >
              Complete suite
            </button>
            <button
              className={batchScope === "selected" ? "active" : ""}
              onClick={() => setBatchScope("selected")}
              type="button"
            >
              Selected scenarios
            </button>
          </div>

          {batchScope === "selected" && (
            <div className="scenario-selector">
              {scenarios.map((scenario) => (
                <label key={scenario.id}>
                  <input
                    checked={batchScenarioIds.includes(scenario.id)}
                    onChange={() => toggleBatchScenario(scenario.id)}
                    type="checkbox"
                  />
                  <span>
                    <strong>{scenario.name}</strong>
                    <small>
                      {scenario.category} · {scenario.severity}
                    </small>
                  </span>
                </label>
              ))}
            </div>
          )}

          <button
            className="primary-button"
            disabled={
              batchRunning ||
              scenarios.length === 0 ||
              (batchScope === "selected" && batchScenarioIds.length === 0)
            }
            onClick={() => void runBatch()}
            type="button"
          >
            {batchRunning
              ? "Running benchmark suite…"
              : batchScope === "all"
                ? "Run complete benchmark"
                : `Run ${batchScenarioIds.length} selected scenarios`}
          </button>
        </div>
      </section>

      {activeBatch ? (
        <>
          <section className="batch-summary">
            <div className="summary-identity">
              <p className="eyebrow">LATEST REPORT</p>
              <div>
                <h3>{activeBatch.agent}</h3>
                <span>{formatDate(activeBatch.completed_at)}</span>
              </div>
              <small>
                Batch {activeBatch.id.slice(0, 8)} · {activeBatch.duration_ms}{" "}
                ms
              </small>
            </div>

            <Metric
              label="Pass rate"
              value={`${activeBatch.summary.pass_rate}%`}
              emphasis
            />
            <Metric
              label="Average score"
              value={`${activeBatch.summary.average_overall}%`}
            />
            <Metric
              label="Passed"
              value={`${activeBatch.summary.passed_runs}/${activeBatch.summary.total_scenarios}`}
            />
            <Metric
              label="Critical"
              value={String(activeBatch.summary.critical_runs)}
            />
          </section>

          <section className="batch-workspace">
            <article className="card results-card">
              <div className="card-heading">
                <div>
                  <p className="eyebrow">SCENARIO RESULTS</p>
                  <h3>Execution matrix</h3>
                </div>
                <div className="export-actions">
                  <a
                    href={api.exportBatchUrl(activeBatch.id, "json")}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Export JSON
                  </a>
                  <a
                    href={api.exportBatchUrl(activeBatch.id, "csv")}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Export CSV
                  </a>
                </div>
              </div>

              <div className="result-table">
                <div className="result-row result-header">
                  <span>Scenario</span>
                  <span>Status</span>
                  <span>Overall</span>
                  <span>Policy</span>
                  <span>Approval</span>
                  <span>Risk</span>
                </div>

                {activeBatch.results.map((result) => (
                  <div className="result-row" key={result.scenario_id}>
                    <span className="scenario-cell">
                      <strong>{result.scenario_name}</strong>
                      <small>{result.scenario_id}</small>
                      {result.error && <em>{result.error}</em>}
                    </span>
                    <span>
                      <StatusPill
                        passed={result.passed}
                        status={result.status}
                      />
                    </span>
                    <span>{scoreValue(result.overall_score)}</span>
                    <span>{scoreValue(result.policy_score)}</span>
                    <span>{scoreValue(result.approval_score)}</span>
                    <span className={`risk ${riskClass(result.risk_level)}`}>
                      {result.risk_level ?? "—"}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <aside className="card history-card">
              <div className="card-heading">
                <div>
                  <p className="eyebrow">HISTORY</p>
                  <h3>Saved batches</h3>
                </div>
                <span>{batches.length}</span>
              </div>

              <div className="history-list">
                {batches.map((batch) => (
                  <button
                    className={batch.id === activeBatchId ? "active" : ""}
                    key={batch.id}
                    onClick={() => setActiveBatchId(batch.id)}
                    type="button"
                  >
                    <span className="history-topline">
                      <strong>{batch.agent}</strong>
                      <b>{batch.summary.pass_rate}%</b>
                    </span>
                    <span>
                      {formatDate(batch.completed_at)} ·{" "}
                      {batch.summary.total_scenarios} scenarios
                    </span>
                    <i>
                      <span
                        style={{
                          width: `${batch.summary.pass_rate}%`,
                        }}
                      />
                    </i>
                  </button>
                ))}
              </div>
            </aside>
          </section>
        </>
      ) : (
        <section className="card empty-batch">
          <span>00</span>
          <div>
            <p className="eyebrow">NO REPORTS YET</p>
            <h3>Run the first benchmark batch</h3>
            <p>
              The persisted report, aggregate metrics, scenario results, and
              export controls will appear here.
            </p>
          </div>
        </section>
      )}
    </>
  );
}

function StatusPill({
  passed,
  status,
}: {
  passed: boolean | null;
  status: "completed" | "error";
}) {
  if (status === "error") {
    return <span className="verdict error-state">ERROR</span>;
  }

  return (
    <span className={`verdict ${passed ? "pass" : "fail"}`}>
      {passed ? "PASS" : "FAIL"}
    </span>
  );
}

function Metric({
  emphasis = false,
  label,
  value,
}: {
  emphasis?: boolean;
  label: string;
  value: string;
}) {
  return (
    <div className={`metric ${emphasis ? "emphasis" : ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function scoreValue(value: number | null) {
  return value === null ? "—" : `${value}%`;
}

function riskClass(risk: string | null) {
  if (!risk) return "unknown";
  return risk.toLowerCase().replace(/_/g, "-");
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export default App;
