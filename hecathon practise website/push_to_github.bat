@echo off
echo ==========================================
echo    GeoWatch AI - GitHub Push Assistant
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/5] Checking Git installation...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/
    pause
    exit /b
)

if not exist ".git" (
    echo [2/5] Initializing Git repository...
    git init
) else (
    echo [2/5] Git repository already initialized.
)

echo [3/5] Staging files and creating commit...
git add .
git commit -m "Auto-push GeoWatch AI Dashboard"

echo [4/5] Configuring remote repository...
git remote add origin https://github.com/tejassheliya7-beep/geowatch.git 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Remote 'origin' already exists, updating URL...
    git remote set-url origin https://github.com/tejassheliya7-beep/geowatch.git
)

git branch -M main

echo [5/5] Pushing to GitHub (main branch)...
echo NOTE: You may be asked for your GitHub credentials in a popup window.
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Push failed. 
    echo This usually happens if the repository is not empty or requires authentication.
    echo If the repo is not empty, try 'git pull origin main --rebase' first.
    pause
) else (
    echo.
    echo [SUCCESS] Code successfully pushed to https://github.com/tejassheliya7-beep/geowatch.git
    pause
)
