# IoT Dashboard DHT11 - Docker Deployment

## Quick Start with Docker

### Build Image
```bash
docker build -t iot-dashboard-dht11 .
```

### Run Container
```bash
docker run -p 8050:8050 iot-dashboard-dht11
```

### Access Dashboard
Open browser and go to: http://localhost:8050

---

## Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8050')"

# Run application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8050", "--workers", "2"]
```

---

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    container_name: iot-dashboard-dht11
    ports:
      - "8050:8050"
    environment:
      - PORT=8050
      - DEBUG=False
    restart: unless-stopped
    networks:
      - iot-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8050"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  iot-network:
    driver: bridge
```

### Run with Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## Production Deployment

### Using Gunicorn with Multiple Workers
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8050", "--workers", "4", "--worker-class", "sync", "--timeout", "60"]
```

### Using Nginx Reverse Proxy
```nginx
upstream dash_app {
    server dashboard:8050;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://dash_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Tips

- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds can reduce image size
- Always use specific Python versions (not `latest`)
- Include health checks for better orchestration
- Use environment variables for configuration
