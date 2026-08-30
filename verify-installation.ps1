# RevPilot Installation Verification Script (PowerShell)
# Run: powershell -ExecutionPolicy Bypass -File verify-installation.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   RevPilot Installation Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$total = 0

# Helper function to check command
function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Check Docker
$total++
Write-Host "[CHECK $total] Docker Desktop..." -ForegroundColor Yellow
if (Test-Command docker) {
    $version = docker --version
    Write-Host "    [OK] $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [FAILED] Docker not found" -ForegroundColor Red
    Write-Host "    Download: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -ForegroundColor Gray
}
Write-Host ""

# Check Docker Compose
$total++
Write-Host "[CHECK $total] Docker Compose..." -ForegroundColor Yellow
if (Test-Command "docker" -and (docker compose version 2>$null)) {
    $version = docker compose version
    Write-Host "    [OK] $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [FAILED] Docker Compose not found" -ForegroundColor Red
}
Write-Host ""

# Check Node.js
$total++
Write-Host "[CHECK $total] Node.js..." -ForegroundColor Yellow
if (Test-Command node) {
    $version = node --version
    Write-Host "    [OK] Node.js $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [FAILED] Node.js not found" -ForegroundColor Red
    Write-Host "    Download: https://nodejs.org/en/download/" -ForegroundColor Gray
}
Write-Host ""

# Check npm
$total++
Write-Host "[CHECK $total] npm..." -ForegroundColor Yellow
if (Test-Command npm) {
    $version = npm --version
    Write-Host "    [OK] npm $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [FAILED] npm not found" -ForegroundColor Red
}
Write-Host ""

# Check PostgreSQL
$total++
Write-Host "[CHECK $total] PostgreSQL..." -ForegroundColor Yellow
if (Test-Command psql) {
    $version = psql --version
    Write-Host "    [OK] $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [FAILED] PostgreSQL not found" -ForegroundColor Red
    Write-Host "    Download: https://www.postgresql.org/download/windows/" -ForegroundColor Gray
}
Write-Host ""

# Check Python (optional)
$total++
Write-Host "[CHECK $total] Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $version = python --version
    Write-Host "    [OK] $version" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [INFO] Python not found (optional for frontend-only dev)" -ForegroundColor Cyan
}
Write-Host ""

# Check Project Files
$total++
Write-Host "[CHECK $total] Project Files..." -ForegroundColor Yellow
if ((Test-Path "backend") -and (Test-Path "frontend") -and (Test-Path "docker-compose.yml")) {
    Write-Host "    [OK] All project files present" -ForegroundColor Green
    $passed++
} else {
    Write-Host "    [WARNING] Project files may be incomplete" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "        VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $passed/$total checks" -ForegroundColor White
Write-Host ""

if ($passed -eq $total) {
    Write-Host "[SUCCESS] All dependencies installed!" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "  1. Open PowerShell or Command Prompt" -ForegroundColor White
    Write-Host "  2. Navigate to project: cd g:\project_Razorpay" -ForegroundColor White
    Write-Host "  3. Start services: docker compose up" -ForegroundColor White
    Write-Host "  4. In another terminal: python data/generator.py" -ForegroundColor White
    Write-Host "  5. Visit: http://localhost:3000" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[INCOMPLETE] Some dependencies are missing." -ForegroundColor Red
    Write-Host "Please install the missing tools from the download links above." -ForegroundColor Red
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
