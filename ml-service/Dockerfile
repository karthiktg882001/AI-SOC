FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p models data

# Copy and make startup script executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

# Use start.sh script to ensure proper execution
CMD ["/app/start.sh"]

