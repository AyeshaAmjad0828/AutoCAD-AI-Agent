@echo off
setlocal

REM Check if a natural language input was provided
if "%~1"=="" (
    echo Usage: run_autodraw.bat "Your natural language instruction"
    exit /b 1
)

REM Extract the input
set "input=%~1"

REM Echo input for confirmation
echo Running AutoDraw with input: "%input%"

REM Run the Python script and capture the exit code
python cli_autodraw.py --natural "%input%"
set "exitCode=%ERRORLEVEL%"

REM Check for errors
if not "%exitCode%"=="0" (
    echo.
    echo [ERROR] AutoDraw failed with exit code %exitCode%
    echo Please check:
    echo - That AutoCAD is open and accessible
    echo - That your input is correctly formatted
    echo - That all required Python packages are installed
    exit /b %exitCode%
)

REM Success message
echo.
echo [✓] AutoDraw executed successfully.
exit /b 0

endlocal
