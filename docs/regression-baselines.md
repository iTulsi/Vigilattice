# Regression baselines

Vigilattice can promote a completed benchmark batch to an approved baseline and
compare later batches for the same agent against it.

A comparison detects:

- pass-rate drops;
- overall, policy and approval score drops;
- newly failing scenarios;
- recovered scenarios;
- missing scenarios;
- increases in critical-risk or execution-error counts.

## Promote a batch

```http
POST /api/v1/regressions/baselines/{batch_id}
```

The selected batch must contain completed evaluations and no execution errors.
Each agent has one current baseline; promoting a new batch replaces the previous
baseline for that agent.

## Read the current baseline

```http
GET /api/v1/regressions/baselines/{agent}
```

## Compare a later batch

```http
GET /api/v1/regressions/compare/{batch_id}
```

Optional thresholds:

```text
max_score_drop=5
max_pass_rate_drop=0
```

The comparison returns `regressed: true` when the candidate exceeds a threshold,
introduces a newly failing or missing scenario, or increases critical or error
counts.

## Export a comparison report

```text
GET /api/v1/regressions/compare/{batch_id}/export?format=json
GET /api/v1/regressions/compare/{batch_id}/export?format=csv
```
