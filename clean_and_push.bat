@echo off
chcp 65001 >nul 2>nul
title Meeting Recorder - One Click Push & Build APK
echo.
echo  ================================================================
echo    Meeting Recorder - One Click Setup & Push to GitHub
echo    Auto build APK after push! Open HTML page for progress!
echo  ================================================================
echo.

cd /d "%~dp0"

set GITHUB_USER=hui461007594-spec
set REPO_NAME=meeting-recorder

echo [Step 1/3] Enter your Personal Access Token (PAT)
echo.
set /p GITHUB_TOKEN="   Paste your PAT token here (ghp_xxxx): "
if "%GITHUB_TOKEN%"=="" (
    echo [ERROR] No token entered!
    pause
    exit /b 1
)
echo [OK] Token received
echo.

echo [Step 2/3] Initialize Git and Commit...
if not exist ".git" (
    git init >nul 2>&1
)
git config user.name "hui461007594-spec"
git config user.email "hui461007594@gmail.com"
git add -A >nul 2>&1
git diff --cached --quiet >nul 2>&1
if %errorlevel% neq 0 (
    git commit -m "Meeting Recorder update %date:~0,4%%date:~5,2%%date:~8,2%-%time:~0,2%%time:~3,2%" >nul 2>&1
)
echo [OK] Git ready
echo.

echo [Step 3/3] Pushing to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%REPO_NAME%.git
git branch -M main >nul 2>&1
git push -u origin main --force 2>&1

if %errorlevel% equ 0 (
    echo.
    echo  ================================================================
    echo                    PUSH SUCCESSFUL !!!
    echo  ================================================================
    echo.
    echo   Opening progress page...
    start "" "%~dp0progress.html"
) else (
    echo.
    echo   [ERROR] Push failed. Check error above.
)

pause
