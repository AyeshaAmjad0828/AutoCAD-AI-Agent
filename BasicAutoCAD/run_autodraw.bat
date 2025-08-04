@echo off
REM AutoDraw Script with Error Handling

REM Step 1: Check if user passed input
IF "%~1"=="" (
    echo [ERROR] No natural language input provided.
    echo Usage: run_autodraw.bat "Your natural language instruction"
    exit /b 1
)

REM Step 2: Run the Python script and capture the exit code
python cli_autodraw.py --natural "%~1"
SET "ERRORLEVEL=%ERRORLEVEL%"

REM Step 3: Check for errors
IF NOT "%ERRORLEVEL%"=="0" (
    echo.
    echo [ERROR] AutoDraw failed with exit code %ERRORLEVEL%
    echo Please check:
    echo - That AutoCAD is open and accessible
    echo - That your input is correctly formatted
    echo - That all required Python packages are installed
    exit /b %ERRORLEVEL%
)

REM Step 4: Success message
echo.
echo [✓] AutoDraw executed successfully.
exit /b 0
