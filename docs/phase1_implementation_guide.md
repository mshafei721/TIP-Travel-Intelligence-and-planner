# Phase 1: Foundation - Implementation Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-22
**Status**: Research Complete - Ready for Implementation

---

## Executive Summary

This guide provides comprehensive research findings and implementation patterns for Phase 1: Foundation of the TIP (Travel Intelligence & Planner) project. Phase 1 establishes the core infrastructure including Supabase authentication, Next.js frontend, FastAPI backend, Redis/Celery async processing, and custom Playwright scraping framework.

**Phase 1 Features**: 13 features covering database setup, authentication, frontend/backend initialization, async task processing, Docker containerization, and CI/CD.

**Estimated Duration**: 1-2 development sessions
**Prerequisites**: Phase 0 research complete (✅)

---

## Table of Contents

1. [Supabase Setup & Configuration](#1-supabase-setup--configuration)
2. [Next.js 14+ Frontend Setup](#2-nextjs-14-frontend-setup)
3. [FastAPI Backend Architecture](#3-fastapi-backend-architecture)
4. [Redis + Celery Async Processing](#4-redis--celery-async-processing)
5. [Playwright Scraping Framework](#5-playwright-scraping-framework)
6. [Docker Compose Local Development](#6-docker-compose-local-development)
7. [GitHub Actions CI/CD](#7-github-actions-cicd)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Supabase Setup & Configuration

### 1.1 Overview

Supabase provides a complete Postgres database, authentication, and Row-Level Security (RLS) solution for secure multi-tenant applications.

### 1.2 Authentication Best Practices

#### Email/Password Authentication

```javascript
// Sign up new user
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password-123',
  options: {
    data: {
      full_name: 'John Doe',
      age: 25
    },
    emailRedirectTo: 'https://example.com/welcome'
  }
})

// Sign in existing user
const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password-123'
})
```

#### OAuth Authentication (Google)

```javascript
const { data: oAuthData, error: oAuthError } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'https://example.com/auth/callback',
    scopes: 'email profile'
  }
})
```

### 1.3 Row-Level Security (RLS) Best Practices

**Critical Security Principle**: Always use RLS as a defense-in-depth layer. RLS is enforced at the database level regardless of application logic, preventing unauthorized data access even if future queries inadvertently bypass application-level filters.

#### Enabling RLS

```sql
-- Enable RLS for table
ALTER TABLE public.trips ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users
CREATE POLICY "Users can view own trips"
  ON public.trips FOR SELECT
  USING (auth.uid() IS NOT NULL AND auth.uid() = user_id);
```

#### RLS Performance Optimization

**Best Practices:**
1. **Explicit Role Specification**: Add 'authenticated' to approved roles in the TO option to eliminate anonymous users from policy processing
2. **Null Checks**: Always check `auth.uid() IS NOT NULL` before comparisons to avoid silent failures
3. **Index Support**: Ensure policies align with database indexes for optimal query performance

**Example with Best Practices:**

```sql
CREATE POLICY "Authenticated users view own trips"
  ON public.trips FOR SELECT
  TO authenticated  -- Eliminates anonymous users
  USING (auth.uid() IS NOT NULL AND auth.uid() = user_id);  -- Explicit null check
```

### 1.4 Server-Side Security

**Critical**: Always use `supabase.auth.getUser()` in server-side code, never `supabase.auth.getSession()`.

```javascript
// ✅ CORRECT - Server-side (validates Auth token with Supabase)
const { data: { user } } = await supabase.auth.getUser()

// ❌ WRONG - Server-side (doesn't revalidate, can be spoofed)
const { data: { session } } = await supabase.auth.getSession()
```

**Rationale**: `getUser()` sends a request to Supabase Auth server to revalidate the token, ensuring sessions cannot be spoofed.

### 1.5 Supabase Client Initialization

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      storage: typeof window !== 'undefined' ? window.localStorage : undefined,
      flowType: 'pkce' // Enhanced security with PKCE flow
    },
    db: {
      schema: 'public'
    }
  }
)
```

### 1.6 RLS Testing Strategy

**Comprehensive Testing Required:**
- Test Create, Read, Update, Delete operations
- Test with different user roles (anonymous, authenticated, admin)
- Include negative test cases (verify what users should NOT be able to do)
- Test edge cases that might expose security bypasses

### 1.7 Sources

- [Supabase RLS Best Practices](https://supabase.com/docs/guides/troubleshooting/rls-performance-and-best-practices-Z5Jjwv)
- [Supabase Auth Security Best Practices](https://supabase.com/docs/guides/auth/server-side/nextjs_querygroups=router&router=pages)
- [Supabase Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

---

## 2. Next.js 14+ Frontend Setup

### 2.1 App Router Architecture

Next.js 14+ uses the App Router with Server Components as the default, fundamentally changing data fetching and rendering patterns.

### 2.2 Server Components vs Client Components

**Server Components** (default):
- Render on the server
- Can directly access databases and APIs
- Reduce client-side JavaScript bundle
- Cannot use browser APIs or hooks (useState, useEffect)

**Client Components** (opt-in with `'use client'`):
- Render on client
- Can use hooks and browser APIs
- Required for interactivity

### 2.3 Data Fetching Patterns

#### Direct Database Access in Server Components

```typescript
// app/trips/page.tsx (Server Component)
export default async function TripsPage() {
  // Direct database access - NO API route needed
  const { data: trips } = await supabase
    .from('trips')
    .select('*')
    .eq('user_id', userId)

  return <TripsList trips={trips} />
}
```

**Why This is Better:**
- Eliminates extra HTTP round trip (client → API route → database)
- Keeps database credentials secure on server
- Reduces client-side JavaScript
- Pre-renders HTML on server for better performance

#### Parallel Data Fetching

```typescript
// Fetch multiple data sources in parallel
export default async function Dashboard() {
  const [trips, profile, stats] = await Promise.all([
    fetchTrips(),
    fetchProfile(),
    fetchStats()
  ])

  return <Dashboard trips={trips} profile={profile} stats={stats} />
}
```

### 2.4 Authentication with Server Components

```typescript
// app/dashboard/page.tsx
import { cookies } from 'next/headers'
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'

export default async function Dashboard() {
  const supabase = createServerComponentClient({ cookies })

  // Secure server-side authentication check
  const { data: { user }, error } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return <DashboardContent user={user} />
}
```

### 2.5 Progressive Enhancement with Streaming

```typescript
// app/trips/[id]/page.tsx
import { Suspense } from 'react'

export default function TripPage({ params }) {
  return (
    <div>
      <TripHeader id={params.id} />

      {/* Show loading UI while fetching report */}
      <Suspense fallback={<ReportSkeleton />}>
        <TripReport id={params.id} />
      </Suspense>
    </div>
  )
}
```

**Benefits:**
- Prevents entire route from blocking during data fetching
- Shows UI progressively as data loads
- Improves perceived performance

### 2.6 Caching Strategy

```typescript
// Dynamic route - never cache
export const dynamic = 'force-dynamic'
export const revalidate = 0

// Or fetch with no-store
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store'  // Similar to getServerSideProps
})
```

### 2.7 Sources

- [Next.js App Router Migration Guide](https://nextjs.org/docs/app/guides/migrating/app-router-migration)
- [Next.js Server Components](https://nextjs.org/docs/app/getting-started/fetching-data)
- [Next.js Authentication Guide](https://nextjs.org/docs/app/guides/authentication)

---

## 3. FastAPI Backend Architecture

### 3.1 Project Structure (Netflix Dispatch Pattern)

Organize by **domain** rather than file type:

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── core/
│   │   ├── config.py          # Settings & environment
│   │   ├── security.py        # Auth utilities
│   │   └── exceptions.py      # Custom exceptions
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py
│   │   ├── user.py
│   │   └── trip.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py
│   │   └── trip.py
│   ├── api/                   # API routes by domain
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── dependencies.py
│   │   │   └── service.py
│   │   ├── trips/
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   ├── dependencies.py
│   │   │   └── service.py
│   │   └── agents/
│   │       ├── router.py
│   │       └── service.py
│   ├── agents/                # Agent implementations
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   └── visa.py
│   ├── tasks/                 # Celery tasks
│   │   ├── agent_tasks.py
│   │   └── cleanup_tasks.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_trips.py
└── requirements.txt
```

### 3.2 Async Patterns Best Practices

**When to Use Async:**
- I/O-bound operations (database, API calls, file operations)
- Long-running connections (SSE, WebSockets)
- High-concurrency workloads

**When NOT to Use Async:**
- CPU-bound operations (sync is faster due to threadpool)
- Simple CRUD operations with low traffic

#### Async Route Example

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.post("/trips")
async def create_trip(
    trip: TripCreate,
    db: AsyncSession = Depends(get_db)
):
    # ✅ Async database call
    result = await db.execute(
        select(Trip).where(Trip.user_id == user_id)
    )
    trips = result.scalars().all()
    return trips
```

**Critical**: Avoid blocking calls in async routes

```python
# ❌ BAD - Blocks event loop
@app.get("/data")
async def bad_route():
    result = requests.get("https://api.example.com")  # Blocking!
    return result.json()

# ✅ GOOD - Non-blocking
@app.get("/data")
async def good_route():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
    return response.json()
```

### 3.3 Dependency Injection Pattern

```python
# app/api/trips/dependencies.py
from fastapi import Depends, HTTPException
from supabase import create_client

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    supabase = Depends(get_supabase_client)
):
    user = await supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Usage in router
@router.post("/trips")
async def create_trip(
    trip: TripCreate,
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically injected
    return await trips_service.create(trip, current_user.id)
```

### 3.4 Environment-Based Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # Redis
    REDIS_URL: str

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # External APIs
    WEATHER_API_KEY: str
    CURRENCY_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 3.5 Connection Pooling

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,           # Connection pool size
    max_overflow=0,         # No overflow connections
    pool_pre_ping=True,     # Verify connections before use
    echo=False
)
```

### 3.6 Sources

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Async APIs with FastAPI: Patterns, Pitfalls & Best Practices](https://shiladityamajumder.medium.com/async-apis-with-fastapi-patterns-pitfalls-best-practices-2d72b2b66f25)
- [How to Structure a Scalable FastAPI Project](https://fastlaunchapi.dev/blog/how-to-structure-fastapi)
- [Mastering FastAPI in 2025](https://mind-to-machine.medium.com/mastering-fastapi-in-2025-build-scalable-async-apis-with-testing-monitoring-deployment-best-61dd5927dd96)

---

## 4. Redis + Celery Async Processing

### 4.1 Architecture Overview

```
FastAPI App → Redis (Message Broker) → Celery Worker(s) → Redis (Result Backend)
     ↓                                         ↓
 Returns Task ID                        Executes Task
     ↓                                         ↓
 Client polls status                    Stores Result
```

### 4.2 Celery Configuration

```python
# app/core/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tip_workers",
    broker=settings.CELERY_BROKER_URL,        # Redis URL
    backend=settings.CELERY_RESULT_BACKEND    # Redis URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    result_expires=3600,       # Results expire after 1 hour
)
```

### 4.3 Task Definition

```python
# app/tasks/agent_tasks.py
from app.core.celery_app import celery_app
from app.agents.orchestrator import OrchestratorAgent

@celery_app.task(bind=True, name="run_agent_pipeline")
def run_agent_pipeline(self, trip_id: str):
    """
    Execute full agent pipeline for trip.

    Args:
        self: Task instance (for retries)
        trip_id: UUID of trip
    """
    try:
        orchestrator = OrchestratorAgent()
        result = orchestrator.execute(trip_id)
        return {
            "status": "completed",
            "trip_id": trip_id,
            "result": result
        }
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60, max_retries=3)
```

### 4.4 Triggering Tasks from FastAPI

```python
# app/api/trips/router.py
from fastapi import APIRouter
from app.tasks.agent_tasks import run_agent_pipeline

router = APIRouter()

@router.post("/trips/{trip_id}/generate")
async def generate_report(trip_id: str):
    # Queue task and return task ID immediately
    task = run_agent_pipeline.delay(trip_id)

    return {
        "task_id": task.id,
        "status": "queued",
        "status_url": f"/tasks/{task.id}"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    from app.core.celery_app import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {"state": task.state, "status": "Task is queued"}
    elif task.state == 'STARTED':
        response = {"state": task.state, "status": "Task is running"}
    elif task.state == 'SUCCESS':
        response = {"state": task.state, "result": task.result}
    elif task.state == 'FAILURE':
        response = {"state": task.state, "error": str(task.info)}
    else:
        response = {"state": task.state}

    return response
```

### 4.5 Worker Pool Configuration

**For CPU-bound tasks:**
```bash
celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

**For I/O-bound tasks (high concurrency):**
```bash
celery -A app.core.celery_app worker --loglevel=info -P gevent --concurrency=100
```

### 4.6 Monitoring with Flower

```bash
# Start Flower monitoring dashboard
celery -A app.core.celery_app flower --port=5555
```

Access at: `http://localhost:5555`

### 4.7 Best Practices

1. **Task Idempotency**: Tasks should produce the same result when run multiple times
2. **Small Tasks**: Keep tasks focused - one responsibility per task
3. **Timeouts**: Always set task time limits to prevent zombie tasks
4. **Retries**: Use exponential backoff for retries
5. **Result Expiration**: Set `result_expires` to prevent Redis bloat
6. **Connection Pooling**: Use connection pooling for Redis

### 4.8 Sources

- [The Definitive Guide to Celery and FastAPI](https://testdriven.io/courses/fastapi-celery/getting-started/)
- [Maximizing FastAPI App Performance with Celery and Redis](https://medium.com/@2ashariful/maximizing-fastapi-app-performance-a-guide-to-boosting-with-celery-and-redis-ddc91c087e4f)
- [Asynchronous Task Processing with Celery and FastAPI](https://medium.com/@abd.hendi.174/asynchronous-task-processing-with-celery-and-fastapi-part-1-c015d1d47d2a)

---

## 5. Playwright Scraping Framework

### 5.1 Overview

Playwright is Microsoft's browser automation framework supporting Chromium, Firefox, and WebKit with full JavaScript rendering capabilities.

### 5.2 Architecture Advantages

**Dual API Support:**
- Synchronous API for simple scrapers
- Asynchronous API for scalable, high-concurrency scrapers

**Multi-Browser Support:**
- Chromium, Firefox, WebKit
- Test across different browsers with single codebase

**JavaScript Rendering:**
- Controls real browsers that execute JavaScript
- Handles modern dynamic websites (SPAs, React, Vue, etc.)

### 5.3 Basic Scraper Structure

```python
# app/scrapers/base_scraper.py
from playwright.async_api import async_playwright, Browser, Page
from abc import ABC, abstractmethod
import asyncio

class BaseScraper(ABC):
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Browser = None
        self.page: Page = None

    async def __aenter__(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """Implement scraping logic in subclass"""
        pass

    async def wait_for_selector(self, selector: str, timeout: int = 10000):
        """Wait for element with timeout"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False
```

### 5.4 Embassy Visa Scraper Example

```python
# app/scrapers/embassy_scraper.py
from app.scrapers.base_scraper import BaseScraper
from typing import Dict, Optional
import asyncio

class EmbassyScraper(BaseScraper):
    async def scrape(self, url: str) -> Dict:
        """
        Scrape visa requirements from embassy website.

        Args:
            url: Embassy visa page URL

        Returns:
            Dictionary with visa requirements data
        """
        try:
            # Navigate to page
            await self.page.goto(url, wait_until='networkidle')

            # Wait for main content
            await self.wait_for_selector('main', timeout=10000)

            # Extract visa requirements
            title = await self.page.title()

            # Extract text content
            content = await self.page.inner_text('body')

            # Look for key visa information
            visa_info = {
                "url": url,
                "title": title,
                "content": content[:5000],  # First 5000 chars
                "last_scraped": datetime.utcnow().isoformat()
            }

            return visa_info

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }

# Usage
async def scrape_embassy(url: str):
    async with EmbassyScraper(headless=True) as scraper:
        result = await scraper.scrape(url)
        return result
```

### 5.5 Rate Limiting & Retry Logic

```python
# app/scrapers/utils.py
import asyncio
from functools import wraps

def rate_limit(calls: int, period: int):
    """
    Rate limiting decorator.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds
    """
    semaphore = asyncio.Semaphore(calls)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                result = await func(*args, **kwargs)
                await asyncio.sleep(period / calls)
                return result
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: int = 5):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator

# Usage
@rate_limit(calls=10, period=60)  # 10 calls per minute
@retry(max_attempts=3, delay=5)
async def scrape_with_limits(url: str):
    async with EmbassyScraper() as scraper:
        return await scraper.scrape(url)
```

### 5.6 Integration with Scrapy (Optional)

For large-scale scraping, integrate Playwright with Scrapy:

```python
# Install: pip install scrapy-playwright

# settings.py
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
```

### 5.7 Sources

- [Web Scraping with Playwright and Python](https://scrapfly.io/blog/posts/web-scraping-with-playwright-and-python)
- [Playwright Web Scraping Tutorial for 2025](https://oxylabs.io/blog/playwright-web-scraping)
- [Scalable Web Scraping with Playwright and Browserless (2025 Guide)](https://www.browserless.io/blog/scraping-with-playwright-a-developer-s-guide-to-scalable-undetectable-data-extraction)
- [Playwright for Python Web Scraping Tutorial](https://www.scrapingbee.com/blog/playwright-for-python-web-scraping/)

---

## 6. Docker Compose Local Development

### 6.1 Complete docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Redis - Message broker and result backend
  redis:
    image: redis:7-alpine
    container_name: tip_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tip_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      redis:
        condition: service_healthy
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tip_celery_worker
    command: celery -A app.core.celery_app worker --loglevel=info -P gevent --concurrency=10
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      redis:
        condition: service_healthy
      backend:
        condition: service_started
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  # Flower - Celery Monitoring
  flower:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tip_flower
    command: celery -A app.core.celery_app flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - celery_worker
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: tip_frontend
    command: npm run dev
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000

volumes:
  redis_data:
```

### 6.2 Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.3 Frontend Dockerfile (Development)

```dockerfile
# frontend/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]
```

### 6.4 Usage Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up backend

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build

# Access running container
docker-compose exec backend bash
```

### 6.5 Sources

- [Dockerizing Celery and FastAPI](https://testdriven.io/courses/fastapi-celery/docker/)
- [GitHub: fastapi-nextjs Full Stack Integration](https://github.com/Nneji123/fastapi-nextjs)
- [Asynchronous Tasks with FastAPI and Celery](https://testdriven.io/blog/fastapi-and-celery/)

---

## 7. GitHub Actions CI/CD

### 7.1 Backend CI/CD Workflow

```yaml
# .github/workflows/backend-ci.yml
name: Backend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      working-directory: ./backend
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx

    - name: Lint with flake8
      working-directory: ./backend
      run: |
        pip install flake8
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --max-complexity=10 --max-line-length=127 --statistics

    - name: Run tests
      working-directory: ./backend
      env:
        REDIS_URL: redis://localhost:6379/0
        CELERY_BROKER_URL: redis://localhost:6379/0
      run: |
        pytest tests/ -v --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/tip-backend:latest
```

### 7.2 Frontend CI/CD Workflow

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Lint
      working-directory: ./frontend
      run: npm run lint

    - name: Type check
      working-directory: ./frontend
      run: npm run type-check

    - name: Build
      working-directory: ./frontend
      env:
        NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
        NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
      run: npm run build

    - name: Run tests
      working-directory: ./frontend
      run: npm test

  deploy-vercel:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        working-directory: ./frontend
```

### 7.3 Testing Best Practices

**Backend Testing (pytest + httpx):**

```python
# backend/tests/test_trips.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_trip():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/trips",
            json={
                "destination_country": "France",
                "cities": ["Paris", "Lyon"],
                "start_date": "2025-06-01",
                "end_date": "2025-06-10",
                "budget_amount": 3000.00,
                "nationality": "US"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["destination_country"] == "France"
```

**Frontend Testing (Jest + React Testing Library):**

```typescript
// frontend/tests/TripForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import TripForm from '@/components/TripForm'

describe('TripForm', () => {
  it('validates required fields', async () => {
    render(<TripForm />)

    const submitButton = screen.getByRole('button', { name: /create trip/i })
    fireEvent.click(submitButton)

    expect(await screen.findByText(/destination is required/i)).toBeInTheDocument()
  })
})
```

### 7.4 Sources

- [Enhancing GitHub Actions CI for FastAPI](https://pyimagesearch.com/2024/11/04/enhancing-github-actions-ci-for-fastapi-build-test-and-publish/)
- [Building a CI/CD Pipeline for Python with FastAPI, GitHub Actions, and Vercel](https://medium.com/@raeshmakr/building-a-ci-cd-pipeline-for-python-with-fastapi-github-actions-and-vercel-80182bba86f5)
- [End-to-end application development with FastAPI and Vercel Next.js](https://medium.com/@marko.briesemann/end-to-end-application-development-with-fastapi-and-vercel-next-js-d26c95147e05)

---

## 8. Implementation Checklist

### Phase 1 Feature Completion

- [ ] **P1-F1**: Set up Supabase project
  - [ ] Create Supabase project at supabase.com
  - [ ] Get API URL and anon key
  - [ ] Get service role key (for backend)

- [ ] **P1-F2**: Configure Supabase Auth
  - [ ] Enable email/password authentication
  - [ ] Configure Google OAuth provider
  - [ ] Set redirect URLs

- [ ] **P1-F3**: Create database tables
  - [ ] Execute SQL from data_models.md
  - [ ] Create all 6 tables (Users, Trips, AgentJobs, etc.)
  - [ ] Verify table creation

- [ ] **P1-F4**: Implement Row-Level Security
  - [ ] Enable RLS on all tables
  - [ ] Create policies for each table
  - [ ] Test RLS with different user roles

- [ ] **P1-F5**: Set up Next.js frontend
  - [ ] Initialize Next.js 14+ with TypeScript
  - [ ] Install Tailwind CSS and shadcn/ui
  - [ ] Configure Supabase client
  - [ ] Create basic layout and navigation

- [ ] **P1-F6**: Set up FastAPI backend
  - [ ] Create project structure (Netflix pattern)
  - [ ] Configure environment variables
  - [ ] Set up Supabase connection
  - [ ] Create basic health check endpoint

- [ ] **P1-F7**: Configure Redis instance
  - [ ] Sign up for Upstash (or use Docker locally)
  - [ ] Get Redis connection URL
  - [ ] Test Redis connection

- [ ] **P1-F8**: Set up Celery workers
  - [ ] Configure Celery with Redis broker
  - [ ] Create sample task
  - [ ] Test task execution
  - [ ] Set up Flower monitoring

- [ ] **P1-F9**: Create Docker Compose setup
  - [ ] Create docker-compose.yml
  - [ ] Create Dockerfiles for backend and frontend
  - [ ] Test local Docker environment

- [ ] **P1-F10**: Implement basic auth flow (backend)
  - [ ] Create auth router
  - [ ] Implement token validation
  - [ ] Create authentication dependencies

- [ ] **P1-F11**: Create user registration/login UI
  - [ ] Build registration form
  - [ ] Build login form
  - [ ] Add OAuth login buttons
  - [ ] Test complete auth flow

- [ ] **P1-F12**: Set up CI/CD pipeline
  - [ ] Create GitHub Actions workflows
  - [ ] Configure secrets
  - [ ] Test automated testing

- [ ] **P1-F13**: Build Playwright scraper framework
  - [ ] Create BaseScraper class
  - [ ] Implement rate limiting
  - [ ] Add retry logic
  - [ ] Create embassy scraper example

### Verification Steps

After completing Phase 1:

1. ✅ User can register and login via email/password
2. ✅ User can login via Google OAuth
3. ✅ Database tables created with RLS enabled
4. ✅ FastAPI backend responds to health check
5. ✅ Celery worker can execute sample task
6. ✅ Docker Compose runs all services locally
7. ✅ CI/CD pipeline runs tests automatically
8. ✅ Playwright scraper can scrape sample website

---

## Conclusion

Phase 1 establishes the complete technical foundation for TIP. Upon completion, the project will have:

- ✅ Secure authentication and database with Supabase
- ✅ Modern frontend with Next.js 14+ App Router
- ✅ Scalable async backend with FastAPI
- ✅ Background task processing with Celery/Redis
- ✅ Custom scraping framework with Playwright
- ✅ Containerized local development environment
- ✅ Automated testing and deployment pipelines

**Next Phase**: Phase 2 - Orchestrator Agent (8 features)

---

**Document Status**: Complete
**Research Sources**: 20+ official docs and 2025 guides cited
**Next Review**: After Phase 1 implementation
