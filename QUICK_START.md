# Quick Start Guide

Get the Data Ingestion Platform running in 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- Google Service Account with Sheets API enabled
- Your Google Sheet ID

## Setup Steps

### 1. Get Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create Service Account credentials
5. Download JSON key file
6. Share your Google Sheet with the service account email

### 2. Configure Environment

**On Linux/Mac**:
```bash
./scripts/setup.sh
```

**On Windows**:
```powershell
.\scripts\setup.ps1
```

Or manually:
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

### 3. Edit Configuration

Edit `.env`:
```env
GOOGLE_SHEET_ID=your_actual_sheet_id_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

### 4. Add Credentials

Place your Google Service Account JSON at:
```
backend/credentials.json
```

### 5. Start Services

```bash
docker-compose up -d
```

### 6. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 7. Access Application

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## First Run

1. Open http://localhost:5173
2. Click "Run All Sources" on the Dashboard
3. Watch the ingestion progress
4. View results in the Runs page
5. Preview data in the Sources page

## Verify Setup

Check backend health:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "service": "ingestion-platform"}
```

## Troubleshooting

### Docker not starting

```bash
docker-compose logs
```

### Backend can't connect to database

Wait 10 seconds for PostgreSQL to initialize, then:
```bash
docker-compose restart backend
```

### Can't read Google Sheet

1. Verify `GOOGLE_SHEET_ID` in `.env`
2. Check `credentials.json` exists at `backend/credentials.json`
3. Ensure sheet is shared with service account email
4. Check sheet tab names match config in `backend/app/source_config.py`

### Frontend can't connect to backend

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Ensure `VITE_API_URL` in `frontend/.env` is correct

## Next Steps

- Read [docs/README.md](docs/README.md) for detailed setup
- Review [docs/SYSTEM_FLOW.md](docs/SYSTEM_FLOW.md) to understand architecture
- See [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md) to add new sources
- Check [docs/API_SPEC.md](docs/API_SPEC.md) for API reference

## Common Commands

**View logs**:
```bash
docker-compose logs -f
```

**Stop services**:
```bash
docker-compose down
```

**Restart services**:
```bash
docker-compose restart
```

**Access database**:
```bash
docker-compose exec postgres psql -U postgres -d ingestion_db
```

**Run backend locally** (without Docker):
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Run frontend locally** (without Docker):
```bash
cd frontend
npm install
npm run dev
```

## Getting Help

1. Check logs: `docker-compose logs`
2. Review documentation in `docs/` folder
3. Verify environment variables in `.env`
4. Ensure all prerequisites are met
5. Check Google Sheet permissions

## What's Next?

Once running, you can:
- Add new data sources (see [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md))
- Customize transformations
- Add authentication
- Deploy to production (see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md))
