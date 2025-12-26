  📊 Current Stack Assessment

  Your Current Agents (from codebase):
  1. AttractionsAgent → OpenTripMap API (needs OPENTRIPMAP_API_KEY)
  2. WeatherAgent → WeatherAPI.com (needs WEATHERAPI_KEY)
  3. CurrencyAgent → Currency Exchange API
  4. VisaAgent → Planned: Sherpa API (very expensive)
  5. FoodAgent → CrewAI with knowledge bases
  6. CultureAgent → CrewAI with knowledge bases
  7. CountryAgent → Implemented

  Planned External Services (from services_config.md):
  - ❌ Visual Crossing (weather): $35/mo
  - ❌ Fixer.io (currency): $10/mo
  - ❌ Sherpa API (visa): Enterprise pricing (expensive)
  - ❌ Skyscanner API (flights): Varies
  - ❌ Mapbox (maps): $25-50/mo
  - ❌ Apify (scraping): $39/mo
  - ❌ Firecrawl (scraping): $49/mo
  - ✅ OpenAI/Anthropic (LLM): $50-200/mo

  Current Cost: ~$75/mo (MVP) → ~$541/mo (Production)

  ---
  💡 Free API Alternatives (Recommended)

  | Category        | Current/Planned          | FREE Alternative             | Free Tier                    |
  |-----------------|--------------------------|------------------------------|------------------------------|
  | Weather         | Visual Crossing ($35/mo) | Open-Meteo                   | Unlimited, no API key needed |
  |                 | WeatherAPI.com           | WeatherAPI.com (keep!)       | 1M calls/month               |
  |                 |                          | OpenWeatherMap               | 30K calls/month              |
  | Currency        | Fixer.io ($10/mo)        | ExchangeRate-API             | 1,500 calls/month            |
  |                 |                          | exchangeratesapi.io          | 100 calls/month              |
  |                 |                          | Open Exchange Rates          | 1,000 calls/month            |
  | Attractions/POI | OpenTripMap              | Overpass API (OpenStreetMap) | Unlimited, free              |
  |                 |                          | Openrouteservice             | Free OpenStreetMap-based     |
  |                 | Google Maps              | Geoapify                     | Credits-based, free tier     |
  | Flights         | Skyscanner (paid)        | Amadeus Self-Service         | Free tier for testing        |
  |                 |                          | SerpAPI Google Flights       | Limited free tier            |
  | Scraping        | Apify ($39/mo)           | Custom Playwright            | Free (self-hosted)           |
  |                 | Firecrawl ($49/mo)       | BeautifulSoup + httpx        | Free (Python)                |
  |                 |                          | Puppeteer                    | Free (Node.js)               |

  ---
  🔍 Insights from awesome-llm-apps Repository

  TripCraft AI Travel Planner (multi-agent team):

  Agent Team Structure (6 agents):
  1. Destination Explorer → Attractions research
  2. Hotel Search Agent → Accommodation
  3. Dining Agent → Restaurants
  4. Budget Agent → Cost optimization
  5. Flight Search Agent → Air travel
  6. Itinerary Specialist → Day-by-day scheduling

  Tools Used:
  - ✅ Exa (search) - Great for semantic search
  - ❌ Firecrawl (web scraping) - $49/mo, avoid
  - ❌ Google Flights, Kayak APIs
  - ✅ Gemini (LLM) - Alternative to Claude/GPT-4
  - ✅ Agno (agent coordination)
  - ✅ PostgreSQL + FastAPI (same as yours!)

  Key Takeaway: They use multi-agent orchestration (good pattern to follow) but rely on expensive scraping services (avoid).

  ---
  🛠️ Scrapers from scraping-apis-for-devs

  Unfortunately, this repo mostly lists Apify actors (paid services), not free scrapers:
  - AI Travel Agent (Apify) → Paid
  - Airbnb Parser Spider (Apify) → Paid
  - TripAdvisor Scraper (Apify) → Paid

  However, your services_config.md already has the right strategy:

  4-Layer Scraping Approach (keep this!):
  1. Layer 1: Custom Playwright Scrapers (FREE, self-hosted) ✅
  2. Layer 2: Apify Actors (fallback, $5/mo free tier)
  3. Layer 3: Firecrawl (critical backup only)
  4. Official APIs: Always try first

  Recommendation: Strengthen Layer 1 (custom scrapers) and use free APIs to reduce reliance on Layers 2-3.

  ---
  🎯 Recommended Changes

  Replace These Paid APIs:

  1. Weather Agent:
  # CURRENT: WeatherAPI.com (1M calls/month free) ✅ Keep this
  # ALTERNATIVE: Open-Meteo (unlimited, no key needed)
  # https://open-meteo.com/
  2. Currency Agent:
  # CURRENT: Fixer.io ($10/mo)
  # REPLACE WITH: ExchangeRate-API (1,500 calls/month free)
  # https://www.exchangerate-api.com/

  # Alternative: exchangeratesapi.io (100 calls/month)
  # https://exchangeratesapi.io/
  3. Attractions Agent:
  # CURRENT: OpenTripMap (limited free tier)
  # REPLACE WITH: Overpass API (OpenStreetMap)
  # https://wiki.openstreetmap.org/wiki/Overpass_API

  # Alternative: Openrouteservice POI API
  # https://openrouteservice.org/dev/#/api-docs/pois
  4. Flight Search (not yet implemented):
  # PLANNED: Skyscanner (paid)
  # USE: Amadeus Self-Service API (free tier)
  # https://developers.amadeus.com/self-service

  # Or: SerpAPI Google Flights (100 searches/month free)
  # https://serpapi.com/google-flights-api
  5. Scraping:
  # PLANNED: Apify ($39/mo) + Firecrawl ($49/mo)
  # USE: Custom Playwright + BeautifulSoup (FREE)
  # Only use Apify free tier ($5/mo credits) as fallback

  Keep These:

  - ✅ WeatherAPI.com (1M calls/month free - excellent)
  - ✅ Supabase (free tier sufficient for MVP)
  - ✅ Redis via Upstash (free tier)
  - ✅ OpenAI/Anthropic (essential for LLM)

  ---
  💰 Cost Comparison

  | Phase      | Current Plan | With Free Alternatives | Savings                 |
  |------------|--------------|------------------------|-------------------------|
  | MVP        | ~$75/mo      | ~$15/mo                | $60/mo (80% reduction)  |
  | Production | ~$541/mo     | ~$150/mo               | $391/mo (72% reduction) |

  Breakdown (Production):
  CURRENT:                    WITH FREE ALTERNATIVES:
  - Supabase: $25             - Supabase: $25
  - Redis: $10                - Redis: $10
  - Scraping: $65             - Scraping: $0 (self-hosted Playwright)
  - Weather: $35              - Weather: $0 (Open-Meteo/WeatherAPI free)
  - Currency: $40             - Currency: $0 (ExchangeRate-API free)
  - Flights: $50              - Flights: $0 (Amadeus free tier)
  - Maps: $50                 - Maps: $0 (OpenStreetMap/Overpass)
  - LLM: $200                 - LLM: $200
  - Vercel: $20               - Vercel: $20
  - Railway: $20              - Railway: $20
  - Sentry: $26               - Sentry: $0 (use free tier)
  -----------------           -----------------
  Total: $541/mo              Total: $275/mo → ~$150/mo optimized

  ---
  🚀 Implementation Priority

  Phase 1: Quick Wins (Do First):
  1. ✅ Keep WeatherAPI.com (already free, 1M calls/month)
  2. 🔄 Replace currency API → ExchangeRate-API (free)
  3. 🔄 Replace attractions → Overpass API (free, OpenStreetMap)

  Phase 2: Scraping Foundation:
  4. 🛠️ Build custom Playwright scrapers (embassy sites, government pages)
  5. 📝 Implement rate limiting and retry logic
  6. 🎯 Only use Apify free tier as fallback

  Phase 3: Advanced:
  7. 🔍 Add Amadeus API for flights (free tier)
  8. 🗺️ Use OpenStreetMap + Mapbox (free tier only)
  9. 📊 Monitor API usage to stay in free tiers

  ---
  🔧 Tools from awesome-llm-apps to Adopt

  Use These:
  - ✅ Exa (semantic search) - Better than Google Custom Search
  - ✅ Multi-agent team pattern - Destination Explorer, Hotel, Dining, Budget, Flight, Itinerary agents
  - ✅ Gemini (optional LLM alternative) - Cheaper than GPT-4

  Avoid These:
  - ❌ Firecrawl ($49/mo) - Use custom Playwright instead
  - ❌ Kayak API (paid) - Use Amadeus free tier

  ---
  📝 Action Items

  Immediate Changes (you can do now):

  1. Update services_config.md:
    - Mark ExchangeRate-API as primary currency provider
    - Mark Overpass API as primary POI provider
    - Mark Open-Meteo as weather alternative
    - Reduce Firecrawl to "emergency backup only"
  2. Update Agent Tools:
    - currency/tools.py → Add ExchangeRate-API client
    - attractions/tools.py → Add Overpass API client
    - weather/tools.py → Add Open-Meteo fallback
  3. Build Scraping Layer:
    - Create backend/app/scrapers/ directory
    - Implement Playwright base scraper class
    - Add rate limiting and proxy rotation

  Would you like me to:
  1. Implement the free API replacements for currency/attractions/weather agents?
  2. Build the custom Playwright scraper framework?
  3. Update the services_config.md with these free alternatives?
  4. Create a migration plan from paid → free services?

  ---
  Sources:

  - https://www.visualcrossing.com/resources/blog/best-weather-api-for-2025/
  - https://blog.apilayer.com/7-best-free-currency-converter-apis-in-2025/
  - https://traveltime.com/blog/google-places-api-alternatives-points-of-interest-data
  - https://www.flightapi.io/blog/travel-apis/
  - https://www.weatherapi.com/pricing.aspx
  - https://alternativeto.net/software/exchangerate-api/
  - https://www.safegraph.com/guides/openstreetmap-api-alternative