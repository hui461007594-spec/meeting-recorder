@echo off
chcp 65001 >nul 2>nul
title Meeting Recorder - Push & Build APK
echo.
echo  ============================================
echo    Meeting Recorder - Push to GitHub
echo    Auto build APK after push!
echo  ============================================
echo.

cd /d "%~dp0"

set GITHUB_USER=hui461007594-spec

REM === Step 1: Initialize Git if needed ===
echo [Step 1/5] Checking Git repository...
if not exist ".git" (
    echo   No .git folder found, initializing...
    git init
    echo [OK] Repository initialized
) else (
    echo [OK] Repository exists
)
echo.

REM === Step 2: Configure Git ===
echo [Step 2/5] Configuring Git...
git config user.name "hui461007594-spec"
git config user.email "hui461007594@gmail.com"
git config credential.helper store
echo [OK] Git configured
echo.

REM === Step 3: Commit code ===
echo [Step 3/5] Committing code...
git add .
git diff --cached --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] No changes to commit
) else (
    git commit -m "Meeting Recorder v1.0.0"
    if %errorlevel% equ 0 (
        echo [OK] Code committed
    ) else (
        echo [WARN] Commit had issues, continuing...
    )
)
echo.

REM === Step 4: Setup remote ===
echo [Step 4/5] Setting up GitHub remote...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/%GITHUB_USER%/meeting-recorder.git
echo [OK] Remote: https://github.com/%GITHUB_USER%/meeting-recorder.git
echo.

REM === Step 5: Push ===
echo [Step 5/5] Pushing to GitHub...
echo.
echo ============================================
echo   CREDENTIALS NEEDED:
echo   Username: hui461007594-spec
echo   Password: (paste your PAT token here)
echo ============================================
echo.
pause

echo.
echo Pushing... (this may take a moment)
echo.

git branch -M main >nul 2>&1
git push -u origin main 2>&1

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   PUSH SUCCESSFUL!
    echo ============================================
    echo.
    echo   GitHub is now building your APK...
    echo   Expected time: 15-20 minutes
    echo.
    echo   MONITOR BUILD PROGRESS:
    echo   https://github.com/%GITHUB_USER%/meeting-recorder/actions
    echo.
    echo   DOWNLOAD APK WHEN READY:
    echo   https://github.com/%GITHUB_USER%/meeting-recorder/releases
    echo.
    echo ============================================
    echo   TIPS:
    echo   - Open the Actions link above to see progress
    echo   - When status shows green checkmark, APK is ready
    echo   - Then go to Releases page to download
    echo   - Share the Releases link with colleagues
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   PUSH FAILED
    echo ============================================
    echo.
    echo   Possible reasons:
    echo   1. Wrong username or token
    echo   2. Token expired or wrong permissions
    echo   3. Network issue
    echo.
    echo   Please check error messages above and retry.
)

echo.
pause
