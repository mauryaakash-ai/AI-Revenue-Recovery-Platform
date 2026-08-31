@echo off
echo ========================================================
echo Starting Razorpay AI Revenue Recovery Backend (FastAPI)
echo Local Mode (No Docker)
echo ========================================================

cd /d "%~dp0backend"
set DATABASE_URL=sqlite:///./revenue_recovery.db
set ENVIRONMENT=development
set DEBUG=true

if exist "C:\Users\Akash\anaconda3\python.exe" (
    "C:\Users\Akash\anaconda3\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)
