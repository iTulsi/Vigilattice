FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "fastapi run src/vigilattice/main.py --host 0.0.0.0 --port ${PORT:-8000}"]
