# Pull Request

## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Infrastructure/CI/CD change
- [ ] Refactoring (no functional changes)
- [ ] Test coverage improvement

## Checklist

### General
- [ ] I have read the contributing guidelines
- [ ] My code follows the code style of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas

### Testing
- [ ] **TDD followed**: I wrote tests BEFORE writing implementation code (RED-GREEN-REFACTOR)
- [ ] All new and existing tests pass locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] Test coverage is ≥80% for modified files
- [ ] Unit tests added for business logic
- [ ] Integration tests added for API endpoints
- [ ] E2E tests added for critical user flows (if applicable)

### Backend (if applicable)
- [ ] Backend tests passing (`pytest tests/ -v`)
- [ ] Code coverage ≥80% (`pytest --cov=app`)
- [ ] Linting passes (`ruff check app/`)
- [ ] Type hints added for all functions
- [ ] API documentation updated (Swagger/OpenAPI)
- [ ] Database migrations created (if schema changes)
- [ ] Celery tasks tested with Redis

### Frontend (if applicable)
- [ ] Frontend tests passing (`npm run test`)
- [ ] ESLint passes (`npm run lint`)
- [ ] TypeScript type check passes (`tsc --noEmit`)
- [ ] Build succeeds (`npm run build`)
- [ ] Accessibility tested (WCAG 2.1 AA)
- [ ] Responsive design verified (mobile, tablet, desktop)

### Documentation
- [ ] README updated (if needed)
- [ ] CHANGELOG updated
- [ ] API documentation updated (if backend changes)
- [ ] Component documentation updated (if UI changes)
- [ ] Migration guide provided (if breaking changes)

### Feature List
- [ ] `feature_list.json` updated with completion status
- [ ] `claude-progress.txt` updated with session summary

## Related Issues
<!-- Link to related issues using #issue_number -->

Closes #

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Testing Instructions
<!-- Describe how to test your changes -->

1.
2.
3.

## Performance Impact
<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (explain why acceptable)

## Breaking Changes
<!-- List any breaking changes and migration steps -->

## Additional Notes
<!-- Any additional information that reviewers should know -->

---

## Reviewer Checklist

- [ ] Code quality is acceptable
- [ ] TDD principles followed
- [ ] Tests are comprehensive and meaningful
- [ ] No security vulnerabilities introduced
- [ ] No hard-coded secrets or credentials
- [ ] Error handling is appropriate
- [ ] Logging is appropriate
- [ ] Documentation is clear and complete
- [ ] Changes align with project architecture
