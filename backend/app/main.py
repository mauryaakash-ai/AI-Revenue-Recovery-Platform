from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.config import get_settings

# Create all tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down RevPilot backend")


app = FastAPI(
    title="RevPilot API",
    description="AI Revenue Intelligence & Action Agent",
    version="0.1.0",
    lifespan=lifespan
)

settings = get_settings()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "revpilot-backend"}


@app.get("/api/v1/health")
async def api_health():
    return {
        "status": "healthy",
        "service": "revpilot-backend",
        "environment": settings.environment
    }


# Import routes after app creation to avoid circular imports
from app.routes import merchants, transactions, analytics, agent

app.include_router(merchants.router, prefix="/api/v1", tags=["merchants"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(agent.router, prefix="/api/v1", tags=["agent"])
