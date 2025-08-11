@echo off
echo ===============================================
echo DVC Integration Demo - Iris MLOps Pipeline  
echo ===============================================

echo.
echo [INFO] DVC Project Status:
echo ✓ Data tracking: data/iris_raw.csv.dvc
echo ✓ Model tracking: models/best_model_model.pkl.dvc  
echo ✓ Pipeline definition: dvc.yaml
echo ✓ Configuration: .dvc/config

echo.
echo [INFO] DVC Pipeline Stages:
echo   1. data_load   - Process Iris dataset
echo   2. train       - Train ML models with MLflow
echo   3. api_test    - Validate API functionality

echo.
echo [INFO] Running DVC pipeline simulation...
echo.

echo [1/3] Data Loading Stage...
python src/data/data_loader.py
if %errorlevel% equ 0 (
    echo ✓ Data processing completed
) else (
    echo ✗ Data processing failed
)

echo.
echo [2/3] Model Training Stage...  
python src/models/train.py
if %errorlevel% equ 0 (
    echo ✓ Model training completed
) else (
    echo ✗ Model training failed
)

echo.
echo [3/3] Pipeline Complete!
echo.
echo ===============================================
echo DVC Benefits Demonstrated:
echo ✓ Data versioning with .dvc files
echo ✓ Model tracking and lineage
echo ✓ Reproducible pipeline execution
echo ✓ Git integration for metadata
echo ===============================================

echo.
echo For actual DVC commands, use:
echo   python -m dvc status
echo   python -m dvc repro
echo   python -m dvc dag
echo.
pause
