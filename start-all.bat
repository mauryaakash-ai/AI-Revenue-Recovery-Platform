@echo off
echo ========================================================
echo Starting Razorpay AI Revenue Recovery Platform
echo Local Execution (Zero Docker Dependencies)
echo ========================================================

start "Razorpay Recovery Backend (Port 8000)" cmd /k "%~dp0start-backend.bat"
start "Razorpay Recovery Frontend (Port 3000)" cmd /k "%~dp0start-frontend.bat"

echo.
echo Both servers are launching in separate windows:
echo - Backend API:  http://localhost:8000
echo - Swagger Docs: http://localhost:8000/docs
echo - Web Control:  http://localhost:3000
echo.

