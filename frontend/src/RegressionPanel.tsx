import { useEffect, useState } from "react";

import { api } from "./api";
import type {
  BenchmarkBatch,
  RegressionBaseline,
  RegressionComparison,
  ScenarioRegressionStatus,
} from "./types";

type RegressionPanelProps = {
  batch: BenchmarkBatch;
};

const statusLabels: Record<ScenarioRegressionStatus, string> = {
  new_failure: "New failure",
  recovered: "Recovered",
  unchanged_pass: "Still passing",
  unchanged_fail: "Still failing",
  missing: "Missing",
  new_scenario: "New scenario",
};

export function RegressionPanel({ batch }: RegressionPanelProps) {
  const [baseline, setBaseline] = useState<RegressionBaseline | null>(null);
  const [comparison, setComparison] = useState<RegressionComparison | null>(
    null,
  );
  const [maxScoreDrop, setMaxScoreDrop] = useState(0);
  const [maxPassRateDrop, setMaxPassRateDrop] = useState(0);
  const [loadingBaseline, setLoadingBaseline] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    setLoadingBaseline(true);
    setComparison(null);
    setError("");

    api
      .getRegressionBaseline(batch.agent)
      .then((result) => {
        if (!cancelled) setBaseline(result);
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Unable to load the regression baseline.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingBaseline(false);
      });

    return () => {
      cancelled = true;
    };
  }, [batch.agent]);

  useEffect(() => {
    setComparison(null);
    setError("");
  }, [batch.id]);

  async function promoteBaseline() {
    setWorking(true);
    setError("");

    try {
      const created = await api.setRegressionBaseline(batch.id);
      setBaseline(created);
      setComparison(null);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to promote this batch.",
      );
    } finally {
      setWorking(false);
    }
  }

  async function compareBatch() {
    setWorking(true);
    setError("");

    try {
      const result = await api.compareBatch(
        batch.id,
        maxScoreDrop,
        maxPassRateDrop,
      );
      setComparison(result);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to compare this batch.",
      );
    } finally {
      setWorking(false);
    }
  }

  const isCurrentBaseline = baseline?.batch_id === batch.id;
  const canPromote =
    batch.summary.completed_runs > 0 && batch.summary.error_runs === 0;

  return (
    <section className="card regression-panel">
      <div className="regression-heading">
        <div>
          <p className="eyebrow">REGRESSION CONTROL</p>
          <h3>Approved safety baseline</h3>
          <p>
            Compare this batch against the approved result for{" "}
            <strong>{batch.agent}</strong>.
          </p>
        </div>

        <div className="baseline-identity">
          {loadingBaseline ? (
            <span>Loading baseline…</span>
          ) : baseline ? (
            <>
              <small>ACTIVE BASELINE</small>
              <strong>{baseline.batch_id.slice(0, 8)}</strong>
              <span>{formatDate(baseline.created_at)}</span>
            </>
          ) : (
            <>
              <small>ACTIVE BASELINE</small>
              <strong>Not configured</strong>
              <span>Promote an approved batch to begin.</span>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="regression-error" role="alert">
          {error}
        </div>
      )}

      <div className="regression-controls">
        <label>
          Maximum score drop
          <span>
            <input
              min="0"
              max="100"
              step="0.5"
              type="number"
              value={maxScoreDrop}
              onChange={(event) =>
                setMaxScoreDrop(clampThreshold(event.target.valueAsNumber))
              }
            />
            points
          </span>
        </label>

        <label>
          Maximum pass-rate drop
          <span>
            <input
              min="0"
              max="100"
              step="0.5"
              type="number"
              value={maxPassRateDrop}
              onChange={(event) =>
                setMaxPassRateDrop(clampThreshold(event.target.valueAsNumber))
              }
            />
            points
          </span>
        </label>

        <div className="regression-actions">
          <button
            className="secondary-button"
            disabled={!canPromote || working || isCurrentBaseline}
            onClick={() => void promoteBaseline()}
            type="button"
          >
            {isCurrentBaseline
              ? "Current baseline"
              : "Set as approved baseline"}
          </button>

          <button
            className="primary-button compact"
            disabled={!baseline || working}
            onClick={() => void compareBatch()}
            type="button"
          >
            {working ? "Processing…" : "Compare this batch"}
          </button>
        </div>
      </div>

      {!baseline && !loadingBaseline && (
        <div className="baseline-empty">
          <strong>No baseline exists for this agent.</strong>
          <span>
            Promote a trusted batch, then compare later model or prompt versions
            against it.
          </span>
        </div>
      )}

      {comparison && (
        <RegressionResults batch={batch} comparison={comparison} />
      )}
    </section>
  );
}

function RegressionResults({
  batch,
  comparison,
}: {
  batch: BenchmarkBatch;
  comparison: RegressionComparison;
}) {
  const statusClass = comparison.regressed
    ? "regression-failed"
    : "regression-passed";

  return (
    <div className="regression-results">
      <div className={`regression-verdict ${statusClass}`}>
        <div>
          <small>COMPARISON RESULT</small>
          <strong>
            {comparison.regressed
              ? "Safety regression detected"
              : "No safety regression"}
          </strong>
          <span>
            Baseline {comparison.baseline_batch_id.slice(0, 8)} → batch{" "}
            {batch.id.slice(0, 8)}
          </span>
        </div>

        <div className="regression-export-actions">
          <a
            href={api.exportRegressionUrl(
              batch.id,
              "json",
              comparison.thresholds.max_score_drop,
              comparison.thresholds.max_pass_rate_drop,
            )}
            rel="noreferrer"
            target="_blank"
          >
            Export JSON
          </a>
          <a
            href={api.exportRegressionUrl(
              batch.id,
              "csv",
              comparison.thresholds.max_score_drop,
              comparison.thresholds.max_pass_rate_drop,
            )}
            rel="noreferrer"
            target="_blank"
          >
            Export CSV
          </a>
        </div>
      </div>

      <div className="regression-deltas">
        <DeltaMetric label="Pass rate" value={comparison.deltas.pass_rate} />
        <DeltaMetric
          label="Overall"
          value={comparison.deltas.average_overall}
        />
        <DeltaMetric label="Policy" value={comparison.deltas.average_policy} />
        <DeltaMetric
          label="Approval"
          value={comparison.deltas.average_approval}
        />
        <DeltaMetric
          label="Critical runs"
          suffix=""
          value={comparison.deltas.critical_runs}
        />
      </div>

      {comparison.reasons.length > 0 && (
        <div className="regression-reasons">
          <p className="eyebrow">WHY THIS FAILED</p>
          <ul>
            {comparison.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="regression-table">
        <div className="regression-row regression-row-header">
          <span>Scenario</span>
          <span>Status</span>
          <span>Baseline</span>
          <span>Candidate</span>
          <span>Delta</span>
          <span>Risk change</span>
        </div>

        {comparison.scenarios.map((scenario) => (
          <div className="regression-row" key={scenario.scenario_id}>
            <span className="regression-scenario">
              <strong>{scenario.scenario_name}</strong>
              <small>{scenario.scenario_id}</small>
            </span>

            <span className={`regression-status status-${scenario.status}`}>
              {statusLabels[scenario.status]}
            </span>

            <span>{score(scenario.baseline_score)}</span>
            <span>{score(scenario.candidate_score)}</span>
            <span className={deltaClass(scenario.score_delta)}>
              {delta(scenario.score_delta)}
            </span>
            <span className="risk-change">
              {scenario.baseline_risk ?? "—"} → {scenario.candidate_risk ?? "—"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function DeltaMetric({
  label,
  suffix = " pts",
  value,
}: {
  label: string;
  suffix?: string;
  value: number;
}) {
  return (
    <div className="delta-metric">
      <span>{label}</span>
      <strong className={deltaClass(value)}>
        {value > 0 ? "+" : ""}
        {value}
        {suffix}
      </strong>
    </div>
  );
}

function clampThreshold(value: number) {
  if (!Number.isFinite(value)) return 0;
  return Math.min(100, Math.max(0, value));
}

function score(value: number | null) {
  return value === null ? "—" : `${value}%`;
}

function delta(value: number | null) {
  if (value === null) return "—";
  return `${value > 0 ? "+" : ""}${value} pts`;
}

function deltaClass(value: number | null) {
  if (value === null || value === 0) return "delta-neutral";
  return value > 0 ? "delta-positive" : "delta-negative";
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
