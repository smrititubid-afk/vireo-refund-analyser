@echo off
setlocal

set PYTHON=python
set STREAMLIT=python -m streamlit
set PYTHONIOENCODING=utf-8

echo ============================================
echo  Vireo Audio Refund Analyser
echo ============================================
echo.

echo Step 1: Installing dependencies...
%PYTHON% -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo Dependencies OK.
echo.

echo Step 2: Running analysis pipeline...
%PYTHON% analyse.py
if errorlevel 1 (
    echo ERROR: Analysis pipeline failed. See error above.
    pause
    exit /b 1
)
echo.

echo Step 3: Generating memo for Arjun Mehta...
%PYTHON% generate_memo.py
echo.

echo Step 4: Launching dashboard...
echo Open http://localhost:8501 in your browser.
echo Press Ctrl+C to stop the dashboard.
echo.
%STREAMLIT% run app.py

endlocal
