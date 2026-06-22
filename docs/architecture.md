# Vigilattice Architecture

## Design principles

1. Every agent action must be observable and replayable.
2. Scenarios are data, not hard-coded control flow.
3. Agent providers sit behind adapters.
4. Graders remain separable from execution.
5. Deterministic evidence is preferred whenever possible.
6. High-risk actions require explicit policy and approval checks.

## Current modules

- `agents`: Provider-independent execution adapters.
- `scenarios`: Versioned benchmark definitions.
- `evaluation`: Deterministic scoring and findings.
- `storage`: Run persistence boundary.
- `services`: Experiment orchestration.
- `api`: HTTP contracts for the dashboard and CI.
- `mcp_servers`: Future simulated enterprise tool domains.

## Next architectural additions

- PostgreSQL repositories and Alembic migrations
- Background worker for long-running experiments
- MCP gateway and isolated scenario state
- Immutable event stream
- Claude Agent SDK trace adapter
- Model grader service
- OpenTelemetry spans and metrics
