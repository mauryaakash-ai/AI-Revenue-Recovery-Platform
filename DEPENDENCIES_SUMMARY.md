# RevPilot Dependencies Summary

**Complete guide to all required dependencies for Windows**

---

## 📊 Dependency Overview

| Dependency | Version | Size | Purpose | Priority |
|------------|---------|------|---------|----------|
| **Docker Desktop** | Latest | 500 MB | Run PostgreSQL, backend, frontend in containers | ⭐⭐⭐ Critical |
| **Docker Compose** | 2.x+ | Included | Orchestrate multi-container setup | ⭐⭐⭐ Critical |
| **PostgreSQL** | 16.x | 200 MB | Database engine | ⭐⭐⭐ Critical |
| **Node.js** | 24.18.0 LTS | 50 MB | JavaScript runtime for frontend | ⭐⭐⭐ Critical |
| **npm** | 10.x+ | Included | Node package manager | ⭐⭐⭐ Critical |
| **Python** | 3.11+ | 100 MB | Backend runtime (optional - comes with Docker) | ⭐⭐⭐ Critical |
| **Tailwind CSS** | 3.4.19 | Auto | CSS framework (installs via npm) | ⭐⭐ Important |
| **Next.js** | 14.2.35 | Auto | React framework (installs via npm) | ⭐⭐ Important |

---

## 🎯 Installation Steps

### Step 1: Docker Desktop (Critical)
**What it does**: Runs PostgreSQL, FastAPI backend, Next.js frontend in isolated containers

**Download**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

**Installation**:
```cmd
# 1. Run Docker Desktop Installer.exe
# 2. Choose "Per-user installation"
# 3. Select "Use WSL 2 backend"
# 4. Restart your computer
# 5. Verify:
docker --version
docker compose --version
```

**Post-install**:
- Docker Desktop starts automatically on boot
- Wait 2-3 minutes before using it
- Check system tray for Docker icon

---

### Step 2: Node.js LTS (Critical)
**What it does**: Runs the frontend (React, TypeScript, Tailwind)

**Download**: https://nodejs.org/en/download/ (select 64-bit Windows Installer)

**Installation**:
```cmd
# 1. Run node-v24.18.0-x64.msi
# 2. Click "Next" through wizard
# 3. Select "Install npm package manager"
# 4. Select "Add to PATH"
# 5. Click "Install"
# 6. Restart terminal
# 7. Verify:
node --version    # Should show v24.18.0
npm --version     # Should show 10.x.x
```

**Post-install**:
- Close and reopen Command Prompt or PowerShell
- Node.js will be available in new terminal windows

---

### Step 3: PostgreSQL (Critical)
**What it does**: Database engine for storing transactions, customers, anomalies

**Download**: https://www.postgresql.org/download/windows/

**Installation**:
```cmd
# 1. Download PostgreSQL 16.x (64-bit) installer
# 2. Run installer
# 3. Follow wizard:
#    - Installation directory: C:\Program Files\PostgreSQL\16
#    - Components: ✓ Server, ✓ pgAdmin, ✓ Stack Builder, ✓ Command Line Tools
#    - Password: postgres (IMPORTANT - remember this!)
#    - Port: 5432 (keep default)
#    - Locale: [Default locale]
# 4. Click "Next" to install
# 5. Verify:
psql --version    # Should show psql (PostgreSQL) 16.x
```

**Post-install**:
- PostgreSQL runs as Windows Service
- Auto-starts on boot
- Can manage via Services app (Ctrl+R → services.msc)

---

### Step 4: Tailwind CSS (Auto-installed)
**What it does**: CSS utility framework for styling

**Installation**:
```cmd
# 1. Navigate to frontend
cd g:\project_Razorpay\frontend

# 2. Install all frontend dependencies (includes Tailwind)
npm install

# This installs:
# - Next.js 14.2.35
# - React 18.3.1
# - TypeScript 5.9.3
# - Tailwind CSS 3.4.19 ✓
# - PostCSS, Autoprefixer, Recharts, etc.

# 3. Verify
npm list tailwindcss    # Should show tailwindcss@3.4.19
```

---

## ✅ Verification Checklist

After installing all tools, run this verification:

### Option 1: Batch Script (cmd.exe)
```cmd
cd g:\project_Razorpay
verify-installation.bat
```

### Option 2: PowerShell Script
```powershell
cd g:\project_Razorpay
powershell -ExecutionPolicy Bypass -File verify-installation.ps1
```

### Option 3: Manual Verification
```cmd
# Check all tools
echo === Checking all dependencies ===
docker --version
docker compose --version
node --version
npm --version
psql --version
python --version
echo === All checked ===
```

**Expected output**:
```
Docker version 27.x.x, build xxxxx
Docker Compose version 2.x.x
v24.18.0
10.x.x
psql (PostgreSQL) 16.x
Python 3.x.x
```

---

## 🚀 Start RevPilot (After Installation)

```cmd
# 1. Navigate to project
cd g:\project_Razorpay

# 2. Start all services (Docker, Database, Backend, Frontend)
docker compose up

# Wait 30-60 seconds for services to start...
# You should see:
#   postgres_1 | PostgreSQL is ready to accept connections
#   backend_1  | Uvicorn running on http://0.0.0.0:8000
#   frontend_1 | Local: http://localhost:3000
```

In a **new terminal** (keep docker compose running):
```cmd
# 3. Generate synthetic data
cd g:\project_Razorpay
python data/generator.py

# Wait for completion...
# Output should show:
#   ✓ Generated 1 merchants
#   ✓ Generated 5000 customers
#   ✓ Generated 50000 transactions
#   Synthetic dataset complete
```

Then open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Database UI**: http://localhost:5050 (pgAdmin)

---

## 📋 Dependency Tree

```
revpilot/
│
├── Backend (Python)
│   ├── FastAPI (web framework)
│   ├── SQLAlchemy (ORM)
│   ├── PostgreSQL driver
│   ├── pandas, numpy (data)
│   ├── scikit-learn (ML)
│   └── pytest (testing)
│
├── Frontend (Node.js/npm)
│   ├── Next.js (framework)
│   ├── React (UI)
│   ├── TypeScript (types)
│   ├── Tailwind CSS (styling)
│   ├── Recharts (charts)
│   └── Axios (HTTP)
│
├── Database
│   └── PostgreSQL (persistence)
│
└── Container Runtime
    ├── Docker (containerization)
    └── Docker Compose (orchestration)
```

---

## 🔧 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **Architecture** | 64-bit | 64-bit |
| **RAM** | 4 GB | 8 GB+ |
| **Disk** | 20 GB free | 30 GB free |
| **CPU Cores** | 2 | 4+ |
| **Network** | Internet (for downloads) | High-speed |
| **Virtualization** | Enabled (for Docker) | Enabled |

---

## 🆘 Common Issues & Solutions

### Docker Issues

**"Docker daemon is not running"**
```
Solution:
1. Open Docker Desktop from Start menu
2. Wait 2-3 minutes for it to fully start
3. Look for Docker icon in system tray
4. Try docker command again
```

**"Cannot connect to Docker daemon"**
```
Solution:
1. Make sure Docker Desktop is running
2. If WSL 2 not available, enable it:
   - Settings > Apps > Apps & features
   - Click "Optional features"
   - Add "Windows Subsystem for Linux"
   - Add "Virtual Machine Platform"
   - Restart computer
3. Reinstall Docker Desktop
```

**"Port 5432 already in use"**
```
Solution:
Option 1: Stop PostgreSQL on host
  sc stop postgresql-x64-16

Option 2: Change Docker port in docker-compose.yml
  postgres:
    ports:
      - "5433:5432"  # Use 5433 instead

Option 3: Use Docker version only (disable host PostgreSQL)
```

---

### Node.js Issues

**"npm: command not found"**
```
Solution:
1. Restart Command Prompt or PowerShell
2. If still missing, reinstall Node.js
3. During install, ensure "Add to PATH" is selected
4. Verify Node.js directory in PATH:
   echo %PATH%
```

**"npm install fails with permission denied"**
```
Solution:
1. Run Command Prompt as Administrator
2. Or delete node_modules and try again:
   rmdir /s /q node_modules
   npm install
```

---

### PostgreSQL Issues

**"psql: could not connect to server"**
```
Solution:
1. Check if PostgreSQL service is running:
   Services app (Ctrl+R > services.msc)
2. Find "postgresql-x64-16" and click "Start"
3. If service won't start, reinstall PostgreSQL
```

**"FATAL: password authentication failed"**
```
Solution:
You entered wrong password during install.
1. Uninstall PostgreSQL
2. Reinstall with password: postgres
3. If you remember password, connect with:
   psql -U postgres -h localhost
```

---

### Tailwind CSS Issues

**"Tailwind CSS not compiling"**
```
Solution:
1. Ensure in frontend directory: cd frontend
2. Run: npm install
3. Check tailwind.config.js exists
4. Clear Next.js cache: rmdir /s /q .next
5. Start development server: npm run dev
```

---

## 📦 Frontend Dependencies (Auto-installed)

When you run `npm install` in frontend:

```json
{
  "dependencies": {
    "next": "14.2.35",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "typescript": "5.9.3",
    "tailwindcss": "3.4.19",
    "postcss": "8.5.26",
    "autoprefixer": "10.5.4"
  },
  "optional": {
    "recharts": "2.15.4",
    "axios": "1.20.0",
    "@heroicons/react": "2.2.0"
  }
}
```

All 167 packages total (see package-lock.json)

---

## 📈 Installation Progress Tracker

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | Download Docker Desktop | 5 min | ⏳ |
| 2 | Install Docker Desktop | 10 min | ⏳ |
| 3 | Download Node.js | 2 min | ⏳ |
| 4 | Install Node.js | 5 min | ⏳ |
| 5 | Download PostgreSQL | 5 min | ⏳ |
| 6 | Install PostgreSQL | 10 min | ⏳ |
| 7 | Run npm install (Tailwind auto) | 3 min | ⏳ |
| 8 | Verify all tools | 5 min | ⏳ |
| **Total** | **All Dependencies** | **45 min** | ⏳ |

---

## 🎯 Next Steps After Installation

1. **Verify Installation**
   ```cmd
   cd g:\project_Razorpay
   verify-installation.bat
   ```

2. **Start Services**
   ```cmd
   docker compose up
   ```

3. **Generate Data**
   ```cmd
   python data/generator.py
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/docs
   - Database: http://localhost:5050

---

## 🔗 Quick Links

| Tool | Download | Documentation |
|------|----------|----------------|
| Docker | https://docker.com/download | https://docs.docker.com |
| Node.js | https://nodejs.org/download | https://nodejs.org/docs |
| PostgreSQL | https://postgresql.org/download | https://postgresql.org/docs |
| Tailwind | Via npm | https://tailwindcss.com |
| Next.js | Via npm | https://nextjs.org/docs |

---

## 💾 Disk Space Requirements

| Component | Size | Total |
|-----------|------|-------|
| Docker Desktop | 1.5 GB | |
| Docker images (Postgres, etc) | 5 GB | |
| Node.js + npm packages | 1 GB | |
| PostgreSQL | 1 GB | |
| Project code + data | 2 GB | |
| Free space needed | 5-10 GB | |
| **Total minimum** | **~20 GB** | ✓ |

---

## ✨ You're Ready!

Once all dependencies are installed:

```cmd
cd g:\project_Razorpay
docker compose up
```

Everything else is automated. Welcome to RevPilot! 🚀

