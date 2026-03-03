
================================================================================
CHAPTER 7    API DESIGN AND INTERFACES
================================================================================
                                                                        Page 85

This chapter documents the RESTful API design, request/response
schemas, error handling conventions, and inter-module communication
protocols.


7.1  API ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────

The system exposes a RESTful HTTP API built on Flask 3.0 with
Flask-CORS for cross-origin resource sharing. All API responses use
JSON (application/json) content type. The API follows resource-
oriented URL design with HTTP method semantics.

Design Principles:
(1) Statelessness: Each request contains all information needed for
    processing. No session state is maintained on the server between
    requests (except in-memory model state and IoT device registry).
(2) Uniform Interface: Consistent URL patterns, HTTP method usage,
    and response envelope structure across all endpoints.
(3) HATEOAS (partial): Error responses include suggestions for
    valid endpoints.
(4) Content Negotiation: All endpoints accept and return JSON,
    with Content-Type validation on POST endpoints.


7.2  ENDPOINT SPECIFICATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 86

Table 7.1: Complete API Endpoint Reference

┌─────────────────────────────┬────────┬──────────────────────────────────────┐
│ Endpoint                    │ Method │ Description                          │
├─────────────────────────────┼────────┼──────────────────────────────────────┤
│ /                           │ GET    │ Main dashboard (HTML)                │
│ /summary                    │ GET    │ System summary page (HTML)           │
│ /waves                      │ GET    │ Wave animation dashboard (HTML)      │
│ /iot                        │ GET    │ IoT management dashboard (HTML)      │
│ /health                     │ GET    │ Health check (JSON)                  │
├─────────────────────────────┼────────┼──────────────────────────────────────┤
│ /predict                    │ POST   │ Single earthquake risk prediction    │
│ /batch-predict              │ POST   │ Multiple earthquake predictions      │
│ /model-info                 │ GET    │ Model metadata and configuration     │
├─────────────────────────────┼────────┼──────────────────────────────────────┤
│ /live-data                  │ GET    │ Real-time USGS data + predictions    │
│ /wave-data                  │ GET    │ Water level / wave data              │
│ /test-data                  │ GET    │ Demo earthquake dataset              │
├─────────────────────────────┼────────┼──────────────────────────────────────┤
│ /iot/cloud/poll             │ GET    │ ESP8266 cloud polling endpoint       │
│ /iot/cloud/alert            │ POST   │ Set cloud alert                      │
│ /iot/cloud/clear            │ POST   │ Clear cloud alert                    │
│ /iot/cloud/status           │ GET    │ Current cloud alert status           │
│ /iot/devices                │ GET    │ List registered IoT devices          │
│ /iot/devices                │ POST   │ Register new IoT device              │
│ /iot/devices/<ip>           │ DELETE │ Remove IoT device                    │
│ /iot/alert                  │ POST   │ Send alert to all devices            │
│ /iot/alert/clear            │ POST   │ Clear all device alerts              │
│ /iot/alert/history          │ GET    │ Alert history log                    │
│ /iot/test/<ip>              │ POST   │ Test specific device                 │
│ /iot/trigger-from-prediction│ POST   │ Auto-trigger IoT from prediction     │
│ /iot/arduino                │ GET    │ Download Arduino source code         │
│ /iot/esp8266                │ GET    │ Download ESP8266 WiFi source code    │
│ /iot/arduino/generate       │ GET    │ Generate custom Arduino code         │
│ /iot/esp8266/generate       │ GET    │ Generate custom ESP8266 code         │
│ /iot/esp8266/cloud/generate │ GET    │ Generate custom cloud ESP8266 code   │
└─────────────────────────────┴────────┴──────────────────────────────────────┘

                                                                        Page 87

7.3  REQUEST AND RESPONSE SCHEMAS
────────────────────────────────────────────────────────────────────────────────

7.3.1  POST /predict

Request Body:
    {
        "magnitude": 7.5,            // Float, earthquake magnitude (Mw)
        "depth": 10.0,               // Float, depth in km
        "latitude": 3.3,             // Float, epicenter latitude
        "longitude": 95.8            // Float, epicenter longitude
    }

Response Body (Success — HTTP 200):
    {
        "tsunami_probability": 0.87,       // Raw model output [0,1]
        "adjusted_probability": 0.78,      // Physics-adjusted output
        "risk_level": "HIGH",              // HIGH|MEDIUM|LOW|MINIMAL
        "confidence": 0.92,               // Model confidence
        "is_tsunami": true,               // Boolean classification
        "details": {
            "magnitude": 7.5,
            "depth": 10.0,
            "latitude": 3.3,
            "longitude": 95.8,
            "depth_factor": 0.967,         // Shallow = high factor
            "magnitude_factor": 0.625,     // (mag-5)/4
            "ocean_factor": 0.8,           // Ocean proximity
            "threshold": 0.1              // Classification threshold
        },
        "message": "HIGH RISK: Strong tsunami potential...",
        "timestamp": "2024-12-15T10:30:45.123456"
    }

Response Body (Error — HTTP 400):
    {
        "error": "Invalid input data",
        "message": "Magnitude must be a positive number"
    }

                                                                        Page 88

7.3.2  POST /batch-predict

Request Body:
    {
        "earthquakes": [
            {"magnitude": 7.5, "depth": 10, "lat": 3.3, "lon": 95.8},
            {"magnitude": 6.8, "depth": 45, "lat": 12.5, "lon": 92.1},
            {"magnitude": 5.2, "depth": 120, "lat": 28.5, "lon": 68.4}
        ]
    }

Response Body (Success — HTTP 200):
    {
        "results": [
            {"tsunami_probability": 0.87, "risk_level": "HIGH", ...},
            {"tsunami_probability": 0.62, "risk_level": "MEDIUM", ...},
            {"tsunami_probability": 0.03, "risk_level": "MINIMAL", ...}
        ],
        "count": 3,
        "timestamp": "2024-12-15T10:30:45.123456"
    }

7.3.3  GET /live-data

Response Body (Success — HTTP 200):
    {
        "earthquakes": [
            {
                "id": "us7000xyz",
                "magnitude": 6.7,
                "depth": 23.4,
                "latitude": 5.12,
                "longitude": 94.56,
                "place": "Off W Coast of Northern Sumatra",
                "time": 1702637445000,
                "tsunami_probability": 0.65,
                "risk_level": "MEDIUM",
                "is_tsunami_risk": true
            },
            ...
        ],
        "count": 47,
        "source": "USGS Real-time Earthquake Feed",
        "last_updated": "2024-12-15T10:30:45Z"
    }

                                                                        Page 89

7.3.4  GET /iot/cloud/poll

Response Body (No Alert — HTTP 200):
    {
        "has_alert": false,
        "timestamp": "2024-12-15T10:30:45Z"
    }

Response Body (Alert Active — HTTP 200):
    {
        "has_alert": true,
        "level": "WARNING",
        "message": "M7.5 Tsunami Warning - Andaman Region",
        "magnitude": 7.5,
        "timestamp": "2024-12-15T10:30:45Z"
    }

7.3.5  GET /health

Response Body (Healthy — HTTP 200):
    {
        "status": "healthy",
        "model_loaded": true,
        "model_file": "models/best_model.keras",
        "uptime_seconds": 3605,
        "endpoints_available": 28,
        "version": "2.0.0",
        "timestamp": "2024-12-15T10:30:45Z"
    }


7.4  ERROR HANDLING
────────────────────────────────────────────────────────────────────────────────

All errors follow a consistent response envelope:

    {
        "error": "Error category",
        "message": "Human-readable error description"
    }

                                                                        Page 90

Table 7.2: HTTP Status Code Usage

┌────────┬──────────────────────────┬──────────────────────────────────────────┐
│ Code   │ Meaning                  │ When Used                                │
├────────┼──────────────────────────┼──────────────────────────────────────────┤
│ 200    │ OK                       │ Successful GET/POST request              │
├────────┼──────────────────────────┼──────────────────────────────────────────┤
│ 400    │ Bad Request              │ Invalid/missing request parameters       │
├────────┼──────────────────────────┼──────────────────────────────────────────┤
│ 404    │ Not Found                │ Unknown endpoint or device not found     │
├────────┼──────────────────────────┼──────────────────────────────────────────┤
│ 408    │ Request Timeout          │ External API timeout (USGS, NOAA)        │
├────────┼──────────────────────────┼──────────────────────────────────────────┤
│ 500    │ Internal Server Error    │ Model inference failure, unhandled       │
│        │                          │ exception                                │
└────────┴──────────────────────────┴──────────────────────────────────────────┘

Exception Handling Strategy:
The application uses a layered exception handling approach:

    Layer 1 — Route-Level:
        Each route wraps its logic in try/except, returning
        appropriate HTTP error responses with descriptive messages.

    Layer 2 — Model-Level:
        Model loading and inference errors are caught separately,
        with fallback to physics-based-only estimation if the
        model is unavailable.

    Layer 3 — External API:
        All external API calls use requests.get() with timeout
        parameters (typically 10-15 seconds). ConnectionError,
        Timeout, and JSONDecodeError are caught and logged.

    Layer 4 — Application-Level:
        Flask's @app.errorhandler decorators provide catch-all
        handlers for 404 and 500 errors.


7.5  INTER-MODULE COMMUNICATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 91

Data Flow Between Modules:

    ┌─────────────────────────────────────────────────────────────┐
    │          INTER-MODULE DATA FLOW                             │
    │                                                              │
    │  config/config.yaml ──→ ConfigLoader ──→ All Modules        │
    │                                                              │
    │  External APIs ──→ Collectors ──→ DataFrames                │
    │                                     │                       │
    │                                     ↓                       │
    │                        DataPreprocessor ──→ NumPy Arrays    │
    │                                               │             │
    │                                               ↓             │
    │                              CNN-LSTM Model ──→ Float [0,1] │
    │                                                   │         │
    │                                                   ↓         │
    │                           IndiaImpactFilter ──→ Dict        │
    │                                                   │         │
    │                                                   ↓         │
    │                              RiskAssessor ──→ Assessment    │
    │                                                   │         │
    │                                                   ↓         │
    │                           Flask Routes ──→ JSON Response    │
    │                                   │                         │
    │                                   ↓                         │
    │                           IoT Devices (HTTP POST)           │
    └─────────────────────────────────────────────────────────────┘

Table 7.3: Inter-Module Data Types

┌───────────────────────┬──────────────────────┬──────────────────────┐
│ From                  │ To                   │ Data Type            │
├───────────────────────┼──────────────────────┼──────────────────────┤
│ USGSCollector         │ DataPreprocessor     │ pandas.DataFrame     │
│ NOAATidesCollector    │ DataPreprocessor     │ pandas.DataFrame     │
│ NOAABuoysCollector    │ DataPreprocessor     │ pandas.DataFrame     │
│ INCOISCollector       │ RiskAssessor         │ dict                 │
│ BathymetryLoader      │ DataPreprocessor     │ numpy.ndarray        │
│ DataPreprocessor      │ CNN-LSTM Model       │ numpy.ndarray(24,32) │
│ CNN-LSTM Model        │ IndiaImpactFilter    │ float [0, 1]         │
│ IndiaImpactFilter     │ RiskAssessor         │ dict                 │
│ RiskAssessor          │ Flask Routes         │ dict                 │
│ Flask Routes          │ Client/IoT           │ JSON (HTTP response) │
└───────────────────────┴──────────────────────┴──────────────────────┘

                                                                        Page 92

7.6  AUTHENTICATION AND RATE LIMITING
────────────────────────────────────────────────────────────────────────────────

Current Implementation:
The system does not implement authentication or rate limiting in the
current version (v2.0). This design decision reflects the following
considerations:

(1) The system is intended for deployment on internal networks or
    behind an API gateway (e.g., AWS API Gateway, Cloudflare) that
    provides authentication and rate limiting at the infrastructure
    level.
(2) For public-facing deployments on Railway/Render, the system relies
    on platform-level DDoS protection.
(3) The IoT cloud polling endpoint (/iot/cloud/poll) is intentionally
    unauthenticated to simplify ESP8266 firmware, which has limited
    memory for TLS certificate storage and HTTP header management.

Future Provisions:
The codebase is structured to support API key authentication through
Flask middleware. The recommended approach for production is:
- API key header (X-API-Key) with server-side validation
- Per-key rate limiting using Flask-Limiter
- JWT tokens for web dashboard authentication

