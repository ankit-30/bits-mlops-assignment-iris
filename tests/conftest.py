"""
Test configuration and fixtures
"""
import pytest
import numpy as np
import os
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_iris_data():
    """Sample Iris data for testing"""
    return {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }

@pytest.fixture
def sample_features_array():
    """Sample features as numpy array"""
    return np.array([[5.1, 3.5, 1.4, 0.2]])

@pytest.fixture
def temp_dir():
    """Temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
