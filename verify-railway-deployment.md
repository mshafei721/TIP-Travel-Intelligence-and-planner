# Railway Deployment Verification Checklist

**Project ID**: bd8a2586-5550-460f-a396-fe173d7505b1
**Project Name**: TIP
**Environment**: production

## Quick Access
- **Railway Dashboard**: https://railway.app/project/bd8a2586-5550-460f-a396-fe173d7505b1
- **Logged in as**: Mohammed Elshafei (mido_721@hotmail.com)

---

## ✅ Services Verification Checklist

### 1. Redis Service
**Purpose**: Cache and message broker for Celery

- [ ] Service Status: Active (green)
- [ ] Service Name: Redis
- [ ] REDIS_URL variable exists
- [ ] Memory usage reasonable
- [ ] No errors in logs

**How to check**:
1. Go to Railway dashboard
2. Click on "Redis" service
3. Check "Deployments" tab - should show "Active"
4. Check "Variables" tab - should have REDIS_URL
5. Check "Metrics" tab - should show activity

---

### 2. Backend API Service
**Purpose**: Main FastAPI application

- [ ] Service Status: Active (green)
- [ ] Service Name: TIP-Travel-Intelligence-and-planner
- [ ] Public domain exists (e.g., tip-backend.up.railway.app)
- [ ] Health endpoint responds: `https://[your-domain]/health` returns `{"status":"ok"}`
- [ ] All required environment variables set (see below)
- [ ] Build successful
- [ ] No errors in logs

**Required Environment Variables**:
```
✅ SUPABASE_URL
✅ SUPABASE_SERVICE_KEY
✅ ANTHROPIC_API_KEY
✅ REDIS_URL (reference: ${{Redis.REDIS_URL}})
✅ CELERY_BROKER_URL (reference: ${{Redis.REDIS_URL}})
✅ CELERY_RESULT_BACKEND (reference: ${{Redis.REDIS_URL}})
✅ ENVIRONMENT=production
✅ PORT (auto-set by Railway)
```

**Optional Variables**:
```
⚪ RAPIDAPI_KEY (for Travel Buddy AI - Visa Agent)
⚪ VISUAL_CROSSING_API_KEY (for Weather Agent)
⚪ EXCHANGERATE_API_KEY (for Currency Agent)
```

**How to check**:
1. Click on Backend API service
2. Go to "Settings" > "Domains" - note your public URL
3. Go to "Variables" tab - verify all required variables exist
4. Go to "Deployments" tab - latest deployment should be "Active"
5. Test health endpoint in browser: `https://[your-domain]/health`
6. Check "Logs" tab for any errors

**Start Command** (should be):
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
```

---

### 3. Celery Worker Service
**Purpose**: Background task processor for AI agents

- [ ] Service Status: Active (green)
- [ ] Service Name: celery-worker
- [ ] All environment variables match Backend API
- [ ] Logs show "celery@worker ready"
- [ ] No errors in logs

**Required Environment Variables** (same as Backend):
```
✅ SUPABASE_URL
✅ SUPABASE_SERVICE_KEY
✅ ANTHROPIC_API_KEY
✅ REDIS_URL (reference: ${{Redis.REDIS_URL}})
✅ CELERY_BROKER_URL (reference: ${{Redis.REDIS_URL}})
✅ CELERY_RESULT_BACKEND (reference: ${{Redis.REDIS_URL}})
✅ ENVIRONMENT=production
```

**How to check**:
1. Click on "celery-worker" service
2. Go to "Variables" tab - verify all required variables exist
3. Go to "Deployments" tab - should show "Active"
4. Check "Logs" tab - should see:
   ```
   [timestamp] celery@worker ready.
   [timestamp] Registered tasks:
   - app.tasks.agent_jobs.execute_visa_agent
   - app.tasks.agent_jobs.execute_country_agent
   - app.tasks.cleanup.cleanup_expired_tasks
   ```

**Start Command** (should be):
```
celery -A app.core.celery_app worker --loglevel=info
```

---

### 4. Celery Beat Service (Optional)
**Purpose**: Periodic task scheduler

- [ ] Service Status: Active (green) OR not deployed yet
- [ ] Service Name: celery-beat
- [ ] All environment variables match Backend API
- [ ] Logs show "Scheduler: Sending" messages

**Note**: This is optional for MVP. Only needed if you want automated cleanup tasks to run daily.

---

## 🔧 Configuration Files Verification

### railway.toml (Root Directory)
Current configuration:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"
dockerContext = "backend"
watchPatterns = ["backend/**"]

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Status**: ✅ Configured for Backend API service

---

## 🧪 Testing Deployment

### 1. Test Backend Health
```bash
curl https://[your-backend-domain]/health
```
**Expected Response**:
```json
{"status":"ok"}
```

### 2. Test API Docs
Open in browser:
```
https://[your-backend-domain]/docs
```
**Expected**: Swagger UI documentation page loads

### 3. Test Visa Agent (if RAPIDAPI_KEY set)
Using the API docs or curl:
```bash
curl -X POST "https://[your-backend-domain]/api/trips/{trip-id}/generate-visa" \
  -H "Authorization: Bearer YOUR_SUPABASE_JWT"
```

---

## 📊 Cost Estimation

Based on Railway Hobby plan pricing:

**Current Services**:
1. Redis: ~$5/month
2. Backend API: ~$5/month (with 2 workers)
3. Celery Worker: ~$5/month

**Total**: ~$15/month (within Hobby plan $20/month limit)

**Notes**:
- Free $5 credit each month
- Actual cost depends on usage
- Can upgrade to Pro ($20/month) if needed

---

## 🐛 Common Issues & Solutions

### Issue 1: Backend service shows "Failed" status
**Solutions**:
- Check "Logs" tab for error messages
- Verify Dockerfile builds locally: `docker build -t tip-backend backend/`
- Check environment variables are all set
- Verify SUPABASE_URL and SUPABASE_SERVICE_KEY are correct

### Issue 2: Celery worker not starting
**Solutions**:
- Verify REDIS_URL is correctly referenced: `${{Redis.REDIS_URL}}`
- Check "Logs" for connection errors
- Ensure all environment variables match Backend service
- Verify Redis service is Active

### Issue 3: Health endpoint returns 404
**Solutions**:
- Check Start Command is correct
- Verify railway.toml healthcheckPath = "/health"
- Check logs for startup errors
- Ensure PORT variable is being used

### Issue 4: Tasks not executing
**Solutions**:
- Verify Celery Worker is Active
- Check Redis connection in both Backend and Worker logs
- Verify CELERY_BROKER_URL and CELERY_RESULT_BACKEND are set
- Check agent job logs in Backend service

---

## 📝 Quick Verification Commands

Run these from your local terminal (project directory):

```bash
# 1. Check Railway login status
railway whoami

# 2. Check project link
railway status

# 3. View logs (requires selecting a service interactively)
railway logs

# 4. Redeploy a service (requires selecting a service)
railway up
```

---

## ✅ Final Checklist

Once you've verified everything above:

- [ ] All 3+ services are Active (Redis, Backend, Celery Worker)
- [ ] Backend health endpoint responds correctly
- [ ] All required environment variables are set
- [ ] No errors in service logs
- [ ] API documentation is accessible
- [ ] Railway domain is working
- [ ] Costs are within expected range

**If all checkboxes are ticked**: ✅ Your Railway deployment is complete and healthy!

**If any issues**: Check the "Common Issues & Solutions" section above.

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/project/bd8a2586-5550-460f-a396-fe173d7505b1
- **Railway Docs**: https://docs.railway.app/
- **Railway CLI Reference**: https://docs.railway.app/develop/cli
- **Supabase Dashboard**: https://app.supabase.com/
- **Anthropic Console**: https://console.anthropic.com/

---

**Last Updated**: 2025-12-25
**Project**: TIP - Travel Intelligence & Planner
**Environment**: production
