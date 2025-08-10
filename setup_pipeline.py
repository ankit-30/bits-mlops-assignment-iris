#!/usr/bin/env python3
"""
Setup and run the complete Iris MLOps pipeline
"""
import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the output"""
    logger.info(f"Starting: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        logger.info(f"Completed: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Iris MLOps Pipeline Setup")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    logger.info(f"Working directory: {project_dir}")
    
    # Create necessary directories
    directories = ['data', 'models', 'logs', 'mlruns']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Step 1: Process data
    logger.info("📊 Step 1: Processing data")
    if not run_command("python -m src.data.data_loader", "Data processing"):
        logger.error("Data processing failed")
        return False
    
    # Step 2: Train models
    logger.info("🤖 Step 2: Training models")
    if not run_command("python -m src.models.train", "Model training"):
        logger.error("Model training failed")
        return False
    
    # Step 3: Run tests
    logger.info("🧪 Step 3: Running tests")
    if not run_command("python -m pytest tests/ -v", "Running tests"):
        logger.warning("Some tests failed, but continuing...")
    
    # Step 4: Start API (in background for testing)
    logger.info("🌐 Step 4: Testing API")
    api_process = None
    try:
        # Start API in background
        api_process = subprocess.Popen([
            "python", "-m", "uvicorn", "src.api.main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for startup
        import time
        time.sleep(5)
        
        # Test API health
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API is running and healthy")
                
                # Test prediction endpoint
                test_data = {
                    "sepal_length": 5.1,
                    "sepal_width": 3.5,
                    "petal_length": 1.4,
                    "petal_width": 0.2
                }
                pred_response = requests.post("http://localhost:8000/predict", json=test_data, timeout=10)
                if pred_response.status_code == 200:
                    result = pred_response.json()
                    logger.info(f"✅ Test prediction successful: {result['prediction']} (confidence: {result['probability']:.3f})")
                else:
                    logger.warning("❌ Prediction endpoint test failed")
            else:
                logger.warning("❌ API health check failed")
        except requests.exceptions.RequestException as e:
            logger.warning(f"❌ API test failed: {e}")
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
    finally:
        if api_process:
            api_process.terminate()
            logger.info("API process terminated")
    
    logger.info("🎉 Pipeline setup completed!")
    logger.info("📋 Next steps:")
    logger.info("  1. Start MLflow: mlflow server --host 0.0.0.0 --port 5000")
    logger.info("  2. Start API: uvicorn src.api.main:app --reload")
    logger.info("  3. Build Docker: docker build -t iris-mlops .")
    logger.info("  4. Run deployment: ./deploy.ps1 (Windows) or ./deploy.sh (Linux/Mac)")

if __name__ == "__main__":
    main()
