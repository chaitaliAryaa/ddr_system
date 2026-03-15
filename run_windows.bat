@echo off
echo.
echo ============================================
echo  DDR Report Generator - Setup ^& Run
echo ============================================
echo.

REM Check if venv exists
IF NOT EXIST "venv" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    echo Done.
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate

echo [3/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo  Launching Streamlit App...
echo  Open: http://localhost:8501
echo ============================================
echo.
streamlit run app.py
