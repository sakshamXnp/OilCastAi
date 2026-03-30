FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent SQLite
RUN mkdir -p /app/data

# Expose port and start
ENV PORT 8000
EXPOSE $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
