FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    dos2unix \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create instance directory with correct permissions
RUN mkdir -p /app/instance && \
    chmod 777 /app/instance

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Convert the entrypoint script to Unix format and make it executable
RUN dos2unix docker-entrypoint.sh && \
    chmod +x docker-entrypoint.sh

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

ENTRYPOINT ["/app/docker-entrypoint.sh"]
