FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mcp_server.py .
COPY original_functions.py .

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user for security
RUN adduser --disabled-password --gecos '' mcpuser
USER mcpuser

# Run the MCP server
CMD ["python", "mcp_server.py"]
