@echo off
echo ========================================================
echo Generating Realistic Synthetic Fintech Data (SQLite)
echo ========================================================

cd /d "%~dp0"

if exist "C:\Users\Akash\anaconda3\python.exe" (
    "C:\Users\Akash\anaconda3\python.exe" data/generator.py
) else (
    python data/generator.py
)

echo.
echo Database seeded successfully!
pause
