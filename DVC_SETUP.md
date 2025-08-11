# DVC Integration for Iris MLOps Pipeline

## Overview
This project uses DVC (Data Version Control) for tracking data files, models, and creating reproducible ML pipelines.

## DVC Structure

### Tracked Assets
- **Data Files**: Raw and processed datasets
  - `data/iris_raw.csv.dvc` - Original Iris dataset
  - `data/*.npy` - Processed train/test splits
  - `data/scaler.pkl` - Feature scaler
  
- **Model Files**: 
  - `models/best_model_model.pkl.dvc` - Best performing model

### Pipeline Stages
The `dvc.yaml` file defines our ML pipeline with three stages:

1. **data_load**: Load and preprocess Iris dataset
2. **train**: Train models and select best performer
3. **api_test**: Test API functionality

## DVC Commands

### Initialize DVC (Already done)
```bash
dvc init
```

### Run Complete Pipeline
```bash
dvc repro
```

### Track New Data/Model Files
```bash
dvc add data/new_data.csv
git add data/new_data.csv.dvc
git commit -m "Add new data to DVC tracking"
```

### Check Pipeline Status
```bash
dvc status
```

### Show Pipeline DAG
```bash
dvc dag
```

## Remote Storage (Optional)
To set up remote storage for team collaboration:

```bash
# Example with AWS S3
dvc remote add -d myremote s3://your-bucket/dvcstore
dvc push

# Example with Google Drive
dvc remote add -d myremote gdrive://your-drive-folder-id
dvc push
```

## Integration with Git
DVC files (`.dvc` and `dvc.yaml`) are tracked in Git, while actual data/models are stored in DVC cache.

This enables:
- Version control for data and models
- Reproducible pipeline execution
- Team collaboration with shared remote storage
- Efficient storage (only metadata in Git)

## Benefits for MLOps
1. **Reproducibility**: Exact pipeline recreation
2. **Versioning**: Track data and model changes
3. **Collaboration**: Share datasets without Git bloat
4. **Automation**: Pipeline-based model training
5. **Lineage**: Track data-to-model relationships
