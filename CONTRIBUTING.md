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
│       ├── evaluation/       Deterministic safety evaluation engine
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
make test             # backend pytest suite
make lint             # Ruff (Python) + TypeScript type-checking
make build            # Python compile-check + frontend production build
make regression-gate  # deterministic safety regression against mock-safe baseline
```

If your change adds a new scenario, the regression gate is expected to report
that the scenario has no approved baseline until a maintainer reviews and adds
that baseline entry. Confirm there are no other unexpected regression reasons
in `/tmp/vigilattice-regression-gate-report.json`.

---

## Adding a new adversarial scenario

Scenarios are YAML files in `backend/src/vigilattice/scenarios/builtin/`. The
scenario registry loads every `.yaml` file in that directory automatically —
no code registration is needed.

See [`docs/scenario-authoring.md`](docs/scenario-authoring.md) for a full
field-by-field reference and an annotated template.

**Quick steps:**

1. Create `backend/src/vigilattice/scenarios/builtin/<your-id>.yaml`.
2. Add matching safe and unsafe trace fixtures in
   `backend/src/vigilattice/agents/mock.py`. Register the scenario ID in both
   mock agents' `builders` dictionaries.
3. Add tests for scenario loading and the expected safe and unsafe results.
4. Run `make api` and verify your scenario appears in
   `GET /api/v1/scenarios`.
5. Run a safe and unsafe evaluation against it:
   ```bash
   curl -X POST http://localhost:8000/api/v1/runs \
     -H 'Content-Type: application/json' \
     -d '{"scenario_id": "<your-id>", "agent": "mock-safe"}'

   curl -X POST http://localhost:8000/api/v1/runs \
     -H 'Content-Type: application/json' \
     -d '{"scenario_id": "<your-id>", "agent": "mock-unsafe"}'
   ```
6. Confirm `mock-safe` passes and `mock-unsafe` fails as intended.
7. Run the PR checklist and document the expected unbaselined-scenario result
   in the PR description.

Do not update `backend/baselines/mock-safe.json` until a maintainer has reviewed
and approved the new scenario's expected result.

---

## Writing a new agent adapter

Agent adapters live in `backend/src/vigilattice/agents/`. Each adapter must
implement the `AgentAdapter` interface (see `agents/base.py`) and return a
structured response with tool events that the graders can evaluate.

Register the adapter in the `agents` dictionary created by
`get_arena_service()` in `backend/src/vigilattice/services/container.py`. The
adapter's `name` becomes the value accepted by `POST /api/v1/runs` in the
`"agent"` field.

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

**TypeScript / React** — `npm run lint` currently runs the TypeScript compiler
with `tsc --noEmit`; formatting is handled by Prettier. Run
`cd frontend && npm run lint` and `npm run format`.

No new `# type: ignore` or `@ts-ignore` suppressions without an accompanying
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
