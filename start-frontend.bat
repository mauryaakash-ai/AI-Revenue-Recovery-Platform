@echo off
echo ========================================================
echo Starting Razorpay AI Revenue Recovery Frontend (Next.js)
echo Local Mode (No Docker)
echo ========================================================

cd /d "%~dp0frontend"
set NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev

