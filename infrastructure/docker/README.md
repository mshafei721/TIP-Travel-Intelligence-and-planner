# TIP Docker Infrastructure

This directory contains Docker-related configuration and documentation for local development.

## Overview

The TIP application uses Docker Compose to orchestrate multiple services:
- **Redis**: Message broker and cache
- **Backend API**: FastAPI application
- **Celery Worker**: Async task processing for AI agents
- **Celery Beat**: Periodic task scheduler
- **Flower**: Celery monitoring UI

## Quick Start

### Prerequisites
- Docker Desktop installed (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git repository cloned
- `.env` file configured (see `.env.example`)

### Starting All Services

From the project root directory:

```powershell
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Stopping All Services

```powershell
# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes Redis data)
docker-compose down -v
```

## Service Access

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Flower UI | http://localhost:5555 | Celery task monitoring |
| Redis | localhost:6379 | Redis server (no UI) |

## Service Details

### Redis
- **Image**: redis:7-alpine
- **Port**: 6379
- **Data**: Persisted in `redis_data` volume
- **Health check**: `redis-cli ping`

### Backend API
- **Build**: `./backend/Dockerfile`
- **Port**: 8000
- **Command**: `uvicorn app.main:app --reload`
- **Depends on**: Redis
- **Health check**: `curl http://localhost:8000/health`

### Celery Worker
- **Build**: `./backend/Dockerfile`
- **Command**: `celery -A app.core.celery_app worker`
- **Concurrency**: 4 workers (prefork pool)
- **Depends on**: Redis
- **Auto-restart**: Yes

### Celery Beat
- **Build**: `./backend/Dockerfile`
- **Command**: `celery -A app.core.celery_app beat`
- **Purpose**: Schedules periodic tasks (cleanup, deletion queue)
- **Depends on**: Redis
- **Auto-restart**: Yes

### Flower
- **Build**: `./backend/Dockerfile`
- **Command**: `celery -A app.core.celery_app flower`
- **Port**: 5555
- **Purpose**: Web UI for monitoring Celery tasks
- **Depends on**: Redis

## Development Workflow

### Backend Development

The backend container uses volume mounting, so code changes are reflected immediately:

```powershell
# Make changes to backend/app/*.py
# Uvicorn will auto-reload

# View backend logs
docker-compose logs -f backend
```

### Testing Celery Tasks

```powershell
# Access backend container
docker-compose exec backend bash

# Run Python shell
python

# Trigger a test task
from app.tasks.example import add
result = add.delay(2, 3)
print(result.get())  # Should print 5

# View task in Flower
# Open http://localhost:5555
```

### Viewing Task Results

1. Go to http://localhost:5555 (Flower UI)
2. Navigate to "Tasks" tab
3. See all executed tasks with status, args, results

## Troubleshooting

### Service won't start
```powershell
# Check logs
docker-compose logs [service-name]

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Redis connection errors
```powershell
# Check if Redis is running
docker-compose ps

# Restart Redis
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

### Celery worker not picking up tasks
```powershell
# Check worker logs
docker-compose logs celery-worker

# Restart worker
docker-compose restart celery-worker

# Verify Redis connection
docker-compose exec celery-worker python -c "from app.core.celery_app import celery_app; print(celery_app.control.inspect().active())"
```

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process or change port in docker-compose.yml
```

## Production Deployment

For production, services are deployed separately:
- **Backend API**: Railway/Render with Uvicorn workers
- **Celery Workers**: Separate Railway/Render services
- **Redis**: Upstash managed Redis
- **Flower**: Optional, for production monitoring

See `DEPLOYMENT.md` for production setup instructions.

## Volumes

### redis_data
- **Purpose**: Persist Redis data between container restarts
- **Location**: Docker managed volume
- **Backup**: Use `redis-cli SAVE` or `BGSAVE`

## Networks

### tip-network
- **Driver**: bridge
- **Purpose**: Internal communication between services
- **Services**: All TIP services on same network

## Health Checks

All services have health checks configured:
- **Redis**: `redis-cli ping` every 5s
- **Backend**: `curl http://localhost:8000/health` every 10s
- **Others**: Depend on Redis health

## Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f flower

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Environment Variables

All services read from the `.env` file in the project root:
- `SUPABASE_*`: Database credentials
- `REDIS_URL`: Redis connection
- `CELERY_*`: Celery configuration
- See `.env.example` for full list

## Next Steps

1. ✅ Start services: `docker-compose up -d`
2. ✅ Check health: `docker-compose ps`
3. ✅ View logs: `docker-compose logs -f`
4. ✅ Test API: http://localhost:8000/docs
5. ✅ Test Celery: http://localhost:5555
6. 🔨 Implement agents (Phase 2)
7. 🔨 Add CI/CD (Phase 1)
