# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 5173)                    │  │
│  │                                                             │  │
│  │  Dashboard │ Sources │ Runs │ Run Detail │ Data Preview   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Port 8000)                    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      API Layer                           │   │
│  │  /health │ /sources │ /ingest │ /runs │ /data           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Service Layer                          │   │
│  │  IngestionService │ SheetService │ TransformService     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Repository Layer                         │   │
│  │  DataRepository │ RunRepository                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                    │                        │
                    │                        │
                    ▼                        ▼
        ┌───────────────────┐    ┌──────────────────────┐
        │  Google Sheets    │    │   PostgreSQL DB      │
        │                   │    │                      │
        │  Meta             │    │  ingestion_runs      │
        │  Shopify          │    │  ingestion_run_items │
        │  GA               │    │  raw_meta            │
        │  GAds             │    │  raw_shopify         │
        │  ...              │    │  raw_ga              │
        └───────────────────┘    │  raw_gads            │
                                 └──────────────────────┘
```

## Component Layers

### Frontend Layer (React + TypeScript)

**Purpose**: User interface for operations and monitoring

**Components**:
- `Layout`: Navigation and page structure
- `Dashboard`: Overview and quick actions
- `Sources`: Source management and triggers
- `Runs`: Run history and status
- `RunDetail`: Detailed run information
- `DataPreview`: Table data preview

**State Management**: React hooks (useState, useEffect)

**API Communication**: Axios client with TypeScript types

### API Layer (FastAPI)

**Purpose**: HTTP interface and request validation

**Endpoints**:
```
GET  /api/health              - Health check
GET  /api/sources             - List configured sources
POST /api/ingest/all          - Run all sources
POST /api/ingest/{source}     - Run single source
GET  /api/runs/latest         - Get latest run
GET  /api/runs                - Get run history
GET  /api/runs/{id}           - Get run details
GET  /api/data/{table}        - Preview table data
```

**Responsibilities**:
- Request validation (Pydantic)
- Response formatting
- Error handling
- CORS configuration

### Service Layer

**Purpose**: Business logic and orchestration

#### IngestionService
- Orchestrates ingestion workflow
- Creates run records
- Handles source iteration
- Manages error recovery
- Updates run status

#### SheetService
- Authenticates with Google
- Reads sheet tabs
- Returns raw data

#### TransformService
- Validates columns
- Converts Excel dates
- Coerces types
- Normalizes column names

### Repository Layer

**Purpose**: Database operations

#### DataRepository
- Bulk inserts
- Data preview queries
- Table operations

#### RunRepository
- Run CRUD operations
- Run history queries
- Run item queries

### Data Layer

**Purpose**: Persistent storage

#### Operational Tables
- `ingestion_runs`: Run metadata
- `ingestion_run_items`: Per-source execution

#### Data Tables
- `raw_meta`: Meta advertising data
- `raw_shopify`: Shopify sales data
- `raw_ga`: Google Analytics data
- `raw_gads`: Google Ads data

## Data Flow

### Ingestion Flow

```
1. User Action
   │
   ├─→ Click "Run All Sources"
   │
2. API Request
   │
   ├─→ POST /api/ingest/all
   │
3. Create Run Record
   │
   ├─→ INSERT INTO ingestion_runs
   │
4. For Each Source
   │
   ├─→ Create Run Item
   │   └─→ INSERT INTO ingestion_run_items
   │
   ├─→ Read Sheet Tab
   │   └─→ Google Sheets API
   │
   ├─→ Validate Columns
   │   └─→ Check required columns
   │
   ├─→ Transform Data
   │   ├─→ Convert dates
   │   ├─→ Coerce types
   │   └─→ Normalize names
   │
   ├─→ Load Data
   │   └─→ INSERT INTO raw_* table
   │
   └─→ Update Run Item
       └─→ UPDATE ingestion_run_items
   │
5. Update Run Status
   │
   ├─→ UPDATE ingestion_runs
   │
6. Return Response
   │
   └─→ JSON with run details
```

### Configuration Flow

```
Source Config (source_config.py)
   │
   ├─→ source_name: "meta"
   ├─→ sheet_tab_name: "Meta"
   ├─→ target_table_name: "raw_meta"
   ├─→ required_columns: [...]
   ├─→ field_types: {...}
   └─→ date_fields: [...]
   │
   ▼
Ingestion Engine
   │
   ├─→ Reads config
   ├─→ Applies rules
   └─→ Loads data
   │
   ▼
Database Table (raw_meta)
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **Pydantic**: Data validation
- **gspread**: Google Sheets API client
- **pandas**: Data transformation

### Frontend
- **React**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **React Router**: Navigation
- **Axios**: HTTP client

### Infrastructure
- **PostgreSQL**: Relational database
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Design Patterns

### Repository Pattern
Separates data access logic from business logic:
- Services call repositories
- Repositories handle database operations
- Easy to test and mock

### Service Layer Pattern
Encapsulates business logic:
- Controllers call services
- Services orchestrate operations
- Reusable across endpoints

### Config-Driven Design
Behavior driven by configuration:
- No hardcoded source logic
- Easy to extend
- Single source of truth

### Dependency Injection
FastAPI's built-in DI:
- Database sessions injected
- Easy to test
- Clean separation

## Scalability Considerations

### Current Limitations
- Single-threaded ingestion
- No connection pooling
- No caching
- Synchronous operations

### Scaling Options

**Horizontal Scaling**:
- Run multiple backend instances
- Use load balancer
- Shared database

**Vertical Scaling**:
- Increase container resources
- Optimize queries
- Add indexes

**Database Scaling**:
- Read replicas for queries
- Partition tables by date
- Archive old data

**Async Processing**:
- Use Celery for background jobs
- Queue ingestion tasks
- Parallel source processing

## Security Architecture

### Current Security
- CORS configuration
- SQL injection protection (SQLAlchemy)
- Environment variable secrets

### Recommended Additions
- API authentication (JWT)
- Rate limiting
- Input sanitization
- Audit logging
- Secrets management
- SSL/TLS encryption

## Monitoring Points

### Health Checks
- API health endpoint
- Database connectivity
- Google Sheets access

### Metrics to Track
- Ingestion success rate
- Rows processed per run
- Run duration
- Error frequency
- API response times

### Logging
- Run start/completion
- Source processing
- Errors and exceptions
- API requests

## Extension Points

### Adding Features

**Authentication**:
- Add auth middleware
- Protect routes
- Track user actions

**Scheduling**:
- Add APScheduler
- Define cron expressions
- Trigger ingestions

**Notifications**:
- Add email service
- Send on failures
- Daily summaries

**Data Quality**:
- Add validation rules
- Track quality metrics
- Alert on issues

**Incremental Loads**:
- Track last load date
- Filter sheet data
- Update existing rows

## Deployment Architecture

### Development
```
Docker Compose
├── PostgreSQL container
├── Backend container
└── Frontend container
```

### Production
```
Load Balancer
├── Frontend (CDN/Static hosting)
└── Backend (Multiple instances)
    └── PostgreSQL (Managed service)
```

## Database Schema

### Entity Relationships

```
ingestion_runs (1) ──< (N) ingestion_run_items

ingestion_run_items.run_id → ingestion_runs.id
```

### Table Purposes

**ingestion_runs**: Tracks overall execution
- One record per "Run All" or "Run Single"
- Stores aggregate status
- Links to individual items

**ingestion_run_items**: Tracks per-source execution
- One record per source per run
- Stores detailed metrics
- Contains error messages

**raw_* tables**: Store ingested data
- One table per source
- Append-only (currently)
- Include ingestion timestamp
