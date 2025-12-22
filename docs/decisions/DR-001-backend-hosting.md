# DR-001: Backend Hosting Platform

**Decision ID:** DR-001
**Title:** Backend Hosting Platform for FastAPI + Celery Workers
**Status:** ✅ **Accepted**
**Date:** 2025-12-22 (Session 2)
**Owner:** TIP Team
**Due Date:** N/A (Decision already made)

---

## Context

The TIP backend requires hosting for:
- **FastAPI application** (Python web server)
- **Celery workers** (background async task processing)
- **Redis** (cache and Celery broker)

The backend must support:
- Async job processing for multi-agent orchestration
- Background workers running continuously
- Scalability from MVP (free tier) to production
- Predictable pricing
- FastAPI-specific deployment patterns

---

## Decision

**Selected Platform:** **Render**

**Deployment Strategy:**
- **MVP (Phases 1-11):** Render Free Tier (testing and development)
- **Production (Phase 12+):** Render Starter Plan
  - Web Service: $7/month
  - Background Worker: $7/month
  - **Total:** $14/month

**Supporting Services:**
- **Frontend:** Vercel (free tier)
- **Redis:** Upstash (free tier → $10/month)
- **Database:** Supabase (free tier → Pro as needed)

---

## Options Considered

### Option 1: Render (SELECTED)
**Pros:**
- ✅ Built-in background worker support (critical for Celery)
- ✅ Predictable flat pricing ($7/service/month)
- ✅ Free tier available for MVP testing
- ✅ Production-ready defaults
- ✅ 24/7 uptime and auto-scaling
- ✅ Well-documented FastAPI support
- ✅ Managed Redis available (if needed)
- ✅ Simple deployment (Docker or native Python)

**Cons:**
- ❌ Slightly more expensive than Railway for low usage
- ❌ Less flexible than AWS for custom infrastructure

**Cost Estimate:**
- MVP: $0/month (free tier)
- Production: $14/month (web + worker)

### Option 2: Railway
**Pros:**
- ✅ Flexible usage-based pricing
- ✅ Potentially cheaper for variable workloads
- ✅ Good developer experience
- ✅ Supports FastAPI

**Cons:**
- ❌ No built-in worker support (requires manual Celery setup)
- ❌ Less predictable costs (usage-based can spike)
- ❌ More complex configuration for background jobs
- ❌ Requires separate service orchestration

**Cost Estimate:**
- MVP: ~$5/month (usage-based)
- Production: $15-30/month (unpredictable)

### Option 3: AWS (EC2/ECS)
**Pros:**
- ✅ Maximum flexibility and control
- ✅ Scalable to millions of users
- ✅ Full infrastructure as code (Terraform)
- ✅ Mature ecosystem

**Cons:**
- ❌ Overkill for MVP
- ❌ High complexity (networking, security groups, load balancers)
- ❌ Expensive for small scale
- ❌ Slow iteration speed during development

**Cost Estimate:**
- MVP: $25-50/month (t3.small instances)
- Production: $100-300/month

---

## Decision Criteria

| Criterion | Weight | Render | Railway | AWS |
|-----------|--------|--------|---------|-----|
| Built-in Worker Support | Critical | ✅ Yes | ❌ No | ⚠️ Manual |
| Predictable Pricing | High | ✅ Flat | ❌ Variable | ❌ Complex |
| Free Tier for MVP | High | ✅ Yes | ✅ Yes | ❌ Limited |
| FastAPI Support | High | ✅ Excellent | ✅ Good | ✅ Manual |
| Ease of Deployment | Medium | ✅ Simple | ✅ Simple | ❌ Complex |
| Scalability | Medium | ✅ Good | ✅ Good | ✅ Excellent |
| Documentation | Medium | ✅ Good | ✅ Good | ✅ Extensive |

**Winner:** Render (highest score on critical criteria)

---

## Analysis

### Why Render Wins:

1. **Built-in Background Workers (Critical):**
   - Render natively supports background workers as a first-class service type
   - Celery can be deployed as a separate "Worker" service that shares code with the web service
   - Railway requires manual Celery setup and doesn't have dedicated worker service type

2. **Predictable Costs:**
   - Render: $7 web + $7 worker = $14/month (fixed)
   - Railway: Usage-based pricing can spike unpredictably with high Celery job volume
   - Budgeting is easier with Render's flat pricing

3. **Production-Ready Defaults:**
   - Render provides 24/7 uptime, auto-scaling, and managed infrastructure out-of-the-box
   - Railway requires more configuration for production readiness

4. **FastAPI Documentation:**
   - Render has official FastAPI deployment guides
   - Railway supports FastAPI but with less documentation

5. **MVP to Production Path:**
   - Free tier allows testing entire stack (web + worker) before paying
   - Smooth upgrade path to Starter plan ($14/month total)

---

## Consequences

### Positive:
- ✅ Simple deployment: Push to GitHub → Auto-deploy to Render
- ✅ Background workers "just work" without manual configuration
- ✅ Predictable monthly costs enable better financial planning
- ✅ Free tier allows full MVP testing before production
- ✅ No vendor lock-in (can migrate to AWS later if needed)

### Negative:
- ⚠️ Slightly more expensive than Railway for very low usage
- ⚠️ Less control than AWS (managed platform constraints)
- ⚠️ Potential cold starts on free tier (acceptable for MVP)

### Mitigation:
- Monitor costs monthly during MVP
- If usage patterns show Railway would be cheaper, re-evaluate in Phase 12
- Plan AWS migration path for Phase 15 if scaling beyond Render's limits

---

## Implementation Notes

**Phase 1 (MVP Setup):**
1. Create Render account
2. Deploy FastAPI as Web Service (free tier)
3. Deploy Celery worker as Background Worker (free tier)
4. Connect to Upstash Redis for Celery broker
5. Configure environment variables
6. Set up automatic deployments from GitHub

**Phase 12 (Production Upgrade):**
1. Upgrade Web Service to Starter ($7/month)
2. Upgrade Background Worker to Starter ($7/month)
3. Monitor performance and scale as needed

**Future (Phase 15):**
- If traffic exceeds Render capacity (>1M requests/month), migrate to AWS
- Use Terraform for infrastructure as code
- Implement blue-green deployments

---

## References

- **Research Sources:**
  - [Render vs Railway comparison (2025)](https://render.com/compare/railway)
  - [FastAPI deployment guide - Render](https://render.com/docs/deploy-fastapi)
  - [Celery worker support - Render](https://render.com/docs/background-workers)
  - [Railway pricing](https://railway.app/pricing)

- **Internal Documentation:**
  - claude-progress.txt:Session 2:171-190 (Decision rationale)
  - docs/services_config.md:30-42 (Redis and backend hosting)
  - docs/comprehensive_plan.md:99 (Backend deployment section)

- **Related Decisions:**
  - DR-002: Map Provider (Mapbox vs Google Maps)

---

**Approved By:** TIP Team
**Effective Date:** 2025-12-22
**Review Date:** Phase 12 (before production deployment)

