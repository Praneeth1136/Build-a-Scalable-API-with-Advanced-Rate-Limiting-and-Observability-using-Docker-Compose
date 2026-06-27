# Stage 1: Build environment
FROM python:3.9-slim-bookworm AS builder
WORKDIR /app 
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Stage 2: Runtime environment 
FROM python:3.9-slim-bookworm
WORKDIR /app
# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install curl for the healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY api ./api
ENV PYTHONPATH=/app 
EXPOSE 8080 

CMD ["uvicorn", "api.src.main:app", "--host", "0.0.0.0", "--port", "8080"]
