# TIP Developer Session Context

> **Use this file at the START of every session to establish context**

## Project Overview

**TIP - Travel Intelligence & Planner**
Multi-agent AI travel planning application that generates comprehensive travel intelligence reports.

## Tech Stack

| Layer | Technology | Status |
|-------|------------|--------|
| Frontend | Next.js 16 + Tailwind v4 + Radix UI | Vercel |
| Backend | FastAPI + Celery + Redis | Railway |
| Database | Supabase PostgreSQL + RLS | Configured |
| AI Agents | CrewAI + Anthropic Claude | Pending |
| Auth | Supabase Auth | Configured |

## Environment

- **OS**: Windows (PowerShell commands only)
- **User**: Non-technical (explain simply)
- **Token Budget**: Keep under 100K per session

## Completed Infrastructure

- [x] Docker Compose (local dev)
- [x] CI/CD Pipeline (GitHub Actions)
- [x] Railway deployment (Backend + Redis + Celery)
- [x] Vercel deployment (Frontend)
- [x] Supabase (9 tables with RLS)

## Increment Status (I1-I10)

| ID | Name | Frontend | Backend | Agents | Overall |
|----|------|----------|---------|--------|---------|
| I1 | Foundation | 100% | 75% | - | 85% |
| I2 | User Profile | 30% | 20% | - | 25% |
| I3 | Dashboard | 100% | 50% | - | 75% |
| I4 | Trip Wizard | 0% | 0% | - | 0% |
| I5 | AI Reports | 0% | 0% | 0% | 0% |
| I6 | Itinerary | 0% | 0% | - | 0% |
| I7 | Collaboration | 0% | 0% | - | 0% |
| I8 | Trip Updates | 0% | 0% | - | 0% |
| I9 | Templates | 0% | 0% | - | 0% |
| I10 | Analytics | 0% | 0% | - | 0% |

## Mandatory Rules (ALL Sessions)

### TDD Workflow
```
1. Write test FIRST → Run → Must FAIL (RED)
2. Write minimal code → Run → Must PASS (GREEN)
3. Refactor → Tests still pass
4. Commit with descriptive message
```

### Before ANY Code
- [ ] Read relevant documentation
- [ ] Check dependencies and affected files
- [ ] Define exact scope
- [ ] Use MCP tools for research

### Key Constraints
- PowerShell commands only (`ls`, not `dir /b`)
- Don't break existing working code
- Ask user when unsure (AskUserQuestion tool)
- Test after every file/batch
- Use /frontend-design skill for UI work

### Design System Compliance
- Colors: Blue (primary), Amber (secondary), Slate (neutral)
- Fonts: DM Sans (body), IBM Plex Mono (code)
- Dark mode on ALL components
- Mobile-first responsive design

## Key Documentation

```
docs/
├── INTEGRATED_PLAN.md       # Master plan (I1-I10)
├── visa-agent-roadmap.md    # First agent specs
└── services_config.md       # External APIs

product-plan/
├── design-system/           # Colors, fonts, tokens
├── instructions/incremental/ # Per-feature guides
└── sections/                # Component specs

feature_list.json            # Feature tracking
claude-progress.txt          # Session history
```

## Start Commands

```powershell
cd "D:\009_Projects_AI\Personal_Projects\TIP-Travel Intelligence-and-planner"

# Local development
.\docker.ps1 up              # Start all services
cd frontend && npm run dev   # Frontend dev server

# Testing
cd backend && python -m pytest
cd frontend && npm test
```

## Session Flow

1. Read this context file
2. Read specific prompt file (01-XX.md)
3. Read claude-progress.txt (latest session)
4. Ask user to confirm task
5. Implement with TDD
6. Update feature_list.json
7. Commit and push
