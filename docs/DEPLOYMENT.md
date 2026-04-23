# Deployment Guide

## Local Development

### Prerequisites

- Docker Desktop installed
- Google Service Account with Sheets API access
- Google Sheet ID

### Setup Steps

1. **Clone and configure**:
```bash
git clone <repository>
cd data-ingestion-platform
cp .env.example .env
cp frontend/.env.example frontend/.env
```

2. **Configure environment**:

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ingestion_db
GOOGLE_SHEET_ID=your_actual_sheet_id
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

3. **Add Google credentials**:

Place your service account JSON at `backend/credentials.json`

4. **Start services**:
```bash
docker-compose up -d
```

5. **Run migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

6. **Access application**:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

### Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_SHEET_ID`: Google Sheet identifier
- `GOOGLE_CREDENTIALS_PATH`: Path to credentials file
- `CORS_ORIGINS`: Comma-separated allowed origins
- `ENVIRONMENT`: Set to `production`

### Database Setup

1. Create PostgreSQL database
2. Set `DATABASE_URL` environment variable
3. Run migrations:
```bash
alembic upgrade head
```

### Backend Deployment

**Option 1: Docker**

```bash
docker build -t ingestion-backend ./backend
docker run -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e GOOGLE_SHEET_ID=$GOOGLE_SHEET_ID \
  -v /path/to/credentials.json:/app/credentials.json \
  ingestion-backend
```

**Option 2: Direct**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment

**Build**:
```bash
cd frontend
npm install
npm run build
```

**Serve**:
- Use nginx, Apache, or any static file server
- Point to `frontend/dist` directory
- Configure `VITE_API_URL` to backend URL

**Example nginx config**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/ingestion-frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Considerations

1. **Credentials**:
   - Never commit `credentials.json` to version control
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate credentials regularly

2. **Database**:
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access
   - Regular backups

3. **API**:
   - Configure CORS properly
   - Use HTTPS in production
   - Implement rate limiting
   - Add authentication if needed

4. **Environment**:
   - Set `ENVIRONMENT=production`
   - Disable debug mode
   - Use production-grade WSGI server (gunicorn)

### Monitoring

**Health Check**:
```bash
curl http://localhost:8000/api/health
```

**Database Connection**:
```bash
docker-compose exec postgres psql -U postgres -d ingestion_db -c "SELECT COUNT(*) FROM ingestion_runs;"
```

**Logs**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Backup Strategy

**Database Backup**:
```bash
pg_dump -h localhost -U postgres ingestion_db > backup_$(date +%Y%m%d).sql
```

**Restore**:
```bash
psql -h localhost -U postgres ingestion_db < backup_20240115.sql
```

### Scaling Considerations

**Backend**:
- Run multiple instances behind load balancer
- Use connection pooling for database
- Consider async workers for long-running ingestions

**Database**:
- Use read replicas for preview queries
- Partition large tables by date
- Archive old ingestion runs

**Frontend**:
- Use CDN for static assets
- Enable gzip compression
- Implement caching headers

### Troubleshooting

**Backend won't start**:
- Check database connectivity
- Verify credentials file exists
- Review environment variables

**Ingestion fails**:
- Verify Google Sheet permissions
- Check sheet tab names match config
- Review error messages in run details

**Frontend can't connect**:
- Verify `VITE_API_URL` is correct
- Check CORS configuration
- Ensure backend is running

**Database migration fails**:
- Check database permissions
- Review migration file
- Ensure no conflicting schema changes
