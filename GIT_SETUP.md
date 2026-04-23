# Git Repository Setup

## Repository Information
- **GitHub URL**: https://github.com/abyt2002-alt/ETL_HYOU.git
- **Current Branch**: `ingestion`
- **Default Branch**: `ingestion` (no main branch yet)

## Branch Strategy
All development work is done on the `ingestion` branch. Any changes to the platform should be committed to this branch.

## Protected Files (Gitignored)
The following files are excluded from version control for security:

### Credentials & Environment
- `.env` - Environment variables (database credentials, API keys)
- `backend/credentials.json` - Google Service Account credentials
- `frontend/.env` - Frontend environment variables

### Data Files
- `backend/sample_data.xlsx` - Local Excel data file
- `syncwith_sample_data/` - Sample data directory

### Temporary Files
- `backend/check_*.py` - Temporary debugging scripts
- `__pycache__/` - Python bytecode
- `node_modules/` - Node.js dependencies

## Setup for New Developers

1. Clone the repository:
```bash
git clone https://github.com/abyt2002-alt/ETL_HYOU.git
cd ETL_HYOU
git checkout ingestion
```

2. Copy example environment files:
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

3. Add your credentials:
   - Edit `.env` with your database credentials
   - Place your Google Service Account JSON in `backend/credentials.json`
   - Place your Excel data file in `backend/sample_data.xlsx`

4. Start the services:
```bash
docker-compose up -d
```

## Making Changes

1. Ensure you're on the ingestion branch:
```bash
git checkout ingestion
```

2. Make your changes

3. Stage and commit:
```bash
git add .
git commit -m "Description of changes"
```

4. Push to GitHub:
```bash
git push origin ingestion
```

## Verifying Gitignore

To check if a file is ignored:
```bash
git check-ignore -v <filename>
```

To see what would be committed:
```bash
git status
```

## Important Notes

- Never commit `.env` files or `credentials.json` to the repository
- The `.gitignore` is configured to prevent accidental commits of sensitive data
- Always verify with `git status` before committing
- Sample data files should not be committed (use `.env.example` pattern instead)
