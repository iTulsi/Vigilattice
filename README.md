# Vigilattice

**Adversarial evaluation infrastructure for autonomous AI agents.**

Vigilattice places agents inside a stateful simulated organization and measures whether they complete tasks while resisting prompt injection, respecting permissions, protecting sensitive data, and escalating high-risk actions for human approval.

## Current foundation

The starter repository already includes:

- A production-style FastAPI backend
- Safe and unsafe deterministic agent adapters
- YAML-defined adversarial scenarios
- A deterministic evaluation and scoring pipeline
- Run history APIs
- A React + TypeScript experiment dashboard
- Backend tests, linting, Docker, and GitHub Actions CI
- Extension points for Claude Agent SDK and MCP servers

No Anthropic API key is required for the first milestone.

## Architecture

```text
React Dashboard
      |
FastAPI Experiment API
      |
Arena Orchestrator
      +-- Scenario Registry
      +-- Agent Adapters
      +-- Tool-event Trace
      +-- Deterministic Graders
      +-- Run Repository

Future adapters
      +-- Claude Agent SDK
      +-- MCP Email Server
      +-- MCP Documents Server
      +-- MCP Git Server
      +-- Model-based Graders
```

## Start locally

### 1. Bootstrap

```bash
cp .env.example .env
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

### 2. Run the API

```bash
make api
```

API docs: `http://localhost:8000/docs`

### 3. Run the dashboard

In another terminal:

```bash
make web
```

Dashboard: `http://localhost:5173`

## Verify the foundation

```bash
make test
make lint
make build
```

Expected backend result: all tests pass.

## First API calls

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/scenarios

curl -X POST http://localhost:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"injected-incident-001","agent":"mock-safe"}'
```

Run the same scenario with `mock-unsafe` to see the safety score collapse.

## Repository layout

```text
Vigilattice/
├── backend/                  FastAPI API, arena, agents, graders, scenarios
├── frontend/                 React experiment dashboard
├── docs/                     Architecture, roadmap, and threat model
├── infra/                    Docker Compose
├── scripts/                  Local bootstrap and checks
└── .github/workflows/        CI
```

## Planned progression

1. Replace in-memory storage with PostgreSQL.
2. Implement real MCP email, documents, and Git servers.
3. Add Claude Agent SDK execution and trace capture.
4. Add permission gates and approval workflows.
5. Expand to 30+ benchmark scenarios.
6. Add repeated trials, confidence intervals, and regression gates.
7. Publish an empirical safety report.

## License

Apache-2.0 is planned. Add a formal `LICENSE` before public release.
