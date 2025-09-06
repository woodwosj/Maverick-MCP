FROM python:3.11-slim

# Install Docker CLI (needed to spawn containers)
RUN apt-get update && \
    apt-get install -y docker.io && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gateway.py .
COPY servers.yaml .

# Create logs directory
RUN mkdir -p logs

# Set Python path
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8000

# Run the gateway
CMD ["python", "gateway.py"]