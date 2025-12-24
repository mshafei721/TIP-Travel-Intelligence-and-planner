# Railway Production Deployment Guide

> **For non-technical users**: This guide will walk you through deploying TIP to Railway step-by-step. Just follow along - no coding required!

## Overview

We'll deploy 4 services to Railway:
1. **Redis** (database for background tasks)
2. **Backend API** (main FastAPI server)
3. **Celery Worker** (processes AI agent tasks in background)
4. **Celery Beat** (scheduler for periodic tasks - optional for now)

**Estimated Time**: 20-30 minutes

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] Railway account (sign up at https://railway.app)
- [ ] GitHub account connected to Railway
- [ ] Supabase project URL and Service Key (from your Supabase dashboard)
- [ ] Anthropic API key (from https://console.anthropic.com)
- [ ] This repository pushed to your GitHub account

---

## Step 1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose this repository: `TIP-Travel-Intelligence-and-planner`
5. Railway will create a new project

**✅ Checkpoint**: You should see a new Railway project with your repo name.

---

## Step 2: Add Redis Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add Redis"**
4. Railway will automatically create a Redis instance
5. **Important**: Railway automatically creates a `REDIS_URL` variable that your other services can use

**✅ Checkpoint**: You should see a Redis service in your project with a green "Active" status.

---

## Step 3: Deploy Backend API Service

1. In your Railway project, you should see a service auto-created from your GitHub repo
2. Click on this service
3. Go to **"Settings"** tab
4. Scroll to **"Start Command"** and verify it says:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
5. Go to **"Variables"** tab
6. Click **"+ New Variable"** and add these one by one:

   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbG...your-key-here

   # Anthropic API (for AI agents)
   ANTHROPIC_API_KEY=sk-ant-...your-key-here

   # Redis (this should auto-populate from Step 2)
   REDIS_URL=${{Redis.REDIS_URL}}
   CELERY_BROKER_URL=${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

   # Environment
   ENVIRONMENT=production
   ```

7. Click **"Deploy"** button
8. Wait 2-3 minutes for deployment

**✅ Checkpoint**:
- Service shows "Active" status
- Click on the service URL (e.g., `https://tip-backend.up.railway.app`)
- Add `/health` to the URL and press Enter
- You should see: `{"status":"ok"}`

---

## Step 4: Deploy Celery Worker Service

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose the same repository: `TIP-Travel-Intelligence-and-planner`
4. Railway creates a new service
5. Click on this new service and rename it to **"celery-worker"**
6. Go to **"Settings"** tab
7. **IMPORTANT**: Override the start command with:
   ```
   celery -A app.core.celery_app worker --loglevel=info --concurrency=2
   ```
8. Set **"Root Directory"** to `backend`
9. Go to **"Variables"** tab
10. **Link variables from Backend API service**:
    - Click **"+ Add Variable"**
    - Select **"Service Variables"**
    - Choose your **Backend API** service
    - This copies all environment variables automatically

**Alternative (Manual)**: Add the same variables as Step 3 if linking doesn't work.

11. Click **"Deploy"**

**✅ Checkpoint**:
- Service shows "Active" status
- Check logs (click "Logs" tab) - you should see:
  ```
  celery@... ready.
  ```

---

## Step 5: Deploy Celery Beat (Optional - for scheduled tasks)

> **Note**: You can skip this for now. Celery Beat is only needed if you want scheduled tasks (e.g., cleanup old trips every night). We'll add this later when needed.

<details>
<summary>Click to expand Celery Beat setup instructions</summary>

1. In your Railway project, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose the same repository
4. Rename service to **"celery-beat"**
5. Go to **"Settings"** tab
6. Override start command:
   ```
   celery -A app.core.celery_app beat --loglevel=info
   ```
7. Set **"Root Directory"** to `backend`
8. Link variables from Backend API service (same as Step 4)
9. **IMPORTANT**: Set replicas to **1** (only one Beat instance should run)
10. Click **"Deploy"**

</details>

---

## Step 6: Update Frontend Environment Variables (Vercel)

Now that your backend is deployed, you need to tell your frontend where to find it.

1. Go to https://vercel.com/dashboard
2. Click on your **TIP** project
3. Go to **"Settings"** → **"Environment Variables"**
4. Update or add:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
   ```
   Replace `your-backend-url` with the actual URL from Railway (found in Step 3)

5. Click **"Save"**
6. Go to **"Deployments"** tab
7. Click **"Redeploy"** to apply the new environment variable

**✅ Checkpoint**:
- Visit your Vercel app URL
- You should be able to log in and see the dashboard
- The frontend can now talk to your production backend!

---

## Step 7: Verify End-to-End Setup

Let's test that everything works together:

### Test 1: Health Check
1. Go to your Railway Backend URL: `https://your-backend.up.railway.app/health`
2. You should see: `{"status":"ok"}`

### Test 2: Frontend Connection
1. Go to your Vercel frontend URL
2. Log in with your test account
3. Navigate to dashboard
4. Create a new trip (don't worry, agents aren't fully implemented yet)
5. Check that data saves correctly

### Test 3: Celery Worker
1. Go to Railway dashboard
2. Click on **celery-worker** service
3. Click **"Logs"** tab
4. You should see worker logs without errors

---

## Troubleshooting

### Backend service won't start
- **Check Logs**: Railway → Backend API → Logs tab
- **Common Issue**: Missing environment variables
  - Go to Variables tab and verify all keys are set
  - Make sure `REDIS_URL` is linked from Redis service

### Celery worker not processing tasks
- **Check Logs**: Railway → celery-worker → Logs
- **Common Issue**: Redis connection failed
  - Verify `REDIS_URL` is set correctly
  - Make sure Redis service is "Active"

### Frontend can't connect to backend
- **Check**: Vercel environment variables
- **Make sure**: `NEXT_PUBLIC_API_URL` matches Railway backend URL
- **Remember**: Redeploy frontend after changing env vars

---

## Cost Estimation

Railway pricing (as of Dec 2024):
- **Hobby Plan**: $5/month (includes $5 credit)
- **Each service**: Uses credits based on usage
- **Estimated monthly cost for TIP**:
  - Redis: ~$2/month
  - Backend API: ~$3-5/month
  - Celery Worker: ~$3-5/month
  - **Total**: ~$8-12/month (within Hobby plan with $5 credit)

**Free Alternative**: Railway offers $5 credit monthly, so if you're under that, it's free!

---

## Next Steps After Deployment

Once everything is deployed:

1. **Test the app thoroughly**
   - Create trips
   - Test all features
   - Monitor logs for errors

2. **Monitor costs**
   - Railway dashboard shows usage
   - Set up billing alerts

3. **Continue development**
   - Next: Implement VisaAgent (I5-AGENT-01)
   - Deploy updates automatically via GitHub push

---

## Quick Commands Reference

```bash
# View backend logs (Railway CLI)
railway logs --service backend-api

# View Celery worker logs
railway logs --service celery-worker

# Redeploy a service
railway up --service backend-api

# Check Redis status
railway run redis-cli ping
```

---

## Support

If you encounter issues:
1. Check Railway logs first (most issues show up there)
2. Check this repository's GitHub Issues
3. Railway Discord: https://discord.gg/railway

---

**🎉 Congratulations!** Your TIP backend is now running in production on Railway!
