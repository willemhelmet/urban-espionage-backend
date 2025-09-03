# WebSocket Production Deployment Guide

## Overview

This guide explains how to deploy the Urban Espionage backend with full WebSocket support for real-time game features.

## Architecture

The production setup runs two parallel servers:
- **Gunicorn** (port 8000): Handles HTTP/REST API requests
- **Daphne** (port 8001): Handles WebSocket connections
- **Redis**: Message broker for WebSocket channels
- **Caddy/nginx**: Reverse proxy to route traffic

```
Internet
    |
    v
Caddy (port 80/443)
    |
    +---> /ws/* ----> Daphne (8001)
    |
    +---> /* -------> Gunicorn (8000)
```

## Prerequisites

1. **Redis Server**: Required for WebSocket message routing
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   
   # Or use Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Environment Variables**: Update `.env.production`
   ```env
   REDIS_HOST=localhost  # or your Redis server IP
   DJANGO_SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://user:pass@host:5432/dbname
   ALLOWED_HOSTS=urban-espionage.rcdis.co,www.urban-espionage.rcdis.co
   ```

## Deployment Options

### Option 1: Using Supervisor (Recommended for VPS)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   sudo apt-get install supervisor
   ```

2. **Copy supervisor config**:
   ```bash
   sudo cp supervisor.conf /etc/supervisor/conf.d/urban-espionage.conf
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

3. **Start services**:
   ```bash
   sudo supervisorctl start urban-espionage:*
   ```

4. **Check status**:
   ```bash
   sudo supervisorctl status
   ```

### Option 2: Using Docker (Recommended for containerized deployments)

1. **Build production image**:
   ```bash
   docker build -f Dockerfile.prod -t urban-espionage-prod .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Option 3: Manual startup script

1. **Use the dual-server script**:
   ```bash
   chmod +x bin/serve-with-websockets.sh
   ./bin/serve-with-websockets.sh
   ```

## Web Server Configuration

### Using Caddy (Automatic HTTPS)

1. **Install Caddy**:
   ```bash
   # See https://caddyserver.com/docs/install
   ```

2. **Copy Caddyfile**:
   ```bash
   sudo cp Caddyfile /etc/caddy/Caddyfile
   sudo systemctl reload caddy
   ```

### Using nginx

Use the existing `nginx.conf` in the repository.

## Testing WebSocket Connection

### 1. Test with wscat
```bash
npm install -g wscat
wscat -c wss://urban-espionage.rcdis.co/ws/game/TEST123/
```

### 2. Test with curl
```bash
# Should return 426 Upgrade Required or similar
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  https://urban-espionage.rcdis.co/ws/game/TEST123/
```

### 3. Browser Console Test
```javascript
const ws = new WebSocket('wss://urban-espionage.rcdis.co/ws/game/TEST123/');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

## Monitoring

### Check server logs
```bash
# Supervisor logs
sudo tail -f /var/log/supervisor/*.log

# Docker logs
docker-compose logs -f daphne
docker-compose logs -f web

# Manual script output
# Will show in terminal
```

### Monitor Redis connections
```bash
redis-cli
> CLIENT LIST
> MONITOR  # Watch real-time commands
```

## Troubleshooting

### WebSocket connection fails

1. **Check if Daphne is running**:
   ```bash
   ps aux | grep daphne
   netstat -tlnp | grep 8001
   ```

2. **Check Redis connection**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

3. **Check Caddy/nginx config**:
   ```bash
   # Test configuration
   caddy validate --config /etc/caddy/Caddyfile
   nginx -t
   ```

4. **Check firewall**:
   ```bash
   # Ensure ports are open
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Daphne not running or wrong port |
| "426 Upgrade Required" | WebSocket headers not being proxied correctly |
| "Redis connection lost" | Redis server down or wrong host |
| "403 Forbidden" | ALLOWED_HOSTS not configured |
| "502 Bad Gateway" | Backend servers not running |

## Performance Tuning

### Redis Configuration
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Supervisor Worker Tuning
```ini
# Increase workers in supervisor.conf
[program:gunicorn]
command=gunicorn ... --workers 4

[program:daphne]
# Run multiple Daphne instances if needed
numprocs=2
process_name=%(program_name)s_%(process_num)02d
```

## Security Considerations

1. **Use HTTPS/WSS in production** - Caddy handles this automatically
2. **Configure CORS properly** in Django settings
3. **Set strong SECRET_KEY** in production
4. **Use firewall** to restrict access to backend ports
5. **Monitor Redis** - Don't expose Redis to internet

## Rollback Procedure

If WebSocket deployment causes issues:

1. **Switch back to HTTP-only**:
   ```bash
   # Stop Daphne
   sudo supervisorctl stop urban-espionage:daphne
   
   # Or use original serve.sh
   ./bin/serve.sh
   ```

2. **Frontend will automatically fallback** to polling if WebSocket unavailable

## Next Steps

1. Set up monitoring with tools like Prometheus/Grafana
2. Configure log aggregation with ELK stack
3. Set up health checks for WebSocket endpoints
4. Implement WebSocket authentication tokens
5. Add rate limiting for WebSocket connections