<div align="center">

# Vigilattice

**Adversarial evaluation and safety-regression infrastructure for autonomous AI agents.**

Evaluate whether an agent completes useful work while resisting prompt injection,
protecting sensitive data, respecting permissions, and escalating high-risk actions.

[Live Dashboard](https://vigilattice-itulsi.onrender.com)
·
[API Documentation](https://vigilattice-api-itulsi.onrender.com/docs)
·
[Deployment Guide](docs/deployment.md)

[![Vigilattice CI](https://github.com/iTulsi/Vigilattice/actions/workflows/ci.yml/badge.svg)](https://github.com/iTulsi/Vigilattice/actions/workflows/ci.yml)
[![Safety Regression Gate](https://github.com/iTulsi/Vigilattice/actions/workflows/regression-gate.yml/badge.svg)](https://github.com/iTulsi/Vigilattice/actions/workflows/regression-gate.yml)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](backend/pyproject.toml)
[![React + TypeScript](https://img.shields.io/badge/React-TypeScript-3178C6?logo=react&logoColor=white)](frontend)
[![License](https://img.shields.io/badge/License-Apache--2.0-6D4AFF)](LICENSE)

</div>

---

## Overview

Vigilattice is an evaluation platform for testing autonomous and tool-using AI
agents against security, policy, and human-approval requirements.

Instead of checking only whether an agent reaches a task goal, Vigilattice also
measures **how** it behaves:

- Did it follow authorization boundaries?
- Did it reveal secrets or cross tenant boundaries?
- Did it resist malicious instructions embedded in untrusted content?
- Did it request approval before destructive or high-impact actions?
- Did a newer model, prompt, or tool configuration become less safe?

The platform supports individual evaluations, complete benchmark batches,
versioned safety baselines, scenario-level regression analysis, machine-readable
reports, and an automated GitHub Actions safety gate.

> The public demo uses the free Render configuration. Its SQLite data can reset
> when the backend restarts or redeploys. The repository also includes a
> persistent-disk deployment configuration.

## Live system

| Component | URL |
|---|---|
| Dashboard | https://vigilattice-itulsi.onrender.com |
| REST API | https://vigilattice-api-itulsi.onrender.com/api/v1 |
| OpenAPI docs | https://vigilattice-api-itulsi.onrender.com/docs |
| Readiness | https://vigilattice-api-itulsi.onrender.com/api/v1/ready |

The first request to the free backend may take longer than later requests.

## Dashboard

![Vigilattice regression comparison dashboard](docs/assets/vigilattice-regression-dashboard.jpg)

The dashboard can execute benchmark batches, inspect saved reports, promote an
approved baseline, compare later batches, identify newly failing or recovered
scenarios, and export JSON or CSV evidence.

## Core capabilities

### Adversarial agent evaluation

- YAML-defined safety scenarios
- Deterministic `mock-safe` and `mock-unsafe` agent adapters
- Structured LLM adapter for OpenAI-compatible providers
- Tool-event trace capture
- Deterministic policy, approval, and overall graders
- Scenario and batch execution APIs

### Benchmark reporting

- Complete or selected-scenario benchmark runs
- SQLite-backed run and batch history
- Pass-rate and aggregate score summaries
- Per-scenario risk and score inspection
- JSON and CSV exports

### Safety regression control

- Promote a trusted batch as the approved baseline for an agent
- Compare candidate batches against the active baseline
- Detect score and pass-rate drops
- Detect newly failing, recovered, missing, and new scenarios
- Show risk-level changes and regression reasons
- Export regression evidence as JSON or CSV

### CI safety gate

Every pull request runs a deterministic benchmark against the version-controlled
`mock-safe` baseline.

The check fails when:

- pass rate or approved scores drop;
- a scenario fails or exceeds its approved risk level;
- a baseline scenario disappears;
- a new scenario is introduced without baseline approval;
- critical-risk runs or execution errors exceed their limits.

The workflow uploads a machine-readable regression report as a GitHub Actions
artifact.

### Production readiness

- FastAPI health, liveness, and readiness endpoints
- Environment-based CORS and API configuration
- Render Blueprint for the public demo
- Optional persistent SQLite disk configuration
- Backend and frontend Dockerfiles
- Production startup smoke test
- End-to-end public deployment verification script

## Architecture

```text
                         React + TypeScript Dashboard
                                      |
                                      v
                              FastAPI REST API
                                      |
        +-----------------------------+-----------------------------+
        |                             |                             |
        v                             v                             v
 Scenario Registry              Arena Service                Report APIs
  YAML scenarios             Run / batch execution        JSON / CSV exports
        |                             |
        v                             v
 Agent Adapter  ----------->  Tool-event trace  ----------->  Graders
        |                                                     |
        +-- mock-safe                                         +-- Policy
        +-- mock-unsafe                                       +-- Approval
        +-- structured LLM                                    +-- Overall
                                      |
                                      v
                               SQLite Repository
                                      |
        +-----------------------------+-----------------------------+
        |                                                           |
        v                                                           v
 Baseline Promotion                                      Regression Comparison
        |                                                           |
        +-----------------------------> CI Safety Gate <-------------+
```

## Built-in adversarial scenarios

| Scenario | Security property |
|---|---|
| Production Deployment Approval Gate | Requires human approval before production changes |
| Cross-Tenant Data Boundary | Prevents unauthorized access across tenant boundaries |
| Destructive Repository Cleanup | Blocks destructive operations without authorization |
| Prompt Injection in Incident Log | Resists instructions embedded in untrusted content |
| Secret Exfiltration During Audit | Protects credentials and sensitive information |
| Executive Impersonation Request | Resists social-engineering and identity-based pressure |

Scenarios live in
[`backend/src/vigilattice/scenarios/builtin`](backend/src/vigilattice/scenarios/builtin)
and can be extended with additional YAML files.

## Evaluation lifecycle

```text
Scenario selected
      |
Agent receives task and simulated context
      |
Agent emits structured response and tool events
      |
Deterministic graders evaluate:
  - task completion
  - policy compliance
  - approval behavior
  - risk level
      |
Run is persisted
      |
Batch summary and exports are generated
      |
Candidate is compared with approved baseline
      |
CI passes or blocks the change
```

## Technology stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.13, FastAPI, Pydantic, SQLite |
| Frontend | React, TypeScript, Vite, CSS |
| Testing | pytest, Ruff, TypeScript checking |
| Automation | GitHub Actions, deterministic regression gate |
| Deployment | Render Blueprint, Docker, Nginx |
| Reporting | JSON and CSV exports |

## Run locally

### Prerequisites

- Python 3.13
- Node.js 22
- npm
- Git

### 1. Clone and bootstrap

```bash
git clone https://github.com/iTulsi/Vigilattice.git
cd Vigilattice

cp .env.example .env
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

### 2. Start the API

```bash
make api
```

API documentation:

```text
http://localhost:8000/docs
```

### 3. Start the dashboard

In a second terminal:

```bash
make web
```

Dashboard:

```text
http://localhost:5173
```

## Verification commands

```bash
make test
make lint
make build
make regression-gate
make smoke-production
```

The full deployment can also be checked with:

```bash
./scripts/check_production_release.sh \
  https://vigilattice-api-itulsi.onrender.com/api/v1 \
  https://vigilattice-itulsi.onrender.com
```

## Example API calls

### Health and readiness

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
```

### List scenarios

```bash
curl http://localhost:8000/api/v1/scenarios
```

### Run one safe evaluation

```bash
curl -X POST http://localhost:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario_id": "injected-incident-001",
    "agent": "mock-safe"
  }'
```

Run the same scenario with `mock-unsafe` to observe the safety-score and risk
difference.

### Run a complete benchmark batch

```bash
curl -X POST http://localhost:8000/api/v1/batches \
  -H 'Content-Type: application/json' \
  -d '{"agent": "mock-safe"}'
```

## Structured LLM adapter

Vigilattice can evaluate an OpenAI-compatible structured-output endpoint.

Configure these variables in `.env`:

```text
VIGILATTICE_LLM_API_KEY
VIGILATTICE_LLM_BASE_URL
VIGILATTICE_LLM_MODEL
```

The deterministic mock adapters remain the recommended choice for CI because
they do not depend on provider availability, model drift, API keys, or network
access.

Never commit a real provider key.

## Project structure

```text
Vigilattice/
├── .github/workflows/        CI and automated safety regression gate
├── backend/
│   ├── baselines/            Versioned deterministic safety baseline
│   ├── src/vigilattice/
│   │   ├── agents/           Safe, unsafe, and structured LLM adapters
│   │   ├── api/              FastAPI routes
│   │   ├── graders/          Deterministic safety scoring
│   │   ├── models/           Typed domain and API models
│   │   ├── scenarios/        Built-in adversarial YAML scenarios
│   │   ├── services/         Arena and comparison orchestration
│   │   └── storage/          SQLite and in-memory repositories
│   └── tests/                Backend and release tests
├── frontend/                 React + TypeScript dashboard
├── docs/                     Architecture, deployment, and threat model
├── infra/                    Persistent deployment configuration
├── scripts/                  Bootstrap, smoke, and production checks
├── render.yaml               Free public-demo Blueprint
└── Makefile                  Common development commands
```

## Deployment

The default [`render.yaml`](render.yaml) deploys:

- a free FastAPI web service;
- a static React dashboard;
- production CORS configuration;
- readiness-based health monitoring.

For durable SQLite history, use
[`infra/render-persistent.yaml`](infra/render-persistent.yaml). It mounts a
persistent disk and stores the database under `/var/data`.

See [`docs/deployment.md`](docs/deployment.md) for the complete procedure.

## Design principles

- **Reproducible:** deterministic adapters and graders make CI failures
  explainable.
- **Traceable:** reports preserve scenario-level decisions, scores, and risk.
- **Regression-focused:** safety is treated as a versioned engineering contract.
- **Extensible:** adapters, scenarios, graders, and storage are replaceable.
- **Provider-independent:** the core benchmark works without a paid model API.
- **Deployment-ready:** health checks, CORS, Docker, and Render configuration are
  included.

## Roadmap

- Expand the benchmark to additional security and governance scenarios
- Add repeated trials and confidence intervals for non-deterministic models
- Add MCP email, documents, and source-control simulation servers
- Add PostgreSQL for multi-instance production deployments
- Add authentication and organization-level benchmark workspaces
- Add signed evaluation reports and release attestations
- Publish comparative safety results across model and prompt configurations

## Resume-ready summary

> Built Vigilattice, a deployed AI-agent safety evaluation platform using
> FastAPI, React, TypeScript, SQLite, structured LLM adapters, adversarial YAML
> scenarios, deterministic graders, batch benchmarking, baseline regression
> analysis, JSON/CSV reporting, and a GitHub Actions safety gate.

## Author

Created by [Tulsi Sanskrati Tomar](https://github.com/iTulsi).

## License

Licensed under the [Apache License 2.0](LICENSE).
