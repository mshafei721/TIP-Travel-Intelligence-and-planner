# Railway Deployment Guide

## Services Required

For the TIP backend to work properly, you need **3 services** on Railway:

### 1. Backend API (FastAPI)
- **Dockerfile**: `Dockerfile`
- **Command**: (uses Dockerfile CMD)
- **Environment Variables**:
  - All variables from `.env.example`
  - `PORT=8000` (Railway sets this automatically)

### 2. Celery Worker (Background Tasks)
- **Dockerfile**: `Dockerfile.worker`
- **Command**: (uses Dockerfile.worker CMD)
- **Environment Variables**: Same as Backend API
- **Purpose**: Processes AI agent tasks for report generation

### 3. Redis (Message Broker)
- **Use Railway's Redis plugin** or deploy your own
- **Environment Variables**:
  - Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` to your Redis URL

## Step-by-Step Deployment

### Option A: Deploy Celery Worker as Separate Service

1. **Create a new service** in Railway
2. **Connect to the same GitHub repo**
3. **Set the Dockerfile path** to `backend/Dockerfile.worker`
4. **Copy all environment variables** from the backend service
5. **Deploy**

### Option B: Use railway.json for Multi-Service Deploy

Create `railway.json` in backend folder:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## Verifying Celery Worker is Running

1. Check Railway logs for the Celery worker service
2. Look for: `celery@... ready`
3. Test by generating a report from the frontend
4. Monitor progress - should move from 0% to 100%

## Troubleshooting

### Report stuck at 0%
- **Cause**: Celery worker not running or not connected to Redis
- **Fix**: Deploy Celery worker service, verify Redis connection

### Agent jobs failing
- Check Celery worker logs for errors
- Verify all environment variables are set (API keys, etc.)

### Redis connection errors
- Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` are correct
- Ensure Redis service is running and accessible
