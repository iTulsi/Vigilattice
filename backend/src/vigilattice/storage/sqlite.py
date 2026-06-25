import sqlite3
from pathlib import Path
from threading import RLock

from vigilattice.models.analytics import AgentAnalytics, BenchmarkAnalytics
from vigilattice.models.run import EvaluationRun


class SQLiteRunRepository:
    """Durable SQLite storage for evaluation runs and benchmark analytics."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_runs (
                    id TEXT PRIMARY KEY,
                    scenario_id TEXT NOT NULL,
                    scenario_name TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    overall_score REAL NOT NULL,
                    policy_score REAL NOT NULL,
                    approval_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_evaluation_runs_created_at
                ON evaluation_runs(created_at DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_evaluation_runs_agent
                ON evaluation_runs(agent)
                """
            )

    def save(self, run: EvaluationRun) -> EvaluationRun:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO evaluation_runs (
                    id,
                    scenario_id,
                    scenario_name,
                    agent,
                    status,
                    created_at,
                    passed,
                    overall_score,
                    policy_score,
                    approval_score,
                    risk_level,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.scenario_id,
                    run.scenario_name,
                    run.agent,
                    run.status.value,
                    run.created_at.isoformat(),
                    int(run.report.passed),
                    run.report.scores.overall,
                    run.report.scores.policy_compliance,
                    run.report.scores.approval_safety,
                    run.report.risk_level.value,
                    run.model_dump_json(),
                ),
            )
        return run

    def get(self, run_id: str) -> EvaluationRun | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM evaluation_runs
                WHERE id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None
        return EvaluationRun.model_validate_json(row["payload_json"])

    def list(self) -> list[EvaluationRun]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM evaluation_runs
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

        return [EvaluationRun.model_validate_json(row["payload_json"]) for row in rows]

    def analytics(self) -> BenchmarkAnalytics:
        with self._connect() as connection:
            summary = connection.execute(
                """
                SELECT
                    COUNT(DISTINCT scenario_id) AS total_scenarios,
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(passed), 0) AS passed_runs,
                    COALESCE(AVG(overall_score), 0) AS average_overall,
                    COALESCE(AVG(policy_score), 0) AS average_policy,
                    COALESCE(AVG(approval_score), 0) AS average_approval,
                    COALESCE(
                        SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END),
                        0
                    ) AS critical_runs
                FROM evaluation_runs
                """
            ).fetchone()

            agent_rows = connection.execute(
                """
                SELECT
                    agent,
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(passed), 0) AS passed_runs,
                    COALESCE(AVG(overall_score), 0) AS average_overall,
                    COALESCE(AVG(policy_score), 0) AS average_policy,
                    COALESCE(AVG(approval_score), 0) AS average_approval,
                    COALESCE(
                        SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END),
                        0
                    ) AS critical_runs
                FROM evaluation_runs
                GROUP BY agent
                ORDER BY average_overall DESC, agent ASC
                """
            ).fetchall()

        total_runs = int(summary["total_runs"])
        passed_runs = int(summary["passed_runs"])

        agents = []
        for row in agent_rows:
            agent_total = int(row["total_runs"])
            agent_passed = int(row["passed_runs"])
            agents.append(
                AgentAnalytics(
                    agent=row["agent"],
                    total_runs=agent_total,
                    passed_runs=agent_passed,
                    failed_runs=agent_total - agent_passed,
                    pass_rate=self._percentage(agent_passed, agent_total),
                    average_overall=round(float(row["average_overall"]), 2),
                    average_policy=round(float(row["average_policy"]), 2),
                    average_approval=round(float(row["average_approval"]), 2),
                    critical_runs=int(row["critical_runs"]),
                )
            )

        return BenchmarkAnalytics(
            total_scenarios=int(summary["total_scenarios"]),
            total_runs=total_runs,
            passed_runs=passed_runs,
            failed_runs=total_runs - passed_runs,
            pass_rate=self._percentage(passed_runs, total_runs),
            average_overall=round(float(summary["average_overall"]), 2),
            average_policy=round(float(summary["average_policy"]), 2),
            average_approval=round(float(summary["average_approval"]), 2),
            critical_runs=int(summary["critical_runs"]),
            agents=agents,
        )

    @staticmethod
    def _percentage(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(100 * numerator / denominator, 2)
