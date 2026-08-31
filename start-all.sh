#!/bin/bash
echo "========================================================"
echo "Starting Razorpay AI Revenue Recovery Platform (Local)"
echo "Zero Docker Dependency"
echo "========================================================"

# Check if SQLite DB exists, else generate
if [ ! -f "backend/revenue_recovery.db" ] && [ ! -f "revenue_recovery.db" ]; then
    echo "Seeding synthetic dataset..."
    python3 data/generator.py
fi

# Start backend in background
cd backend
export DATABASE_URL="sqlite:///./revenue_recovery.db"
export ENVIRONMENT="development"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
export NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend running on http://localhost:8000 (PID $BACKEND_PID)"
echo "Frontend running on http://localhost:3000 (PID $FRONTEND_PID)"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait

