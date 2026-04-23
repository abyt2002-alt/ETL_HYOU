# Data Ingestion Platform

A maintainable full-stack data ingestion platform that pulls data from Google Sheets and loads it into PostgreSQL.

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic
- **Design**: Config-driven, modular, extensible

## Local Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Google Service Account credentials

### Environment Setup

1. Copy environment files:
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

2. Update `.env` with your values:
   - `DATABASE_URL`: PostgreSQL connection string
   - `GOOGLE_SHEET_ID`: Your Google Sheet ID
   - `GOOGLE_CREDENTIALS_PATH`: Path to service account JSON

3. Place your Google Service Account credentials at `backend/credentials.json`

### Running with Docker

```bash
docker-compose up -d
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Running Locally (Development)

Backend:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

## Adding a New Source

1. Open `backend/app/source_config.py`
2. Add a new `SourceConfig` to the `SOURCES` list:

```python
SourceConfig(
    source_name="new_source",
    sheet_tab_name="NewTab",
    target_table_name="raw_new_source",
    required_columns=["Column1", "Column2"],
    optional_columns=[],
    field_types={
        "Column1": "string",
        "Column2": "integer"
    },
    date_fields=[],
    numeric_fields=[],
    load_mode="append"
)
```

3. Create the corresponding model in `backend/app/models.py`:

```python
class RawNewSource(Base):
    __tablename__ = "raw_new_source"
    
    id = Column(Integer, primary_key=True, index=True)
    column1 = Column(String(255))
    column2 = Column(Integer)
    ingested_at = Column(DateTime, default=datetime.utcnow)
```

4. Generate and apply migration:
```bash
alembic revision --autogenerate -m "add new_source table"
alembic upgrade head
```

That's it! The ingestion engine will automatically handle the new source.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API routes and schemas
│   │   ├── services/     # Business logic
│   │   ├── repositories/ # Data access layer
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   └── source_config.py  # Source definitions
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   └── pages/        # Page components
│   └── package.json
├── docs/                 # Documentation
└── docker-compose.yml
```
