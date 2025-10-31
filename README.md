# FastAPI Project

A simple FastAPI application built with modern Python practices.

## Features

- FastAPI web framework
- Pydantic for data validation
- Uvicorn ASGI server
- Pytest for testing
- UV for dependency management

## Setup

1. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

## Running the Application

Start the development server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint
- `GET /items/{item_id}` - Get an item by ID
- `POST /items/` - Create a new item

## Testing

Run tests with pytest:
```bash
uv run pytest
```

## Project Structure

```
fastapi-project/
├── app/
│   ├── __init__.py
│   └── main.py          # Main application file
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Test file
├── .gitignore
├── pyproject.toml       # Project configuration
├── uv.lock             # Dependency lock file
└── README.md
```
