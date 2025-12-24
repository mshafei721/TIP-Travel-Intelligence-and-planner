# TIP - Deployment Guide

Complete guide for deploying the Travel Intelligence & Planner application to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Post-Deployment](#post-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- ✅ **Supabase Account** (already configured)
- 🆕 **Railway Account** - [railway.app](https://railway.app) (free tier available)
- 🆕 **Vercel Account** - [vercel.com](https://vercel.com) (free tier available)
- ✅ **GitHub Account** (repository already created)

### Required Information
You'll need the following from your Supabase project:
- Supabase Project URL
- Supabase Anon Key
- Supabase Service Role Key
- Supabase JWT Secret

---

## Environment Variables

### Backend Environment Variables (Railway)

Create these environment variables in Railway:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...  # Public anon key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # Service role key (KEEP SECRET!)
SUPABASE_JWT_SECRET=your-jwt-secret

# Feature Flags
FEATURE_DASHBOARD_HOME=true
FEATURE_RECOMMENDATIONS=true
FEATURE_ANALYTICS=true

# CORS Configuration
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Optional: Redis (if using Celery)
REDIS_URL=redis://localhost:6379/0
```

### Frontend Environment Variables (Vercel)

Create these environment variables in Vercel:

```bash
# Supabase Configuration (Public)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...  # Public anon key only!

# Backend API
NEXT_PUBLIC_BACKEND_URL=https://tip-backend.railway.app

# Feature Flags
NEXT_PUBLIC_FEATURE_DASHBOARD_HOME=true
NEXT_PUBLIC_FEATURE_RECOMMENDATIONS=true
NEXT_PUBLIC_FEATURE_ANALYTICS=true
```

---

## Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your TIP repository
5. Select "tip-backend" as the service name

### Step 2: Configure Build Settings

Railway will automatically detect the Dockerfile. Verify:
- **Build Command**: Uses `Dockerfile`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
- **Root Directory**: `/backend`

### Step 3: Set Environment Variables

In Railway project settings → Variables:

1. Click "+ New Variable"
2. Add each environment variable from the Backend section above
3. **Important**: Never commit secrets to Git!

### Step 4: Deploy

1. Railway will automatically deploy on push to main branch
2. Wait for build to complete (~2-3 minutes)
3. Railway will provide a URL: `https://tip-backend.railway.app`

### Step 5: Verify Deployment

Test the health endpoint:
```bash
curl https://tip-backend.railway.app/health
# Expected: {"status": "healthy"}
```

Test an API endpoint:
```bash
curl https://tip-backend.railway.app/api/trips \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### Step 2: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import your TIP repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Set Environment Variables

In Vercel project settings → Environment Variables:

1. Add each environment variable from the Frontend section above
2. **Important**: Only use `NEXT_PUBLIC_SUPABASE_ANON_KEY` (not service role!)
3. Update `NEXT_PUBLIC_BACKEND_URL` with your Railway URL

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete (~1-2 minutes)
3. Vercel will provide a URL: `https://your-app.vercel.app`

### Step 5: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate will be auto-provisioned

---

## Post-Deployment

### 1. Update CORS Configuration

Update `ALLOWED_ORIGINS` in Railway to include your Vercel URL:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### 2. Update Supabase Redirect URLs

In Supabase Dashboard → Authentication → URL Configuration:
- Add redirect URL: `https://your-app.vercel.app/auth/callback`
- Add site URL: `https://your-app.vercel.app`

### 3. Test Authentication Flow

1. Visit `https://your-app.vercel.app`
2. Click "Sign In"
3. Try email/password login
4. Try Google OAuth login
5. Verify redirect works correctly

### 4. Test Dashboard

1. Log in to the application
2. Navigate to `/dashboard`
3. Verify all cards load:
   - ✅ Quick Actions
   - ✅ Statistics Summary
   - ✅ Recent Trips
   - ✅ Upcoming Trips
   - ✅ Recommendations

### 5. Monitor Logs

**Railway Logs:**
- Go to Railway project → Deployments → View Logs
- Check for errors or warnings

**Vercel Logs:**
- Go to Vercel project → Deployments → View Function Logs
- Check for build errors or runtime errors

---

## Troubleshooting

### Backend Issues

#### Error: "Connection refused" or 502 Bad Gateway
**Cause**: Railway service not running or health check failing

**Solution**:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Restart the deployment: Railway → Deployments → Restart

#### Error: "Supabase connection failed"
**Cause**: Invalid Supabase credentials

**Solution**:
1. Verify `SUPABASE_URL` is correct
2. Verify `SUPABASE_SERVICE_ROLE_KEY` is the service role key (not anon key)
3. Check Supabase project is active

#### Error: "JWT validation failed"
**Cause**: Invalid JWT secret

**Solution**:
1. Get JWT secret from Supabase: Settings → API → JWT Secret
2. Update `SUPABASE_JWT_SECRET` in Railway
3. Restart deployment

### Frontend Issues

#### Error: "Network Error" when fetching data
**Cause**: Incorrect backend URL or CORS issue

**Solution**:
1. Verify `NEXT_PUBLIC_BACKEND_URL` in Vercel matches Railway URL
2. Verify `ALLOWED_ORIGINS` in Railway includes Vercel URL
3. Check Railway logs for CORS errors

#### Error: "Supabase session not found"
**Cause**: Invalid Supabase configuration

**Solution**:
1. Verify `NEXT_PUBLIC_SUPABASE_URL` is correct
2. Verify `NEXT_PUBLIC_SUPABASE_ANON_KEY` is the **anon key** (not service role!)
3. Check redirect URLs in Supabase settings

#### Build Error: "Module not found"
**Cause**: Missing dependencies

**Solution**:
1. Run `npm install` locally to verify dependencies
2. Check `package.json` has all required dependencies
3. Trigger rebuild in Vercel

### Dashboard Issues

#### Dashboard shows 404
**Cause**: Feature flag disabled

**Solution**:
1. Verify `NEXT_PUBLIC_FEATURE_DASHBOARD_HOME=true` in Vercel
2. Redeploy frontend

#### No data showing in dashboard
**Cause**: Backend API not responding or no trips created

**Solution**:
1. Check browser console for API errors
2. Test backend health: `curl https://tip-backend.railway.app/health`
3. Create a test trip to verify data flow

#### Recommendations not showing
**Cause**: Recommendations feature disabled or no visited countries

**Solution**:
1. Verify `FEATURE_RECOMMENDATIONS=true` in Railway
2. Verify `NEXT_PUBLIC_FEATURE_RECOMMENDATIONS=true` in Vercel
3. Check user has at least one completed trip

---

## Performance Optimization

### Backend

1. **Enable Caching** (future enhancement):
   - Add Redis for caching frequently accessed data
   - Configure in Railway as a separate service

2. **Database Optimization**:
   - Ensure database indexes exist (handled by Supabase)
   - Monitor query performance in Supabase Dashboard

3. **Horizontal Scaling** (if needed):
   - Increase worker count in start command: `--workers 4`
   - Upgrade Railway plan for more resources

### Frontend

1. **Image Optimization**:
   - Use Next.js Image component for all images
   - Configure image domains in next.config.ts

2. **Code Splitting**:
   - Already handled by Next.js automatic code splitting
   - Monitor bundle size in Vercel deployment logs

3. **CDN Configuration**:
   - Already handled by Vercel Edge Network
   - No additional configuration needed

---

## Monitoring & Alerts

### Backend Monitoring

**Railway built-in monitoring:**
- CPU usage
- Memory usage
- Request count
- Response times

**Set up alerts:**
1. Railway → Project → Settings → Notifications
2. Enable email/Slack notifications for:
   - Deployment failures
   - High error rates
   - Resource limits

### Frontend Monitoring

**Vercel Analytics (optional):**
1. Enable in Vercel project settings
2. Track:
   - Page views
   - Core Web Vitals
   - User engagement

**Error Tracking:**
- Browser console errors logged automatically
- View in Vercel → Deployments → Function Logs

---

## Backup & Recovery

### Database Backups

Supabase automatically backs up your database:
- Point-in-time recovery available
- Access via Supabase Dashboard → Database → Backups

### Configuration Backups

Environment variables are version-controlled:
- Document all variables in this file
- Store secrets in a secure password manager (1Password, LastPass, etc.)

---

## Security Checklist

- [ ] All API keys stored as environment variables (not in code)
- [ ] Service role key only used on backend (never exposed to frontend)
- [ ] CORS configured to only allow your frontend domain
- [ ] Supabase redirect URLs configured correctly
- [ ] HTTPS enabled on all domains (handled by Vercel/Railway)
- [ ] Security headers configured (X-Frame-Options, CSP, etc.)
- [ ] Rate limiting enabled in Supabase Dashboard

---

## Support

**Deployment Issues:**
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs

**Application Issues:**
- Check GitHub Issues
- Review section documentation in `product-plan/`

---

**Last Updated**: 2025-12-24
**Status**: Ready for Production Deployment
