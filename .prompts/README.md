# TIP Developer Prompts

This folder contains structured prompts for Claude Code developer sessions.

## How to Use

1. **Start every session** by reading `00-session-context.md`
2. **Choose the relevant increment** prompt (01-10)
3. **Follow the TDD workflow** in each prompt
4. **Update feature_list.json** after completing tasks
5. **Commit and push** at the end of each session

---

## Prompt Index

| File | Increment | Description | Status |
|------|-----------|-------------|--------|
| `00-session-context.md` | - | Session setup & project context | Always read first |
| `01-I2-user-profile-settings.md` | I2 | User profile & traveler preferences | Pending |
| `02-I4-trip-creation-wizard.md` | I4 | 4-step trip creation wizard | Pending |
| `03-I5-ai-agents-backend.md` | I5 | All 10 AI agents (CrewAI) | Pending |
| `04-I5-report-display-frontend.md` | I5 | Report UI with 9 sections | Pending |
| `05-I6-visual-itinerary-builder.md` | I6 | Drag-drop itinerary + map | Pending |
| `06-I7-collaboration-pdf-export.md` | I7 | Sharing, comments, PDF export | Pending |
| `07-I8-trip-updates-recalculation.md` | I8 | Edit trips & selective recalc | Pending |
| `08-I9-templates-travel-history.md` | I9 | Templates & travel history | Pending |
| `09-I10-analytics-settings.md` | I10 | Analytics dashboard & settings | Pending |
| `10-integration-testing-deployment.md` | - | E2E testing & production deploy | Final |

---

## Recommended Order

### Phase 1: Core Features (Frontend + Backend)
1. `01-I2-user-profile-settings.md` - Complete user profiles
2. `02-I4-trip-creation-wizard.md` - Trip creation flow

### Phase 2: AI Intelligence
3. `03-I5-ai-agents-backend.md` - Implement all agents
4. `04-I5-report-display-frontend.md` - Display reports

### Phase 3: Enhanced Features
5. `05-I6-visual-itinerary-builder.md` - Itinerary editing
6. `06-I7-collaboration-pdf-export.md` - Sharing & export

### Phase 4: Advanced Features
7. `07-I8-trip-updates-recalculation.md` - Trip updates
8. `08-I9-templates-travel-history.md` - Templates & history
9. `09-I10-analytics-settings.md` - Analytics & settings

### Phase 5: Launch
10. `10-integration-testing-deployment.md` - Testing & deploy

---

## Session Guidelines

### Token Budget
- Keep each session under **100K tokens**
- Complete **one increment** per session (or less)
- Commit frequently

### TDD Workflow
```
1. Write test FIRST → Run → Must FAIL (RED)
2. Write minimal code → Run → Must PASS (GREEN)
3. Refactor → Tests still pass
4. Commit with descriptive message
```

### Before Starting
```powershell
cd "D:\009_Projects_AI\Personal_Projects\TIP-Travel Intelligence-and-planner"

# Start local services
.\docker.ps1 up

# Verify services
.\docker.ps1 ps
```

### After Completing
```powershell
# Run tests
cd frontend && npm test
cd backend && python -m pytest

# Update tracking
# Edit feature_list.json - mark completed features

# Commit
git add .
git commit -m "feat(I{n}): description"
git push origin main
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `docs/INTEGRATED_PLAN.md` | Master project plan |
| `docs/visa-agent-roadmap.md` | Agent implementation guide |
| `feature_list.json` | Feature tracking (I1-I10) |
| `claude-progress.txt` | Session history |
| `product-plan/` | Design specs & component docs |

---

## Deployment Info

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | TBD |
| Backend | Railway | TBD |
| Database | Supabase | Configured |
| Redis | Railway | Configured |

---

## Getting Help

- **Project rules**: See `CLAUDE.md`
- **Design system**: See `product-plan/design-system/`
- **Component specs**: See `product-plan/sections/`
- **Ask user**: Use `AskUserQuestion` tool when unsure
