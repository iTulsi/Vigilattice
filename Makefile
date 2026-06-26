.PHONY: bootstrap dev api web test lint format build regression-gate clean

bootstrap:
	./scripts/bootstrap.sh

dev:
	@echo "Run these in two terminals:"
	@echo "  make api"
	@echo "  make web"

api:
	cd backend && .venv/bin/fastapi dev src/vigilattice/main.py --host 0.0.0.0 --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/python -m pytest -q

lint:
	cd backend && .venv/bin/ruff check .
	cd frontend && npm run lint

format:
	cd backend && .venv/bin/ruff format .
	cd frontend && npm run format

build:
	cd backend && .venv/bin/python -m compileall -q src
	cd frontend && npm run build

regression-gate:
	cd backend && .venv/bin/python -m vigilattice.regression_gate \
		--baseline baselines/mock-safe.json \
		--output /tmp/vigilattice-regression-gate-report.json

clean:
	rm -rf backend/.venv backend/.pytest_cache backend/.ruff_cache frontend/node_modules frontend/dist
