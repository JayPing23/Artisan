@echo off
echo ========================================
echo    Artisan AI Text-to-3D Generator
echo ========================================
echo.

echo [1/4] Stopping any existing containers...
docker-compose down

echo.
echo [2/4] Pulling latest images...
docker-compose pull

echo.
echo [3/4] Starting all services...
docker-compose up -d

echo.
echo [4/4] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo    Services Status
echo ========================================
docker-compose ps

echo.
echo ========================================
echo    Ready to Use!
echo ========================================
echo Web Interface: http://localhost:8000
echo.
echo To test the system:
echo   python debug_artisan.py
echo.
echo To view logs:
echo   docker-compose logs -f web
echo   docker-compose logs -f worker
echo.
echo To stop services:
echo   docker-compose down
echo.
pause 