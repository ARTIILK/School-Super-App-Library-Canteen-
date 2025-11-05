# ==========================================
# install.sh (Linux/Mac Installation Script)
# ==========================================
#!/bin/bash

echo "========================================"
echo "Indian Record Book System - Installer"
echo "========================================"
echo ""

echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
python3 --version
echo "✓ Python found"
echo ""

echo "[2/3] Installing required packages..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi
echo "✓ Packages installed"
echo ""

echo "[3/3] Starting application..."
echo ""
echo "========================================"
echo "Setup complete! Opening browser..."
echo "Access the app at: http://127.0.0.1:5000"
echo ""
echo "First-time setup:"
echo "1. Visit http://127.0.0.1:5000/setup-2fa"
echo "2. Scan QR code with Google Authenticator"
echo "3. Login with 6-digit code"
echo "========================================"
echo ""

# Open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000/setup-2fa
elif command -v open &> /dev/null; then
    open http://127.0.0.1:5000/setup-2fa
fi

python3 app.py
