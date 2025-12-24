# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. `backend-ci.yml` - Backend CI/CD Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Changes to `backend/**` files

**Jobs:**
- **Lint**: Ruff linter + Black formatter
- **Test**: Unit tests with pytest + Redis service + Coverage (>80%)
- **Docker**: Build validation
- **Security**: Trivy vulnerability scanning
- **Type Check**: mypy type checking

**Requirements:**
- Python 3.12
- Redis 7 (service container)
- Coverage ≥80%

### 2. `frontend-ci.yml` - Frontend CI/CD Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Changes to `frontend/**` files

**Jobs:**
- **Lint**: ESLint + TypeScript type check
- **Test**: Jest/Vitest unit tests with coverage
- **Build**: Next.js production build

**Requirements:**
- Node.js 20
- All tests passing

### 3. `ci.yml` - Full Stack CI/CD Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- **Changes**: Detect which parts of the codebase changed
- **Backend**: Run backend-ci.yml (if backend changed)
- **Frontend**: Run frontend-ci.yml (if frontend changed)
- **Integration**: Docker Compose validation + Redis connectivity
- **Summary**: Report overall CI/CD status

## Secrets Configuration

Required GitHub Secrets (Settings → Secrets and variables → Actions):

### Supabase
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `SUPABASE_JWT_SECRET`: Supabase JWT secret
- `DATABASE_URL`: PostgreSQL connection string

### Optional
- `CODECOV_TOKEN`: Codecov upload token (for coverage reports)

## Pull Request Template

`.github/pull_request_template.md` provides a comprehensive checklist for:
- Code quality
- Testing requirements (TDD)
- Documentation
- Performance impact
- Breaking changes

## Local Testing

Before pushing, run these commands locally:

### Backend
```bash
cd backend

# Lint
ruff check app/
black --check app/

# Test with coverage
pytest tests/ -v --cov=app --cov-report=term --cov-fail-under=80

# Type check
mypy app/ --ignore-missing-imports

# Docker build
docker build -t tip-backend:local .
```

### Frontend
```bash
cd frontend

# Lint
npm run lint

# Type check
npx tsc --noEmit

# Test
npm run test

# Build
npm run build
```

### Docker Compose
```bash
# Validate configuration
docker-compose config

# Build and start services
docker-compose up -d

# Run tests
docker-compose exec backend pytest tests/ -v

# Stop services
docker-compose down
```

## CI/CD Status Badges

Add these to your README.md:

```markdown
![Backend CI](https://github.com/YOUR_USERNAME/TIP-Travel-Intelligence-and-planner/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/YOUR_USERNAME/TIP-Travel-Intelligence-and-planner/actions/workflows/frontend-ci.yml/badge.svg)
![Full Stack CI](https://github.com/YOUR_USERNAME/TIP-Travel-Intelligence-and-planner/actions/workflows/ci.yml/badge.svg)
```

## Troubleshooting

### Backend Tests Failing
- Check Redis service is running (`docker-compose ps redis`)
- Verify environment variables are set correctly
- Run locally: `pytest tests/ -v`

### Frontend Build Failing
- Check Node.js version (should be 20)
- Clear cache: `npm ci`
- Run locally: `npm run build`

### Coverage Below 80%
- Write more tests for uncovered code
- Check coverage report: `pytest --cov=app --cov-report=html`
- Open `htmlcov/index.html` to see uncovered lines

### Docker Build Failing
- Check Dockerfile syntax
- Verify base image is accessible
- Test locally: `docker build -t test .`

## Best Practices

1. **TDD**: Write tests BEFORE implementation (RED-GREEN-REFACTOR)
2. **Coverage**: Maintain ≥80% test coverage
3. **Linting**: Fix all linting errors before pushing
4. **Type Safety**: Add type hints for all Python functions
5. **Documentation**: Update docs with code changes
6. **Feature List**: Mark features complete in `feature_list.json`
7. **Progress Log**: Update `claude-progress.txt` after sessions

## Performance

CI/CD pipelines run in parallel where possible:
- Backend lint, test, docker, security run concurrently
- Frontend lint, test, build run concurrently
- Full stack pipeline only runs changed workflows

Average runtime:
- Backend CI: ~3-5 minutes
- Frontend CI: ~2-3 minutes
- Full Stack CI: ~5-7 minutes

## Next Steps

- [ ] Add E2E tests with Playwright
- [ ] Set up automatic deployments to Railway/Vercel
- [ ] Add performance testing
- [ ] Implement dependency scanning
- [ ] Add semantic versioning automation
