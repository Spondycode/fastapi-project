# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a FastAPI application following modern Python practices with UV as the dependency manager. The project uses Python 3.14+ and follows async/await patterns throughout the codebase.

## Architecture

- **Entry Point**: `app/main.py` contains the FastAPI application instance and all route definitions
- **Data Models**: Pydantic models are defined in the same file as their routes (currently `Item` model in `app/main.py`)
- **Testing**: Tests use FastAPI's TestClient for synchronous API testing, located in `tests/`
- **Dependencies**: Managed via UV with `pyproject.toml` and `uv.lock` for reproducible builds

## Common Commands

### Setup & Dependencies
```bash
# Install all dependencies (creates/syncs virtual environment)
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>
```

### Running the Application
```bash
# Start development server with auto-reload
uv run uvicorn app.main:app --reload

# Start without reload (production-like)
uv run uvicorn app.main:app

# Specify host and port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**API Documentation URLs:**
- Interactive Swagger UI: http://localhost:8000/docs
- ReDoc alternative: http://localhost:8000/redoc
- OpenAPI JSON schema: http://localhost:8000/openapi.json

### Testing
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_main.py

# Run specific test function
uv run pytest tests/test_main.py::test_read_root

# Run with coverage
uv run pytest --cov=app

# Run tests in watch mode (requires pytest-watch)
uv run ptw
```

### Code Quality
```bash
# Note: Linting/formatting tools not yet configured in this project
# To add them, install with: uv add --dev ruff black mypy

# Format code (if black installed)
uv run black app/ tests/

# Lint code (if ruff installed)
uv run ruff check app/ tests/

# Type checking (if mypy installed)
uv run mypy app/
```

## Development Guidelines

### Dependency Management
- **Always use UV** instead of pip for this project (per user preference)
- Run `uv sync` after pulling changes that modify `pyproject.toml` or `uv.lock`
- UV automatically manages the virtual environment in `.venv/`

### API Development
- All endpoints should be async (`async def`)
- Use Pydantic models for request/response validation
- Include docstrings for all endpoint functions
- Follow the existing pattern: path operations are defined directly in `app/main.py`

### Testing
- Write tests using FastAPI's TestClient (synchronous testing)
- Test file naming: `test_*.py` in the `tests/` directory
- Test function naming: `test_<description>`
- Include docstrings in test functions
- Test both success and error cases for each endpoint

### Code Structure
- **Current**: Simple structure with all routes in `app/main.py`
- **For growth**: Consider splitting into `app/routers/` when adding more endpoints
- **Models**: Move Pydantic models to `app/models.py` when they grow in number
- **Config**: Create `app/config.py` for environment variables and settings

## Project Constraints

- Python version: 3.14+ (see `.python-version`)
- Uses modern Python type hints with `|` for unions (e.g., `str | None`)
- ASGI server: Uvicorn with standard extras
- Testing framework: Pytest with httpx for async client support
