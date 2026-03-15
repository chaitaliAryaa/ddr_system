#!/bin/bash

echo ""
echo "============================================"
echo " DDR Report Generator - Setup & Run"
echo "============================================"
echo ""

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv venv
    echo "Done."
fi

echo "[2/3] Activating virtual environment..."
source venv/bin/activate

echo "[3/3] Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "============================================"
echo " Launching Streamlit App..."
echo " Open: http://localhost:8501"
echo "============================================"
echo ""
streamlit run app.py
