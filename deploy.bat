@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Deploying gorhino-fastapi to Azure...
echo ========================================
echo.

:: Generate timestamp tag (format: YYYYMMDDHHmm)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
set TAG=%dt:~0,12%
set IMAGE_BASE=gor20206acr.azurecr.io/gorhino-fastapi
set APP_NAME=gor26-Q
set RESOURCE_GROUP=DEVOPS

echo Tag: %TAG%
echo.

echo [1/4] Building Docker image...
docker build -t %IMAGE_BASE%:%TAG% -t %IMAGE_BASE%:latest .
if %errorlevel% neq 0 ( echo ERROR: Docker build failed & pause & exit /b 1 )

echo.
echo [2/4] Pushing image to ACR...
docker push %IMAGE_BASE%:%TAG%
if %errorlevel% neq 0 ( echo ERROR: Docker push failed & pause & exit /b 1 )
docker push %IMAGE_BASE%:latest
if %errorlevel% neq 0 ( echo ERROR: Docker push latest failed & pause & exit /b 1 )

echo.
echo [3/4] Updating Azure Web App to tag: %TAG%...
az webapp config container set --name %APP_NAME% --resource-group %RESOURCE_GROUP% --container-image-name %IMAGE_BASE%:%TAG%
if %errorlevel% neq 0 ( echo ERROR: Container config failed & pause & exit /b 1 )

echo.
echo [4/4] Waiting for Azure Web App to pull new image...
timeout /t 15 /nobreak > nul
az webapp show --name %APP_NAME% --resource-group %RESOURCE_GROUP% --query "state" -o tsv
if %errorlevel% neq 0 ( echo ERROR: Could not check app state & pause & exit /b 1 )

echo.
echo ========================================
echo  Deploy complete! Tag: %TAG%
echo  NOTE: Azure may take 1-2 min to fully swap containers.
echo ========================================
echo.
pause