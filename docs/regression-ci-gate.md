# Automated safety regression gate

Vigilattice includes a deterministic CI gate that runs the approved
`mock-safe` benchmark on every pull request and push to `main`.

The gate fails when:

- the benchmark pass rate drops below the approved minimum;
- overall, policy or approval scores fall below the baseline;
- a scenario fails or exceeds its approved risk level;
- a baseline scenario disappears;
- a new scenario is added without baseline approval;
- critical-risk runs or execution errors exceed the allowed count.

## Run locally

```bash
make regression-gate
```

The local target writes its JSON report to:

```text
/tmp/vigilattice-regression-gate-report.json
```

## Versioned baseline

The approved deterministic baseline is stored at:

```text
backend/baselines/mock-safe.json
```

Changes to this file should be reviewed like code. Lowering a threshold
or allowing a weaker scenario result changes the project's accepted
safety contract.

## GitHub Actions

`.github/workflows/regression-gate.yml` installs the backend, executes
the gate, and uploads the machine-readable report as a workflow
artifact. A regression exits with status `1`, which blocks the check.

The deterministic mock adapter is used because CI should not depend on
provider availability, API keys, model drift or network access.
