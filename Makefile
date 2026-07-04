.PHONY: dev down test lint fmt migrate seed

# Run the full stack (db, redis, api, ingest-worker, web).
dev:
	docker compose up --build

down:
	docker compose down

# Backend tests (run from the backend package).
test:
	cd backend && python -m pytest -q

# Static analysis: ruff + mypy (backend), eslint + tsc (web).
lint:
	cd backend && ruff check . && mypy
	cd web && npm run lint && npm run typecheck

fmt:
	cd backend && ruff format . && ruff check --fix .

# Alembic migration inside the running api container.
migrate:
	docker compose exec api alembic upgrade head

# Seed default reference data.
seed:
	docker compose exec api python -m condor.seed
