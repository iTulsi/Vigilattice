import { useEffect, useMemo, useState } from "react";

import { api } from "./api";
import type {
  BenchmarkAnalytics,
  EvaluationRun,
  Scenario,
} from "./types";

const scoreLabels: Array<[keyof EvaluationRun["report"]["scores"], string]> = [
  ["task_completion", "Task completion"],
  ["policy_compliance", "Policy compliance"],
  ["injection_resistance", "Injection resistance"],
  ["least_privilege", "Least privilege"],
  ["approval_safety", "Approval safety"],
];

function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [analytics, setAnalytics] = useState<BenchmarkAnalytics | null>(null);
  const [selectedScenario, setSelectedScenario] = useState("");
  const [agent, setAgent] = useState("mock-safe");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.listScenarios(),
      api.listRuns(),
      api.getAnalytics(),
    ])
      .then(([scenarioData, runData, analyticsData]) => {
        setScenarios(scenarioData);
        setRuns(runData);
        setAnalytics(analyticsData);
        setSelectedScenario(scenarioData[0]?.id ?? "");
      })
      .catch((reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Unable to connect to the API.");
      });
  }, []);

  const latestRun = runs[0];
  const selected = useMemo(
    () => scenarios.find((scenario) => scenario.id === selectedScenario),
    [scenarios, selectedScenario],
  );

  async function runEvaluation() {
    if (!selectedScenario) return;
    setRunning(true);
    setError("");
    try {
      const result = await api.createRun(selectedScenario, agent);
      setRuns((current) => [result, ...current]);
      const updatedAnalytics = await api.getAnalytics();
      setAnalytics(updatedAnalytics);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Evaluation failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">
          VL
        </div>
        <div>
          <p className="eyebrow">AGENT SAFETY UNDER PRESSURE</p>
          <h1>Vigilattice</h1>
        </div>
        <span className="status"><i /> Foundation online</span>
      </header>

      <section className="hero">
        <div>
          <p className="eyebrow">ADVERSARIAL EVALUATION INFRASTRUCTURE</p>
          <h2>Observe what an agent does when the environment fights back.</h2>
          <p className="hero-copy">
            Run stateful scenarios, capture every tool decision, and turn failures into
            reproducible safety evidence.
          </p>
        </div>
        <div className="run-panel">
          <label>
            Scenario
            <select value={selectedScenario} onChange={(event) => setSelectedScenario(event.target.value)}>
              {scenarios.map((scenario) => (
                <option key={scenario.id} value={scenario.id}>{scenario.name}</option>
              ))}
            </select>
          </label>
          <label>
            Agent adapter
            <select value={agent} onChange={(event) => setAgent(event.target.value)}>
              <option value="mock-safe">mock-safe</option>
              <option value="mock-unsafe">mock-unsafe</option>
              <option value="llm-structured">llm-structured · real model</option>
            </select>
          </label>
          <button onClick={runEvaluation} disabled={running || !selectedScenario}>
            {running ? "Executing…" : "Run evaluation"}
          </button>
          {selected && <p className="scenario-note">{selected.description}</p>}
          {error && <p className="error">{error}</p>}
        </div>
      </section>

      <section className="metrics" aria-label="Latest evaluation metrics">
        <Metric
          label="Persistent runs"
          value={String(analytics?.total_runs ?? runs.length)}
        />
        <Metric
          label="Average overall"
          value={analytics ? `${analytics.average_overall}%` : "—"}
        />
        <Metric label="Risk level" value={latestRun ? latestRun.report.risk_level.toUpperCase() : "—"} />
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
            {latestRun && <span className={`verdict ${latestRun.report.passed ? "pass" : "fail"}`}>{latestRun.report.passed ? "PASS" : "FAIL"}</span>}
          </div>
          <div className="timeline">
            {latestRun ? latestRun.trace.events.map((event) => (
              <div className="event" key={`${latestRun.id}-${event.sequence}`}>
                <span className="event-index">{String(event.sequence).padStart(2, "0")}</span>
                <div>
                  <strong>{event.action}</strong>
                  <p>{event.detail}</p>
                  <small>{event.kind} · {event.resource ?? "no resource"}</small>
                </div>
              </div>
            )) : <p className="empty">Run the safe and unsafe adapters to compare their behaviour.</p>}
          </div>
        </article>

        <aside className="card score-card">
          <p className="eyebrow">EVALUATION</p>
          <div className="overall-score">
            <span>{latestRun?.report.scores.overall ?? 0}</span><small>/100</small>
          </div>
          <div className="score-list">
            {scoreLabels.map(([key, label]) => {
              const value = latestRun?.report.scores[key] ?? 0;
              return (
                <div className="score-row" key={key}>
                  <div><span>{label}</span><b>{value}%</b></div>
                  <progress value={value} max="100" />
                </div>
              );
            })}
          </div>
          <div className="findings">
            <h4>Findings</h4>
            {latestRun?.report.findings.length ? latestRun.report.findings.map((finding, index) => (
              <div className="finding" key={`${finding.code}-${index}`}>
                <p><b>{finding.severity}</b> {finding.message}</p>
                <small>Evidence: {finding.evidence}</small>
                <small>Fix: {finding.recommendation}</small>
              </div>
            )) : <p>No policy findings in the latest trace.</p>}
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
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

export default App;
