# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI-based semiconductor reliability calculator application with frontend, authentication, and usage tracking. The application provides various reliability calculators (MTBF, Duane Model, Test Sample Size) and is designed for deployment on Vercel.

## Architecture

### Backend Structure
- **Framework**: FastAPI with uvicorn server
- **Database**: SQLite (development) with SQLAlchemy ORM
- **Authentication**: JWT tokens via python-jose
- **API Structure**: Modular calculator system with base classes
- **Testing**: pytest with both unit and integration tests

### Key Directories
- `backend/app/`: Main application code
  - `calculators/`: Individual calculator implementations inheriting from `base.py`
  - `auth/`: Authentication routes, schemas, and utilities
  - `database/`: Database models and connection handling
  - `middleware/`: Usage tracking and rate limiting
- `frontend/`: Static HTML/JavaScript frontend
- `api/`: Vercel serverless function entry points

## Common Development Commands

### Backend Development
```bash
# Setup and activate environment
cd backend && ./activate.sh

# Run development server
python -m app.main

# Run unit tests (calculator logic)
python test_calculators.py

# Run API integration tests (requires running server)
python test_api.py

# Run specific test with pytest
pytest test_calculators.py::TestMTBFCalculator::test_basic_mtbf_calculation -v
```

### Deployment
```bash
# Deploy to Vercel production
./deploy.sh

# Test Vercel deployment locally
vercel dev
```

## Testing Patterns

### Calculator Tests
- Unit tests in `test_calculators.py` test mathematical logic directly
- Each calculator inherits from `BaseCalculator` and implements `calculate()` method
- Tests verify both correct calculations and input validation

### API Tests
- Integration tests in `test_api.py` test full HTTP endpoints
- Requires running backend server (`python -m app.main`)
- Tests authentication, usage tracking, and all calculator endpoints

### Running Tests
- Always run calculator unit tests first (faster, no server required)
- API tests automatically skip if server not running
- Use pytest with `-v` flag for verbose output

## Calculator Development

### Adding New Calculators
1. Create new file in `backend/app/calculators/`
2. Inherit from `BaseCalculator` class
3. Implement `info` property and `calculate()` method
4. Register in `backend/app/calculators/__init__.py`
5. Add tests in `test_calculators.py`

### Calculator Structure
```python
from .base import BaseCalculator, CalculatorInfo, InputField

class NewCalculator(BaseCalculator):
    @property
    def info(self) -> CalculatorInfo:
        return CalculatorInfo(
            id="new_calc",
            name="New Calculator",
            # ... other fields
        )
    
    def calculate(self, inputs: dict) -> dict:
        # Implementation with input validation
        return results
```

## Database and Migrations

- Database file: `backend/semiconductor_calc.db`
- Models defined in `backend/app/database/models.py`
- Migrations handled through `backend/migrations/` (Alembic)

## Authentication System

- JWT-based authentication with usage tracking
- Free tier: 10 calculations/day, Premium: unlimited
- Anonymous usage tracking by IP, authenticated by user ID
- Token-based API access with Bearer authentication

## Deployment Architecture

### Vercel Configuration
- Entry point: `api/test-simple.py` (configured in `vercel.json`)
- Static frontend served from `public/` directory
- Serverless functions for API endpoints

### Environment Requirements
- Python 3.7+ for backend
- Modern web browser for frontend
- Vercel CLI for deployment