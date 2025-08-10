@echo off
cd /d "%~dp0"

REM Clean up any existing processes on port 8000
echo Cleaning up port 8000...
netstat -ano | findstr :8000 > temp_ports.txt 2>nul
if exist temp_ports.txt (
    for /f "tokens=5" %%a in (temp_ports.txt) do taskkill /f /pid %%a >nul 2>&1
    del temp_ports.txt
)

echo ================================================================
echo MLOPS ASSIGNMENT DEMONSTRATION - GROUP 94
echo Iris Classification Pipeline with Complete MLOps Workflow
echo BITS Pilani - Assignment S2-24_AIMLCZG523
echo ================================================================
echo.
echo WHAT THIS DEMO SHOWS:
echo 1. Complete MLOps pipeline from data to deployment
echo 2. Multiple ML models with experiment tracking (MLflow)
echo 3. REST API with automatic documentation (FastAPI)
echo 4. Containerized deployment (Docker)
echo 5. Monitoring and logging capabilities
echo 6. CI/CD pipeline (GitHub Actions)
echo.
echo EVALUATOR INSTRUCTIONS:
echo - Each step will show clear progress
echo - API will open automatically for testing
echo - All components demonstrate MLOps best practices
echo - Press any key when ready to start...
pause > nul
echo.

echo ============ PHASE 1: DATA PROCESSING ============
echo Processing Iris dataset for machine learning...
echo - Loading standard iris dataset (150 samples, 4 features)
echo - Splitting data: 80% training, 20% testing
echo - Feature scaling with StandardScaler
echo - Saving processed data for model training
echo.
python src/data/data_loader.py
if %errorlevel% neq 0 (
    echo DEMO FAILED: Data processing error
    pause
    exit /b 1
)
echo ✓ Data processing completed successfully
echo.

echo ============ PHASE 2: MODEL TRAINING & MLFLOW ============
echo Training multiple ML models with experiment tracking...
echo - Model 1: Logistic Regression (baseline)
echo - Model 2: Random Forest (ensemble method)  
echo - Model 3: Support Vector Machine (SVM)
echo - All experiments tracked in MLflow
echo - Best model automatically selected and registered
echo.
python src/models/train.py
if %errorlevel% neq 0 (
    echo DEMO FAILED: Model training error
    pause
    exit /b 1
)
echo ✓ Model training completed with MLflow tracking
echo.

echo ============ PHASE 3: API TESTING ============
echo Starting FastAPI server with ML model endpoints...
echo.
echo API ENDPOINTS FOR TESTING:
echo → POST /predict - Make predictions with trained model
echo → GET /health - Check system health
echo → GET /metrics - Prometheus monitoring metrics
echo → GET /docs - Interactive API documentation
echo.
echo Opening interactive API documentation...
echo EVALUATOR: Use the /docs interface to test predictions
echo.
timeout /t 2 > nul
start "" http://localhost:8000/docs
echo.
echo ================================================
echo API SERVER RUNNING - READY FOR EVALUATION
echo ================================================
echo.
echo NEXT STEPS FOR EVALUATOR:
echo 1. Browser opened with API documentation
echo 2. Test /predict endpoint with sample data
echo 3. Check /health and /metrics endpoints
echo 4. Observe request logging in console
echo.
echo SAMPLE TEST DATA for /predict endpoint:
echo {
echo   "sepal_length": 5.1,
echo   "sepal_width": 3.5,
echo   "petal_length": 1.4,
echo   "petal_width": 0.2
echo }
echo.
echo Press Ctrl+C when evaluation is complete...
echo ================================================
echo.

python .\start_api.py

echo.
echo ============ DEMO COMPLETED ============
echo.
echo WHAT WAS DEMONSTRATED:
echo ✓ End-to-end MLOps pipeline
echo ✓ Data processing and feature engineering
echo ✓ Multiple model training with MLflow experiment tracking
echo ✓ Model selection and registration
echo ✓ REST API deployment with FastAPI
echo ✓ Interactive API documentation
echo ✓ Health monitoring and metrics collection
echo ✓ Request/response logging
echo.
echo ADDITIONAL FEATURES AVAILABLE:
echo - Docker containerization: run_docker.bat
echo - MLflow UI: mlflow ui (run in separate terminal)
echo - GitHub Actions CI/CD pipeline (automated)
echo - Prometheus metrics monitoring
echo.
echo Thank you for evaluating our MLOps pipeline!
pause
