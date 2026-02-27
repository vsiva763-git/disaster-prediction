# API Examples for Tsunami Early Warning System

This document provides examples of how to interact with the API.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently no authentication required (add in production).

## Endpoints

### 1. System Status

Get current system status and monitoring state.

**Request:**
```bash
curl -X GET http://localhost:5000/api/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_monitoring": true,
    "last_check": "2026-01-16T10:30:00",
    "check_interval_seconds": 300,
    "model_loaded": true,
    "current_assessment": {...},
    "system_time": "2026-01-16T10:35:00"
  }
}
```

### 2. Current Assessment

Get the latest tsunami risk assessment.

**Request:**
```bash
curl -X GET http://localhost:5000/api/current-assessment
```

**Response:**
```json
{
  "success": true,
  "data": {
    "assessment_id": "TSUNAMI_20260116_103000",
    "timestamp": "2026-01-16T10:30:00",
    "alert_level": "NONE",
    "india_at_risk": false,
    "india_risk_score": 0.15,
    "model_confidence": 0.92,
    "earthquake_info": {
      "magnitude": 6.8,
      "depth_km": 45.2,
      "location": {
        "latitude": 10.5,
        "longitude": 95.3
      },
      "time": "2026-01-16T10:15:00",
      "place": "Andaman Sea"
    },
    "affected_regions": [],
    "alert_message": "✓ No tsunami threat to Indian coast",
    "recommendations": [
      "No special action required",
      "Continue normal activities"
    ]
  }
}
```

### 3. Run Manual Check

Trigger an immediate tsunami risk check.

**Request:**
```bash
curl -X POST http://localhost:5000/api/run-check
```

**Response:**
```json
{
  "success": true,
  "data": {
    "assessment_id": "TSUNAMI_20260116_104500",
    "timestamp": "2026-01-16T10:45:00",
    "alert_level": "WARNING",
    "india_at_risk": true,
    "india_risk_score": 0.85,
    "affected_regions": ["west_coast", "andaman_nicobar"],
    "alert_message": "⚠️ TSUNAMI WARNING for Indian coast..."
  }
}
```

### 4. Start Monitoring

Start real-time continuous monitoring.

**Request:**
```bash
curl -X POST http://localhost:5000/api/monitoring/start \
  -H "Content-Type: application/json" \
  -d '{
    "interval_seconds": 300
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Monitoring started with 300s interval",
  "data": {
    "interval_seconds": 300
  }
}
```

### 5. Stop Monitoring

Stop real-time monitoring.

**Request:**
```bash
curl -X POST http://localhost:5000/api/monitoring/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Monitoring stopped"
}
```

### 6. Recent Earthquakes

Get recent earthquakes from USGS.

**Request:**
```bash
curl -X GET "http://localhost:5000/api/earthquake/recent?hours=24&min_magnitude=6.0"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 3,
    "earthquakes": [
      {
        "id": "us7000abc1",
        "magnitude": 7.2,
        "depth": 35.5,
        "latitude": 12.4,
        "longitude": 93.2,
        "time": "2026-01-16T08:30:15",
        "place": "Andaman Islands",
        "tsunami": 1
      },
      ...
    ]
  }
}
```

### 7. Ocean Conditions

Get current ocean conditions from tides and buoys.

**Request:**
```bash
curl -X GET http://localhost:5000/api/ocean/conditions
```

**Response:**
```json
{
  "success": true,
  "data": {
    "conditions": {
      "sea_level_anomaly": "normal",
      "wave_height_anomaly": "normal",
      "tsunami_indicators": []
    },
    "tide_stations": {
      "9001234": {
        "latest_reading": {
          "time": "2026-01-16T10:00:00",
          "water_level": 1.23
        },
        "anomaly_score": 0.5
      }
    },
    "buoy_stations": {
      "23001": {
        "latest_reading": {
          "time": "2026-01-16T10:00:00",
          "wave_height": 2.1,
          "dominant_period": 8.5
        },
        "tsunami_signature": {
          "detected": false,
          "confidence": 0.0
        }
      }
    }
  }
}
```

### 8. INCOIS Advisories

Get current official advisories from INCOIS.

**Request:**
```bash
curl -X GET http://localhost:5000/api/advisories/incois
```

**Response:**
```json
{
  "success": true,
  "data": {
    "advisories": [],
    "risk_assessment": {
      "risk_level": "normal",
      "active_advisories": 0,
      "affected_regions": [],
      "last_update": "2026-01-16T10:45:00"
    }
  }
}
```

### 9. Alert History

Get historical alerts.

**Request:**
```bash
curl -X GET "http://localhost:5000/api/alert-history?hours=24"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "count": 5,
    "alerts": [
      {
        "assessment_id": "TSUNAMI_20260116_080000",
        "timestamp": "2026-01-16T08:00:00",
        "alert_level": "WATCH",
        "india_risk_score": 0.35
      },
      ...
    ]
  }
}
```

### 10. Model Information

Get model architecture and configuration details.

**Request:**
```bash
curl -X GET http://localhost:5000/api/model/info
```

**Response:**
```json
{
  "success": true,
  "data": {
    "model_loaded": true,
    "architecture": "CNN-LSTM Multi-modal",
    "input_features": {
      "earthquake": ["magnitude", "depth", "latitude", "longitude"],
      "ocean": ["sea_level_anomaly", "wave_height", "wave_period"],
      "spatial": ["bathymetry", "distance_to_coast"],
      "temporal_window": 72
    },
    "thresholds": {
      "high_risk": 0.75,
      "medium_risk": 0.50,
      "low_risk": 0.25
    }
  }
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request
- `404`: Endpoint not found
- `500`: Internal server error

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:5000"

# Get current assessment
response = requests.get(f"{BASE_URL}/api/current-assessment")
data = response.json()

if data['success']:
    assessment = data['data']
    print(f"Alert Level: {assessment['alert_level']}")
    print(f"Risk Score: {assessment['india_risk_score']}")
else:
    print(f"Error: {data['error']}")

# Start monitoring
response = requests.post(
    f"{BASE_URL}/api/monitoring/start",
    json={"interval_seconds": 300}
)
print(response.json())
```

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:5000';

// Get current assessment
async function getCurrentAssessment() {
  const response = await fetch(`${BASE_URL}/api/current-assessment`);
  const data = await response.json();
  
  if (data.success) {
    console.log('Alert Level:', data.data.alert_level);
    console.log('Risk Score:', data.data.india_risk_score);
  } else {
    console.error('Error:', data.error);
  }
}

// Start monitoring
async function startMonitoring() {
  const response = await fetch(`${BASE_URL}/api/monitoring/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ interval_seconds: 300 })
  });
  
  const data = await response.json();
  console.log(data);
}

getCurrentAssessment();
```
