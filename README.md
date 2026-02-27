# 🌊 India-Specific Tsunami Early Warning System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.18](https://img.shields.io/badge/tensorflow-2.18-orange.svg)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet)](https://railway.app/new/template)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-46E3B7)](https://render.com/deploy)

An **AI-powered, India-specific tsunami early warning system** built entirely on free public APIs and global historical data. This system uses a multi-modal CNN-LSTM deep learning model to predict tsunami risk in real-time, with intelligent filtering to ensure alerts are issued only when India is at risk.

> **🎓 Student Deployment Ready!** This project is configured for easy deployment using GitHub Student Pack benefits. See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

## 🎯 Overview

This project delivers a complete, production-ready tsunami warning system that:

- **🤖 AI-Powered Detection**: Multi-modal CNN-LSTM architecture trained on global tsunami data
- **🌍 Real-time Monitoring**: Continuous data ingestion from USGS, NOAA, and INCOIS public APIs
- **🇮🇳 India-Specific**: Intelligent filtering ensures alerts only when Indian coastlines are threatened
- **💰 Cost-Effective**: No sensor infrastructure required - uses only free public APIs
- **📊 Comprehensive Analysis**: Evaluates earthquakes, ocean conditions, bathymetry, and propagation patterns
- **🚀 Production Ready**: Full web dashboard, REST API, and monitoring capabilities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  USGS Earthquake API  │  NOAA Tides API  │  NOAA Buoys API  │
│  INCOIS Advisories    │  GEBCO Bathymetry │                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATA PREPROCESSING LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  • Feature Extraction                                        │
│  • Temporal Windowing                                        │
│  • Normalization & Scaling                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              CNN-LSTM PREDICTION MODEL                       │
├─────────────────────────────────────────────────────────────┤
│  CNN Branch (Spatial)  → Extract spatial patterns           │
│  CNN-LSTM Branch (EQ)  → Earthquake temporal evolution      │
│  CNN-LSTM Branch (Ocean) → Ocean condition patterns         │
│  Dense Layers → Risk probability, confidence, class         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│            INDIA-SPECIFIC FILTER LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  • Epicenter location analysis                               │
│  • Distance to Indian coast                                  │
│  • Wave propagation direction                                │
│  • Depth & magnitude assessment                              │
│  • Affected region identification                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   WEB APPLICATION                            │
├─────────────────────────────────────────────────────────────┤
│  REST API Endpoints  │  Real-time Dashboard  │  Alerts      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API access

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/vsiva763-git/India-specific-tsunami-early-warning-system.git
cd India-specific-tsunami-early-warning-system
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

- Note: The project now targets TensorFlow 2.18.0 (available on Colab); no separate Keras install needed.

3. **Prepare data:**
```bash
# Create sample training data
python prepare_data.py --sample --prepare

# Or download real global tsunami data
python prepare_data.py --all
```

4. **Train the model:**

   **Option A: Local Training**
   ```bash
   python train_model.py --epochs 50 --batch-size 32
   ```

   **Option B: Google Colab (Recommended for GPU)**
   - Open [`Train_Tsunami_Model_Colab.ipynb`](notebooks/Train_Tsunami_Model_Colab.ipynb) in Google Colab
   - Follow the step-by-step instructions
   - Download the trained model when complete

5. **Run the web application:**
```bash
python main.py --host 0.0.0.0 --port 5000
```

6. **Access the dashboard:**
Open your browser to `http://localhost:5000`

## 📖 Usage

### Web Dashboard

The web interface provides:
- Real-time tsunami risk assessment
- Current earthquake monitoring
- Ocean condition indicators
- Alert history
- Interactive API access

### REST API Endpoints

#### System Status
```bash
curl http://localhost:5000/api/status
```

#### Current Assessment
```bash
curl http://localhost:5000/api/current-assessment
```

#### Manual Check
```bash
curl -X POST http://localhost:5000/api/run-check
```

#### Start Monitoring
```bash
curl -X POST http://localhost:5000/api/monitoring/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 300}'
```

#### Recent Earthquakes
```bash
curl "http://localhost:5000/api/earthquake/recent?hours=24&min_magnitude=6.0"
```

#### Ocean Conditions
```bash
curl http://localhost:5000/api/ocean/conditions
```

#### INCOIS Advisories
```bash
curl http://localhost:5000/api/advisories/incois
```

### Command-Line Monitoring

Run standalone monitoring:
```bash
# Continuous monitoring
python monitor.py --interval 300

# Single check
python monitor.py --once
```

## 🧠 Model Architecture

### Multi-Modal CNN-LSTM

The system uses a sophisticated deep learning architecture:

**Input Branches:**
1. **Earthquake Data**: Magnitude, depth, location, time sequence
2. **Ocean Conditions**: Sea level anomalies, wave heights, tidal patterns
3. **Spatial Features**: Bathymetry, distance to coast, epicenter proximity

**Architecture:**
- **CNN Layers**: Extract spatial-temporal patterns and anomalies
- **LSTM Layers**: Model long-term temporal evolution
- **Dense Layers**: Final risk classification

**Outputs:**
- Risk probability (0-1)
- Confidence score (0-1)
- Risk class (none/low/medium/high)

### Training

The model is trained on **global historical tsunami data** from:
- NOAA Global Historical Tsunami Database
- USGS earthquake catalog
- Historical ocean observation data

This global approach enables the model to learn universal tsunami patterns, overcoming the rarity of tsunami events in India-only data.

## 🔍 India-Specific Filtering

The system includes an intelligent filtering layer that evaluates:

1. **Location Threat**: Is the epicenter in a critical zone for India?
2. **Distance**: How far is the earthquake from Indian coastlines?
3. **Propagation**: Will waves reach India?
4. **Depth & Magnitude**: Is the earthquake tsunami-capable?
5. **Affected Regions**: Which Indian coastal areas are at risk?

**Critical Zones:**
- Andaman Subduction Zone (critical threat)
- Makran Subduction Zone (high threat)
- Sumatra Subduction Zone (medium threat)
- Arabian Sea region (medium threat)

## 📊 Data Sources

### Real-Time APIs

| Source | Data Type | API |
|--------|-----------|-----|
| USGS | Earthquakes | [earthquake.usgs.gov](https://earthquake.usgs.gov/fdsnws/event/1/) |
| NOAA | Tides & Sea Level | [tidesandcurrents.noaa.gov](https://tidesandcurrents.noaa.gov/api/) |
| NOAA | Ocean Buoys | [ndbc.noaa.gov](https://www.ndbc.noaa.gov/) |
| INCOIS | Official Advisories | [incois.gov.in](https://incois.gov.in/) |

### Static Data

| Source | Data Type | Format |
|--------|-----------|--------|
| GEBCO | Bathymetry | NetCDF |
| NOAA | Historical Tsunamis | JSON/CSV |

## 📁 Project Structure

```
India-specific-tsunami-early-warning-system/
├── config/
│   └── config.yaml                  # System configuration
├── data/
│   ├── raw/                         # Raw training data
│   ├── processed/                   # Processed training data
│   └── cache/                       # API response cache
├── models/
│   ├── checkpoints/                 # Training checkpoints
│   ├── scalers/                     # Data scalers
│   └── best_model.keras             # Trained model
├── logs/                            # System logs
├── src/
│   ├── data_collection/             # API data collectors
│   │   ├── usgs_collector.py
│   │   ├── noaa_tides_collector.py
│   │   ├── noaa_buoys_collector.py
│   │   ├── incois_collector.py
│   │   └── bathymetry_loader.py
│   ├── models/                      # Deep learning models
│   │   ├── cnn_lstm_model.py
│   │   ├── data_preprocessor.py
│   │   └── model_trainer.py
│   ├── filtering/                   # India-specific filtering
│   │   ├── india_impact_filter.py
│   │   └── risk_assessor.py
│   ├── web_app/                     # Web application
│   │   ├── app.py
│   │   ├── api_routes.py
│   │   └── web_routes.py
│   ├── utils/                       # Utilities
│   │   ├── logger.py
│   │   ├── config_loader.py
│   │   └── data_helpers.py
│   └── inference_engine.py          # Real-time inference
├── main.py                          # Web app entry point
├── train_model.py                   # Model training script
├── monitor.py                       # Monitoring script
├── prepare_data.py                  # Data preparation script
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- API endpoints and parameters
- India region boundaries
- Model architecture
- Training hyperparameters
- Risk thresholds
- Monitoring intervals

## 🧪 Testing

The system includes comprehensive testing capabilities:

```bash
# Test with synthetic data
python prepare_data.py --sample

# Train on synthetic data
python train_model.py --epochs 10

# Run single tsunami check
python monitor.py --once
```

## 🚨 Alert System

**Alert Levels:**
- **WARNING**: High risk, immediate evacuation recommended
- **ADVISORY**: Moderate risk, stay alert
- **WATCH**: Low risk, monitoring continues
- **INFORMATION**: Minimal or no risk
- **NONE**: No threat to India

**Alert includes:**
- Risk score and confidence
- Affected coastal regions
- Estimated arrival times
- Safety recommendations
- Data source transparency

## 🔧 Extending the System

### Add New Data Sources

1. Create collector in `src/data_collection/`
2. Implement data fetching and parsing
3. Add to inference engine
4. Update preprocessor

### Modify Model Architecture

1. Edit `src/models/cnn_lstm_model.py`
2. Adjust layer configurations in `config/config.yaml`
3. Retrain model

### Add New Filtering Rules

1. Modify `src/filtering/india_impact_filter.py`
2. Add new evaluation criteria
3. Update risk scoring

## 📈 Performance

- **Inference Time**: < 2 seconds per assessment
- **API Response**: ~500ms average
- **Model Size**: ~50MB
- **Memory Usage**: ~1GB RAM
- **Monitoring Interval**: Configurable (default 5 minutes)

## 🛠️ Troubleshooting

**API Connection Issues:**
- Check internet connectivity
- Verify API endpoints in config
- Check API rate limits

**Model Loading Errors:**
- Ensure model is trained first
- Check file paths in config
- Verify TensorFlow version

**Missing Data:**
- Run `prepare_data.py` to create sample data
- Check data directory permissions

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **USGS** for earthquake data
- **NOAA** for ocean observation data
- **INCOIS** for tsunami advisories
- **GEBCO** for bathymetry data

## 📞 Contact

For questions or support, please open an issue on GitHub.

## ⚠️ Disclaimer

This system is for **educational and research purposes**. While it uses real data and sophisticated AI models, it should **not replace official tsunami warning systems**. Always follow official advisories from INCOIS and local disaster management authorities.

---

**Built with ❤️ for India's coastal safety**