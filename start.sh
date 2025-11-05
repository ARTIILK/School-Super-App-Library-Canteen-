# ==========================================
# start.sh (Linux/Mac Quick Start)
# ==========================================
#!/bin/bash
echo "Starting Record Book System..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000
elif command -v open &> /dev/null; then
    open http://127.0.0.1:5000
fi
python3 app.py
