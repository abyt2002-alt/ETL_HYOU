# Directory Structure

Complete file tree with descriptions of each component.

```
data-ingestion-platform/
│
├── 📄 README.md                          # Main project documentation
├── 📄 QUICK_START.md                     # 5-minute setup guide
├── 📄 IMPLEMENTATION_SUMMARY.md          # Implementation details and design decisions
├── 📄 PROJECT_SUMMARY.md                 # High-level project overview
├── 📄 CHECKLIST.md                       # Complete feature checklist
├── 📄 DIRECTORY_STRUCTURE.md             # This file
├── 📄 .env.example                       # Environment variables template
├── 📄 .env                               # Environment configuration (not in repo)
├── 📄 .gitignore                         # Git ignore rules
├── 📄 docker-compose.yml                 # Docker orchestration configuration
│
├── 📁 backend/                           # FastAPI backend application
│   ├── 📄 Dockerfile                     # Backend container definition
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 alembic.ini                    # Alembic migration configuration
│   ├── 📄 credentials.json               # Google service account credentials (not in repo)
│   │
│   ├── 📁 app/                           # Main application package
│   │   ├── 📄 __init__.py               # Package initializer
│   │   ├── 📄 main.py                   # FastAPI application entry point
│   │   ├── 📄 config.py                 # Application configuration (env vars)
│   │   ├── 📄 database.py               # Database connection and session
│   │   ├── 📄 models.py                 # SQLAlchemy database models
│   │   ├── 📄 source_config.py          # Source definitions (config-driven)
│   │   │
│   │   ├── � api/                      # API layer (split by concern)
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 schemas.py            # Pydantic request/response models
│   │   │   ├── � health_routes.py      # Health check endpoint
│   │   │   ├── 📄 source_routes.py      # List sources endpoint
│   │   │   ├── 📄 ingestion_routes.py   # Trigger ingestion endpoints
│   │   │   ├── 📄 run_routes.py         # Run history and details endpoints
│   │   │   └── 📄 data_routes.py        # Data preview endpoint
│   │   │
│   │   ├── 📁 services/                 # Business logic layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 ingestion_service.py  # Orchestrates ingestion workflow
│   │   │   ├── 📄 sheet_service.py      # Google Sheets API integration (service account)
│   │   │   └── � transform_service.py  # Data validation and transformation
│   │   │
│   │   └── � repositories/             # Data access layer
│   │       ├── 📄 __init__.py
│   │       ├── � danta_repository.py    # Data table operations (replace mode)
│   │       └── 📄 run_repository.py     # Run tracking operations
│   │
│   └── � alembic/                      # Database migrations
│       ├── 📄 env.py                    # Alembic environment configuration
│       ├── 📄 script.py.mako            # Migration template
│       └── � versions/
│           └── 📄 001_initial_schema.py # Initial database schema
│
├── � frontend/                          # React frontend application
│   ├── 📄 Dockerfile                     # Frontend container definition
│   ├── 📄 package.json                   # Node.js dependencies and scripts
│   ├── 📄 vite.config.ts                 # Vite build configuration
│   ├── � tsconfig.json                  # TypeScript configuration
│   ├── 📄 tsconfig.node.json             # TypeScript config for Node
│   ├── 📄 tailwind.config.js             # Tailwind CSS configuration
│   ├── 📄 postcss.config.js              # PostCSS configuration
│   ├── 📄 index.html                     # HTML entry point
│   ├── 📄 .env.example                   # Frontend environment template
│   ├── 📄 .env                           # Frontend environment config (not in repo)
│   │
│   └── � src/                           # Source code
│       ├── � main.tsx                   # Application entry point
│       ├── 📄 App.tsx                    # Root component with routing
│       ├── � index.css                  # Global styles (Tailwind)
│       │
│       ├── � api/                       # API client
│       │   └── 📄 client.ts              # Axios client with TypeScript types
│       │
│       ├── � components/                # Reusable components
│       │   └── 📄 Layout.tsx             # App layout with navigation
│       │
│       └── 📁 pages/                     # Page components
│           ├── 📄 Dashboard.tsx          # Main dashboard page
│           ├── 📄 Sources.tsx            # Source list and management
│           ├── 📄 Runs.tsx               # Run history table
│           ├── 📄 RunDetail.tsx          # Detailed run view
│           └── 📄 DataPreview.tsx        # Data table preview
│
├── � docs/                              # Documentation
│   ├── 📄 README.md                      # Setup and configuration guide
│   ├── � SYSTEM_FLOW.md                 # Architecture and data flow
│   ├── 📄 API_SPEC.md                    # API endpoint reference
│   ├── 📄 SCHEMA_CONTRACTS.md            # Source definitions and mappings
│   ├── 📄 ADDING_SOURCES.md              # How to add new sources (3 steps)
│   ├── 📄 DEPLOYMENT.md                  # Production deployment guide
│   ├── 📄 ARCHITECTURE.md                # Architecture diagrams and patterns
│   └── 📄 GOOGLE_SHEETS_SETUP.md         # Google Sheets configuration
│
└── 📁 scripts/                           # Setup scripts
    ├── 📄 setup.sh                       # Linux/Mac setup script
    └── 📄 setup.ps1                      # Windows PowerShell setup script
```

## Key Files Explained

### Root Level

- **README.md**: Main entry point, project overview, quick links
- **QUICK_START.md**: Get running in 5 minutes
- **IMPLEMENTATION_SUMMARY.md**: Design decisions, rationale, scope
- **PROJECT_SUMMARY.md**: High-level overview, current scope, limitations
- **CHECKLIST.md**: Feature checklist with accurate terminology
- **docker-compose.yml**: Defines all services (PostgreSQL, backend, frontend)
- **.env.example**: Template for environment variables
- **.env**: Actual environment configuration (not in repo)

### Backend Structure

#### Core Files
- **main.py**: FastAPI app initialization, CORS, route registration (modular)
- **config.py**: Environment variable loading with Pydantic
- **database.py**: SQLAlchemy engine and session management
- **models.py**: All database table definitions
- **source_config.py**: Source definitions with replace mode default
- **credentials.json**: Google service account credentials (not in repo)

#### API Layer (`app/api/`) - Split by Concern
- **health_routes.py**: Health check endpoint
- **source_routes.py**: List configured sources
- **ingestion_routes.py**: Trigger ingestion (all or single)
- **run_routes.py**: Run history and details
- **data_routes.py**: Data preview
- **schemas.py**: Pydantic models for request/response validation

#### Service Layer (`app/services/`)
- **ingestion_service.py**: Orchestrates the entire ingestion workflow
- **sheet_service.py**: Google Sheets API (service account authentication)
- **transform_service.py**: Data validation, type conversion, column normalization

#### Repository Layer (`app/repositories/`)
- **data_repository.py**: Database operations for data tables (replace mode)
- **run_repository.py**: Database operations for run tracking

#### Migrations (`alembic/`)
- **versions/001_initial_schema.py**: Creates all tables

### Frontend Structure

#### Core Files
- **main.tsx**: React app initialization and mounting
- **App.tsx**: Router configuration and route definitions
- **index.css**: Tailwind CSS imports and global styles

#### API Client (`src/api/`)
- **client.ts**: Axios instance, TypeScript interfaces, API methods

#### Components (`src/components/`)
- **Layout.tsx**: Navigation bar and page wrapper

#### Pages (`src/pages/`)
- **Dashboard.tsx**: Latest run status, quick actions
- **Sources.tsx**: Source list, individual run triggers, preview links
- **Runs.tsx**: Run history table with filtering
- **RunDetail.tsx**: Detailed view of a specific run
- **DataPreview.tsx**: Table data preview with pagination

### Documentation

- **README.md**: Setup instructions, environment configuration
- **SYSTEM_FLOW.md**: Architecture diagrams, component responsibilities, load modes
- **API_SPEC.md**: Complete API reference with examples
- **SCHEMA_CONTRACTS.md**: Source-to-table mappings, validation rules, load modes
- **ADDING_SOURCES.md**: 3-step guide for adding sources (low-code)
- **DEPLOYMENT.md**: Production deployment strategies
- **ARCHITECTURE.md**: Visual architecture diagrams
- **GOOGLE_SHEETS_SETUP.md**: Google Cloud and Sheets configuration (service account)

### Scripts

- **setup.sh**: Automated setup for Linux/Mac
- **setup.ps1**: Automated setup for Windows

## File Count by Category

- **Backend Code**: 18 files
- **Frontend Code**: 11 files
- **Documentation**: 13 files
- **Configuration**: 12 files
- **Scripts**: 2 files
- **Infrastructure**: 3 files

**Total**: 59 files (excluding generated files and .env)

## Important Paths

### Configuration
- Backend env: `.env`
- Frontend env: `frontend/.env`
- Source config: `backend/app/source_config.py`
- Database config: `backend/alembic.ini`

### Credentials
- Google credentials: `backend/credentials.json` (not in repo)

### Logs
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs postgres`

### Database
- Connection: `postgresql://postgres:postgres@localhost:5432/ingestion_db`
- Migrations: `backend/alembic/versions/`

## Navigation Tips

### To modify API endpoints:
→ `backend/app/api/` (split by concern)
  - Health: `health_routes.py`
  - Sources: `source_routes.py`
  - Ingestion: `ingestion_routes.py`
  - Runs: `run_routes.py`
  - Data: `data_routes.py`

### To add a new source (3 steps):
1. → `backend/app/source_config.py` (add SourceConfig)
2. → `backend/app/models.py` (add model class)
3. → Generate and apply migration

### To change data transformation:
→ `backend/app/services/transform_service.py`

### To change load mode:
→ `backend/app/source_config.py` (change `load_mode`)
→ `backend/app/repositories/data_repository.py` (modify `bulk_insert`)

### To modify UI:
→ `frontend/src/pages/` (page components)  
→ `frontend/src/components/` (reusable components)

### To update API client:
→ `frontend/src/api/client.ts`

### To change database schema:
→ `backend/app/models.py`  
→ Generate migration with Alembic

### To add documentation:
→ `docs/` folder

## File Naming Conventions

- **Python files**: `snake_case.py`
- **TypeScript files**: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- **Config files**: `lowercase.config.js`
- **Documentation**: `UPPERCASE.md` (root), `PascalCase.md` (docs/)

## Import Paths

### Backend
```python
from app.models import IngestionRun
from app.services.ingestion_service import IngestionService
from app.repositories.data_repository import DataRepository
from app.config import get_settings
from app.api.health_routes import router as health_router
```

### Frontend
```typescript
import { api } from '../api/client'
import Layout from '../components/Layout'
import Dashboard from '../pages/Dashboard'
```

## Where to Start

1. **Understanding the system**: Read `IMPLEMENTATION_SUMMARY.md`
2. **Setting up locally**: Follow `QUICK_START.md`
3. **Understanding architecture**: Read `docs/SYSTEM_FLOW.md`
4. **Adding a source**: Follow `docs/ADDING_SOURCES.md` (3 steps)
5. **API reference**: Check `docs/API_SPEC.md`
6. **Deploying**: Read `docs/DEPLOYMENT.md`

## Key Design Decisions Reflected in Structure

### Modular API Routes
API routes are split by concern (health, sources, ingestion, runs, data) to prepare for future growth and reporting features.

### Replace Mode Default
All sources configured with `load_mode="replace"` to prevent duplicate data on repeated runs.

### Service Account Authentication
`credentials.json` file for service account, not OAuth tokens.

### Low-Code Source Onboarding
Adding a source requires 3 steps: config + model + migration (not no-code).

### Production-Structured Foundation
Clean architecture and separation of concerns, but not production-ready (missing auth, tests, monitoring).

## Current Scope vs Not Implemented

### Implemented (in structure)
- Config-driven sources
- Generic ingestion engine
- Replace mode
- Column validation (fail on missing, warn on unexpected)
- Service account auth
- Modular API routes
- Comprehensive tracking

### Not Implemented
- Authentication/Authorization
- Scheduling
- Incremental loading
- Retry logic
- Tests
- Monitoring/Alerting
- Upsert mode (structure exists, not tested)
