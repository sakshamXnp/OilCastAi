FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories so models/data can be mapped locally if needed
RUN mkdir -p /app/data /app/ml_models

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001", "--reload"]
