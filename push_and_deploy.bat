@echo off
title Zenelait Infotech Billing System - Push and Deploy Utility
color 0A
cls

echo =========================================================================
echo             ZENELAIT INFOTECH - PUSH AND DEPLOY COMMAND HUB
echo =========================================================================
echo.
echo  This utility will help you push your error-free, responsive project
echo  to GitHub and deploy it live permanently on Firebase Hosting!
echo.
echo  Your GitHub:   https://github.com/Annamalai2382
echo  Firebase ID:   billing-system-d9295 (Live Web URL: https://billing-system-d9295.web.app)
echo.
echo =========================================================================
echo  Please select an operation:
echo =========================================================================
echo  [1] Link and Push Project to GitHub (https://github.com/Annamalai2382)
echo  [2] Deploy Application Live to Firebase Hosting
echo  [3] Execute Both (Full Publish and Sync)
echo  [4] Run Local Django Verification Check
echo  [5] Exit
echo =========================================================================
set /p opt="Enter your choice (1-5): "

if "%opt%"=="1" goto push_git
if "%opt%"=="2" goto deploy_firebase
if "%opt%"=="3" goto run_both
if "%opt%"=="4" goto verify_local
if "%opt%"=="5" goto end
goto invalid

:push_git
cls
echo =========================================================================
echo  STEP 1: PUSHING TO GITHUB
echo =========================================================================
echo.
echo  Linking remote repository to:
echo  https://github.com/Annamalai2382/Billing-system.git
echo.
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Annamalai2382/Billing-system.git
git branch -M main

echo.
echo  IMPORTANT: Ensure you have created a public repository named "Billing-system"
echo  on your GitHub account (https://github.com/new) before proceeding.
echo.
pause
echo.
echo  Pushing main branch...
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Git push failed. Please ensure you are logged in to Git or have
    echo  configured your personal access tokens / SSH keys.
) else (
    echo.
    echo  [SUCCESS] Code successfully pushed to https://github.com/Annamalai2382/Billing-system!
)
echo.
pause
goto end

:deploy_firebase
cls
echo =========================================================================
echo  STEP 2: DEPLOYING LIVE TO FIREBASE
echo =========================================================================
echo.
echo  Collecting static assets for production...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo [ERROR] Static collection failed. Ensure Python and dependencies are active.
    pause
    goto end
)
echo.
echo  Deploying functions and hosting to Firebase Project "billing-system-d9295"...
firebase deploy
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Firebase deployment failed. Make sure you are logged in.
    echo  Try running 'firebase login' in your command prompt first.
) else (
    echo.
    echo  [SUCCESS] Application is now live permanently!
    echo  Visit your website: https://billing-system-d9295.web.app
)
echo.
pause
goto end

:run_both
cls
echo =========================================================================
echo  STEP 3: EXECUTING FULL DEPLOYMENT HUB
echo =========================================================================
echo.
echo  1. Connecting to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/Annamalai2382/Billing-system.git
git branch -M main
echo  Ensure repository is created on https://github.com/new
pause
git push -u origin main

echo.
echo  2. Collecting Static Files...
python manage.py collectstatic --noinput

echo.
echo  3. Deploying Live to Firebase...
firebase deploy
echo.
echo  Done!
pause
goto end

:verify_local
cls
echo =========================================================================
echo  STEP 4: RUN LOCAL VERIFICATION CHECK
echo =========================================================================
echo.
echo  Running Django system verification checks...
python manage.py check
if %errorlevel% eq 0 (
    echo.
    echo  [SUCCESS] Local checks passed! No system errors detected.
) else (
    echo.
    echo  [WARNING] Checks found some warnings or issues. Inspect output above.
)
echo.
pause
goto end

:invalid
echo Invalid option selected.
pause
goto end

:end
echo =========================================================================
echo  Thank you for using Zenelait Infotech Deploy Tools. Have a great day!
echo =========================================================================
pause
