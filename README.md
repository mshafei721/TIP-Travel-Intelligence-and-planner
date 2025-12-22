# TIP – Travel Intelligence & Planner

> **Decision-grade travel intelligence system** powered by AI agents

[![Status](https://img.shields.io/badge/status-Phase%200-yellow)](./feature_list.json)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## 🌍 Overview

TIP is an AI-powered travel intelligence platform that provides travelers with **accurate, legally compliant, and actionable** travel reports. Unlike booking platforms, TIP focuses on delivering **world-class intelligence** covering:

- ✅ Visa requirements & entry conditions
- 🌤️ Weather forecasts & climate insights
- 💰 Currency conversion & budget analysis
- 🏛️ Cultural etiquette & legal warnings
- 🍽️ Culinary intelligence & restaurants
- 🎭 Top attractions & experiences
- 📅 Smart itinerary generation
- ✈️ Flight price intelligence

---

## 🎯 Mission

Provide travelers with a **single, accurate, legally compliant, and actionable** travel intelligence report tailored to their nationality, residency, budget, and travel dates.

### Non-Goals
- ❌ NOT a booking platform
- ❌ NOT a social travel app
- ❌ NOT a content or inspiration blog

TIP is a **decision-grade travel intelligence system**.

---

## 🏗️ Architecture

### Multi-Agent System

TIP uses **10 specialized AI agents** orchestrated by CrewAI:

1. **Orchestrator Agent** - Coordinates all agents, validates outputs
2. **Visa & Entry Agent** - Determines visa requirements (CRITICAL)
3. **Country Intelligence Agent** - Politics, demographics, safety
4. **Weather Agent** - Forecasts, historical data, warnings
5. **Currency & Budget Agent** - Exchange rates, cost estimates
6. **Culture & Law Agent** - Etiquette, religious norms, unusual laws
7. **Food Agent** - National dishes, restaurants, safety
8. **Attractions Agent** - Top sites, costs, durations
9. **Itinerary Agent** - Day-by-day schedules, weather-aware
10. **Flight Agent** - Real-time prices, booking links

### Tech Stack

**Frontend**: Next.js 14+ (TypeScript) + Tailwind CSS + shadcn/ui + Mapbox
**Backend**: FastAPI (Python) + CrewAI + Celery + Redis
**Database**: Supabase (Postgres + Auth)
**AI**: OpenAI GPT-4 + Anthropic Claude 3.5
**Deployment**: Vercel (frontend) + Render/Railway (backend)

---

## 📋 Project Status

**Current Phase**: Phase 0 - Research & Planning (53% Complete)

Total: **134 features** across **15 phases**

| Phase | Name | Status |
|-------|------|--------|
| 0 | Research & Planning | 🟡 53% |
| 1 | Foundation | ⚪ Not Started |
| 2 | Orchestrator Agent | ⚪ Not Started |
| 3-11 | Individual Agents (9) | ⚪ Not Started |
| 12 | Trip Creation & Input | ⚪ Not Started |
| 13 | Report Generation | ⚪ Not Started |
| 14 | Data Lifecycle | ⚪ Not Started |
| 15 | Polish & Production | ⚪ Not Started |

See [feature_list.json](./feature_list.json) for complete feature breakdown.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.11+ ([Download](https://www.python.org/))
- Git ([Download](https://git-scm.com/))
- Docker (optional, for Redis) ([Download](https://www.docker.com/))

### Installation

#### Windows (PowerShell)

```powershell
# Clone the repository
git clone <repository-url>
cd TIP-Travel-Intelligence-and-planner

# Run initialization script
.\init.ps1
```

#### Linux/macOS

```bash
# Clone the repository
git clone <repository-url>
cd TIP-Travel-Intelligence-and-planner

# TODO: Create init.sh for Unix systems
```

### Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys to `.env`:
   ```env
   # Database & Auth
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_key

   # External APIs
   WEATHER_API_KEY=your_key
   CURRENCY_API_KEY=your_key
   FLIGHT_API_KEY=your_key
   MAPBOX_API_KEY=your_key

   # LLM APIs
   OPENAI_API_KEY=your_key
   ```

3. Start development servers:
   ```powershell
   # Frontend (in one terminal)
   cd frontend
   npm run dev

   # Backend (in another terminal)
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.main:app --reload

   # Celery worker (in third terminal)
   cd backend
   .\venv\Scripts\Activate.ps1
   celery -A app.tasks.celery worker --loglevel=info
   ```

4. Open browser: `http://localhost:3000`

---

## 📚 Documentation

- [PRD.md](./PRD.md) - Product Requirements Document
- [docs/comprehensive_plan.md](./docs/comprehensive_plan.md) - Complete architectural plan
- [docs/data_models.md](./docs/data_models.md) - Database schema
- [docs/services_config.md](./docs/services_config.md) - External services configuration
- [feature_list.json](./feature_list.json) - Complete feature breakdown
- [claude-progress.txt](./claude-progress.txt) - Development progress log

---

## 🛠️ Development Workflow

### Agent-by-Agent Development

1. **Design**: Define inputs, outputs, data sources
2. **Implement**: Write agent class, integrate APIs
3. **Test**: Unit → Integration → E2E
4. **Review**: Code review before merge
5. **Deploy**: Merge to main, test on staging

### Git Workflow

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/<agent-name>`: Per-agent branches

---

## 🔒 Security & Privacy

- **Data Encryption**: All data encrypted at rest
- **Auto-Deletion**: Trip data auto-deleted 7 days after trip ends
- **GDPR Compliant**: Minimal data collection, user data export
- **Row-Level Security**: Database-level user isolation
- **Official Sources**: Visa data from government sources only

---

## 📊 Success Metrics

- Report generation success rate > 90%
- Visa data completeness > 95%
- Time to first result < 15 seconds
- PDF export success rate > 95%
- User satisfaction > 4.5/5

---

## 🤝 Contributing

This is currently a private project. Contribution guidelines TBD.

---

## 📄 License

[MIT License](./LICENSE) - TBD

---

## 🙏 Acknowledgments

**Research Sources**:
- [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) - CrewAI patterns
- [scraping-apis-for-devs](https://github.com/cporter202/scraping-apis-for-devs) - Scraping patterns

**APIs & Services**:
- Visual Crossing (Weather)
- Fixer.io (Currency)
- Sherpa API (Visa)
- Mapbox (Maps)
- Supabase (Database & Auth)

---

## 📞 Contact

For questions or feedback, please contact [TBD]

---

**Built with ❤️ using AI-powered multi-agent architecture**
