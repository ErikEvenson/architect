# Testing Strategy

## Test Types

### Unit Tests
- **Location:** `services/backend/tests/` (colocated with service)
- **Framework:** pytest + pytest-asyncio
- **Scope:** Individual functions, service methods, schema validation
- **Database:** Test database (separate from dev) or mocked where appropriate
- **Coverage target:** 80% line coverage minimum

### Integration Tests
- **Location:** `tests/integration/`
- **Framework:** pytest + httpx
- **Scope:** API endpoint tests against running backend with real database
- **Database:** Real PostgreSQL (test database)
- **Derived from:** Gherkin scenarios in `specs/behavior/*.feature`

### Frontend Tests
- **Location:** `services/frontend/tests/`
- **Framework:** Vitest + jsdom
- **Scope:** Component rendering, state management, API client
- **Coverage target:** 70% line coverage minimum

## Test Execution

### Local Development
```bash
# Backend unit tests
cd services/backend && pytest

# Frontend tests
cd services/frontend && npm test

# Integration tests (requires running services)
pytest tests/integration/
```

### CI Pipeline
Tests run inside Docker containers (same as Galaxy pattern):
1. Build service image
2. Build test image on top (installs test dependencies)
3. Run ruff lint check
4. Run pytest with coverage

### Script
`scripts/run-tests.sh` runs all test suites:
- Backend unit tests with coverage
- Frontend tests with coverage
- Integration tests (if services are running)

## Test Configuration

### pytest (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
branch = true
```

### Vitest (`vitest.config.ts`)
- jsdom environment
- Coverage via @vitest/coverage-v8
- Test files: `**/*.test.{ts,tsx}`

## Spec-to-Test Mapping

| Spec Type | Test Type | Example |
|---|---|---|
| Gherkin `.feature` | Integration tests (pytest) | `client_management.feature` → `test_client_api.py` |
| OpenAPI `rest-api.yaml` | API contract tests | Endpoint paths, status codes, response shapes |
| `database.md` | Database constraint tests | Unique slugs, FK cascades, enum values |
| Rendering specs | Unit tests | Renderer input/output, error handling |

## Linting

- **Backend:** ruff (line-length 100, target Python 3.12)
- **Frontend:** ESLint + TypeScript strict mode
