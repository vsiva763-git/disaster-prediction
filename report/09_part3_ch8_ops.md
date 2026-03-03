
================================================================================
CHAPTER 8    STORAGE, SECURITY, SCALABILITY, TESTING, AND SETUP
================================================================================
                                                                        Page 93

This chapter addresses cross-cutting system concerns: data storage
strategy, security measures, scalability architecture, testing
methodology, and installation procedures.


8.1  STORAGE ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────

The system uses a file-based storage strategy, deliberately avoiding
database dependencies to simplify deployment and reduce operational
overhead.

Table 8.1: Storage Components

┌────────────────────────┬────────────────┬──────────────────────────────────┐
│ Component              │ Format         │ Purpose                          │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Model Weights          │ .keras (HDF5)  │ Trained CNN-LSTM parameters      │
│ (best_model.keras)     │ 2.1 MB         │ (Keras 3 native format)          │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Model Metadata         │ .json          │ Training metrics, parameters,    │
│ (model_metadata.json)  │ 2 KB           │ feature importance, thresholds   │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Configuration          │ .yaml          │ System parameters, API URLs,     │
│ (config.yaml)          │ 5 KB           │ region boundaries, thresholds    │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Training Logs          │ .csv           │ Per-epoch loss, accuracy, AUC    │
│ (training_log.csv)     │ Variable       │                                  │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Application Logs       │ .log           │ Runtime events, errors, alerts   │
│ (logs/app.log)         │ ≤100 MB/file   │ Rotated, 30-day retention        │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ IoT Device Registry    │ In-memory dict │ IP addresses, labels, status     │
│                        │                │ (Lost on restart)                │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Alert History          │ In-memory list │ Past assessments and alerts      │
│                        │                │ (Lost on restart)                │
├────────────────────────┼────────────────┼──────────────────────────────────┤
│ Cached API Responses   │ In-memory dict │ USGS, NOAA data for efficiency   │
│                        │ TTL-based      │ Refreshed per polling interval   │
└────────────────────────┴────────────────┴──────────────────────────────────┘

                                                                        Page 94

Design Rationale for File-Based Storage:
(1) Portability: No database server installation required, enabling
    one-command deployment on any platform with Python.
(2) Simplicity: The system's primary data flow is real-time (API→
    prediction→response), with minimal need for persistent query-able
    storage.
(3) Platform Compatibility: Railway, Render, and Docker deployments
    avoid the need for managed database services (cost reduction).
(4) Trade-off: IoT device registrations and alert history are lost
    on restart. For production deployments, Redis or SQLite would be
    recommended as a lightweight persistence layer.


8.2  SECURITY MEASURES
────────────────────────────────────────────────────────────────────────────────

8.2.1  Input Validation
All API endpoints validate incoming data before processing:

    # From app.py /predict route
    magnitude = data.get('magnitude', 7.0)
    depth = data.get('depth', 10)
    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 90)

    # Type and range validation
    try:
        magnitude = float(magnitude)
        depth = float(depth)
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input types"}), 400

    # Bounds checking
    if magnitude < 0 or magnitude > 12:
        return jsonify({"error": "Magnitude out of range"}), 400

8.2.2  CORS Configuration
Flask-CORS is configured to allow cross-origin requests from any
origin (CORS(app)), enabling dashboard access from any domain. In
production, this should be restricted to specific dashboard origins.

8.2.3  Dependency Security
Requirements files pin specific version ranges:
    TensorFlow>=2.18,<2.21 — avoids known CVEs in earlier versions
    Flask>=3.0 — addresses security patches in Flask 3.x releases
    requests>=2.31 — includes security fixes for URL parsing

                                                                        Page 95

8.2.4  IoT Communication Security
Current implementation uses plain HTTP for IoT communication. The
ESP8266 supports HTTPS via WiFiClientSecure, but this is disabled
by default to reduce memory usage and simplify initial setup. For
production deployments, the following measures are recommended:
- Enable HTTPS with Let's Encrypt certificates
- Add device authentication (pre-shared API key)
- Encrypt alert payloads with AES-128

8.2.5  Model Security
The trained model file (best_model.keras) should be treated as a
sensitive asset. An adversary who obtains the model could study its
decision boundaries to craft earthquake parameters that evade
detection (adversarial inputs). Mitigation: serve predictions via
API only; do not distribute model files publicly.


8.3  SCALABILITY ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 96

Table 8.2: Scalability Design Decisions

┌────────────────────┬────────────────────────┬────────────────────────────┐
│ Concern            │ Current Design         │ Scaling Strategy           │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ Compute            │ Single process,        │ Gunicorn workers (N×CPU), │
│                    │ Gunicorn WSGI server   │ Kubernetes HPA             │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ Model Inference    │ Single model instance  │ Model replicas, TF Serving │
│                    │ per worker             │ with load balancing        │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ Data Collection    │ Sequential polling     │ Async polling with aiohttp │
│                    │ with threading         │ and message queues         │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ IoT Devices        │ In-memory registry,    │ Redis-backed registry,     │
│                    │ sequential HTTP push   │ WebSocket connections      │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ Logging            │ File-based with        │ Centralized logging (ELK   │
│                    │ rotation               │ stack, CloudWatch)         │
├────────────────────┼────────────────────────┼────────────────────────────┤
│ Configuration      │ YAML file              │ Environment variables +    │
│                    │                        │ config server              │
└────────────────────┴────────────────────────┴────────────────────────────┘

Docker Deployment Configuration:
The system provides two Dockerfile variants:

    # Dockerfile (full stack — 1.2 GB image)
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 5000
    CMD ["gunicorn", "--bind", "0.0.0.0:5000",
         "--workers", "2", "--timeout", "120",
         "app:app"]

    # Dockerfile.api (API only — 800 MB image)
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements-render.txt requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt
    COPY app.py models/ config/ templates/ src/ ./
    EXPOSE 10000
    CMD ["gunicorn", "--bind", "0.0.0.0:10000",
         "--workers", "1", "--timeout", "120",
         "app:app"]

                                                                        Page 97

8.4  TESTING METHODOLOGY
────────────────────────────────────────────────────────────────────────────────

8.4.1  API Testing
The project includes comprehensive API testing scripts in the
examples/ directory:

    api_usage_examples.py — Demonstrates all major API endpoints
    test_api_live.py      — Live integration tests against running server
    quick_test.py         — Rapid smoke test for deployment verification

Example API test (from examples/test_api_live.py):

    def test_predict():
        """Test the /predict endpoint"""
        payload = {
            "magnitude": 7.5,
            "depth": 10,
            "latitude": 3.3,
            "longitude": 95.8
        }
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'tsunami_probability' in data
        assert 0 <= data['tsunami_probability'] <= 1
        assert data['risk_level'] in ['HIGH', 'MEDIUM', 'LOW', 'MINIMAL']

8.4.2  Health Check Testing
Automated health checks are implemented for containerized deployments:

    # scripts/check_health.py
    def check_health():
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'healthy' and data['model_loaded']:
                    return True
        except Exception:
            pass
        return False

                                                                        Page 98

8.4.3  Model Validation
Model performance is validated during training using:
(1) Train-test split (80/20) with stratified sampling
(2) Metrics computed on held-out test set: Accuracy, AUC, Recall,
    Precision, F1-Score, Specificity
(3) Confusion matrix analysis
(4) ROC curve analysis with optimal threshold selection
(5) Cross-validation during hyperparameter tuning

8.4.4  Manual Testing Protocol
The system provides demo scripts for manual verification:

    # examples/demo.py — Interactive demonstration
    # Runs through 5 test scenarios:
    # 1. Strong earthquake near Andaman (M7.5, 10km) → HIGH
    # 2. Moderate earthquake in Makran (M6.8, 45km) → MEDIUM
    # 3. Deep earthquake, irrelevant (M5.2, 120km) → MINIMAL
    # 4. Pacific earthquake, distant (M8.0, 15km) → LOW (not India)
    # 5. Weak earthquake, any location (M4.5, 80km) → MINIMAL


8.5  INSTALLATION AND SETUP
────────────────────────────────────────────────────────────────────────────────

8.5.1  Prerequisites
- Python 3.10 or later
- pip package manager
- 4 GB RAM minimum (for TensorFlow)
- Internet connection (for real-time data collection)

8.5.2  Local Installation Steps

    # Step 1: Clone repository
    git clone <repository-url>
    cd project_archive

    # Step 2: Create virtual environment
    python -m venv venv
    source venv/bin/activate      # Linux/macOS
    venv\Scripts\activate         # Windows

    # Step 3: Install dependencies
    pip install -r requirements.txt

    # Step 4: Start the application
    python app.py
    # Server starts on http://localhost:5000

                                                                        Page 99

8.5.3  Deployment Options

Table 8.3: Deployment Platform Comparison

┌─────────────┬─────────────────┬──────────────────────────────────────────┐
│ Platform    │ Configuration   │ Notes                                    │
├─────────────┼─────────────────┼──────────────────────────────────────────┤
│ Local       │ python app.py   │ Development mode with Flask debug server │
├─────────────┼─────────────────┼──────────────────────────────────────────┤
│ Docker      │ docker-compose  │ Full-stack (model + API + monitoring)    │
│             │ up              │ or API-only (Dockerfile.api)             │
├─────────────┼─────────────────┼──────────────────────────────────────────┤
│ Railway     │ railway.json    │ Auto-deploy from GitHub, NIXPACKS        │
│             │                 │ builder, free tier with 500 hours/month  │
├─────────────┼─────────────────┼──────────────────────────────────────────┤
│ Render      │ render.yaml     │ Auto-deploy from GitHub, free tier,      │
│             │                 │ spins down after 15 min inactivity       │
├─────────────┼─────────────────┼──────────────────────────────────────────┤
│ Gunicorn    │ Procfile        │ Production WSGI server, configurable     │
│             │                 │ workers and timeout                      │
└─────────────┴─────────────────┴──────────────────────────────────────────┘

8.5.4  Configuration Reference
All system parameters are configurable through config/config.yaml:

    Key Configuration Parameters:
    - model.path: Path to trained model file (default: models/best_model.keras)
    - model.threshold: Classification threshold (default: 0.1)
    - monitoring.interval_seconds: Polling interval (default: 300)
    - region.indian_ocean.lat_range: [-20, 30]
    - region.indian_ocean.lon_range: [40, 110]
    - alerts.critical_radius_km: 3000
    - dashboard.refresh_interval: 30

────────────────────────────────────────────────────────────────────────────────
End of Part III — Methodology
Chapters 3 through 8 have provided comprehensive documentation of the
system's architecture, data pipeline, algorithms, module implementation,
API design, and operational concerns. Part IV presents the experimental
results and performance analysis.
────────────────────────────────────────────────────────────────────────────────

