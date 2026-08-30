# Windows Setup Guide: RevPilot Dependencies

**Complete installation guide for Docker, Node.js, PostgreSQL, and Tailwind**

---

## 📋 Prerequisites Check

Before starting, ensure you have:
- Windows 10/11 (64-bit)
- Administrator access
- ~20 GB free disk space
- Internet connection

---

## 1️⃣ Install Docker Desktop

Docker is required to run PostgreSQL, FastAPI backend, and Next.js frontend in containers.

### Download
**👉 [Docker Desktop for Windows (x86_64)](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)**

Or visit: https://www.docker.com/products/docker-desktop/

### Installation Steps

1. **Download** the installer (~500 MB)
2. **Run** `Docker Desktop Installer.exe`
3. **Follow** the installation wizard:
   - Choose **Per-user installation** (recommended)
   - Select **Use WSL 2 backend** (better performance)
   - Check **Add Docker to PATH**
4. **Restart** your computer when prompted
5. **Verify** installation:
   ```cmd
   docker --version
   docker compose --version
   ```
   Should output:
   ```
   Docker version 27.x.x
   Docker Compose version 2.x.x
   ```

### Post-Installation
- Docker Desktop will start automatically on boot
- If not running, search "Docker Desktop" in Start menu and click it
- Wait 2-3 minutes for Docker Engine to start before using it

---

## 2️⃣ Install Node.js (LTS)

Node.js is required for the frontend (Next.js, React, TypeScript, Tailwind).

### Download
**👉 [Node.js 24.18.0 LTS for Windows (x64)](://nodejs.org/enhttps/download/)**

Current LTS: **v24.18.0** (supports until April 2028)  
Alternative: **v22.x LTS** (if you prefer older version)

### Installation Steps

1. **Download** the `.msi` installer (~50 MB)
2. **Run** `node-v24.18.0-x64.msi`
3. **Follow** the installation wizard:
   - Click **Next** through all screens
   - Accept **License Agreement**
   - Choose **Install for all users** (or current user)
   - Select **Install npm package manager** ✓
   - Select **Add to PATH** ✓
4. **Click** **Install** and wait for completion
5. **Restart** your computer (or at least close/reopen terminal)
6. **Verify** installation (open new Command Prompt):
   ```cmd
   node --version
   npm --version
   ```
   Should output:
   ```
   v24.18.0
   10.x.x
   ```

---

## 3️⃣ Install PostgreSQL

PostgreSQL is the database engine for RevPilot.

### Download
**👉 [PostgreSQL 16.x Windows Installer (64-bit)](https://www.postgresql.org/download/windows/)**

Or direct download: **https://www.enterprisedb.com/downloads/postgres-postgresql-downloads** (EnterpriseDB)

### Installation Steps

1. **Download** the installer (~200 MB)
   - Look for latest version (16.x or 15.x)
   - Select **64-bit** version
2. **Run** the installer
3. **Follow** the setup wizard:

   **Step 1: Installation Directory**
   - Default: `C:\Program Files\PostgreSQL\16`
   - Click **Next**

   **Step 2: Select Components**
   - ✓ PostgreSQL Server
   - ✓ pgAdmin 4 (management tool)
   - ✓ Stack Builder (extensions)
   - ✓ Command Line Tools
   - Click **Next**

   **Step 3: Data Directory**
   - Default: `C:\Program Files\PostgreSQL\16\data`
   - Click **Next**

   **Step 4: PostgreSQL Password**
   - **Password**: `postgres` (or your choice, but remember it!)
   - **Confirm**: `postgres`
   - ⚠️ **Keep this safe — you'll need it for Docker**
   - Click **Next**

   **Step 5: Port**
   - Default: `5432`
   - ✓ Keep this unchanged
   - Click **Next**

   **Step 6: Locale**
   - Default: `[Default locale]`
   - Click **Next**

   **Step 7: Ready to Install**
   - Click **Next** to begin installation
   - Wait 2-3 minutes for completion

4. **Verify** installation:
   ```cmd
   psql --version
   ```
   Should output: `psql (PostgreSQL) 16.x`

5. **Test Connection**:
   ```cmd
   psql -U postgres -h localhost -c "SELECT 1"
   ```
   Should output: `1` (or similar result)

### Important Notes
- PostgreSQL installs as Windows Service (runs on boot)
- You can manage it via **Services** app (`services.msc`)
- pgAdmin 4 provides web UI (http://localhost:5050)

---

## 4️⃣ Install Tailwind CSS

Tailwind CSS is automatically installed when you run `npm install` in the frontend folder. **No separate installation needed!**

### How It Works

1. Navigate to frontend folder:
   ```cmd
   cd g:\project_Razorpay\frontend
   ```

2. Install all dependencies (including Tailwind):
   ```cmd
   npm install
   ```
   This will install:
   - Next.js
   - React
   - TypeScript
   - **Tailwind CSS** ✓
   - PostCSS
   - Autoprefixer
   - Other UI packages

3. Verify Tailwind is installed:
   ```cmd
   npm list tailwindcss
   ```
   Should output: `tailwindcss@3.4.19`

---

## 5️⃣ Verify All Installations

Run these commands to verify everything is installed correctly:

```cmd
# Check all tools
echo === Docker ===
docker --version

echo === Docker Compose ===
docker compose --version

echo === Node.js ===
node --version

echo === npm ===
npm --version

echo === PostgreSQL ===
psql --version

echo === All Good! ===
echo Proceeding to setup RevPilot...
```

Expected output:
```
=== Docker ===
Docker version 27.x.x

=== Docker Compose ===
Docker Compose version 2.x.x

=== Node.js ===
v24.18.0

=== npm ===
10.x.x

=== PostgreSQL ===
psql (PostgreSQL) 16.x

=== All Good! ===
Proceeding to setup RevPilot...
```

---

## 🚀 Next Steps: Set Up RevPilot

Once all dependencies are installed, follow these commands:

### Step 1: Navigate to Project
```cmd
cd g:\project_Razorpay
```

### Step 2: Configure Environment
```cmd
copy .env.example .env
```

Edit `.env` with your settings (optional — defaults work for local dev):
```
ENVIRONMENT=development
DATABASE_URL=postgresql://revpilot_user:revpilot_password@localhost:5432/revpilot
FRONTEND_URL=http://localhost:3000
```

### Step 3: Start All Services
```cmd
docker compose up
```

**Wait 30-60 seconds** for services to start. You should see:
```
postgres_1   | PostgreSQL is ready to accept connections
backend_1    | Uvicorn running on http://0.0.0.0:8000
frontend_1   | Local: http://localhost:3000
```

### Step 4: Generate Synthetic Data
In a **new terminal** (keep docker compose running):
```cmd
cd g:\project_Razorpay
python data/generator.py
```

Expected output:
```
✓ Generated 1 merchants
✓ Generated 5000 customers
✓ Generated 50000 transactions
✓ Synthetic dataset complete
```

### Step 5: Access Application
- **Frontend**: http://localhost:3000
  - Dashboard
  - Chat
  - Audit Log
  
- **API Docs**: http://localhost:8000/docs
  - Interactive Swagger documentation
  - Test all endpoints

- **pgAdmin**: http://localhost:5050
  - Database management
  - Default: admin@admin.com / admin

---

## 🆘 Troubleshooting

### Docker Issues

**"Docker daemon is not running"**
- Open Docker Desktop from Start menu
- Wait 2-3 minutes for it to start
- Try command again

**"Port 5432 already in use"**
- PostgreSQL might be running on host
- Stop host PostgreSQL: `sc stop postgresql-x64-16`
- Or change port in `docker-compose.yml`

**"WSL 2 backend not available"**
- Enable virtualization in BIOS
- Install WSL 2: `wsl --install`
- Restart computer
- Reinstall Docker

### Node.js Issues

**"npm command not found"**
- Restart terminal or computer
- Reinstall Node.js
- Ensure PATH includes Node.js directory

**"EACCES permission denied"**
- You may have permission issues
- Run Command Prompt as **Administrator**
- Or reinstall Node.js for all users

### PostgreSQL Issues

**"psql: could not connect to server"**
- PostgreSQL service might not be running
- Open `services.msc` and start `postgresql-x64-16`
- Or reinstall PostgreSQL

**"FATAL: password authentication failed"**
- You may have entered wrong password during install
- Uninstall PostgreSQL
- Reinstall with correct password: `postgres`
- Or reset password (advanced)

### Tailwind Issues

**"Tailwind CSS not compiling"**
- Run from `frontend/` folder:
  ```cmd
  npm install
  npm run dev
  ```
- Check `tailwind.config.js` exists
- Clear `.next` folder: `rmdir /s /q .next`

---

## 📦 Complete Dependency List

| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| **Docker Desktop** | Latest | Containerization | ✅ Install |
| **Docker Compose** | 2.x+ | Multi-container orchestration | ✅ Included with Docker |
| **Node.js** | 24.18.0 LTS | JavaScript runtime | ✅ Install |
| **npm** | 10.x+ | Package manager | ✅ Included with Node.js |
| **PostgreSQL** | 16.x | Database | ✅ Install |
| **Python** | 3.11+ | Backend runtime | ✅ Pre-installed on Windows |
| **Tailwind CSS** | 3.4.19 | CSS framework | ✅ Installed via npm |
| **Next.js** | 14.2.35 | Frontend framework | ✅ Installed via npm |
| **React** | 18.3.1 | UI library | ✅ Installed via npm |
| **TypeScript** | 5.9.3 | Type safety | ✅ Installed via npm |

---

## ⏱️ Installation Time Estimate

| Component | Time | Difficulty |
|-----------|------|-----------|
| Docker Desktop | 10-15 min | ⭐ Easy |
| Node.js | 5-10 min | ⭐ Easy |
| PostgreSQL | 10-15 min | ⭐ Easy |
| Tailwind (auto) | < 1 min | ⭐ Easy |
| Verify all | 5 min | ⭐ Easy |
| **Total** | **30-45 min** | ✅ |

---

## ✅ Installation Checklist

- [ ] Docker Desktop installed and running
- [ ] `docker --version` works
- [ ] Node.js 24.18.0 LTS installed
- [ ] `node --version` shows v24.18.0
- [ ] `npm --version` works
- [ ] PostgreSQL 16.x installed
- [ ] `psql --version` works
- [ ] PostgreSQL service running
- [ ] All downloads completed
- [ ] Antivirus/firewall allowing Docker
- [ ] WSL 2 enabled (for Docker)
- [ ] Enough disk space (~20 GB)
- [ ] Ready for `docker compose up`

---

## 🎯 What's Next

Once all installations are complete, run:

```cmd
cd g:\project_Razorpay
docker compose up
```

Then in another terminal:
```cmd
python data/generator.py
```

Then visit: **http://localhost:3000**

---

## 📞 Quick Reference

| Command | Purpose |
|---------|---------|
| `docker --version` | Check Docker version |
| `docker ps` | List running containers |
| `docker compose up` | Start all services |
| `docker compose down` | Stop all services |
| `node --version` | Check Node.js version |
| `npm list -g` | List global npm packages |
| `npm install` | Install frontend dependencies |
| `psql -U postgres` | Connect to PostgreSQL |
| `psql --version` | Check PostgreSQL version |

---

**Ready to install? Start with Docker Desktop, then Node.js, then PostgreSQL. Tailwind will install automatically via npm.**

**Estimated total time: 30-45 minutes**

