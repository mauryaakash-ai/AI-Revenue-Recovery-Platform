# 🚀 START HERE - RevPilot Setup Guide

**Welcome to RevPilot! Follow this guide to get up and running in 45 minutes.**

---

## ⏱️ 5-Minute Quick Overview

RevPilot is an AI Revenue Intelligence platform. Here's what you need:

1. **Docker** - Runs everything in containers
2. **Node.js** - Runs the frontend (React + TypeScript + Tailwind)
3. **PostgreSQL** - Stores all data
4. **Tailwind** - Auto-installs via npm

**Total download**: ~750 MB  
**Total installation time**: 30-45 minutes  
**Total disk space**: 20 GB free

---

## 📥 Step-by-Step Installation

### Step 1: Install Docker Desktop (15 minutes)

**What**: Container platform that runs your entire app (database + backend + frontend)

**Download**: 
- Click: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- Or visit: https://www.docker.com/products/docker-desktop/

**Install**:
1. Run `Docker Desktop Installer.exe`
2. Choose **"Per-user installation"**
3. Choose **"Use WSL 2 backend"**
4. Click through and install
5. **RESTART YOUR COMPUTER**
6. Open Command Prompt and run:
   ```cmd
   docker --version
   ```
   Should show: `Docker version 27.x.x`

✅ **Status**: Docker is installed and running

---

### Step 2: Install Node.js LTS (10 minutes)

**What**: JavaScript runtime for the frontend (React + Tailwind)

**Download**: 
- Click: https://nodejs.org/en/download/
- Look for: **Windows 64-bit Installer** (v24.18.0 or latest LTS)

**Install**:
1. Run the `.msi` installer
2. Click **"Next"** through all screens
3. Make sure **"Add to PATH"** is checked ✓
4. Click **"Install"**
5. **Close and reopen Command Prompt** (important!)
6. Run:
   ```cmd
   node --version
   npm --version
   ```
   Should show: `v24.18.0` and `10.x.x`

✅ **Status**: Node.js is installed

---

### Step 3: Install PostgreSQL (15 minutes)

**What**: Database that stores all merchant data, transactions, customers

**Download**: 
- Click: https://www.postgresql.org/download/windows/
- Or: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
- Select: **PostgreSQL 16.x** (64-bit)

**Install**:
1. Run the installer
2. Follow the wizard:
   - Installation directory: `C:\Program Files\PostgreSQL\16` (default)
   - **Password**: `postgres` ⚠️ **IMPORTANT - remember this!**
   - Port: `5432` (keep default)
   - Locale: Default (keep default)
3. Click **"Next"** and wait for installation
4. Open Command Prompt and run:
   ```cmd
   psql --version
   ```
   Should show: `psql (PostgreSQL) 16.x`

✅ **Status**: PostgreSQL is installed

---

### Step 4: Install Tailwind CSS (Automatic) (1 minute)

**What**: CSS framework for styling the frontend

**This happens automatically!** When you run:
```cmd
cd g:\project_Razorpay\frontend
npm install
```

This will install:
- ✓ Next.js
- ✓ React  
- ✓ TypeScript
- ✓ **Tailwind CSS** 
- ✓ Other UI libraries

✅ **Status**: Will be installed in next step

---

## ✅ Verify Everything Is Installed

Open Command Prompt and run:

```cmd
docker --version
docker compose --version
node --version
npm --version
psql --version
```

All should show version numbers (no errors).

**Or use the automated verification script:**

```cmd
cd g:\project_Razorpay
verify-installation.bat
```

You should see: **[SUCCESS] All dependencies installed!**

---

## 🚀 Start RevPilot (Final Step)

### Terminal 1: Start Services

```cmd
cd g:\project_Razorpay
docker compose up
```

**Wait 30-60 seconds.** You should see:
```
postgres_1   | PostgreSQL is ready to accept connections
backend_1    | Uvicorn running on http://0.0.0.0:8000
frontend_1   | Local: http://localhost:3000
```

✅ All services are running!

### Terminal 2: Generate Synthetic Data

**Open a NEW Command Prompt** (keep the first one running):

```cmd
cd g:\project_Razorpay
python data/generator.py
```

**Wait 30 seconds.** You should see:
```
✓ Generated 1 merchants
✓ Generated 5000 customers
✓ Generated 50000 transactions
Synthetic dataset complete
```

✅ Data is generated!

---

## 🌐 Access Your Application

### Option 1: Frontend (The App)
📱 **http://localhost:3000**
- Dashboard with KPIs and metrics
- Chat with AI agent
- Audit log of all actions

### Option 2: API Documentation
📚 **http://localhost:8000/docs**
- Interactive Swagger API explorer
- Test all 16 endpoints
- See request/response examples

### Option 3: Database Manager (pgAdmin)
🗄️ **http://localhost:5050**
- Manage PostgreSQL databases
- Query the data
- View tables and relationships

---

## 🎯 What's Installed

### Backend (Python + FastAPI)
- ✅ Real-time anomaly detection
- ✅ Root cause analysis
- ✅ Financial impact calculation
- ✅ Recovery probability prediction
- ✅ 20+ action tools
- ✅ Approval gating for sensitive actions

### Frontend (React + Next.js)
- ✅ Dashboard (KPIs, revenue leaks, recommendations)
- ✅ Chat (AI agent Q&A with live streaming)
- ✅ Audit Log (action history and approval status)
- ✅ Responsive design (mobile + desktop)

### Database (PostgreSQL)
- ✅ 9 data models (Merchants, Customers, Transactions, etc.)
- ✅ 30+ strategic indexes for performance
- ✅ Synthetic test data with realistic anomalies

### ML Models
- ✅ Isolation Forest (anomaly detection)
- ✅ Logistic Regression (recovery probability)

---

## 🆘 Troubleshooting

### Docker won't start
```
Solution: Restart Docker Desktop
1. Open Docker Desktop from Start menu
2. Wait 2-3 minutes
3. Try again
```

### Port 5432 already in use
```
Solution: Stop PostgreSQL on host
1. Open Services (Ctrl+R > services.msc)
2. Find "postgresql-x64-16"
3. Right-click > Stop
```

### "npm: command not found"
```
Solution: Restart terminal
1. Close all Command Prompt windows
2. Open a new Command Prompt
3. Try npm again
```

### Can't connect to PostgreSQL
```
Solution: Start PostgreSQL service
1. Open Services (Ctrl+R > services.msc)
2. Find "postgresql-x64-16"
3. Right-click > Start
```

---

## 📚 Additional Documentation

For more details, read:

1. **WINDOWS_SETUP_GUIDE.md** - Detailed step-by-step setup
2. **QUICK_DOWNLOAD_LINKS.md** - All download links in one place
3. **DEPENDENCIES_SUMMARY.md** - Complete dependency reference
4. **README.md** - Full product overview
5. **QUICKSTART.md** - Quick reference commands

---

## ✨ Next Steps After Setup

### Run Tests
```cmd
cd backend
pytest tests/ -v
```
All 22 tests should pass ✅

### Explore the API
```
Visit: http://localhost:8000/docs
Try: GET /api/v1/merchants/
Try: POST /api/v1/merchants/{id}/agent/query
```

### Test the Chat
1. Go to http://localhost:3000
2. Click "Chat"
3. Type: "Why is revenue down?"
4. Watch the live investigation timeline

### View the Dashboard
1. Go to http://localhost:3000
2. Click "Dashboard"
3. See KPIs, revenue leaks, and recommendations

---

## 📋 Installation Checklist

- [ ] Downloaded Docker Desktop
- [ ] Installed Docker Desktop
- [ ] Restarted computer
- [ ] `docker --version` works
- [ ] Downloaded Node.js
- [ ] Installed Node.js
- [ ] Restarted Command Prompt
- [ ] `node --version` works
- [ ] Downloaded PostgreSQL
- [ ] Installed PostgreSQL
- [ ] Set password to `postgres`
- [ ] `psql --version` works
- [ ] Run `docker compose up` (all services running)
- [ ] Run `python data/generator.py` (data generated)
- [ ] Visit http://localhost:3000 (frontend loads)
- [ ] Visit http://localhost:8000/docs (API docs work)
- [ ] ✅ Everything working!

---

## ⏱️ Time Estimate

| Step | Time |
|------|------|
| Install Docker | 15 min |
| Install Node.js | 10 min |
| Install PostgreSQL | 15 min |
| Verify tools | 5 min |
| `docker compose up` | 2 min |
| Generate data | 1 min |
| **TOTAL** | **~45 min** |

---

## 🎓 Learning Resources

**Docker**: https://docs.docker.com/get-started/  
**Node.js**: https://nodejs.org/docs/  
**PostgreSQL**: https://www.postgresql.org/docs/  
**Next.js**: https://nextjs.org/docs/  
**FastAPI**: https://fastapi.tiangolo.com/  

---

## 🆘 Still Having Issues?

1. **Read**: WINDOWS_SETUP_GUIDE.md (Troubleshooting section)
2. **Check**: DEPENDENCIES_SUMMARY.md (Common Issues)
3. **Run**: verify-installation.bat or verify-installation.ps1
4. **Verify**: All commands in this guide work
5. **Ask**: Check the logs in terminal

---

## ✅ You're Done!

Once you see:
- ✅ Docker services running
- ✅ Data generated successfully
- ✅ Frontend loads at http://localhost:3000
- ✅ API docs at http://localhost:8000/docs

**You're ready to use RevPilot!**

---

## 🚀 What You Can Do Now

### Try This First
1. Go to Dashboard (http://localhost:3000)
2. View KPIs and revenue leaks
3. Click "Chat"
4. Ask: "Why did revenue drop yesterday?"
5. Watch the live investigation

### Then Explore
- **API**: Test endpoints at http://localhost:8000/docs
- **Database**: Manage data at http://localhost:5050
- **Code**: Review implementation in `backend/` and `frontend/`
- **Tests**: Run test suite with `pytest tests/ -v`

---

## 💡 Pro Tips

- Keep `docker compose up` running in one terminal
- Keep data generator output visible (errors are shown)
- Use `http://localhost:8000/docs` to test API before frontend
- Check browser console (F12) for frontend errors
- Use `docker compose logs -f servicename` to debug

---

## 🎉 Welcome to RevPilot!

You now have a complete AI revenue intelligence system running locally.

**Start exploring, testing, and building on top of it!**

---

**Questions?** Read the documentation files in the project root.  
**Ready?** Start with `docker compose up` 🚀

