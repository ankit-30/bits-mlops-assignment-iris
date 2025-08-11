#!/usr/bin/env python3
"""
DVC Pipeline Demonstration Script
Simulates DVC workflow for Iris MLOps Pipeline
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    print("=" * 50)
    print(f" {title}")
    print("=" * 50)

def print_step(step, description):
    print(f"\n[{step}] {description}")
    print("-" * 30)

def check_dvc_installation():
    """Check if DVC is properly installed"""
    try:
        import dvc
        print(f"✓ DVC is installed (version: {dvc.__version__})")
        return True
    except ImportError:
        print("⚠ DVC not found, demonstrating concepts without CLI")
        return False

def show_dvc_structure():
    """Display DVC project structure"""
    print_step("1", "DVC Project Structure")
    
    dvc_files = [
        "data/iris_raw.csv.dvc",
        "models/best_model_model.pkl.dvc", 
        "dvc.yaml",
        ".dvc/config"
    ]
    
    for file in dvc_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"⚠ {file} (should exist)")

def show_pipeline_definition():
    """Show DVC pipeline configuration"""
    print_step("2", "DVC Pipeline Definition")
    
    pipeline_config = {
        "stages": {
            "data_load": {
                "cmd": "python src/data/data_loader.py",
                "deps": ["src/data/data_loader.py"],
                "outs": ["data/iris_raw.csv", "data/X_train.npy", "data/X_test.npy", "data/y_train.npy", "data/y_test.npy", "data/scaler.pkl"]
            },
            "train": {
                "cmd": "python src/models/train.py", 
                "deps": ["src/models/train.py", "data/X_train.npy", "data/X_test.npy", "data/y_train.npy", "data/y_test.npy", "data/scaler.pkl"],
                "outs": ["models/best_model_model.pkl"],
                "metrics": ["mlruns/"]
            },
            "api_test": {
                "cmd": "python -m pytest tests/test_api.py -v",
                "deps": ["tests/test_api.py", "src/api/", "models/best_model_model.pkl"]
            }
        }
    }
    
    print("Pipeline stages:")
    for stage, config in pipeline_config["stages"].items():
        print(f"  • {stage}: {config['cmd']}")

def run_pipeline_stage(stage_name, command):
    """Run a pipeline stage"""
    print(f"\n🔄 Running {stage_name}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {stage_name} completed successfully")
            return True
        else:
            print(f"✗ {stage_name} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {stage_name} error: {str(e)}")
        return False

def simulate_dvc_pipeline():
    """Simulate DVC pipeline execution"""
    print_step("3", "Running DVC Pipeline Simulation")
    
    stages = [
        ("Data Loading", "python src/data/data_loader.py"),
        ("Model Training", "python src/models/train.py")
    ]
    
    results = []
    for stage_name, command in stages:
        success = run_pipeline_stage(stage_name, command)
        results.append((stage_name, success))
    
    print("\n📊 Pipeline Execution Summary:")
    for stage, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {stage}: {status}")

def show_dvc_benefits():
    """Explain DVC benefits for MLOps"""
    print_step("4", "DVC Benefits for MLOps")
    
    benefits = [
        "📦 Version Control: Track data and model changes alongside code",
        "🔄 Reproducibility: Exact pipeline recreation across environments", 
        "🤝 Collaboration: Share datasets without bloating Git repositories",
        "📊 Lineage: Track data-to-model relationships and dependencies",
        "⚡ Efficiency: Only download needed data/models for specific versions",
        "🔀 Branching: Experiment with different datasets on Git branches"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")

def main():
    """Main DVC demonstration function"""
    print_header("DVC Integration Demo - Iris MLOps Pipeline")
    
    # Check DVC installation
    dvc_available = check_dvc_installation()
    
    # Show project structure
    show_dvc_structure()
    
    # Show pipeline definition
    show_pipeline_definition()
    
    # Run pipeline simulation
    simulate_dvc_pipeline()
    
    # Explain benefits
    show_dvc_benefits()
    
    print_header("Demo Complete")
    print("📚 For more details, see DVC_SETUP.md")
    print("🔗 DVC Documentation: https://dvc.org/doc")
    
    if dvc_available:
        print("\n💡 Try these DVC commands:")
        print("  python -m dvc status")
        print("  python -m dvc repro") 
        print("  python -m dvc dag")

if __name__ == "__main__":
    main()
