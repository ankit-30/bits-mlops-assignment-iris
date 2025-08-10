"""
Data loading and preprocessing for Iris dataset
"""
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import joblib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IrisDataProcessor:
    """Class to handle Iris dataset loading and preprocessing"""
    
    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load the Iris dataset"""
        logger.info("Loading Iris dataset")
        iris = load_iris()
        
        # Create DataFrame
        df = pd.DataFrame(iris.data, columns=iris.feature_names)
        df['target'] = iris.target
        df['target_name'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
        
        logger.info(f"Dataset loaded with shape: {df.shape}")
        return df, iris.feature_names, iris.target_names
    
    def preprocess_data(self, df, feature_names):
        """Preprocess the data"""
        logger.info("Preprocessing data")
        
        # Separate features and target
        X = df[feature_names]
        y = df['target']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Training set size: {X_train_scaled.shape[0]}")
        logger.info(f"Test set size: {X_test_scaled.shape[0]}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def save_data(self, X_train, X_test, y_train, y_test, data_dir="data"):
        """Save processed data"""
        os.makedirs(data_dir, exist_ok=True)
        
        np.save(os.path.join(data_dir, "X_train.npy"), X_train)
        np.save(os.path.join(data_dir, "X_test.npy"), X_test)
        np.save(os.path.join(data_dir, "y_train.npy"), y_train)
        np.save(os.path.join(data_dir, "y_test.npy"), y_test)
        
        # Save scaler
        joblib.dump(self.scaler, os.path.join(data_dir, "scaler.pkl"))
        
        logger.info(f"Data saved to {data_dir}")
    
    def load_processed_data(self, data_dir="data"):
        """Load processed data"""
        X_train = np.load(os.path.join(data_dir, "X_train.npy"))
        X_test = np.load(os.path.join(data_dir, "X_test.npy"))
        y_train = np.load(os.path.join(data_dir, "y_train.npy"))
        y_test = np.load(os.path.join(data_dir, "y_test.npy"))
        
        self.scaler = joblib.load(os.path.join(data_dir, "scaler.pkl"))
        
        return X_train, X_test, y_train, y_test

def main():
    """Main function to process and save data"""
    processor = IrisDataProcessor()
    
    # Load and preprocess data
    df, feature_names, target_names = processor.load_data()
    X_train, X_test, y_train, y_test = processor.preprocess_data(df, feature_names)
    
    # Save processed data
    processor.save_data(X_train, X_test, y_train, y_test)
    
    # Save raw data for reference
    df.to_csv("data/iris_raw.csv", index=False)
    
    logger.info("Data processing completed successfully")

if __name__ == "__main__":
    main()
