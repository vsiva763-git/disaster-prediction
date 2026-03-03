
================================================================================
              PART III: METHODOLOGY AND SYSTEM DESIGN
================================================================================


================================================================================
CHAPTER 3    SYSTEM ARCHITECTURE AND TECHNOLOGY STACK
================================================================================
                                                                        Page 30

3.1  OVERVIEW OF THE SYSTEM ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────

The India-Specific Tsunami Early Warning System follows a five-layer
architecture that reflects the natural information flow from raw sensor
data to actionable alerts. Each layer is implemented as a set of
independently testable modules connected through well-defined interfaces,
enabling modification or replacement of any component without affecting
the overall system integrity.

                              [Figure 3.1]
    ┌═══════════════════════════════════════════════════════════════┐
    ║              FIVE-LAYER SYSTEM ARCHITECTURE                  ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║                                                               ║
    ║  LAYER 5: APPLICATION & ALERT LAYER                          ║
    ║  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ║
    ║  │Flask Web │  │REST API  │  │IoT Alert │  │SocketIO  │    ║
    ║  │Dashboard │  │Endpoints │  │Subsystem │  │Real-time │    ║
    ║  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘    ║
    ║        └──────────────┴──────────────┴─────────────┘         ║
    ║                          ↑                                    ║
    ║  ─────────────────────────────────────────────────────────    ║
    ║  LAYER 4: INDIA-SPECIFIC FILTERING LAYER                     ║
    ║  ┌──────────────────┐  ┌──────────────────┐                  ║
    ║  │ India Impact     │  │ Risk Assessor    │                  ║
    ║  │ Filter           │  │ (Alert Generator)│                  ║
    ║  └────────┬─────────┘  └────────┬─────────┘                  ║
    ║           └─────────────────────┘                             ║
    ║                    ↑                                          ║
    ║  ─────────────────────────────────────────────────────────    ║
    ║  LAYER 3: AI PREDICTION ENGINE                               ║
    ║  ┌──────────────────────────────────────────┐                ║
    ║  │  CNN-LSTM Binary Model (Focal Loss)      │                ║
    ║  │  Input: 24 timesteps × 32 features       │                ║
    ║  │  Output: Tsunami probability (sigmoid)    │                ║
    ║  └──────────────────┬───────────────────────┘                ║
    ║                     ↑                                         ║
    ║  ─────────────────────────────────────────────────────────    ║
    ║  LAYER 2: DATA PREPROCESSING LAYER                           ║
    ║  ┌──────────────────────────────────────────┐                ║
    ║  │  Feature Extraction & Normalization       │                ║
    ║  │  StandardScaler + MinMaxScaler             │                ║
    ║  │  Temporal Windowing (24 timesteps)         │                ║
    ║  └──────────────────┬───────────────────────┘                ║
    ║                     ↑                                         ║
    ║  ─────────────────────────────────────────────────────────    ║
    ║  LAYER 1: DATA INGESTION LAYER                               ║
    ║  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐         ║
    ║  │ USGS  │ │ NOAA  │ │ NOAA  │ │INCOIS │ │ GEBCO │         ║
    ║  │Quakes │ │Tides  │ │Buoys  │ │Advise │ │Bathy  │         ║
    ║  └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘         ║
    ║      └─────────┴─────────┴─────────┴─────────┘               ║
    ║                     ↑                                         ║
    ║         [ Public APIs & Open Datasets ]                       ║
    ╚═══════════════════════════════════════════════════════════════╝

           Figure 3.1: Five-Layer System Architecture Diagram

                                                                        Page 31

Layer 1 — Data Ingestion Layer: Five collector modules independently
query public APIs and datasets to obtain real-time earthquake parameters,
sea level measurements, wave buoy observations, official tsunami
advisories, and ocean bathymetry data. Each collector implements error
handling, retry logic, and fallback data generation to ensure system
operation even when individual data sources are unavailable.

Layer 2 — Data Preprocessing Layer: Raw data from Layer 1 is transformed
into the standardized input format required by the prediction model.
This includes feature extraction (computing 32 features from raw
measurements), temporal windowing (organizing features into 24-timestep
sequences), normalization (StandardScaler for earthquake/ocean features,
MinMaxScaler for spatial features), and missing data imputation through
zero-padding.

Layer 3 — AI Prediction Engine: The preprocessed 24×32 feature matrix
is fed into the trained CNN-LSTM binary model, which outputs a single
sigmoid probability representing the estimated likelihood that the
observed seismic event is tsunamigenic. The production model uses Binary
Focal Loss for training and achieves inference in under two seconds on
commodity hardware.

Layer 4 — India-Specific Filtering Layer: The model's raw prediction
is contextualized through geographic filtering that evaluates: (a) the
earthquake's location relative to four critical subduction zones
(Andaman, Makran, Sumatra, Arabian Sea); (b) the minimum Haversine
distance from the epicenter to India's coastline; (c) the wave
propagation direction relative to Indian shores; (d) the earthquake's
depth and magnitude as indicators of tsunamigenic potential. The output
is a composite India Risk Score and identification of specific affected
coastal regions.

                                                                        Page 32

Layer 5 — Application and Alert Layer: The filtered risk assessment is
disseminated through four channels: (a) a Flask web dashboard with
interactive Leaflet.js map for visual situational awareness; (b) a
RESTful API providing JSON-formatted data for programmatic consumers;
(c) an IoT alert subsystem that sends HTTP-based alerts to registered
Arduino + ESP8266 devices; and (d) a SocketIO real-time communication
channel for push-based web updates.

The separation of concerns across these five layers provides several
architectural advantages. First, each layer can be tested independently
— the data collectors can be validated against known API responses, the
model can be evaluated against held-out test data, and the filters can
be tested against known earthquake scenarios. Second, the model (Layer
3) can be retrained without modifying any other layer. Third, additional
data sources can be added to Layer 1 without modifying the prediction
pipeline. Fourth, new alert channels (e.g., SMS, voice) can be added to
Layer 5 without affecting the upstream layers.


3.2  COMPONENT INTERACTION AND DATA FLOW
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 33

The system provides two distinct entry points, each serving a different
operational use case:

Entry Point 1 — Standalone Flask API (app.py):
This 1,800-line monolithic application serves as the primary
production deployment. It loads the trained model at startup,
provides all REST API endpoints for prediction, live data, IoT
management, and dashboard serving. This entry point is optimized
for deployment on resource-constrained cloud platforms (Railway,
Render free tier) where memory is limited.

Entry Point 2 — Full-Stack Application (main.py):
This entry point uses the Flask application factory pattern through
src/web_app/app.py, initializing the complete inference engine with
all five data collectors, the filtering pipeline, and Flask-SocketIO
for real-time communication. This mode is suitable for development
and for deployments where the full monitoring loop is desired.

                              [Figure 3.2]
    ┌─────────────────────────────────────────────────────────────┐
    │            COMPONENT INTERACTION DIAGRAM                     │
    │                                                              │
    │  ┌─────────────────────────────────────────────────────────┐│
    │  │                    app.py (Standalone)                  ││
    │  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ││
    │  │  │/predict  │ │/live-data │ │/wave-data│ │/iot/*    │ ││
    │  │  │/batch-   │ │(USGS Live)│ │(IOC/NOAA)│ │(devices, │ ││
    │  │  │ predict  │ │           │ │          │ │ alerts)  │ ││
    │  │  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └────┬─────┘ ││
    │  │       │             │            │            │        ││
    │  │       ↓             ↓            ↓            ↓        ││
    │  │  ┌──────────────────────────────────────────────────┐  ││
    │  │  │         TensorFlow Model (best_model.keras)      │  ││
    │  │  └──────────────────────────────────────────────────┘  ││
    │  └─────────────────────────────────────────────────────────┘│
    │                                                              │
    │  ┌─────────────────────────────────────────────────────────┐│
    │  │                 main.py (Full-Stack)                    ││
    │  │  ┌─────────────────────────────────────┐               ││
    │  │  │    RealTimeInferenceEngine           │               ││
    │  │  │  ┌──────────────────────────────┐    │               ││
    │  │  │  │ USGSCollector                │    │               ││
    │  │  │  │ NOAATidesCollector           │    │               ││
    │  │  │  │ NOAABuoysCollector           │    │               ││
    │  │  │  │ INCOISCollector              │    │               ││
    │  │  │  │ BathymetryLoader             │    │               ││
    │  │  │  └──────────────────────────────┘    │               ││
    │  │  │  ┌──────────────────────────────┐    │               ││
    │  │  │  │ DataPreprocessor             │    │               ││
    │  │  │  │ TsunamiPredictionBinaryModel │    │               ││
    │  │  │  └──────────────────────────────┘    │               ││
    │  │  │  ┌──────────────────────────────┐    │               ││
    │  │  │  │ IndiaImpactFilter            │    │               ││
    │  │  │  │ RiskAssessor                 │    │               ││
    │  │  │  └──────────────────────────────┘    │               ││
    │  │  └─────────────────────────────────────┘               ││
    │  │                                                         ││
    │  │  ┌──────────────┐  ┌──────────────┐                    ││
    │  │  │ api_routes.py│  │web_routes.py │                    ││
    │  │  └──────────────┘  └──────────────┘                    ││
    │  └─────────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────────┘

     Figure 3.2: Component interaction for both entry points

                                                                        Page 34

The data flow in a typical prediction cycle proceeds as follows:

Step 1: A seismic event is detected through the USGS API (polled every
        30 seconds by the live dashboard or every 300 seconds by the
        monitoring loop).

Step 2: If the earthquake magnitude exceeds 5.5 and is located within
        the Indian Ocean bounding box (Lat -20° to 30°, Lon 40° to
        110°), the event is flagged for analysis.

Step 3: In the standalone mode (app.py), the earthquake's parameters
        (magnitude, depth, latitude, longitude) are converted into a
        24×32 input matrix using the create_seismic_pattern() function,
        which synthesizes temporal evolution features using sinusoidal
        modulation.

Step 4: The model processes the input matrix and outputs a raw
        probability between 0 and 1.

Step 5: The raw probability is adjusted using physics-based factors
        (depth factor, magnitude factor, ocean location factor) with
        a weighting of 40% model output and 60% physics-based
        adjustment.

Step 6: In full-stack mode (main.py), the India Impact Filter evaluates
        the earthquake against critical subduction zones, calculates
        distance to India's coastline, and generates an India Risk
        Score.

Step 7: The Risk Assessor compiles a comprehensive assessment with
        alert level, affected regions, estimated arrival times, and
        safety recommendations.

Step 8: The assessment is delivered to all connected clients through
        the web dashboard, API endpoints, and IoT alert subsystem.


3.3  TECHNOLOGY STACK AND DESIGN RATIONALE
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 35

The technology stack was selected through systematic evaluation of each
component against four criteria: (1) open-source availability with
permissive licensing; (2) production-grade maturity and stability;
(3) community support and documentation quality; and (4) resource
efficiency for deployment on constrained cloud platforms.

3.3.1  Python 3.10 as Primary Language

Python was selected as the primary implementation language for the
following reasons. First, TensorFlow — the chosen deep learning
framework — provides its most comprehensive API through Python, including
the Keras high-level interface used for model construction. Second,
Python's scientific computing ecosystem (NumPy, Pandas, SciPy) provides
efficient numerical operations essential for data preprocessing and
geospatial calculations. Third, Flask — a well-established Python web
framework — enables rapid API development with minimal boilerplate.
Fourth, Python's type hinting (introduced in Python 3.5 and refined
through subsequent versions) enables self-documenting code and supports
static analysis tools. The project uses Python 3.10 specifically for
its structural pattern matching capabilities and improved error messages.

                                                                        Page 36

3.3.2  TensorFlow 2.18–2.20 and Keras 3.10

TensorFlow was selected over PyTorch for the following reasons. First,
TensorFlow's SavedModel and .keras formats provide robust model
serialization that integrates naturally with production deployment
workflows. Second, TensorFlow Lite provides a pathway for future edge
deployment on IoT devices (e.g., Raspberry Pi). Third, TensorFlow's
integration with Kaggle and Google Colab GPU runtimes simplified the
training pipeline. The project supports TensorFlow versions 2.18
through 2.20, with Keras 3.10 providing the high-level model-building
API. The custom Focal Loss function is implemented using tf.clip_by_value
and tf.math.log for Keras 3 compatibility, avoiding deprecated K.backend
operations.

3.3.3  Flask 3.0 as Web Framework

Flask was selected over heavier frameworks (Django, FastAPI) due to its
minimalist design philosophy and the project's requirement for a single-
file deployment option. Flask's blueprint system enables modular route
registration (api_routes.py, web_routes.py) in the full-stack mode while
maintaining compatibility with monolithic deployment in the standalone
mode. Flask-CORS enables cross-origin requests from the Leaflet.js
frontend, Flask-SocketIO provides WebSocket support for real-time
updates, and Flask-Swagger-UI enables API documentation.

3.3.4  Arduino UNO and ESP8266 for IoT

Arduino UNO was selected as the alert device microcontroller for its
ubiquity, low cost (approximately USD 3 for clone boards), and extensive
educational documentation. The ESP8266 was selected as the WiFi module
for its integrated TCP/IP stack, HTTP client/server capabilities, and
cost of approximately USD 2 per unit. The total hardware cost for one
alert device (Arduino UNO + ESP8266 + LCD 16×2 + buzzer + resistors +
wiring) is under USD 10. The combination supports both direct HTTP
push communication (ESP8266 runs as an HTTP server receiving POST
requests from the cloud) and cloud polling communication (ESP8266
periodically requests alerts from the server), providing flexibility
for different network environments.

                                                                        Page 37

3.3.5  Leaflet.js for Cartographic Visualization

Leaflet.js was selected as the JavaScript mapping library for the web
dashboard. Its lightweight footprint (42 KB gzipped), open-source
BSD-2-Clause license, and extensive plugin ecosystem make it suitable
for rendering earthquake markers with risk-level color coding, drawing
propagation circles, and displaying background tile layers from
OpenStreetMap. The dashboard uses custom marker icons with color-coded
borders (green for low risk, amber for moderate, red for high) to
provide immediate visual assessment of regional risk levels.

3.3.6  Docker for Containerization

Docker was selected for deployment packaging to ensure environment
consistency across development, testing, and production. Two Dockerfile
configurations are provided: a full-system image (Python 3.10-slim base,
gcc, HDF5, NetCDF4, all Python dependencies) and a lightweight API-only
image (minimal dependencies for Flask + TensorFlow + model file). Docker
Compose configurations orchestrate multi-container deployments with
optional Nginx reverse proxy for production HTTPS termination.


3.4  THIRD-PARTY LIBRARIES AND DEPENDENCIES
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 38

Table 3.1: Python Library Dependencies (from requirements.txt)

┌─────────────────────┬──────────┬──────────────────────────────────────┐
│ Library             │ Version  │ Purpose                              │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ tensorflow          │ >=2.18   │ Deep learning framework & Keras API  │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ numpy               │ >=1.24   │ Numerical array operations           │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ pandas              │ >=2.0    │ DataFrame manipulation for data      │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ scikit-learn        │ >=1.3    │ StandardScaler, MinMaxScaler, metrics│
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ flask               │ >=3.0    │ Web application framework            │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ flask-cors          │ >=4.0    │ Cross-origin resource sharing        │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ flask-socketio      │ >=5.3    │ WebSocket real-time communication    │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ gunicorn            │ >=21.2   │ Production WSGI server               │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ requests            │ >=2.31   │ HTTP client for API calls            │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ pyyaml              │ >=6.0    │ YAML configuration parsing           │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ loguru              │ >=0.7    │ Structured logging with rotation     │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ netcdf4             │ >=1.6    │ NetCDF file format for bathymetry    │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ xarray              │ >=2023.1 │ N-dimensional array dataset handling │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ matplotlib          │ >=3.7    │ Training visualization plots         │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ seaborn             │ >=0.12   │ Statistical data visualization       │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ scipy               │ >=1.11   │ Scientific computing utilities       │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ joblib              │ >=1.3    │ Scaler persistence (pickle)          │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ pytest              │ >=7.4    │ Testing framework                    │
├─────────────────────┼──────────┼──────────────────────────────────────┤
│ pytest-cov          │ >=4.1    │ Test coverage reporting              │
└─────────────────────┴──────────┴──────────────────────────────────────┘


3.5  INFRASTRUCTURE AND DEPLOYMENT ENVIRONMENT
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 39

The system is designed for deployment across three tiers:

Tier 1 — Development: Local machine (Windows/Linux/macOS) with Python
3.10+ virtual environment. No GPU required for inference; GPU
recommended for training (NVIDIA GPU with CUDA support via Kaggle or
Google Colab).

Tier 2 — Containerized: Docker containers running on any Docker-
compatible host. The full-system Dockerfile packages all dependencies
including system-level libraries (libhdf5-dev, libnetcdf-dev) that may
be difficult to install on some operating systems.

Tier 3 — Cloud Platform: Configurations are provided for two free-tier
platforms:

(a) Railway (railway.json): Uses the NIXPACKS builder (automatic
    dependency detection), start command "bash start.sh",
    healthcheck at /health endpoint. Railway offers $5/month free
    credit, sufficient for continuous operation of this system.

(b) Render (render.yaml): Uses the free tier with gunicorn as the
    WSGI server (1 worker, 180-second timeout), Oregon region,
    automatic deploys from GitHub repository.

The deployment configuration follows a "works everywhere" principle:
the Procfile (compatible with Heroku, Railway, Render) specifies
a single deployment command:

    gunicorn app:app --bind 0.0.0.0:$PORT --timeout 180

This command launches the standalone Flask application with a
180-second timeout (necessary because model loading at startup takes
approximately 30–60 seconds depending on the platform's memory and
CPU allocation).

                                                                        Page 40

The deployment architecture includes health monitoring through the
/health endpoint, which returns the model loading status and system
operational status. Cloud platforms use this endpoint to verify that
the application has started successfully and to restart the container
if the health check fails:

    # Health check response format
    {
        "status": "healthy",
        "model_loaded": true,
        "version": "1.0.0",
        "timestamp": "2026-03-01T12:00:00Z"
    }

