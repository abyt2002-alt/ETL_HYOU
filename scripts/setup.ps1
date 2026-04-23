# Data Ingestion Platform Setup Script (PowerShell)

Write-Host "🚀 Setting up Data Ingestion Platform..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env with your Google Sheet ID and credentials path" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create frontend .env file if it doesn't exist
if (-not (Test-Path frontend/.env)) {
    Write-Host "📝 Creating frontend/.env file..." -ForegroundColor Yellow
    Copy-Item frontend/.env.example frontend/.env
    Write-Host "✅ Frontend .env created" -ForegroundColor Green
} else {
    Write-Host "✅ Frontend .env file already exists" -ForegroundColor Green
}

# Check for Google credentials
if (-not (Test-Path backend/credentials.json)) {
    Write-Host "⚠️  Warning: backend/credentials.json not found" -ForegroundColor Yellow
    Write-Host "   Please place your Google Service Account credentials at backend/credentials.json" -ForegroundColor Yellow
    Write-Host "   Press Enter to continue or Ctrl+C to exit..." -ForegroundColor Yellow
    Read-Host
}

# Start Docker containers
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Cyan
docker-compose up -d

# Wait for PostgreSQL to be ready
Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Run database migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
docker-compose exec -T backend alembic upgrade head

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173"
Write-Host "   Backend API: http://localhost:8000"
Write-Host "   API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f"
Write-Host ""
Write-Host "🛑 Stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down"
Write-Host ""
