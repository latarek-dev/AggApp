FROM python:3.10-slim

# (opcjonalnie) narzędzia do kompilacji, gdyby brakło gotowych wheel-i
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1) najpierw zależności, żeby caching builda działał
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) potem cały kod (w tym ABI jsony, których używa config.py)
COPY . .

EXPOSE 8000

# Prosto i stabilnie: uvicorn bez reload (prod/dev)
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]