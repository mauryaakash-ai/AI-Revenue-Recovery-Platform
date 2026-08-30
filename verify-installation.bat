@echo off
REM RevPilot Installation Verification Script
REM Run this batch file after installing all dependencies

setlocal enabledelayedexpansion
color 0A
title RevPilot - Installation Verification

cls
echo ========================================
echo    RevPilot Installation Verification
echo ========================================
echo.

REM Counter for checks
set /a passed=0
set /a total=0

REM Function to check command
:check_docker
set /a total+=1
echo [CHECK %total%] Docker Desktop...
docker --version >nul 2>&1
if !errorlevel! equ 0 (
    echo     [OK] Docker installed
    set /a passed+=1
) else (
    echo     [FAILED] Docker not found. Please install Docker Desktop.
    echo     Download: https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe
)
echo.

:check_docker_compose
set /a total+=1
echo [CHECK %total%] Docker Compose...
docker compose --version >nul 2>&1
if !errorlevel! equ 0 (
    echo     [OK] Docker Compose installed
    set /a passed+=1
) else (
    echo     [FAILED] Docker Compose not found. Reinstall Docker Desktop.
)
echo.

:check_node
set /a total+=1
echo [CHECK %total%] Node.js...
node --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('node --version') do (
        echo     [OK] Node.js %%i installed
    )
    set /a passed+=1
) else (
    echo     [FAILED] Node.js not found. Please install Node.js LTS.
    echo     Download: https://nodejs.org/en/download/
)
echo.

:check_npm
set /a total+=1
echo [CHECK %total%] npm...
npm --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('npm --version') do (
        echo     [OK] npm %%i installed
    )
    set /a passed+=1
) else (
    echo     [FAILED] npm not found. Reinstall Node.js LTS.
)
echo.

:check_psql
set /a total+=1
echo [CHECK %total%] PostgreSQL...
psql --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('psql --version') do (
        echo     [OK] %%i
    )
    set /a passed+=1
) else (
    echo     [FAILED] PostgreSQL not found. Please install PostgreSQL.
    echo     Download: https://www.postgresql.org/download/windows/
)
echo.

:check_python
set /a total+=1
echo [CHECK %total%] Python...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%i in ('python --version') do (
        echo     [OK] %%i
    )
    set /a passed+=1
) else (
    echo     [INFO] Python not found (optional for frontend-only dev)
)
echo.

:check_project_files
set /a total+=1
echo [CHECK %total%] Project Files...
if exist "backend" if exist "frontend" if exist "docker-compose.yml" (
    echo     [OK] All project files present
    set /a passed+=1
) else (
    echo     [WARNING] Project files may be incomplete
)
echo.

REM Summary
echo ========================================
echo           VERIFICATION SUMMARY
echo ========================================
echo Passed: %passed%/%total% checks
echo.

if %passed% equ %total% (
    color 0A
    echo [SUCCESS] All dependencies installed!
    echo.
    echo Next steps:
    echo   1. Open Command Prompt
    echo   2. Navigate to project: cd g:\project_Razorpay
    echo   3. Start services: docker compose up
    echo   4. In another terminal: python data/generator.py
    echo   5. Visit: http://localhost:3000
    echo.
) else (
    color 0C
    echo [INCOMPLETE] Some dependencies are missing.
    echo Please install the missing tools from the download links above.
    echo.
)

echo ========================================
pause
endlocal
