"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json
import os
import sys
import numpy as np
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "model_loaded" in data
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should return Prometheus format
        assert "text/plain" in response.headers.get("content-type", "")
    
    @patch('src.api.main.model')
    @patch('src.api.main.scaler')
    def test_predict_endpoint_success(self, mock_scaler, mock_model, sample_iris_data):
        """Test successful prediction"""
        # Mock the model and scaler
        mock_model.predict.return_value = np.array([0])
        mock_model.predict_proba.return_value = np.array([[0.9, 0.05, 0.05]])
        mock_scaler.transform.return_value = np.array([[0.1, 0.2, 0.3, 0.4]])
        
        response = client.post("/predict", json=sample_iris_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "prediction" in data
        assert "probability" in data
        assert "all_probabilities" in data
        assert "timestamp" in data
        assert data["prediction"] == "setosa"
    
    def test_predict_endpoint_validation(self):
        """Test input validation"""
        # Test missing field
        invalid_data = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4
            # missing petal_width
        }
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422
        
        # Test invalid range
        invalid_data = {
            "sepal_length": -1.0,  # negative value
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422
    
    def test_predict_endpoint_no_model(self):
        """Test prediction when model is not loaded"""
        with patch('src.api.main.model', None):
            response = client.post("/predict", json={
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            })
            assert response.status_code == 503
    
    def test_prediction_history_endpoint(self):
        """Test prediction history endpoint"""
        response = client.get("/predictions/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "count" in data
        assert isinstance(data["history"], list)
        assert isinstance(data["count"], int)
    
    def test_prediction_history_with_limit(self):
        """Test prediction history with limit parameter"""
        response = client.get("/predictions/history?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) <= 50

class TestInputValidation:
    
    def test_iris_features_validation(self):
        """Test Pydantic model validation"""
        from src.api.main import IrisFeatures
        
        # Valid data
        valid_data = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
        features = IrisFeatures(**valid_data)
        assert features.sepal_length == 5.1
        
        # Invalid data (negative value)
        with pytest.raises(ValueError):
            IrisFeatures(
                sepal_length=-1.0,
                sepal_width=3.5,
                petal_length=1.4,
                petal_width=0.2
            )
        
        # Invalid data (too large value)
        with pytest.raises(ValueError):
            IrisFeatures(
                sepal_length=15.0,
                sepal_width=3.5,
                petal_length=1.4,
                petal_width=0.2
            )
