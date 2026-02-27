# Deployment Guide

## Quick Start

### 1. Local Deployment

```bash
# Install dependencies
pip install flask flask-cors tensorflow numpy

# Run API server
python app.py

# In another terminal, open the web interface
# Visit http://localhost:5000 (if serving HTML)
# Or use the standalone HTML file in a browser
```

### 2. Docker Deployment

```bash
# Build image
docker build -t tsunami-detector .

# Run container
docker run -p 5000:5000 tsunami-detector

# API available at http://localhost:5000
```

### 3. Kaggle API Usage

```python
import requests
import numpy as np

# Generate sample data
data = np.random.randn(24, 32).tolist()

# Make prediction
response = requests.post(
    'http://localhost:5000/predict',
    json={'data': data, 'threshold': 0.1}
)

print(response.json())
```

## API Endpoints

### Health Check
```
GET /health
```
Returns: API status and model status

### Single Prediction
```
POST /predict
Content-Type: application/json

{
    "data": [[...24 timesteps × 32 features...]],
    "threshold": 0.1
}
```

Returns:
```json
{
    "success": true,
    "probabilities": [0.95],
    "alerts": [1],
    "threshold": 0.1,
    "interpretation": ["Tsunami detected"]
}
```

### Batch Predictions
```
POST /batch-predict
Content-Type: application/json

{
    "samples": [[[...]], [[...]]],
    "threshold": 0.1
}
```

Returns: Batch results with alert count and rate

### Model Information
```
GET /model-info
```
Returns: Complete model metadata and performance metrics

## Recommended Thresholds

| Use Case | Threshold | Recall | Precision |
|----------|-----------|--------|-----------|
| **Maximum Safety** | 0.1-0.3 | 100% | 100% |
| **Balanced** | 0.4-0.5 | 99%+ | 100% |
| **Conservative** | 0.6-0.7 | 90%+ | 100% |

## Production Deployment

### AWS Lambda
```bash
# Requires: tensorflow-io-gcs-filesystem, etc.
# Deploy app.py with model file
```

### Google Cloud Run
```bash
# Containerize and deploy
docker build -t tsunami-detector .
gcloud run deploy tsunami-detector --image tsunami-detector
```

### Azure Container Instances
```bash
# Create container registry
az acr build --registry <registry-name> -t tsunami-detector .
az container create --registry <registry-name> -n tsunami-detector
```

### On-Premise Server
```bash
# Install Docker
docker pull tsunami-detector:latest
docker run -d -p 5000:5000 --name tsunami-api tsunami-detector

# Monitor logs
docker logs -f tsunami-api
```

## Performance Monitoring

### API Latency
- Single prediction: ~50-100ms (CPU), ~20-50ms (GPU)
- Batch prediction (100 samples): ~100-200ms (CPU), ~30-100ms (GPU)

### Model Size
- Model file: ~2.1 MB
- Memory footprint: ~100-200 MB
- Inference memory: ~50 MB per prediction

### Recommended Specs
- **Minimum**: 1 CPU, 512 MB RAM
- **Recommended**: 2+ CPU, 2+ GB RAM
- **Optimal**: GPU with CUDA support

## Error Handling

### Common Errors

1. **Model not loaded**
   - Ensure `tsunami_detection_binary_focal.keras` is in working directory
   - Check file permissions

2. **Invalid input shape**
   - Input must be (24, 32) for single sample
   - Batch input must be (N, 24, 32)

3. **Memory issues**
   - Reduce batch size
   - Use GPU if available

## Monitoring Checklist

- ✓ API responds to /health endpoint
- ✓ Model predictions are consistent
- ✓ Response times are acceptable
- ✓ Memory usage is stable
- ✓ Error logs are captured
- ✓ Model predictions are saved for auditing

## Integration with Existing Systems

### With NOAA/USGS Data Pipeline
```python
# Fetch real seismic data
seismic_data = fetch_seismic_data()  # Shape: (24, 16)

# Fetch ocean monitoring data
ocean_data = fetch_ocean_data()      # Shape: (24, 16)

# Combine features
combined = np.hstack([seismic_data, ocean_data])  # (24, 32)

# Predict
response = requests.post(
    'http://api.tsunami-detector/predict',
    json={'data': combined.tolist(), 'threshold': 0.1}
)

if response.json()['alerts'][0]:
    trigger_warning_system()
```

### Alert Triggering Rules
```python
if prediction_probability > threshold:
    # Stage 1: Internal alert
    notify_duty_officers()
    
    # Stage 2: Public alert
    if prediction_probability > 0.7:
        trigger_sms_alert()
        activate_siren_systems()
        notify_coastal_communities()
    
    # Stage 3: Tracking
    log_prediction(data, probability)
    send_to_archive()
```

## Maintenance

### Regular Updates
- Monitor model performance on real data
- Retrain with new historical events
- Update thresholds based on feedback
- Patch dependencies monthly

### Backup Strategy
- Daily model snapshots
- Version control for model files
- Maintain prediction logs
- Archive all alerts and outcomes

## Support & Troubleshooting

For issues or questions:
1. Check the API logs: `docker logs tsunami-api`
2. Verify model file exists and is accessible
3. Test endpoint connectivity
4. Check system resources (CPU, memory, GPU)
5. Review deployment guide

## Additional Resources

- Model Training: See [TRAINING_GUIDE.md](TRAINING_GUIDE.md)
- Architecture: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- Examples: See [API_EXAMPLES.md](API_EXAMPLES.md)
