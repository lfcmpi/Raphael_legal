FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY raphael_legal/ raphael_legal/
COPY api/ api/
COPY templates/ templates/

# Create runtime directories
RUN mkdir -p uploads output

EXPOSE 8000

CMD ["sh", "-c", "python -m api.seed && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
