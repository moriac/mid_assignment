@echo off
REM Quick setup script for ChromaDB environment on Windows

echo ============================================================
echo ChromaDB Quick Setup for Windows
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

echo Installing dependencies...
python setup_chromadb_env.py
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Make sure you have .env file with OPENAI_API_KEY
echo   2. Run: python chromadb_chunk_pdf.py
echo   3. Then: python test_chromadb_retrieval.py
echo.
echo Virtual environment is now active. Type 'deactivate' to exit.
echo.

cmd /k
