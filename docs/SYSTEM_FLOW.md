# System Flow Documentation

## Architecture Overview

The Data Ingestion Platform is a config-driven system that extracts data from Google Sheets and loads it into PostgreSQL tables. The architecture follows a clean separation of concerns with modular components.

## Component Responsibilities

### Frontend (React + TypeScript)

**Purpose**: Operational UI for monitoring and triggering ingestion jobs

**Components**:
- `Dashboard`: Overview of latest run and source status
- `Sources`: List all configured sources with run triggers
- `Runs`: History of all ingestion runs
- `RunDetail`: Detailed view of a specific run
- `DataPreview`: Preview loaded data from tables

**Key Features**:
- Trigger ingestion for all sources or single source
- View run status and error messages
- Preview ingested data
- Real-time status updates

### Backend (FastAPI)

**API Layer** (split by concern):
- `health_routes.py`: Health check endpoint
- `source_routes.py`: List configured sources
- `ingestion_routes.py`: Trigger ingestion jobs
- `run_routes.py`: Run history and details
- `data_routes.py`: Data preview

**Service Layer**:
- `IngestionService`: Orchestrates ingestion workflow
- `SheetService`: Reads data from Google Sheets (service account auth)
- `TransformService`: Validates and transforms data

**Repository Layer**:
- `DataRepository`: Handles bulk inserts and data queries
- `RunRepository`: Manages ingestion run records

**Models**:
- `IngestionRun`: Tracks overall run metadata
- `IngestionRunItem`: Tracks per-source execution
- `RawMeta`, `RawShopify`, `RawGA`, `RawGAds`: Data tables

**Configuration**:
- `source_config.py`: Defines all data sources
- Specifies column mappings, types, and load modes
- Drives ingestion behavior

## End-to-End Flow

### 1. User Triggers Ingestion

User clicks "Run All Sources" or "Run Single Source" in the UI.

### 2. API Request

Frontend sends POST request to:
- `/api/ingest/all` for all sources
- `/api/ingest/{source_name}` for single source

### 3. Run Creation

`IngestionService` creates an `IngestionRun` record:
- Sets status to "running"
- Records trigger type and timestamp
- Commits to database

### 4. Source Processing Loop

For each configured source:

**a. Create Run Item**
- Create `IngestionRunItem` record
- Link to parent run
- Set status to "running"

**b. Extract Data**
- `SheetService` reads from Google Sheet tab using service account
- Returns raw data as list of dictionaries
- Records row count

**c. Validate Data**
- `TransformService` validates columns
- **Missing required columns**: Hard failure, ingestion stops
- **Unexpected extra columns**: Warning logged, columns ignored (unless strict mode)
- Returns validation result

**d. Transform Data**
- Convert Excel date serials to datetime
- Coerce numeric types
- Filter to only required and optional columns
- Normalize column names (lowercase, underscores)
- Create pandas DataFrame

**e. Load Data**
- **Replace mode** (default): Truncate table first, then insert
- **Upsert mode** (if configured): Update existing, insert new
- `DataRepository` performs bulk insert
- Uses pandas `to_sql` with chunking
- Returns rows loaded count

**f. Update Run Item**
- Set status to "completed" or "failed"
- Record rows read/loaded/failed
- Store error message if failed
- Set completion timestamp

### 5. Run Completion

After all sources processed:
- Update run status ("completed", "partial", or "failed")
- Generate summary message
- Set completion timestamp
- Commit to database

### 6. Response

API returns run details to frontend, which updates the UI.

## Source-to-Table Flow

### Configuration

Each source is defined in `source_config.py`:

```python
SourceConfig(
    source_name="meta",
    sheet_tab_name="Meta",
    target_table_name="raw_meta",
    required_columns=["Day", "DMA region", "Impressions", "Amount spent"],
    field_types={"Day": "date", "Impressions": "integer", ...},
    date_fields=["Day"],
    numeric_fields=["Amount spent"],
    load_mode="replace",  # Truncate and reload
    strict_columns=False  # Warn on unexpected, don't fail
)
```

### Mapping

Sheet columns → Database columns:
- "Day" → `day` (date)
- "DMA region" → `dma_region` (string)
- "Impressions" → `impressions` (integer)
- "Amount spent" → `amount_spent` (numeric)

### Transformation Rules

1. **Date Fields**: Excel serial dates converted to datetime
2. **Numeric Fields**: Coerced to numeric, nulls handled
3. **Integer Fields**: Coerced to integer, nulls become 0
4. **String Fields**: Preserved as-is
5. **Column Names**: Lowercased, spaces replaced with underscores
6. **Extra Columns**: Filtered out after warning

### Load Modes

**Replace Mode** (default):
- Truncates table before loading
- Prevents duplicate data on repeated runs
- Suitable for Google Sheets (current state, not incremental)
- Acceptable for datasets < 100K rows

**Upsert Mode** (configurable):
- Updates existing records based on unique keys
- Inserts new records
- Preserves historical data not in current sheet
- Requires `unique_keys` configuration
- Structure exists but not fully tested

## Error Handling

### Source-Level Failures

If one source fails:
- Error captured in `IngestionRunItem.error_message`
- Other sources continue processing
- Run status set to "partial"

### Run-Level Failures

If entire run fails:
- Run status set to "failed"
- Summary message contains error details
- All items marked appropriately

### Data Validation Failures

**Missing Required Columns**:
- Fail immediately
- No data loaded for that source
- Error message specifies missing columns

**Unexpected Extra Columns**:
- Default: Log warning, ignore columns, continue
- Strict mode: Fail immediately
- Configurable per source with `strict_columns`

**Type Coercion Errors**:
- Invalid values → NULL in database
- Logged but doesn't fail ingestion

## Database Schema

### Operational Tables

**ingestion_runs**:
- Tracks each ingestion execution
- Stores overall status and timing
- Links to individual source items

**ingestion_run_items**:
- One record per source per run
- Tracks rows read/loaded/failed
- Stores error messages

### Data Tables

**raw_meta**, **raw_shopify**, **raw_ga**, **raw_gads**:
- Store ingested data
- Include `ingested_at` timestamp
- Use replace mode by default (truncate and reload)

## Authentication Strategy

### Google Sheets Authentication

**Method**: Service Account with JSON credentials

**Not OAuth**: This system does not use OAuth with refresh tokens.

**Setup**:
1. Create Google Cloud project
2. Enable Google Sheets API
3. Create service account
4. Download JSON credentials to `backend/credentials.json`
5. Share sheet with service account email

**Rationale**:
- No user interaction required
- Suitable for automated systems
- Simpler than OAuth flow
- Credentials can be rotated

## Extensibility

### Adding New Sources (3 Steps)

1. **Define `SourceConfig`** in `source_config.py` (10-15 lines)
2. **Create model** in `models.py` (5-10 lines)
3. **Generate migration** with Alembic and apply

This is **low-code source onboarding**, not no-code. Requires:
- Python knowledge for model definition
- Understanding of database migrations
- Ability to restart backend service

### Modifying Transformations

Edit `TransformService` methods:
- `convert_excel_date()`: Date conversion logic
- `validate_columns()`: Validation rules
- `transform_data()`: Type coercion and mapping

### Changing Load Behavior

Modify `DataRepository.bulk_insert()`:
- Switch from replace to upsert
- Add deduplication logic
- Implement incremental loads

## Current Scope

### Implemented
✅ Config-driven source definitions  
✅ Generic ingestion engine  
✅ Replace mode (prevents duplicates)  
✅ Column validation (fail on missing, warn on unexpected)  
✅ Service account authentication  
✅ Comprehensive run tracking  
✅ Error isolation per source  
✅ Modular API routes  

### Not Implemented
❌ Authentication/Authorization  
❌ Scheduling (must be triggered manually)  
❌ Incremental loading  
❌ Retry logic  
❌ Data quality checks (beyond column validation)  
❌ Tests  
❌ Monitoring/Alerting  
❌ Upsert mode (structure exists, not tested)  

## Design Rationale

### Why Replace Mode is Default

**Problem**: Google Sheets contain current state, not incremental changes. Repeated runs with append mode would duplicate all data.

**Solution**: Replace mode truncates table before loading, ensuring no duplicates.

**Trade-off**: Full table reload each time (acceptable for < 100K rows).

**Alternative**: Upsert mode for large datasets (requires unique keys).

### Why Warn on Unexpected Columns (Not Fail)

**Problem**: Sheets often have helper columns, notes, or formatting columns that aren't needed for ingestion.

**Solution**: Log warning, ignore extra columns, continue ingestion.

**Trade-off**: Might miss actual data quality issues.

**Alternative**: Strict mode available (`strict_columns=True`) to fail on unexpected columns.

### Why Service Account (Not OAuth)

**Problem**: OAuth requires user interaction and token refresh.

**Solution**: Service account with JSON credentials requires no user interaction.

**Trade-off**: Credentials must be securely managed.

**Alternative**: OAuth for user-specific sheets (not implemented).

## Performance Considerations

### Current Limitations
- Single-threaded ingestion (sources processed sequentially)
- No connection pooling
- No caching
- Full table reload each time (replace mode)

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

## Next Steps for Production

1. Add authentication (JWT or OAuth)
2. Implement scheduling (APScheduler, cron, Airflow)
3. Add comprehensive tests
4. Implement monitoring (Prometheus, Grafana)
5. Add alerting (email, Slack)
6. Set up automated backups
7. Implement retry logic
8. Add data quality checks
9. Configure SSL/TLS
10. Implement rate limiting

## Summary

This is a **production-structured foundation** with:
- Clean architecture
- Config-driven design
- Replace mode to prevent duplicates
- Comprehensive tracking
- Error isolation

It is **not production-ready** without:
- Authentication
- Scheduling
- Tests
- Monitoring
- Additional security features
