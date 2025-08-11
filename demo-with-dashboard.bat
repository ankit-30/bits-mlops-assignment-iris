@echo off
echo ============================================
echo    Iris MLOps Pipeline with Dashboard Demo
echo ============================================
echo.

echo Starting complete MLOps pipeline with monitoring dashboard...
echo.

echo [1/6] Starting Docker services (API + MLflow + Prometheus + Grafana)...
docker-compose up -d

echo.
echo [2/6] Waiting for services to start...
timeout /t 30 /nobreak > nul

echo.
echo [3/6] Running data processing...
python src/data/data_loader.py

echo.
echo [4/6] Training models with MLflow tracking...
python src/models/train.py

echo.
echo [5/6] Testing API with sample predictions...
curl -X POST "http://localhost:8000/predict" ^
     -H "Content-Type: application/json" ^
     -d "{\"sepal_length\": 5.1, \"sepal_width\": 3.5, \"petal_length\": 1.4, \"petal_width\": 0.2}"

echo.
echo.
echo [6/6] Opening monitoring interfaces...
start http://localhost:8000/docs
start http://localhost:5000
start http://localhost:3000
start http://localhost:9090

echo.
echo ============================================
echo    Demo Complete! Services Running:
echo ============================================
echo FastAPI Documentation: http://localhost:8000/docs
echo MLflow Tracking UI:    http://localhost:5000
echo Grafana Dashboard:     http://localhost:3000 (admin/admin123)
echo Prometheus Metrics:    http://localhost:9090
echo API Health Check:      http://localhost:8000/health
echo Prometheus Metrics:    http://localhost:8000/metrics
echo.
echo ============================================
echo    Grafana Setup Instructions:
echo ============================================
echo 1. Go to http://localhost:3000
echo 2. Login with admin/admin123
echo 3. The Iris MLOps Dashboard should be auto-configured
echo 4. Make some API calls to see metrics populate
echo.
echo To stop all services: docker-compose down
echo ============================================
pause
