# 🌸 Iris Classification MLOps Pipeline

A production-ready MLOps pipeline for Iris flower classification using modern machine learning operations practices.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Train models
python src/models/train.py

# Start API
uvicorn src.api.main:app --reload

# Visit: http://localhost:8000/docs
```

## 📊 Features

- **Machine Learning**: 3 models with MLflow experiment tracking
- **REST API**: FastAPI with automatic documentation
- **Containerization**: Docker deployment ready
- **CI/CD**: GitHub Actions pipeline
- **Monitoring**: Prometheus metrics and logging
- **Data Validation**: Pydantic input validation

## 🏗️ Architecture

```
iris-mlops/
├── src/
│   ├── data/          # Data processing
│   ├── models/        # ML training
│   ├── api/           # FastAPI service
│   └── monitoring/    # Logging & metrics
├── tests/             # Unit tests
├── notebooks/         # EDA analysis
├── .github/workflows/ # CI/CD
└── Dockerfile         # Container
```

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Interactive API documentation |
| `/health` | GET | Health check |
| `/predict` | POST | Iris classification |
| `/metrics` | GET | Prometheus metrics |

## 📈 Model Performance

| Model | Accuracy | F1-Score |
|-------|----------|----------|
| Logistic Regression | 96.7% | 96.7% |
| Random Forest | 100% | 100% |
| SVM | 100% | 100% |

## 🐳 Docker Deployment

```bash
# Build image
docker build -t iris-mlops .

# Run container
docker run -p 8000:8000 iris-mlops

# Or use docker-compose
docker-compose up
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Check code quality
black --check .
flake8 .
```

## 🔍 Example Usage

```python
import requests

# Make prediction
response = requests.post("http://localhost:8000/predict", json={
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
})

print(response.json())
# Output: {"prediction": "setosa", "probability": 0.999, ...}
```

## 📚 Documentation

- **API Docs**: `http://localhost:8000/docs`
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **EDA Notebook**: [notebooks/iris_eda.ipynb](notebooks/iris_eda.ipynb)

## 🛠️ Tech Stack

- **ML**: scikit-learn, MLflow
- **API**: FastAPI, Pydantic
- **Container**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, SQLite
- **Testing**: pytest

---

Built with ❤️ using modern MLOps practices
