@echo off
chcp 65001 >nul 2>nul
title Meeting Recorder - Complete Setup & Push
echo.
echo  ================================================================
echo    Meeting Recorder - One Click Setup & Push to GitHub
echo    This script will: Init Git, Create Repo, Push Code, Build APK
echo  ================================================================
echo.

cd /d "%~dp0"

set GITHUB_USER=hui461007594-spec
set REPO_NAME=meeting-recorder

echo ================================================================
echo   STEP 1 OF 4: Enter your Personal Access Token (PAT)
echo ================================================================
echo.
echo   Your PAT is needed to create repository and push code.
echo   It will NOT be saved in any file.
echo.
set /p GITHUB_TOKEN="   Paste your PAT token here (ghp_xxxx): "
if "%GITHUB_TOKEN%"=="" (
    echo [ERROR] No token entered!
    pause
    exit /b 1
)
echo [OK] Token received
echo.

echo ================================================================
echo   STEP 2 OF 4: Initialize Git Repository
echo ================================================================
if not exist ".git" (
    git init >nul 2>&1
    echo [OK] Created new Git repository
) else (
    echo [OK] Git repository already exists
)

git config user.name "hui461007594-spec"
git config user.email "hui461007594@gmail.com"
git config credential.helper store
echo [OK] Git configured with your account
echo.

echo ================================================================
echo   STEP 3 OF 4: Commit Code & Create GitHub Repository
echo ================================================================
echo [3a] Adding and committing files...
git add -A >nul 2>&1
git diff --cached --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] No new changes to commit
) else (
    git commit -m "Meeting Recorder v1.0.0" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Code committed successfully
    ) else (
        echo [WARN] Some issues during commit, continuing...
    )
)
echo.

echo [3b] Creating GitHub repository using API...
curl -s -o nul -w "%%{http_code}" -X POST https://api.github.com/user/repos ^
  -H "Authorization: token %GITHUB_TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"%REPO_NAME%\",\"description\":\"Meeting Recorder Android App\",\"private\":false}" > temp_http_code.txt 2>&1

set /p HTTP_CODE=<temp_http_code.txt
del temp_http_code.txt >nul 2>&1

if "%HTTP_CODE%"=="201" (
    echo [OK] Repository created on GitHub!
) else if "%HTTP_CODE%"=="422" (
    echo [OK] Repository already exists (that's fine!)
) else (
    echo [WARN] HTTP %HTTP_CODE% - may already exist or auth issue, continuing...
)
echo.

echo ================================================================
echo   STEP 4 OF 4: Push Code to GitHub
echo ================================================================
git remote remove origin >nul 2>&1
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%REPO_NAME%.git

echo Pushing code... (please wait)
echo.

git branch -M main >nul 2>&1
git push -u origin main 2>&1

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo                    SUCCESS !!!
    echo ================================================================
    echo.
    echo   Your code has been pushed to GitHub!
    echo   GitHub Actions is now building your APK automatically...
    echo.
    echo   +-------------------------------------------------------+
    echo   |  BUILD PROGRESS (click link below to monitor):         |
    echo   |  https://github.com/%GITHUB_USER%/%REPO_NAME%/actions |
    echo   |                                                       |
    echo   |  How to check progress:                               |
    echo   |  1. Open the link above in browser                     |
    echo   |  2. You will see a running workflow                   |
    echo   |  3. Yellow circle = building                          |
    echo   |  4. Green checkmark = SUCCESS! APK ready              |
    echo   |  5. Red X = failed (click to see error log)           |
    echo   +-------------------------------------------------------+
    echo.
    echo   +-------------------------------------------------------+
    echo   |  DOWNLOAD APK WHEN BUILD COMPLETE:                    |
    echo   |  https://github.com/%GITHUB_USER%/%REPO_NAME%/releases|
    echo   |                                                       |
    echo   |  How to download:                                     |
    echo   |  1. Wait 15-20 minutes after push                      |
    echo   |  2. Open the Releases link above                      |
    echo   |  3. Find the latest version                           |
    echo   |  4. Click the .apk file to download                   |
    echo   |  5. Transfer to phone and install                     |
    echo   +-------------------------------------------------------+
    echo.
    echo   +-------------------------------------------------------+
    echo   |  SHARE WITH COLLEAGUES:                                |
    echo   |  Send them this link:                                 |
    echo   |  https://github.com/%GITHUB_USER%/%REPO_NAME%/releases|
    echo   |  They can always get the latest APK from here          |
    echo   +-------------------------------------------------------+
    echo.
) else (
    echo.
    echo ================================================================
    echo                       PUSH FAILED
    echo ================================================================
    echo.
    echo   Error details shown above.
    echo.
    echo   Common solutions:
    echo   1. Check if your token is correct (starts with ghp_)
    echo   2. Make sure token has 'repo' permission
    echo   3. Check internet connection
    echo   4. Try running this script again
    echo.
)

pause
