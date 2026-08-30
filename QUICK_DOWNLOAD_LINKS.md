# Quick Download Links

**Copy & paste these links directly into your browser**

---

## 🐳 Docker Desktop (500 MB)
**Windows 64-bit:**
```
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

**Or visit:** https://www.docker.com/products/docker-desktop/

---

## 📦 Node.js LTS (50 MB)
**Windows 64-bit Installer - Latest LTS:**
```
https://nodejs.org/en/download/
```

**Direct link (v24.18.0):**
```
https://nodejs.org/dist/v24.18.0/node-v24.18.0-x64.msi
```

---

## 🗄️ PostgreSQL (200 MB)
**Windows Installer - Latest Version:**
```
https://www.postgresql.org/download/windows/
```

**Or EnterpriseDB (easier installer):**
```
https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
```

**Look for:** PostgreSQL 16.x (64-bit)

---

## 🎨 Tailwind CSS
**Auto-installed when you run:**
```cmd
cd g:\project_Razorpay\frontend
npm install
```

---

## ⚡ Installation Sequence

### 1. Download & Install Docker Desktop
- Download: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- Run installer
- Restart computer
- Verify: `docker --version`

### 2. Download & Install Node.js
- Download: https://nodejs.org/en/download/
- Run installer
- Restart terminal
- Verify: `node --version` and `npm --version`

### 3. Download & Install PostgreSQL
- Download: https://www.postgresql.org/download/windows/
- Run installer
- Set password: `postgres`
- Keep port: `5432`
- Verify: `psql --version`

### 4. Tailwind Auto-Installs
```cmd
cd g:\project_Razorpay\frontend
npm install
```

---

## ✅ Quick Verification

```cmd
docker --version
docker compose --version
node --version
npm --version
psql --version
```

All should show version numbers (✓)

---

## 🚀 After Installation Complete

```cmd
cd g:\project_Razorpay
docker compose up
```

Then in another terminal:
```cmd
python data/generator.py
```

Visit: **http://localhost:3000**

---

## 📋 What You Need

- **Windows 10/11** (64-bit)
- **20 GB free space**
- **Administrator access**
- **Internet connection**
- **15-30 minutes**

---

## 💡 System Requirements

| Requirement | Value |
|-------------|-------|
| OS | Windows 10/11 (64-bit) |
| RAM | 4 GB minimum, 8 GB recommended |
| Disk | 20 GB free space |
| Processor | 2+ cores |
| Virtualization | Enabled in BIOS (for Docker) |

---

## 🆘 If Something Goes Wrong

1. **Docker won't start** → Enable WSL 2 in Windows Features
2. **Node not found** → Restart terminal after install
3. **Port 5432 in use** → PostgreSQL on host is running (disable if you want Docker version)
4. **npm install fails** → Run Command Prompt as Administrator

---

**Total Download Size: ~750 MB**  
**Total Installation Time: 30-45 minutes**

Go ahead and download these in order. I'll help you verify once installed!

