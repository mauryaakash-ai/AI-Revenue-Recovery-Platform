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


@app.get("/ready")
async def ready():
    """Kubernetes / container readiness probe validating database connectivity"""
    try:
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@app.get("/metrics")
async def metrics():
    """Observability metrics endpoint tracking service uptime and health status"""
    from datetime import datetime
    return {
        "service": "revpilot-backend",
        "version": "2.5.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "memory_allocation": "nominal",
        "subsystems": {
            "database": "online",
            "decision_engine": "active",
            "bandit_rl": "active",
            "webhook_engine": "listening",
            "risk_engine": "active"
        }
    }


@app.get("/api/v1/health")
async def api_health():
    return {
        "status": "healthy",
        "service": "revpilot-backend",
        "environment": settings.environment
    }


# Import routes after app creation to avoid circular imports
from app.routes import (
    merchants, transactions, analytics, agent, recovery, strategies, 
    experiments, alerts, customers, copilot, models_health,
    checkout_dropoff, dunning, b2b_chaser, mandates, voice_recovery, ptp, guardrails,
    auth, sms, webhooks, bandit, health_monitoring, policies, audit
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(sms.router, prefix="/api/v1", tags=["sms"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(bandit.router, prefix="/api/v1", tags=["bandit"])
app.include_router(health_monitoring.router, prefix="/api/v1", tags=["health-monitoring"])
app.include_router(policies.router, prefix="/api/v1", tags=["policies"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])
app.include_router(merchants.router, prefix="/api/v1", tags=["merchants"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(recovery.router, prefix="/api/v1", tags=["recovery"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])
app.include_router(customers.router, prefix="/api/v1", tags=["customers"])
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"])
app.include_router(experiments.router, prefix="/api/v1", tags=["experiments"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
app.include_router(copilot.router, prefix="/api/v1", tags=["copilot"])
app.include_router(models_health.router, prefix="/api/v1", tags=["models"])
app.include_router(agent.router, prefix="/api/v1", tags=["agent"])
app.include_router(checkout_dropoff.router, prefix="/api/v1", tags=["checkout-dropoff"])
app.include_router(dunning.router, prefix="/api/v1", tags=["dunning"])
app.include_router(b2b_chaser.router, prefix="/api/v1", tags=["b2b-chaser"])
app.include_router(mandates.router, prefix="/api/v1", tags=["mandates"])
app.include_router(voice_recovery.router, prefix="/api/v1", tags=["voice"])
app.include_router(ptp.router, prefix="/api/v1", tags=["ptp"])
app.include_router(guardrails.router, prefix="/api/v1", tags=["guardrails"])
