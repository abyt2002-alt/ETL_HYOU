from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import health_routes, source_routes, ingestion_routes, run_routes, data_routes
from app.database import engine, Base

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Data Ingestion Platform",
    description="Config-driven data ingestion from Google Sheets to PostgreSQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router, prefix="/api", tags=["health"])
app.include_router(source_routes.router, prefix="/api", tags=["sources"])
app.include_router(ingestion_routes.router, prefix="/api", tags=["ingestion"])
app.include_router(run_routes.router, prefix="/api", tags=["runs"])
app.include_router(data_routes.router, prefix="/api", tags=["data"])


@app.get("/")
def root():
    return {"message": "Data Ingestion Platform API", "version": "1.0.0"}
