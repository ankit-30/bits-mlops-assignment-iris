"""
Model training and experiment tracking with MLflow
"""
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os
import logging
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data.data_loader import IrisDataProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Class to handle model training and MLflow tracking"""
    
    def __init__(self, experiment_name="iris_classification"):
        self.experiment_name = experiment_name
        self.models = {
            "logistic_regression": LogisticRegression(random_state=42, max_iter=1000),
            "random_forest": RandomForestClassifier(random_state=42, n_estimators=100),
            "svm": SVC(random_state=42, probability=True)
        }
        
        # Setup MLflow
        mlflow.set_experiment(experiment_name)
        
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model and return metrics"""
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted')
        }
        
        return metrics, y_pred
    
    def train_model(self, model_name, X_train, y_train, X_test, y_test):
        """Train a single model with MLflow tracking"""
        logger.info(f"Training {model_name}")
        
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Get model
            model = self.models[model_name]
            
            # Log parameters
            mlflow.log_params(model.get_params())
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            metrics, y_pred = self.evaluate_model(model, X_test, y_test)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(
                model, 
                model_name,
                registered_model_name=f"iris_{model_name}"
            )
            
            # Log classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            mlflow.log_dict(report, "classification_report.json")
            
            logger.info(f"{model_name} - Accuracy: {metrics['accuracy']:.4f}")
            
            return model, metrics
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train all models and return results"""
        results = {}
        
        for model_name in self.models.keys():
            model, metrics = self.train_model(model_name, X_train, y_train, X_test, y_test)
            results[model_name] = {
                "model": model,
                "metrics": metrics
            }
        
        return results
    
    def select_best_model(self, results):
        """Select the best model based on accuracy"""
        best_model_name = max(results.keys(), key=lambda k: results[k]["metrics"]["accuracy"])
        best_model = results[best_model_name]["model"]
        best_metrics = results[best_model_name]["metrics"]
        
        logger.info(f"Best model: {best_model_name} with accuracy: {best_metrics['accuracy']:.4f}")
        
        return best_model_name, best_model, best_metrics
    
    def save_model(self, model, model_name, models_dir="models"):
        """Save the best model"""
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        return model_path

def main():
    """Main training pipeline"""
    # Load data
    processor = IrisDataProcessor()
    
    try:
        # Try to load processed data
        X_train, X_test, y_train, y_test = processor.load_processed_data()
        logger.info("Loaded processed data")
    except FileNotFoundError:
        # Process data if not available
        logger.info("Processing data from scratch")
        df, feature_names, target_names = processor.load_data()
        X_train, X_test, y_train, y_test = processor.preprocess_data(df, feature_names)
        processor.save_data(X_train, X_test, y_train, y_test)
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Train all models
    results = trainer.train_all_models(X_train, y_train, X_test, y_test)
    
    # Select best model
    best_model_name, best_model, best_metrics = trainer.select_best_model(results)
    
    # Save best model
    model_path = trainer.save_model(best_model, "best_model")
    
    # Register best model in MLflow
    with mlflow.start_run(run_name=f"best_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        mlflow.log_params(best_model.get_params())
        mlflow.log_metrics(best_metrics)
        mlflow.sklearn.log_model(
            best_model,
            "best_model",
            registered_model_name="iris_best_model"
        )
        mlflow.log_param("model_type", best_model_name)
        mlflow.log_artifact(model_path)
    
    logger.info("Training pipeline completed successfully")

if __name__ == "__main__":
    main()
