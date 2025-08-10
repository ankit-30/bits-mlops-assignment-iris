"""
FastAPI application for Iris classification
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import logging
import os
from datetime import datetime
import json
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import sqlite3
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Prometheus metrics
prediction_counter = Counter('iris_predictions_total', 'Total number of predictions made')
prediction_histogram = Histogram('iris_prediction_duration_seconds', 'Time spent on predictions')

app = FastAPI(
    title="Iris Classification API",
    description="A machine learning API for classifying Iris flowers",
    version="1.0.0"
)

# Pydantic models for request/response validation
class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., ge=0, le=10, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, le=10, description="Sepal width in cm") 
    petal_length: float = Field(..., ge=0, le=10, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, le=10, description="Petal width in cm")
    
    class Config:
        schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }

class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    all_probabilities: dict
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    model_loaded: bool

# Global variables
model = None
scaler = None
target_names = ['setosa', 'versicolor', 'virginica']

def init_database():
    """Initialize SQLite database for logging predictions"""
    conn = sqlite3.connect('logs/predictions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sepal_length REAL,
            sepal_width REAL,
            petal_length REAL,
            petal_width REAL,
            prediction TEXT,
            probability REAL,
            all_probabilities TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_model_and_scaler():
    """Load the trained model and scaler"""
    global model, scaler
    
    try:
        model_path = "models/best_model_model.pkl"
        scaler_path = "data/scaler.pkl"
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            logger.info("Model and scaler loaded successfully")
            return True
        else:
            logger.error(f"Model or scaler files not found: {model_path}, {scaler_path}")
            return False
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def log_prediction(features: IrisFeatures, prediction: str, probability: float, all_probs: dict):
    """Log prediction to database"""
    try:
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (timestamp, sepal_length, sepal_width, petal_length, petal_width, 
             prediction, probability, all_probabilities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            features.sepal_length,
            features.sepal_width,
            features.petal_length,
            features.petal_width,
            prediction,
            probability,
            json.dumps(all_probs)
        ))
        conn.commit()
        conn.close()
        logger.info(f"Prediction logged: {prediction}")
    except Exception as e:
        logger.error(f"Error logging prediction: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    init_database()
    model_loaded = load_model_and_scaler()
    if not model_loaded:
        logger.warning("Starting API without loaded model")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Iris Classification API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        model_loaded=model is not None and scaler is not None
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures):
    """Make a prediction on Iris features"""
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    with prediction_histogram.time():
        try:
            # Prepare input data
            input_data = np.array([[
                features.sepal_length,
                features.sepal_width,
                features.petal_length,
                features.petal_width
            ]])
            
            # Scale the input
            input_scaled = scaler.transform(input_data)
            
            # Make prediction
            prediction_idx = model.predict(input_scaled)[0]
            prediction_proba = model.predict_proba(input_scaled)[0]
            
            # Convert to readable format
            prediction = target_names[prediction_idx]
            probability = float(prediction_proba[prediction_idx])
            
            all_probabilities = {
                target_names[i]: float(prob) 
                for i, prob in enumerate(prediction_proba)
            }
            
            # Log the prediction
            log_prediction(features, prediction, probability, all_probabilities)
            
            # Update metrics
            prediction_counter.inc()
            
            logger.info(f"Prediction made: {prediction} (confidence: {probability:.4f})")
            
            return PredictionResponse(
                prediction=prediction,
                probability=probability,
                all_probabilities=all_probabilities,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/predictions/history")
async def get_prediction_history(limit: int = 100):
    """Get recent prediction history"""
    try:
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return {"history": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error retrieving prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving history")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
