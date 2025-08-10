"""
Tests for data loading and preprocessing
"""
import pytest
import numpy as np
import pandas as pd
import os
from src.data.data_loader import IrisDataProcessor

class TestIrisDataProcessor:
    
    def test_init(self):
        """Test initialization"""
        processor = IrisDataProcessor()
        assert processor.test_size == 0.2
        assert processor.random_state == 42
        assert processor.scaler is not None
    
    def test_load_data(self):
        """Test data loading"""
        processor = IrisDataProcessor()
        df, feature_names, target_names = processor.load_data()
        
        # Check DataFrame shape
        assert df.shape == (150, 6)  # 4 features + target + target_name
        
        # Check columns
        expected_columns = ['sepal length (cm)', 'sepal width (cm)', 
                          'petal length (cm)', 'petal width (cm)', 'target', 'target_name']
        assert all(col in df.columns for col in expected_columns)
        
        # Check feature names
        assert len(feature_names) == 4
        
        # Check target names
        assert len(target_names) == 3
        assert 'setosa' in target_names
        assert 'versicolor' in target_names
        assert 'virginica' in target_names
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        processor = IrisDataProcessor()
        df, feature_names, target_names = processor.load_data()
        X_train, X_test, y_train, y_test = processor.preprocess_data(df, feature_names)
        
        # Check shapes
        assert X_train.shape[0] == 120  # 80% of 150
        assert X_test.shape[0] == 30   # 20% of 150
        assert X_train.shape[1] == 4   # 4 features
        assert X_test.shape[1] == 4    # 4 features
        
        # Check that features are scaled (mean should be close to 0)
        assert abs(np.mean(X_train)) < 0.1
        
        # Check target distribution (should be stratified)
        unique_train, counts_train = np.unique(y_train, return_counts=True)
        unique_test, counts_test = np.unique(y_test, return_counts=True)
        assert len(unique_train) == 3
        assert len(unique_test) == 3
    
    def test_save_and_load_data(self, temp_dir):
        """Test saving and loading processed data"""
        processor = IrisDataProcessor()
        df, feature_names, target_names = processor.load_data()
        X_train, X_test, y_train, y_test = processor.preprocess_data(df, feature_names)
        
        # Save data
        processor.save_data(X_train, X_test, y_train, y_test, temp_dir)
        
        # Check files exist
        assert os.path.exists(os.path.join(temp_dir, "X_train.npy"))
        assert os.path.exists(os.path.join(temp_dir, "X_test.npy"))
        assert os.path.exists(os.path.join(temp_dir, "y_train.npy"))
        assert os.path.exists(os.path.join(temp_dir, "y_test.npy"))
        assert os.path.exists(os.path.join(temp_dir, "scaler.pkl"))
        
        # Load data
        X_train_loaded, X_test_loaded, y_train_loaded, y_test_loaded = processor.load_processed_data(temp_dir)
        
        # Check loaded data matches original
        np.testing.assert_array_equal(X_train, X_train_loaded)
        np.testing.assert_array_equal(X_test, X_test_loaded)
        np.testing.assert_array_equal(y_train, y_train_loaded)
        np.testing.assert_array_equal(y_test, y_test_loaded)
