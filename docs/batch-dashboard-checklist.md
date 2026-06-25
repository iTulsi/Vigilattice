# Batch dashboard verification checklist

Use this checklist after changing the benchmark dashboard.

- Start the backend with `make api`.
- Start the frontend with `make web`.
- Confirm all built-in scenarios are available.
- Run the complete suite with `mock-safe`.
- Confirm the batch reports a 100% pass rate.
- Run the complete suite with `mock-unsafe`.
- Confirm failed scenarios and risk levels are displayed.
- Verify saved batch history.
- Verify JSON report export.
- Verify CSV report export.
- Run tests, lint and the production build.
