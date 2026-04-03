@echo off
echo.
echo ========================================
echo  Deploying gorhino-fastapi to Azure...
echo ========================================
echo.

echo [1/3] Building Docker image...
docker build -t gor20206acr.azurecr.io/gorhino-fastapi:latest .
if %errorlevel% neq 0 ( echo ERROR: Docker build failed & pause & exit /b 1 )

echo.
echo [2/3] Pushing image to ACR...
docker push gor20206acr.azurecr.io/gorhino-fastapi:latest
if %errorlevel% neq 0 ( echo ERROR: Docker push failed & pause & exit /b 1 )

echo.
echo [3/3] Updating Azure Web App container config...
az webapp config container set --name gor26-Q --resource-group DEVOPS --container-image-name gor20206acr.azurecr.io/gorhino-fastapi:latest
if %errorlevel% neq 0 ( echo ERROR: Container config failed & pause & exit /b 1 )

echo.
echo [4/4] Restarting Azure Web App...
az webapp restart --name gor26-Q --resource-group DEVOPS
if %errorlevel% neq 0 ( echo ERROR: Web App restart failed & pause & exit /b 1 )

echo.
echo ========================================
echo  Deploy complete!
echo ========================================
echo.
pause