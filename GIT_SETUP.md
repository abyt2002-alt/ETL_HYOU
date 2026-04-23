# Git Repository Setup

## Repository Information
- **GitHub URL**: https://github.com/abyt2002-alt/ETL_HYOU.git
- **Branches**:
  - `ingestion` - Initial ingestion layer implementation
  - `preprocessing` - Preprocessing layer implementation (current)

## Branch Strategy
Development is organized by major modules:
- `ingestion` branch - Layer 1: Data ingestion from Excel to raw PostgreSQL tables
- `preprocessing` branch - Layer 2: Data preprocessing from raw to curated tables

All changes to the preprocessing layer should be committed to the `preprocessing` branch.

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
```

2. Choose the branch you want to work on:
```bash
# For ingestion layer
git checkout ingestion

# For preprocessing layer
git checkout preprocessing
```

3. Copy example environment files:
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

1. Ensure you're on the correct branch:
```bash
# For ingestion changes
git checkout ingestion

# For preprocessing changes
git checkout preprocessing
```

2. Make your changes

3. Stage and commit:
```bash
git add .
git commit -m "Description of changes"
```

4. Push to GitHub:
```bash
# Push ingestion changes
git push origin ingestion

# Push preprocessing changes
git push origin preprocessing
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
