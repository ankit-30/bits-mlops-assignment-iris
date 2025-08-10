#!/usr/bin/env python3
"""
Setup script for CI/CD environment
Creates necessary directories and dummy files for testing
"""
import os

def setup_ci_environment():
    """Setup environment for CI/CD testing"""
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Create .gitkeep files to ensure directories exist in git
    for directory in ['logs', 'models', 'data']:
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('')
    
    print("CI environment setup complete")

if __name__ == "__main__":
    setup_ci_environment()
