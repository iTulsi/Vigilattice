# Changelog

All notable changes to Vigilattice are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Vigilattice uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-26

First stable release of Vigilattice, an adversarial evaluation and
safety-regression platform for autonomous and tool-using AI agents.

### Added

**Core evaluation**
- YAML-defined adversarial safety scenarios
- Deterministic `mock-safe` and `mock-unsafe` agent adapters
- Structured LLM adapter for OpenAI-compatible providers
- Tool-event trace capture
- Deterministic policy, approval, and overall graders

**Built-in scenarios**
- Production Deployment Approval Gate
- Cross-Tenant Data Boundary
- Destructive Repository Cleanup
- Prompt Injection in Incident Log
- Secret Exfiltration During Audit
- Executive Impersonation Request

**Benchmark reporting**
- Individual and batch benchmark execution
- SQLite-backed run and batch history
- Pass-rate and aggregate score summaries
- JSON and CSV report exports

**Safety regression control**
- Approved safety baselines (version-controlled)
- Scenario-level regression comparison
- Detection of score drops, newly failing scenarios, risk-level changes,
  missing baseline scenarios, and unapproved new scenarios
- Regression evidence export as JSON or CSV

**CI safety gate**
- Automated GitHub Actions safety regression gate
- Blocks PRs when pass rate, approved scores, or risk levels regress
- Uploads machine-readable regression report as a GitHub Actions artifact

**Dashboard and API**
- React and TypeScript evaluation dashboard
- FastAPI production API with OpenAPI documentation
- Health, liveness, and readiness endpoints
- Environment-based CORS configuration

**Deployment**
- Render Blueprint for the public demo (`render.yaml`)
- Persistent-disk deployment configuration (`infra/render-persistent.yaml`)
- Backend and frontend Dockerfiles
- Production startup smoke test
- End-to-end public deployment verification script

**Verification (at release)**
- 47 backend tests passing
- Backend lint and frontend type-check passing
- Production frontend build passing
- Automated safety regression gate passing
- Production startup smoke test passing
- Public health, readiness, scenario, and CORS checks passing

---

[1.0.0]: https://github.com/iTulsi/Vigilattice/releases/tag/v1.0.0
