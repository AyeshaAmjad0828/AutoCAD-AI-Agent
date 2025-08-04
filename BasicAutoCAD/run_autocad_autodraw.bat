@echo off
REM AutoDraw CLI Launcher with Natural Language Input

REM Step 1: Install Python dependencies
IF EXIST requirements.txt (
    echo Installing Python requirements...
    pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo Failed to install requirements. Aborting.
        exit /b 1
    )
)

REM Step 2: Check if user provided arguments
IF "%~1"=="" (
    echo [!] Please provide a natural language drawing instruction.
    echo Example:
    echo     run_autocad_autodraw.bat "Draw a 10-foot linear light..."
    exit /b 1
)

REM Step 3: Combine ALL args into a single string
SETLOCAL ENABLEDELAYEDEXPANSION
SET NL_INPUT=
:loop
IF "%~1"=="" GOTO done
SET NL_INPUT=!NL_INPUT! %~1
SHIFT
GOTO loop
:done

REM Step 4: Call the Python script with --natural and the full quoted input
echo Running AutoDraw...
python cli_autodraw.py --natural "!NL_INPUT!" --verbose

REM Step 5: Done
echo.
echo [✓] AutoDraw execution finished.
pause
