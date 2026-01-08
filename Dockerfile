FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY auth_setup.py .
COPY auth_setup_manual.py .

# Create directory for credentials
RUN mkdir -p /app/credentials

# Set environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]
