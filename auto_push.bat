@echo off
chcp 65001 >nul 2>nul
title Auto Push to GitHub (Retry until success)
echo.
echo  ================================================================
echo    Auto Push - Will retry until successful!
echo  ================================================================
echo.

cd /d "%~dp0"

set MAX_RETRIES=10
set RETRY_COUNT=0

:RETRY_LOOP
set /a RETRY_COUNT+=1
echo [Attempt %RETRY_COUNT%/%MAX_RETRIES%] Trying to push...
echo.

git push -u origin main --force 2>&1

if %errorlevel% equ 0 (
    echo.
    echo  ================================================================
    echo                    PUSH SUCCESSFUL !!!
    echo  ================================================================
    echo.
    start "" "https://github.com/hui461007594-spec/meeting-recorder/actions"
    goto :END
)

if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo.
    echo [ERROR] Failed after %MAX_RETRIES% attempts. Check your network.
    goto :END
)

echo [WARNING] Push failed. Waiting 5 seconds before retry...
timeout /t 5 /nobreak >nul
goto :RETRY_LOOP

:END
pause
