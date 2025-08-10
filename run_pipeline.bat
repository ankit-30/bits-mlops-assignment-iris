@echo off
cd /d "%~dp0"

REM Clean up any existing processes on port 8000
echo Cleaning up port 8000...
netstat -ano | findstr :8000 > temp_ports.txt 2>nul
if exist temp_ports.txt (
    for /f "tokens=5" %%a in (temp_ports.txt) do taskkill /f /pid %%a >nul 2>&1
    del temp_ports.txt
)

echo ========================================
echo MLOps Pipeline - Iris Classification
echo Group 94 - BITS Pilani Assignment
echo ========================================
echo.

echo [STEP 1] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [STEP 2] Installing required packages (if needed)...
pip install --quiet --requirement requirements.txt
echo Dependencies ready.
echo.

echo [STEP 3] Processing Iris dataset...
echo - Loading iris.csv data
echo - Splitting into train/test sets
echo - Saving processed data to /data folder
python src/data/data_loader.py
if %errorlevel% neq 0 (
    echo ERROR: Data processing failed!
    pause
    exit /b 1
)
echo Data processing completed successfully.
echo.

echo [STEP 4] Training ML models with MLflow tracking...
echo - Training Logistic Regression model
echo - Training Random Forest model  
echo - Training SVM model
echo - Selecting best model automatically
echo - Registering best model in MLflow
python src/models/train.py
if %errorlevel% neq 0 (
    echo ERROR: Model training failed!
    pause
    exit /b 1
)
echo Model training completed. Best model registered.
echo.

echo [STEP 5] Running basic tests...
python -m pytest tests/ -v -x --tb=short
echo Tests completed (warnings are normal).
echo.

echo [STEP 6] Starting FastAPI server...
echo.
echo ================================================
echo SERVER STARTING - DO NOT CLOSE THIS WINDOW
echo ================================================
echo.
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo Metrics: http://localhost:8000/metrics
echo.
echo The browser will open automatically.
echo To test predictions, use the /docs interface.
echo.
echo PRESS CTRL+C TO STOP THE SERVER
echo ================================================
echo.

timeout /t 3 > nul
start "" http://localhost:8000/docs

echo Starting API server...
python .\start_api.py
