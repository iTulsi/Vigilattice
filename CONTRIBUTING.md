# Contributing to Vigilattice

Thank you for your interest in contributing! Vigilattice is an adversarial
evaluation platform for autonomous AI agents, and contributions that expand its
scenario library, improve its grading logic, or strengthen its documentation
are especially welcome.

---

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Development setup](#development-setup)
- [Project layout](#project-layout)
- [PR checklist](#pr-checklist)
- [Adding a new adversarial scenario](#adding-a-new-adversarial-scenario)
- [Writing a new agent adapter](#writing-a-new-agent-adapter)
- [Tests](#tests)
- [Code style](#code-style)
- [Commit conventions](#commit-conventions)
- [Opening a pull request](#opening-a-pull-request)

---

## Ways to contribute

- **New adversarial scenarios** — YAML files that test a security or policy
  property not yet covered by the six built-in scenarios.
- **Bug fixes** — correctness issues in graders, the regression gate, or the
  API.
- **Documentation** — clearer setup instructions, scenario authoring guides,
  architecture diagrams.
- **Roadmap items** — see the roadmap section in `README.md` for planned work
  (repeated trials, PostgreSQL support, signed reports, etc.).

If you are unsure whether a change is in scope, open an issue first.

---

## Development setup

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.13 |
| Node.js | 22 |
| npm | bundled with Node 22 |
| Git | any recent version |

### Bootstrap

```bash
git clone https://github.com/iTulsi/Vigilattice.git
cd Vigilattice

cp .env.example .env          # fill in VIGILATTICE_LLM_API_KEY if you want
                              # the LLM adapter; mock adapters work without it
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

The bootstrap script creates the Python virtualenv under `backend/.venv` and
installs all Python and Node dependencies.

### Run locally

Open two terminals:

```bash
# Terminal 1 — API (http://localhost:8000/docs)
make api

# Terminal 2 — Dashboard (http://localhost:5173)
make web
```

---

## Project layout

```
Vigilattice/
├── backend/
│   ├── baselines/            Approved safety baselines (JSON, version-controlled)
│   └── src/vigilattice/
│       ├── agents/           Agent adapters (mock-safe, mock-unsafe, LLM)
│       ├── api/              FastAPI route handlers
│       ├── graders/          Deterministic policy / approval / overall graders
│       ├── models/           Pydantic domain and API models
│       ├── scenarios/
│       │   └── builtin/      Built-in adversarial YAML scenarios ← add yours here
│       ├── services/         Arena orchestration and regression comparison
│       └── storage/          SQLite and in-memory repositories
├── frontend/                 React + TypeScript dashboard
├── docs/                     Architecture, deployment, scenario authoring guides
├── scripts/                  Bootstrap, smoke, and production-check scripts
└── Makefile                  Common development commands
```

---

## PR checklist

Before opening a pull request, run all of the following locally and make sure
each command exits cleanly:

```bash
make test             # 47+ backend pytest tests
make lint             # Ruff (Python) + ESLint (TypeScript)
make build            # Python compile-check + frontend production build
make regression-gate  # deterministic safety regression against mock-safe baseline
```

If your change adds a new scenario or modifies grader logic, also verify the
regression-gate report at `/tmp/vigilattice-regression-gate-report.json` shows
no unexpected regressions before and after your change.

---

## Adding a new adversarial scenario

Scenarios are YAML files in `backend/src/vigilattice/scenarios/builtin/`. The
scenario registry loads every `.yaml` file in that directory automatically —
no code registration is needed.

See [`docs/scenario-authoring.md`](docs/scenario-authoring.md) for a full
field-by-field reference and an annotated template.

**Quick steps:**

1. Create `backend/src/vigilattice/scenarios/builtin/<your-id>.yaml`.
2. Run `make api` and verify your scenario appears in
   `GET /api/v1/scenarios`.
3. Run a safe and unsafe evaluation against it:
   ```bash
   curl -X POST http://localhost:8000/api/v1/runs \
     -H 'Content-Type: application/json' \
     -d '{"scenario_id": "<your-id>", "agent": "mock-safe"}'

   curl -X POST http://localhost:8000/api/v1/runs \
     -H 'Content-Type: application/json' \
     -d '{"scenario_id": "<your-id>", "agent": "mock-unsafe"}'
   ```
4. Confirm `mock-safe` passes and `mock-unsafe` fails with the expected risk
   level.
5. Run `make regression-gate` to verify the existing baseline is unaffected.

New scenarios introduced without an approved baseline are flagged by the CI
safety gate. If you intend the scenario to become part of the gate, note that
in your PR description and the maintainer will promote the baseline after
review.

---

## Writing a new agent adapter

Agent adapters live in `backend/src/vigilattice/agents/`. Each adapter must
implement the `AgentAdapter` interface (see `agents/base.py`) and return a
structured response with tool events that the graders can evaluate.

Register your adapter by adding it to the adapter registry in
`agents/__init__.py` under a new string key. That key becomes the value
accepted by `POST /api/v1/runs` in the `"agent"` field.

The deterministic `mock-safe` and `mock-unsafe` adapters are the reference
implementations to read first.

---

## Tests

Backend tests live in `backend/tests/`. Run them with:

```bash
make test
# or directly:
cd backend && .venv/bin/python -m pytest -q
```

When adding a scenario, include at least one test that asserts:
- `mock-safe` produces a passing overall grade.
- `mock-unsafe` produces a failing overall grade with the expected risk level.

When modifying a grader, update or add tests in `backend/tests/` that cover
the changed logic path.

---

## Code style

**Python** — Ruff is the linter and formatter. Run `make lint` and
`make format` before committing. Configuration lives in
`backend/pyproject.toml`.

**TypeScript / React** — ESLint with the project's config. Run
`cd frontend && npm run lint` and `npm run format`.

No new `# type: ignore` or `eslint-disable` comments without an accompanying
explanation comment.

---

## Commit conventions

Use the conventional commits format:

```
feat: add tool-poisoning adversarial scenario
fix: approval grader now handles missing approval_requested field
docs: add scenario-authoring guide
test: add grader tests for cross-tenant boundary scenario
chore: bump ruff to 0.9
```

Keep commit messages in the imperative mood ("add", "fix", "remove") and under
72 characters in the subject line.

---

## Opening a pull request

1. Fork the repository and create a branch off `main`:
   ```bash
   git checkout -b feat/your-scenario-name
   ```
2. Make your changes, run the checklist above, commit.
3. Push and open a PR against `main` in the upstream repo.
4. In the PR description, include:
   - **What** the change adds or fixes.
   - **Why** it matters (which security property it covers, which bug it
     resolves).
   - The output of `make regression-gate` (copy the summary line).
   - For new scenarios: the `mock-safe` and `mock-unsafe` run results (JSON
     snippet is fine).

The CI pipeline runs `make test`, `make lint`, `make build`, and the safety
regression gate automatically on every PR.
