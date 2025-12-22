# External Services Configuration

## Overview
This document tracks all external services, APIs, and third-party integrations for TIP.

## Service Status Legend
- ✅ Configured & Ready
- ⏳ Decision Made, Pending Configuration
- 🔍 Researching Options
- ❌ Not Yet Started

---

## Critical Services (Must Configure Before Phase 1)

### 1. Supabase (Database & Auth)
- **Status**: ⏳ Pending Configuration
- **Purpose**: PostgreSQL database, authentication, Row-Level Security
- **Plan**: Free tier → Pro as needed
- **Configuration Required**:
  - [ ] Create Supabase project
  - [ ] Enable email/password auth
  - [ ] Enable Google OAuth
  - [ ] Get API keys (anon, service)
  - [ ] Configure redirect URLs
- **Env Vars**: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`
- **Documentation**: https://supabase.com/docs

### 2. Redis (Caching & Celery Backend)
- **Status**: ⏳ Decision Made
- **Purpose**: Caching, Celery job queue backend
- **Options**:
  - **Local Dev**: Docker (redis:alpine) - ✅ Included in init.ps1
  - **Production**: Upstash (serverless) or Redis Cloud or AWS ElastiCache
- **Decision**: Upstash for MVP (generous free tier, serverless)
- **Configuration Required**:
  - [ ] Sign up for Upstash
  - [ ] Create Redis database
  - [ ] Get connection URL
- **Env Vars**: `REDIS_URL`
- **Pricing**: Free tier: 10K commands/day
- **Documentation**: https://upstash.com/docs/redis

### 3. Firecrawl (Web Scraping)
- **Status**: ⏳ Decision Made
- **Purpose**: Structured web scraping for visa info, cultural data, news
- **Plan**: Starter plan ($49/mo) → Growth as needed
- **Rate Limits**: Starter: 500 credits/mo
- **Configuration Required**:
  - [ ] Sign up for Firecrawl
  - [ ] Get API key
  - [ ] Test scraping endpoints
- **Env Vars**: `FIRECRAWL_API_KEY`
- **Alternatives**: Apify, Scrapy Cloud, Crawlbase
- **Documentation**: https://docs.firecrawl.dev

---

## Agent-Specific Services

### 4. Weather API - Visual Crossing
- **Status**: ⏳ Decision Made
- **Purpose**: Weather forecasts, historical data, climate warnings
- **Plan**: Free tier (1,000 records/day) → Paid as needed
- **Rate Limits**: Free: 1K records/day, Paid: $35/mo for more
- **Features**: 15-day forecast, 50-year history, commercial use OK
- **Configuration Required**:
  - [ ] Sign up for Visual Crossing
  - [ ] Get API key
  - [ ] Test forecast endpoint
- **Env Vars**: `WEATHER_API_KEY`
- **Alternatives**: OpenWeatherMap, WeatherAPI.com
- **Documentation**: https://www.visualcrossing.com/resources/documentation/weather-api/
- **API Endpoint**: `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline`
- **Sources**:
  - [Best Weather API for 2025](https://www.visualcrossing.com/resources/blog/best-weather-api-for-2025/)
  - [The Best Weather APIs for 2025](https://www.tomorrow.io/blog/top-weather-apis/)

### 5. Currency API - Fixer.io
- **Status**: ⏳ Decision Made
- **Purpose**: Real-time exchange rates, currency conversion
- **Plan**: Free tier (100 requests/mo) → Basic ($10/mo, 1K requests)
- **Rate Limits**: Free: 100/mo, Basic: 1K/mo
- **Features**: 170+ currencies, 60-second updates, historical data
- **Configuration Required**:
  - [ ] Sign up for Fixer.io
  - [ ] Get API key
  - [ ] Test latest rates endpoint
- **Env Vars**: `CURRENCY_API_KEY`
- **Alternatives**: ExchangeRate-API (better free tier: 1,500/mo), Open Exchange Rates
- **Documentation**: https://fixer.io/documentation
- **API Endpoint**: `https://api.fixer.io/latest`
- **Sources**:
  - [Free Currency Converter API: 7 Best Conversion APIs of 2025](https://blog.apilayer.com/7-best-free-currency-converter-apis-in-2025/)

### 6. Visa Data - Sherpa API
- **Status**: ⏳ Decision Made
- **Purpose**: Visa requirements, entry rules, passport validity
- **Plan**: Contact for pricing (enterprise)
- **Features**: 2,000+ official sources, IATA compliance, government-backed
- **Configuration Required**:
  - [ ] Contact Sherpa for API access
  - [ ] Get API key
  - [ ] Test visa check endpoint
- **Env Vars**: `VISA_API_KEY`
- **Alternatives**: IATA Travel Centre (1,000+ sources), Manual scraping (high risk)
- **Documentation**: https://docs.joinsherpa.io/
- **API Endpoint**: `https://api.joinsherpa.com/v2/`
- **Sources**:
  - [Sherpa - Visa and Travel Rules API](http://docs.joinsherpa.io/)
  - [IATA - Travel Centre](https://www.iata.org/en/services/compliance/timatic/travel-documentation/)
- **Critical Note**: For MVP, may use IATA Travel Centre or build custom scraper with Firecrawl + official embassy sites

### 7. Flight Price API - Skyscanner (MVP) / Amadeus (Production)
- **Status**: ⏳ Decision Made
- **Purpose**: Real-time flight prices, availability, booking links
- **Plan**:
  - **MVP**: Skyscanner API (free tier for testing)
  - **Production**: Amadeus Self-Service (free tier → paid)
- **Rate Limits**: Varies by plan
- **Configuration Required**:
  - [ ] Sign up for Skyscanner API
  - [ ] Get API key
  - [ ] Test flight search endpoint
  - [ ] (Later) Migrate to Amadeus if needed
- **Env Vars**: `FLIGHT_API_KEY`
- **Alternatives**: Serpapi Google Flights ($50/mo), Kiwi Tequila API
- **Documentation**: https://developers.skyscanner.net/docs/
- **API Endpoint**: `https://partners.api.skyscanner.net/apiservices/`
- **Sources**:
  - [Top 5 Flights APIs for Travel Apps](https://www.codebridge.tech/articles/top-5-flights-apis-for-travel-apps)
  - [Connect to Amadeus travel APIs](https://developers.amadeus.com/)

### 8. Map Provider - Mapbox
- **Status**: ⏳ Decision Made
- **Purpose**: Interactive maps, POI data, navigation links, geocoding
- **Plan**: Free tier (50K map loads/mo) → Pay-as-you-go
- **Rate Limits**: Free: 50K web loads/mo, 25K mobile users/mo
- **Features**: Offline maps, custom styling, 3D views, geocoding API
- **Configuration Required**:
  - [ ] Sign up for Mapbox
  - [ ] Get API access token
  - [ ] Test geocoding and map embed
- **Env Vars**: `MAPBOX_API_KEY`
- **Alternatives**: Google Maps (more POI data, but expensive)
- **Documentation**: https://docs.mapbox.com/
- **API Endpoint**: `https://api.mapbox.com/`
- **Sources**:
  - [Mapbox vs. Google Maps API: 2026 comparison](https://radar.com/blog/mapbox-vs-google-maps-api)
  - [Mapbox API vs Google Maps API for app development in 2025](https://volpis.com/blog/mapbox-vs-google-maps-api-for-app-development/)

---

## LLM Services (for Agents)

### 9. OpenAI API (Primary LLM)
- **Status**: ⏳ Pending Configuration
- **Purpose**: Power CrewAI agents with GPT-4
- **Plan**: Pay-as-you-go
- **Model**: GPT-4-turbo or GPT-4o (latest)
- **Configuration Required**:
  - [ ] Get OpenAI API key
  - [ ] Set up billing
  - [ ] Configure model in CrewAI
- **Env Vars**: `OPENAI_API_KEY`
- **Documentation**: https://platform.openai.com/docs

### 10. Anthropic API (Backup LLM)
- **Status**: ⏳ Pending Configuration
- **Purpose**: Fallback for OpenAI, potentially better for reasoning tasks
- **Plan**: Pay-as-you-go
- **Model**: Claude 3.5 Sonnet or Claude Opus
- **Configuration Required**:
  - [ ] Get Anthropic API key
  - [ ] Configure as fallback in CrewAI
- **Env Vars**: `ANTHROPIC_API_KEY`
- **Documentation**: https://docs.anthropic.com/

---

## Deployment & Infrastructure

### 11. Vercel (Frontend Hosting)
- **Status**: ❌ Not Yet Started
- **Purpose**: Host Next.js frontend
- **Plan**: Free tier → Pro as needed
- **Features**: Auto-deployments, edge functions, analytics
- **Configuration Required**:
  - [ ] Connect GitHub repo to Vercel
  - [ ] Configure environment variables
  - [ ] Set up custom domain
- **Documentation**: https://vercel.com/docs

### 12. Railway / Render (Backend Hosting - MVP)
- **Status**: 🔍 Researching
- **Purpose**: Host FastAPI backend, Celery workers
- **Options**:
  - **Railway**: $5/mo, easy setup, good for MVP
  - **Render**: Free tier available, good for MVP
- **Decision**: Start with Render (free tier), migrate to Railway or AWS as needed
- **Configuration Required**:
  - [ ] Deploy FastAPI to Render
  - [ ] Deploy Celery worker to Render
  - [ ] Configure environment variables
- **Documentation**: https://render.com/docs

### 13. AWS (Production - Future)
- **Status**: 🔍 Future Consideration
- **Purpose**: Production-grade hosting with full control
- **Services**: EC2 (FastAPI), ECS/Fargate (containers), ElastiCache (Redis), S3 (PDFs)
- **Plan**: Migrate from Railway/Render once MVP is validated
- **Configuration Required**: TBD

---

## Monitoring & Analytics

### 14. Sentry (Error Tracking)
- **Status**: ❌ Not Yet Started
- **Purpose**: Error tracking, performance monitoring
- **Plan**: Free tier (5K errors/mo) → Team plan
- **Configuration Required**:
  - [ ] Create Sentry project
  - [ ] Install Sentry SDK (frontend & backend)
  - [ ] Configure error reporting
- **Env Vars**: `SENTRY_DSN`
- **Documentation**: https://docs.sentry.io/

---

## Service Configuration Checklist

### Phase 0 (Planning) - Before Coding
- [x] Research and select all services
- [x] Document decisions and rationale
- [ ] Review pricing and free tier limits

### Phase 1 (Foundation) - Before Development
- [ ] Supabase: Create project, configure auth
- [ ] Redis: Set up Upstash or local Docker
- [ ] OpenAI: Get API key, set up billing
- [ ] Create .env file with all keys

### Phase 3 (Visa Agent) - Before Building Agent
- [ ] Sherpa API: Get access OR
- [ ] Firecrawl: Configure for embassy scraping

### Phase 4-11 (Other Agents) - Before Building Each Agent
- [ ] Visual Crossing: Get API key (Weather Agent)
- [ ] Fixer.io: Get API key (Currency Agent)
- [ ] Mapbox: Get API key (Food, Attractions Agents)
- [ ] Skyscanner: Get API key (Flight Agent)

### Phase 13 (Report Generation) - Before PDF Export
- [ ] Mapbox: Ensure static map API configured

### Phase 15 (Production) - Before Launch
- [ ] Vercel: Deploy frontend
- [ ] Railway/Render: Deploy backend
- [ ] Sentry: Configure error tracking
- [ ] All API keys: Migrate to production keys

---

## Cost Estimates (Monthly)

### MVP Phase (Phases 1-14)
- Supabase: Free tier
- Redis (Upstash): Free tier
- Firecrawl: $49/mo
- Visual Crossing: Free tier (1K records/day)
- Fixer.io: $10/mo (Basic plan)
- Skyscanner: Free tier
- Mapbox: Free tier (50K loads/mo)
- OpenAI: ~$50/mo (estimated)
- Vercel: Free tier
- Render: Free tier
- **Total: ~$110/mo**

### Production Phase (Phase 15+)
- Supabase: Pro $25/mo
- Upstash: $10/mo
- Firecrawl: $99/mo (Growth)
- Visual Crossing: $35/mo
- Fixer.io: $40/mo (Professional)
- Amadeus: Custom pricing
- Mapbox: $50/mo (estimated)
- OpenAI: ~$200/mo (scaled usage)
- Vercel: $20/mo (Pro)
- Railway: $20/mo
- Sentry: $26/mo
- **Total: ~$525/mo**

---

## Notes
- All service selections are based on 2025 research
- Free tiers prioritized for MVP to minimize upfront costs
- Production migration plan ensures scalability
- Monitor API usage closely during MVP phase to avoid overages

Last Updated: 2025-12-22
