# AIRCTRL Docker Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config.yaml .
COPY assets/ ./assets/

# Create logs and screenshots directories
RUN mkdir -p logs screenshots

# Expose metrics port (if using Prometheus)
EXPOSE 8000

# Run application
CMD ["python", "-m", "src.main"]
