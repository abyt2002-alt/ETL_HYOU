# Data Ingestion Platform

A maintainable, config-driven full-stack data ingestion platform that extracts data from Google Sheets and loads it into PostgreSQL.

## Features

- Config-driven architecture - add new sources without code changes
- Generic ingestion engine for all sources
- Run all sources or individual sources
- Per-source validation and transformation
- Comprehensive logging and error tracking
- Clean operational UI for monitoring
- Excel date conversion support
- Type coercion and validation

## Tech Stack

**Frontend**: React, TypeScript, Vite, Tailwind CSS  
**Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic  
**Infrastructure**: Docker, Docker Compose

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Place Google Service Account credentials at `backend/credentials.json`
4. Run with Docker:

```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Documentation

- [Setup Guide](docs/README.md) - Local setup and configuration
- [System Flow](docs/SYSTEM_FLOW.md) - Architecture and component responsibilities
- [API Specification](docs/API_SPEC.md) - API endpoints and contracts
- [Schema Contracts](docs/SCHEMA_CONTRACTS.md) - Source definitions and mappings

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes and schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access
│   │   ├── models.py    # Database models
│   │   └── source_config.py  # Source definitions
│   └── alembic/         # Database migrations
├── frontend/            # React frontend
│   └── src/
│       ├── api/         # API client
│       ├── components/  # React components
│       └── pages/       # Page components
├── docs/                # Documentation
└── docker-compose.yml   # Docker setup
```

## Adding a New Source

1. Add source configuration to `backend/app/source_config.py`
2. Create database model in `backend/app/models.py`
3. Generate migration: `alembic revision --autogenerate -m "add new source"`
4. Apply migration: `alembic upgrade head`

No other code changes needed - the ingestion engine handles everything automatically.

## License

MIT
