# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies (sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system mluser && \
    useradd --system --create-home --gid mluser mluser

# Workdir
WORKDIR /app

# Create dirs for artifacts and db
RUN mkdir -p /app/mlruns /app/db && \
    chown -R mluser:mluser /app

# Install mlflow (pin version if you want)
RUN pip install --no-cache-dir mlflow[extras]

# Switch to non-root user
USER mluser

# Environment variables
ENV MLFLOW_BACKEND_STORE_URI=sqlite:////app/db/mlflow.db \
    MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlruns \
    MLFLOW_HOST=0.0.0.0 \
    MLFLOW_PORT=5000 \
    MLFLOW_SERVER_ALLOWED_HOSTS=*

# Expose MLflow port
EXPOSE 5000

# Run MLflow tracking server
CMD ["mlflow", "server"]
