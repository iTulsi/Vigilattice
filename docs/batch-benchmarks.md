# Batch benchmarks and reports

Vigilattice can evaluate one agent across the complete adversarial benchmark
suite with a single API request.

A batch:

- executes every selected scenario;
- persists each successful evaluation run;
- continues when an individual provider-backed scenario fails;
- calculates batch pass rate and average safety scores;
- records critical-risk evaluations;
- persists the aggregate batch;
- exports reproducible JSON and CSV reports.

## API

Run the complete built-in benchmark suite:

```http
POST /api/v1/batches
Content-Type: application/json

{
  "agent": "mock-safe"
}
```

Run selected scenarios:

```json
{
  "agent": "llm-structured",
  "scenario_ids": [
    "injected-incident-001",
    "approval-bypass-001"
  ]
}
```

Export a report:

```text
GET /api/v1/batches/{batch_id}/export?format=json
GET /api/v1/batches/{batch_id}/export?format=csv
```
