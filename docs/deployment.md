# Vigilattice production deployment

Vigilattice ships with two Render Blueprints:

- `render.yaml` — free public-demo configuration.
- `infra/render-persistent.yaml` — paid backend with a persistent
  SQLite disk.

## Public demo deployment

1. Merge the production-release pull request into `main`.
2. Open Render and choose **New → Blueprint**.
3. Connect `iTulsi/Vigilattice`.
4. Keep the default Blueprint path: `render.yaml`.
5. Review the two services and apply the Blueprint.

Expected public URLs:

```text
https://vigilattice-itulsi.onrender.com
https://vigilattice-api-itulsi.onrender.com
```

The frontend is configured to call:

```text
https://vigilattice-api-itulsi.onrender.com/api/v1
```

If Render requires different service names, update all three matching
values before deploying:

- the frontend service name;
- `VIGILATTICE_CORS_ORIGINS`;
- `VITE_API_BASE_URL`.

## Verify the deployment

```bash
./scripts/check_production_release.sh \
  https://vigilattice-api-itulsi.onrender.com/api/v1 \
  https://vigilattice-itulsi.onrender.com
```

The check validates health, liveness, readiness, scenarios, frontend
availability and the production CORS response.

## Persistence choices

The free Blueprint stores SQLite at `/tmp/vigilattice.db`. This makes
the public demo inexpensive, but saved runs, batches and baselines can
reset when Render restarts or redeploys the backend.

For durable SQLite storage, create the Blueprint using:

```text
infra/render-persistent.yaml
```

That configuration uses a paid `starter` backend, mounts a disk at
`/var/data`, and stores the database at:

```text
/var/data/vigilattice.db
```

A disk-backed SQLite deployment must remain a single backend instance.

## Optional real LLM adapter

The public demo works without a provider key because the deterministic
`mock-safe` and `mock-unsafe` adapters are included.

To enable the structured LLM adapter, add these backend environment
variables in Render:

```text
VIGILATTICE_LLM_API_KEY
VIGILATTICE_LLM_BASE_URL
VIGILATTICE_LLM_MODEL
```

Never commit a real provider key.

## Local production startup test

```bash
make smoke-production
```

This starts the FastAPI production command against a temporary SQLite
database and verifies the public system endpoints.
