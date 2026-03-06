@echo off
REM Freqtrade Runner Script (Batch file - no execution policy needed)
REM This script sets up the environment and runs freqtrade

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Add current directory to PYTHONPATH
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Disable aiodns to use system DNS resolver (fixes DNS issues on Windows)
REM This tells aiohttp to use system DNS instead of aiodns
set AIOHTTP_NO_EXTENSIONS=1

REM Force system DNS by importing patch before freqtrade
REM This forces aiohttp to use system DNS instead of aiodns
python -c "import sys; sys.path.insert(0, r'%CD%'); import force_system_dns" 2>nul

REM Run freqtrade with all passed arguments
python -m freqtrade %*
