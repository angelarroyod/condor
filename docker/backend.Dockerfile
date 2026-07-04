# Shared image for the `api` and `ingest-worker` services — they differ only by
# the compose `command:`. One image, one dependency set, no drift.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/src ./src
COPY backend/alembic.ini ./
COPY backend/alembic ./alembic

RUN pip install --upgrade pip && pip install .

# Default command runs the API; the worker service overrides it in compose.
EXPOSE 8000
CMD ["uvicorn", "condor.main:app", "--host", "0.0.0.0", "--port", "8000"]
