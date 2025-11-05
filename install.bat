# ==========================================
# install.bat (Windows Installation Script)
# ==========================================
@echo off
echo ========================================
echo Indian Record Book System - Installer
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b
)
echo ✓ Python found
echo.

echo [2/3] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b
)
echo ✓ Packages installed
echo.

echo [3/3] Starting application...
echo.
echo ========================================
echo Setup complete! Opening browser...
echo Access the app at: http://127.0.0.1:5000
echo.
echo First-time setup:
echo 1. Visit http://127.0.0.1:5000/setup-2fa
echo 2. Scan QR code with Google Authenticator
echo 3. Login with 6-digit code
echo ========================================
echo.

start http://127.0.0.1:5000/setup-2fa
python app.py

pause

