# MLOps Dashboard Setup Guide

## 🎯 Overview

This setup includes a complete monitoring stack with visual dashboards for your Iris MLOps pipeline:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visual dashboard and alerting
- **Custom MLOps Dashboard**: Real-time model performance monitoring

## 🚀 Quick Start

### Option 1: Full Stack with Dashboard
```bash
# Start everything including dashboard
docker-compose up -d

# Or use the demo script
demo-with-dashboard.bat
```

### Option 2: API Only (Original)
```bash
# Just the API and MLflow
demo.bat
```

## 🌐 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **FastAPI Docs** | http://localhost:8000/docs | - |
| **MLflow UI** | http://localhost:5000 | - |
| **Grafana Dashboard** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **API Health** | http://localhost:8000/health | - |
| **Metrics Endpoint** | http://localhost:8000/metrics | - |

## 📊 Dashboard Features

### Real-time Monitoring:
- **API Request Rate**: Requests per second over time
- **Response Time**: 95th percentile prediction latency
- **Prediction Distribution**: Pie chart of model predictions by class
- **Error Rate**: API error rate monitoring
- **Model Confidence**: Average prediction confidence tracking
- **Total Predictions**: 24-hour prediction count

### Key Metrics Tracked:
- `http_requests_total` - Total HTTP requests
- `prediction_duration_seconds` - Prediction response time
- `predictions_total` - Predictions by class
- `model_confidence` - Model confidence scores

## 🛠️ Setup Instructions

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Access Grafana
1. Open http://localhost:3000
2. Login with `admin` / `admin123`
3. Navigate to "Dashboards" → "Iris MLOps Pipeline Dashboard"

### 3. Generate Sample Data
```bash
# Make some API calls to populate metrics
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

### 4. View Real-time Metrics
- Dashboard will show metrics as you make API calls
- Prometheus scrapes metrics every 5 seconds
- Grafana updates visualizations in real-time

## 📁 Configuration Files

```
grafana/
├── dashboards/
│   ├── dashboard.yml          # Dashboard provider config
│   └── iris-mlops-dashboard.json  # MLOps dashboard definition
└── datasources/
    └── prometheus.yml         # Prometheus datasource config
```

## 🔧 Customization

### Adding New Metrics:
1. Add metrics to your FastAPI app using `prometheus_client`
2. Update `prometheus.yml` scrape configuration if needed
3. Create new panels in Grafana dashboard

### Dashboard Modifications:
1. Edit dashboard in Grafana UI
2. Export JSON and save to `grafana/dashboards/`
3. Restart services to apply changes

## 🐛 Troubleshooting

### Dashboard Not Loading:
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs grafana
docker-compose logs prometheus
```

### No Metrics Showing:
1. Verify API is running: http://localhost:8000/health
2. Check metrics endpoint: http://localhost:8000/metrics
3. Verify Prometheus targets: http://localhost:9090/targets

### Reset Dashboard:
```bash
# Stop services and remove volumes
docker-compose down -v

# Restart
docker-compose up -d
```

## 📈 Production Considerations

### Security:
- Change default Grafana password
- Enable HTTPS for production
- Configure proper authentication

### Scaling:
- Use external Prometheus storage for large datasets
- Configure Grafana for high availability
- Set up alerting rules for critical metrics

### Monitoring:
- Set up alerts for error rates
- Monitor resource usage
- Configure backup for dashboard configurations

## 🎯 Assignment Integration

This dashboard setup enhances your MLOps assignment by providing:

✅ **Visual Monitoring** - Beyond basic logging requirements  
✅ **Real-time Metrics** - Production-grade observability  
✅ **Professional Presentation** - Enterprise-level monitoring stack  
✅ **Bonus Points** - Exceeds assignment requirements  

Perfect for demonstrating advanced MLOps capabilities in your demo video!
