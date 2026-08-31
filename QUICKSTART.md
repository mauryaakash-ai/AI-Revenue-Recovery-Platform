# Razorpay AI Revenue Recovery Platform — Quickstart Guide

> **Zero Docker Dependency — Direct Local Machine Execution**

---

## ⚡ 1-Minute Quick Start

### Windows
Double-click:
```cmd
start-all.bat
```

### macOS / Linux / WSL
```bash
chmod +x start-all.sh
./start-all.sh
```

---

## 🌐 Live URLs

- **Web Control Center**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🛠 Manual Step-by-Step

### 1. Re-Seed Synthetic Dataset (3,000+ Records)
```cmd
seed-data.bat
```
*Or via command line:*
```bash
python data/generator.py
```

### 2. Run Backend
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run Frontend
```bash
cd frontend
npm run dev
```

### 4. Run Automated Test Suite
```bash
cd backend
pytest tests/ -v
```
*(All 24 unit & scenario tests pass with 0 errors)*
