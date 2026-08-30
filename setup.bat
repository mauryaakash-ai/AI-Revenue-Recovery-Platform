@echo off
setlocal enabledelayedexpansion

echo =========================================
echo RevPilot Setup
echo =========================================

REM Check if .env exists
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
) else (
    echo .env already exists, skipping
)

REM Start Docker Compose
echo.
echo Starting Docker Compose...
docker compose up -d

echo.
echo Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak

REM Create database tables
echo.
echo Creating database tables...
docker compose exec -T backend python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine); print('Tables created')"

REM Generate synthetic data
echo.
echo Generating synthetic data...
docker compose exec -T backend python /app/../data/generator.py

echo.
echo =========================================
echo + RevPilot is ready!
echo =========================================
echo.
echo Services:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Database:  localhost:5432
echo.
echo View logs:
echo   docker compose logs -f
echo.
