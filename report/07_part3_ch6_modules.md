
================================================================================
CHAPTER 6    MODULE-BY-MODULE IMPLEMENTATION BREAKDOWN
================================================================================
                                                                        Page 65

This chapter provides detailed technical analysis of each major module
in the system. For each module, the following aspects are documented:
purpose, internal design, key code segments with annotations, design
decisions, and integration points with other modules.


6.1  MODULE A: CNN-LSTM BINARY MODEL
     (src/models/cnn_lstm_binary_model.py — 155 lines)
────────────────────────────────────────────────────────────────────────────────

Purpose:
This module implements the production prediction model — a binary
classifier that determines whether a given seismic event is
tsunamigenic. It is the simpler of two model architectures in the
system (the other being the multi-modal three-branch model), optimized
for deployment on resource-constrained platforms.

Architecture Overview:

    Input (24 × 32) → Reshape (24 × 32 × 1)
        → Conv2D(32, 3×3, ReLU) → MaxPool(2×2) → Dropout(0.3)
        → Conv2D(64, 3×3, ReLU) → MaxPool(2×2) → Dropout(0.3)
        → Reshape(-1, 64)
        → LSTM(128, ReLU, return_sequences=True) → Dropout(0.3)
        → LSTM(64, ReLU, return_sequences=False) → Dropout(0.3)
        → Dense(128, ReLU) → Dropout(0.3)
        → Dense(64, ReLU) → Dropout(0.2)
        → Dense(32, ReLU)
        → Dense(1, Sigmoid) → Output

                                                                        Page 66

                              [Figure 6.1]
    ┌─────────────────────────────────────────────────────────────┐
    │          BINARY CNN-LSTM MODEL ARCHITECTURE                 │
    │                                                              │
    │  INPUT: (batch, 24, 32) ─ 24 timesteps × 32 features       │
    │         ↓                                                    │
    │  ┌──────────────────┐                                       │
    │  │ Reshape to       │  (batch, 24, 32, 1)                   │
    │  │ (24, 32, 1)      │                                       │
    │  └────────┬─────────┘                                       │
    │           ↓                                                  │
    │  ┌──────────────────┐  ┌──────────────────┐                 │
    │  │ Conv2D(32, 3×3)  │→ │ MaxPool(2×2)     │                 │
    │  │ ReLU, padding=   │  │ Dropout(0.3)     │                 │
    │  │ 'same'           │  │                  │                 │
    │  └──────────────────┘  └────────┬─────────┘                 │
    │                                 ↓   (batch, 12, 16, 32)     │
    │  ┌──────────────────┐  ┌──────────────────┐                 │
    │  │ Conv2D(64, 3×3)  │→ │ MaxPool(2×2)     │                 │
    │  │ ReLU, padding=   │  │ Dropout(0.3)     │                 │
    │  │ 'same'           │  │                  │                 │
    │  └──────────────────┘  └────────┬─────────┘                 │
    │                                 ↓   (batch, 6, 8, 64)       │
    │  ┌──────────────────┐                                       │
    │  │ Reshape(-1, 64)  │  (batch, 48, 64)                      │
    │  └────────┬─────────┘                                       │
    │           ↓                                                  │
    │  ┌──────────────────┐                                       │
    │  │ LSTM(128, ReLU)  │  return_sequences=True                │
    │  │ Dropout(0.3)     │                                       │
    │  └────────┬─────────┘                                       │
    │           ↓                                                  │
    │  ┌──────────────────┐                                       │
    │  │ LSTM(64, ReLU)   │  return_sequences=False               │
    │  │ Dropout(0.3)     │                                       │
    │  └────────┬─────────┘                                       │
    │           ↓   (batch, 64)                                    │
    │  ┌──────────────────┐                                       │
    │  │ Dense(128→64→32) │  ReLU, Dropout 0.3→0.2               │
    │  └────────┬─────────┘                                       │
    │           ↓   (batch, 32)                                    │
    │  ┌──────────────────┐                                       │
    │  │ Dense(1, Sigmoid)│  Binary output                        │
    │  └────────┬─────────┘                                       │
    │           ↓                                                  │
    │  OUTPUT: Tsunami probability [0, 1]                          │
    └─────────────────────────────────────────────────────────────┘

         Figure 6.1: Binary CNN-LSTM model architecture

                                                                        Page 67

Table 6.1: Binary CNN-LSTM Layer Configuration

┌────┬──────────────────────┬─────────────────┬──────────────┬──────────┐
│ #  │ Layer                │ Output Shape    │ Parameters   │ Notes    │
├────┼──────────────────────┼─────────────────┼──────────────┼──────────┤
│ 1  │ Input                │ (24, 32)        │ 0            │          │
│ 2  │ Reshape              │ (24, 32, 1)     │ 0            │ For CNN  │
│ 3  │ Conv2D(32, 3×3)      │ (24, 32, 32)    │ 320          │ ReLU     │
│ 4  │ MaxPooling2D(2×2)    │ (12, 16, 32)    │ 0            │          │
│ 5  │ Dropout(0.3)         │ (12, 16, 32)    │ 0            │          │
│ 6  │ Conv2D(64, 3×3)      │ (12, 16, 64)    │ 18,496       │ ReLU     │
│ 7  │ MaxPooling2D(2×2)    │ (6, 8, 64)      │ 0            │          │
│ 8  │ Dropout(0.3)         │ (6, 8, 64)      │ 0            │          │
│ 9  │ Reshape              │ (48, 64)        │ 0            │ For LSTM │
│ 10 │ LSTM(128)            │ (48, 128)       │ 98,816       │ seq=True │
│ 11 │ Dropout(0.3)         │ (48, 128)       │ 0            │          │
│ 12 │ LSTM(64)             │ (64)            │ 49,408       │ seq=False│
│ 13 │ Dropout(0.3)         │ (64)            │ 0            │          │
│ 14 │ Dense(128)           │ (128)           │ 8,320        │ ReLU     │
│ 15 │ Dropout(0.3)         │ (128)           │ 0            │          │
│ 16 │ Dense(64)            │ (64)            │ 8,256        │ ReLU     │
│ 17 │ Dropout(0.2)         │ (64)            │ 0            │          │
│ 18 │ Dense(32)            │ (32)            │ 2,080        │ ReLU     │
│ 19 │ Dense(1)             │ (1)             │ 33           │ Sigmoid  │
├────┼──────────────────────┼─────────────────┼──────────────┼──────────┤
│    │ TOTAL                │                 │ ~185,729     │          │
└────┴──────────────────────┴─────────────────┴──────────────┴──────────┘

Design Decisions:
(1) The use of Conv2D (rather than Conv1D) treats the 24×32 matrix as a
    2D "image," enabling the model to capture cross-feature spatial
    correlations — for example, the relationship between magnitude
    (column 0) and depth (column 1) at the same timestep.
(2) Two Conv2D blocks provide sufficient feature extraction without
    excessive parameter count. Each block uses 'same' padding to
    maintain spatial dimensions before pooling.
(3) The Reshape layer between CNN and LSTM converts the 2D feature maps
    into a sequence of 48 vectors (6×8=48 spatial positions), each of
    dimension 64 (number of Conv2D filters). This allows the LSTM to
    process the spatial features as a temporal sequence.
(4) Two stacked LSTM layers capture hierarchical temporal patterns.
    The first LSTM returns full sequences, enabling the second LSTM to
    attend to all positions. The second LSTM returns only the final
    hidden state, providing a fixed-length summary.
(5) Progressive dropout (0.3 → 0.2) in the dense layers provides
    regularization while allowing the final layers to retain more
    information for the binary decision.
(6) The optimizer (Adam, lr=0.0005) uses a conservative learning rate
    to ensure stable convergence with Focal Loss, which can produce
    large gradient magnitudes for hard examples.

Integration:
This module is instantiated by both app.py (standalone) and
inference_engine.py (full-stack). The model is loaded from
models/best_model.keras using Keras's load_model() with custom
objects registered for the focal_loss function.

                                                                        Page 68

6.2  MODULE B: MULTI-MODAL CNN-LSTM MODEL
     (src/models/cnn_lstm_model.py — 271 lines)
────────────────────────────────────────────────────────────────────────────────

Purpose:
This module implements a more complex, multi-modal architecture that
processes three distinct input types through separate branches before
fusing features for prediction. It is designed for the full-stack
deployment mode where all data sources are available.

Architecture Overview (Three-Branch Fusion):

    Branch 1 — Spatial:
        Input (64×64×2) → Conv2D(64) → BatchNorm → MaxPool
            → Conv2D(128) → BatchNorm → MaxPool
            → Conv2D(256) → BatchNorm → MaxPool
            → GlobalAvgPool → (256)

    Branch 2 — Earthquake Temporal:
        Input (timesteps×4) → Conv1D(64) → Conv1D(128)
            → LSTM(128) → LSTM(64) → (64)

    Branch 3 — Ocean Temporal:
        Input (locations×3) → Conv1D(64) → Conv1D(128)
            → LSTM(128) → LSTM(64) → (64)

    Fusion:
        Concatenate(Branch1, Branch2, Branch3) → (384)
            → Dense(64, ReLU) → Dropout(0.3)
            → Dense(32, ReLU) → Dropout(0.3)

    Output Heads:
        Head 1: Dense(1, Sigmoid) — Risk Probability
        Head 2: Dense(1, Sigmoid) — Confidence
        Head 3: Dense(4, Softmax) — Risk Class

                                                                        Page 69

Table 6.2: Multi-Modal CNN-LSTM Layer Configuration (Summary)

┌──────────┬──────────────────────────┬─────────────┬────────────────┐
│ Branch   │ Layer Sequence           │ Output      │ Parameters     │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ Spatial  │ 3× (Conv2D+BN+MaxPool)  │ (256)       │ ~160,000       │
│          │ + GlobalAvgPool          │             │                │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ Earthquake│ 2× Conv1D + 2× LSTM    │ (64)        │ ~150,000       │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ Ocean    │ 2× Conv1D + 2× LSTM     │ (64)        │ ~150,000       │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ Fusion   │ Concat + 2× Dense       │ (32)        │ ~27,000        │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ Outputs  │ 3× Dense heads          │ (1)+(1)+(4) │ ~200           │
├──────────┼──────────────────────────┼─────────────┼────────────────┤
│ TOTAL    │                          │             │ ~487,000       │
└──────────┴──────────────────────────┴─────────────┴────────────────┘

Design Decisions:
(1) Three separate branches allow each data modality (spatial bathymetry,
    earthquake sequences, ocean conditions) to be processed with
    architecture specifically suited to its characteristics.
(2) The spatial branch uses deeper Conv2D (3 blocks with 64→128→256
    filters) and BatchNormalization for the higher-dimensional 64×64×2
    bathymetry/distance grid.
(3) Three output heads enable the model to simultaneously predict risk
    probability, model confidence, and categorized risk class (Low,
    Medium, High, Critical). The loss function weights these outputs:
    risk probability (5.0), confidence (0.5), risk class (1.0).
(4) The fusion layer concatenates the three branch outputs into a 384-
    dimensional vector before dense layers reduce dimensionality. This
    late-fusion approach allows each branch to develop specialized
    feature representations before combination.

Integration:
This model is used in the full-stack mode (main.py → inference_engine.py)
where all five data collectors provide multi-modal input. It is not used
in the standalone mode (app.py).

                                                                        Page 70

6.3  MODULE C: DATA PREPROCESSOR
     (src/models/data_preprocessor.py — 299 lines)
────────────────────────────────────────────────────────────────────────────────

Purpose:
This module bridges the gap between raw sensor data (DataFrames from
collectors) and the normalized tensor format required by the neural
network models. It handles feature extraction, scaling, temporal
windowing, and missing data imputation.

Key Methods:

(1) preprocess_earthquake_data(df) → ndarray:
    Extracts earthquake features from a DataFrame, creates temporal
    sequences of 24 timesteps, and applies StandardScaler normalization.

    def preprocess_earthquake_data(self, earthquakes):
        """Convert earthquake DataFrame to model input tensor"""
        features = []
        for _, eq in earthquakes.iterrows():
            feat = [
                eq['magnitude'],
                eq['depth'],
                eq['latitude'],
                eq['longitude']
            ]
            features.append(feat)

        # Create temporal sequences with padding
        features = np.array(features)
        if len(features) < 24:
            padding = np.zeros((24 - len(features), features.shape[1]))
            features = np.vstack([padding, features])
        elif len(features) > 24:
            features = features[-24:]  # Take most recent 24

        # Apply scaling
        if self.earthquake_scaler is not None:
            features = self.earthquake_scaler.transform(
                features.reshape(-1, features.shape[-1])
            ).reshape(features.shape)

        return features

                                                                        Page 71

(2) preprocess_ocean_data(tide_data, buoy_data) → ndarray:
    Extracts statistical features from tide and buoy observations,
    including mean water level, standard deviation, rate of change,
    mean and maximum wave height, and dominant period.

(3) preprocess_spatial_data(bathymetry, center_coords) → ndarray:
    Extracts a 64×64 grid from the bathymetry dataset centered on
    the earthquake epicenter, with two channels: ocean depth and
    distance to coast. Applies MinMaxScaler normalization.

(4) fit_scalers(X_earthquake, X_ocean, X_spatial):
    Fits StandardScaler and MinMaxScaler on training data. Called
    during model training; the fitted scalers are serialized using
    joblib for use during inference.

(5) save_scalers(path) / load_scalers(path):
    Serializes and deserializes fitted scalers using joblib, enabling
    consistent normalization between training and inference.

Design Decisions:
(1) StandardScaler (zero mean, unit variance) is used for earthquake
    and ocean features because their distributions are approximately
    Gaussian. MinMaxScaler ([0,1] range) is used for spatial features
    because bathymetry values have natural bounds and relative
    magnitudes are meaningful.
(2) Zero-padding for insufficient temporal data is preferred over
    interpolation because the model was trained with zero-padded
    sequences during training, ensuring consistency.
(3) The module maintains state (fitted scalers) that must persist
    between training and inference, introducing a coupling between
    the training pipeline and the inference pipeline. This is managed
    through the save/load scaler mechanism.


6.4  MODULE D: MODEL TRAINER
     (src/models/model_trainer.py — 303 lines)
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 72

Purpose:
This module orchestrates the complete model training pipeline, from
data loading through training execution to evaluation and visualization.

Training Configuration:

    # From model_trainer.py
    callbacks = [
        ModelCheckpoint(
            'models/best_model.keras',
            monitor='val_auc',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=7,
            min_lr=1e-7,
            verbose=1
        ),
        TensorBoard(
            log_dir='logs/tensorboard',
            histogram_freq=1
        ),
        CSVLogger(
            'logs/training_log.csv'
        )
    ]

                                                                        Page 73

Table 6.3: Training Hyperparameters

┌────────────────────────────┬──────────────────────────────────────────┐
│ Hyperparameter             │ Value                                    │
├────────────────────────────┼──────────────────────────────────────────┤
│ Optimizer                  │ Adam                                     │
├────────────────────────────┼──────────────────────────────────────────┤
│ Learning Rate              │ 0.0005 (initial)                         │
├────────────────────────────┼──────────────────────────────────────────┤
│ Learning Rate Schedule     │ ReduceLROnPlateau (factor=0.5,           │
│                            │ patience=7, min_lr=1e-7)                 │
├────────────────────────────┼──────────────────────────────────────────┤
│ Loss Function              │ Binary Focal Loss (γ=2.0, α=0.25)       │
├────────────────────────────┼──────────────────────────────────────────┤
│ Batch Size                 │ 128                                      │
├────────────────────────────┼──────────────────────────────────────────┤
│ Maximum Epochs             │ 100                                      │
├────────────────────────────┼──────────────────────────────────────────┤
│ Actual Epochs (early stop) │ 8                                        │
├────────────────────────────┼──────────────────────────────────────────┤
│ Early Stopping Patience    │ 15 epochs                                │
├────────────────────────────┼──────────────────────────────────────────┤
│ Validation Split           │ 20%                                      │
├────────────────────────────┼──────────────────────────────────────────┤
│ Training Samples           │ 8,000                                    │
├────────────────────────────┼──────────────────────────────────────────┤
│ Positive Class Ratio       │ 39.78%                                   │
├────────────────────────────┼──────────────────────────────────────────┤
│ Training Platform          │ Kaggle GPU (Tesla T4 × 2)                │
├────────────────────────────┼──────────────────────────────────────────┤
│ Model File Size            │ 2.1 MB                                   │
├────────────────────────────┼──────────────────────────────────────────┤
│ Metrics Monitored          │ Binary Accuracy, AUC, Recall, Precision  │
└────────────────────────────┴──────────────────────────────────────────┘

The training pipeline also includes evaluation methods that compute
comprehensive metrics on the test set and generate visualizations:
- Loss and accuracy curves over epochs
- ROC curve with AUC
- Confusion matrix
- Precision-recall curve
- Threshold analysis
- Per-class performance metrics

Design Decisions:
(1) ModelCheckpoint monitors val_auc (rather than val_loss) to save the
    model with the highest validation AUC, prioritizing discriminative
    performance over raw loss minimization.
(2) Early stopping patience of 15 epochs allows the model sufficient
    opportunity to overcome local minima, while ReduceLROnPlateau with
    patience 7 provides an intermediate intervention.
(3) The large batch size of 128 (relative to the 8,000 training samples)
    provides stable gradient estimates for Focal Loss, which can produce
    high-variance gradients from individual hard examples.


6.5  MODULE E: INDIA IMPACT FILTER
     (src/filtering/india_impact_filter.py — 391 lines)
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 74

Purpose:
This module determines whether a detected tsunami threat poses risk to
India's coastline. It implements geographic filtering that reduces false
alarms by rejecting signals from earthquakes that are unlikely to
affect Indian shores, based on four criteria: epicenter location,
distance, wave propagation direction, and earthquake depth.

Critical Subduction Zones:
The module defines four critical earthquake zones known to produce
tsunamis affecting India:

    Andaman Subduction Zone:    Lat 0°–15°N,  Lon 90°–100°E
                                Threat: CRITICAL
    Makran Subduction Zone:     Lat 20°–27°N, Lon 60°–68°E
                                Threat: HIGH
    Sumatra Subduction Zone:    Lat 10°S–5°N, Lon 90°–105°E
                                Threat: MEDIUM
    Arabian Sea Zone:           Lat 10°–25°N, Lon 60°–75°E
                                Threat: MEDIUM

Table 6.4: India Coastal Region Boundaries

┌─────────────────────┬───────────┬───────────┬───────────┬───────────┐
│ Region              │ Min Lat   │ Max Lat   │ Min Lon   │ Max Lon   │
├─────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ West Coast          │ 8.0°N     │ 23.0°N    │ 68.0°E    │ 75.0°E    │
│ (Gujarat to Kerala) │           │           │           │           │
├─────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ East Coast          │ 8.0°N     │ 22.0°N    │ 80.0°E    │ 90.0°E    │
│ (TN to West Bengal) │           │           │           │           │
├─────────────────────┼───────────┼───────────┼───────────┼───────────┤
│ Andaman & Nicobar   │ 6.0°N     │ 14.0°N    │ 92.0°E    │ 94.0°E    │
│ Islands             │           │           │           │           │
└─────────────────────┴───────────┴───────────┴───────────┴───────────┘

                                                                        Page 75

Assessment Pipeline (from assess_india_risk()):

    Step 1: Check model risk threshold. If model prediction < 0.25,
            return "no risk" immediately.
    Step 2: Evaluate epicenter against four critical zones. If outside
            all zones, return "no risk" (epicenter in non-threatening
            location).
    Step 3: Calculate minimum Haversine distance to India's coastline.
            If distance > 3,000 km (critical radius), return "no risk."
    Step 4: Evaluate wave propagation direction. For M≥8.0, assume
            omnidirectional (1.0). For smaller events, evaluate bearing
            from epicenter toward India center (20°N, 77°E).
    Step 5: Assess depth factor using magnitude-depth matrix (Table 5.1).
    Step 6: Identify affected coastal regions (west coast, east coast,
            Andaman) based on impact radius (magnitude-dependent:
            M≥8.5→4000km, M≥8.0→3000km, M≥7.5→2000km, M≥7.0→1500km,
            otherwise→1000km).
    Step 7: Compute composite India Risk Score using weighted formula.
    Step 8: Determine risk level (HIGH≥0.75, MEDIUM≥0.50, LOW≥0.25).

Table 6.5: India Risk Score Weight Distribution

┌────────────────────┬────────┬─────────────────────────────────────────┐
│ Component          │ Weight │ Description                             │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ Model Risk (AI)    │ 0.35   │ CNN-LSTM sigmoid output probability     │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ Location Threat    │ 0.25   │ Critical zone proximity assessment      │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ Distance Factor    │ 0.20   │ Normalized Haversine dist. to coastline │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ Propagation Factor │ 0.10   │ Wave direction toward India assessment  │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ Depth Factor       │ 0.10   │ Magnitude-depth tsunamigenic potential  │
├────────────────────┼────────┼─────────────────────────────────────────┤
│ TOTAL              │ 1.00   │                                         │
└────────────────────┴────────┴─────────────────────────────────────────┘

Design Decisions:
(1) The 35% weight on model risk ensures that AI predictions are the
    primary driver while being tempered by geographic reality checks.
(2) Location threat (25%) reflects the geological understanding that
    earthquakes in specific subduction zones are far more likely to
    generate India-affecting tsunamis than events in other regions.
(3) The critical radius of 3,000 km is based on the maximum distance
    at which a M7.0 earthquake has historically generated destructive
    tsunami waves in the Indian Ocean.
(4) The multi-step early-exit design (returning "no risk" at Steps 1–3)
    ensures that clearly non-threatening events are processed with
    minimal computation.

                                                                        Page 76

6.6  MODULE F: RISK ASSESSOR
     (src/filtering/risk_assessor.py — 338 lines)
────────────────────────────────────────────────────────────────────────────────

Purpose:
This module generates comprehensive, human-readable risk assessments
from the technical outputs of the model prediction and India filter.
It produces alert levels, safety messages, arrival time estimates, and
actionable recommendations.

Alert Level Determination:
The assessor assigns one of five alert levels:

    WARNING:     India Risk Score ≥ 0.75 (or INCOIS WARNING active)
    ADVISORY:    India Risk Score ≥ 0.50 (or INCOIS ADVISORY active)
    WATCH:       India Risk Score ≥ 0.25 (or INCOIS WATCH active)
    INFORMATION: India at risk but score < 0.25
    NONE:        No threat detected

Official INCOIS advisories take precedence: if INCOIS has issued a
WARNING-level advisory, the system will not downgrade this to a lower
level regardless of the model's prediction. This ensures that the
AI system supplements rather than overrides official institutional
warning mechanisms.

Key Methods:

(1) generate_comprehensive_assessment(): Compiles all data into a
    single assessment dictionary with 15 top-level keys:
    assessment_id, timestamp, alert_level, india_at_risk,
    india_risk_score, model_confidence, earthquake_info,
    affected_regions, estimated_arrival_times, ocean_conditions,
    official_advisories, alert_message, recommendations,
    data_sources, system_status.

(2) _generate_alert_message(): Produces human-readable alert text
    with appropriate severity indicators (⚠️ for WARNING/ADVISORY,
    ℹ️ for WATCH/INFORMATION, ✓ for NONE) and includes earthquake
    parameters, affected regions, and recommended actions.

(3) _generate_recommendations(): Produces a list of safety
    recommendations calibrated to the alert level:
    - WARNING: "Evacuate coastal areas immediately", "Move to higher
      ground (at least 20 meters elevation)", "Stay away from
      beaches and harbors"
    - ADVISORY: "Monitor official advisories", "Prepare for possible
      evacuation", "Avoid coastal areas"
    - WATCH: "Stay informed", "Review evacuation routes"

                                                                        Page 77

Design Decisions:
(1) INCOIS advisory override ensures institutional authority is not
    undermined by AI predictions, maintaining trust in the official
    warning chain.
(2) Assessment history is maintained in-memory (list of dicts) for
    retrieval through the /api/alert-history endpoint.
(3) Messages are formatted with Unicode symbols (⚠️, ℹ️, ✓) for
    visual distinction on web dashboards, while remaining meaningful
    in plain-text contexts (IoT LCD displays receive simplified text).


6.7  MODULE G: INFERENCE ENGINE
     (src/inference_engine.py — 299 lines)
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 78

Purpose:
The RealTimeInferenceEngine orchestrates the complete prediction
pipeline, coordinating all five data collectors, the preprocessor,
the model, the India filter, and the risk assessor into a single
monitoring loop.

                              [Figure 6.7]
    ┌─────────────────────────────────────────────────────────────┐
    │          INFERENCE ENGINE MONITORING LOOP                    │
    │                                                              │
    │  START ─→ Initialize Components                              │
    │           │                                                  │
    │           ├─ USGSCollector                                   │
    │           ├─ NOAATidesCollector                              │
    │           ├─ NOAABuoysCollector                              │
    │           ├─ INCOISCollector                                 │
    │           ├─ BathymetryLoader                               │
    │           ├─ CNN-LSTM Model + Scalers                       │
    │           ├─ IndiaImpactFilter                               │
    │           └─ RiskAssessor                                    │
    │           ↓                                                  │
    │  ┌───→ WAIT (300 seconds) ◄─────────────────────────┐       │
    │  │       ↓                                           │       │
    │  │     Fetch Earthquakes (USGS, last 2 hours)        │       │
    │  │       ↓                                           │       │
    │  │     Any M≥6.5? ──NO──→ Log "No threat" ──────────┤       │
    │  │       │ YES                                       │       │
    │  │       ↓                                           │       │
    │  │     Fetch Ocean Data (NOAA Tides + Buoys)         │       │
    │  │       ↓                                           │       │
    │  │     Check INCOIS Advisories                       │       │
    │  │       ↓                                           │       │
    │  │     Preprocess → Model Prediction                 │       │
    │  │       ↓                                           │       │
    │  │     India Impact Filter                           │       │
    │  │       ↓                                           │       │
    │  │     Risk Assessment                               │       │
    │  │       ↓                                           │       │
    │  │     India at risk? ──NO──→ Log "No threat" ──────┤       │
    │  │       │ YES                                       │       │
    │  │       ↓                                           │       │
    │  │     GENERATE ALERT                                │       │
    │  │       ↓                                           │       │
    │  │     Dispatch to IoT / Web / Log                   │       │
    │  │       │                                           │       │
    │  └───────┴───────────────────────────────────────────┘       │
    └─────────────────────────────────────────────────────────────┘

      Figure 6.7: Inference engine monitoring loop

                                                                        Page 79

Threading Model:
The monitoring loop runs in a daemon thread, allowing the Flask web
server to operate concurrently on the main thread:

    def start_monitoring(self, interval_seconds=300):
        self.is_running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop
        )
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

The daemon thread designation ensures that the monitoring loop
terminates automatically when the main process exits, preventing
orphaned threads in containerized deployments.

State Management:
The engine maintains three pieces of state:
- is_running (bool): Controls the monitoring loop
- current_assessment (dict or None): Most recent assessment
- last_check_time (datetime): Timestamp of last check

Design Decisions:
(1) The 300-second (5-minute) default interval balances responsiveness
    against API rate limits. USGS provides near-real-time updates with
    typical latency of 2–5 minutes; polling more frequently would not
    yield additional information.
(2) The M≥6.5 threshold for triggering full analysis filters out the
    vast majority of earthquakes that cannot generate tsunamis,
    conserving computational resources.
(3) graceful error handling ensures that a failure in any single data
    source does not crash the monitoring loop. Each collector's failure
    is logged but processing continues with available data.


6.8  MODULE H: FLASK WEB APPLICATION
     (app.py — 1,800 lines)
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 80

Purpose:
The standalone Flask application (app.py) is the primary production
deployment entry point. It is a comprehensive, self-contained web
application that provides prediction API endpoints, live data
visualization, IoT device management, and wave animation dashboards.

Route Architecture:

    ┌──────────────────────────────────────────────────────────┐
    │                    FLASK ROUTES                           │
    │                                                           │
    │  Page Routes:                                             │
    │  ├── GET /              → index_live.html (dashboard)    │
    │  ├── GET /summary       → summary.html (summary page)   │
    │  ├── GET /waves         → wave_animation.html (canvas)  │
    │  ├── GET /iot           → iot_dashboard.html (IoT mgmt) │
    │  └── GET /health        → JSON health check              │
    │                                                           │
    │  Prediction Routes:                                       │
    │  ├── POST /predict      → Single prediction              │
    │  ├── POST /batch-predict→ Batch prediction               │
    │  └── GET  /model-info   → Model metadata                 │
    │                                                           │
    │  Data Routes:                                             │
    │  ├── GET /live-data     → Real-time USGS + predictions   │
    │  ├── GET /wave-data     → IOC/NOAA water levels          │
    │  └── GET /test-data     → Demo earthquake data           │
    │                                                           │
    │  IoT Routes:                                              │
    │  ├── GET  /iot/cloud/poll    → ESP8266 polls for alerts  │
    │  ├── POST /iot/cloud/alert   → Set cloud alert           │
    │  ├── POST /iot/cloud/clear   → Clear cloud alert         │
    │  ├── GET  /iot/cloud/status  → Current alert status      │
    │  ├── GET  /iot/devices       → List registered devices   │
    │  ├── POST /iot/devices       → Register new device       │
    │  ├── DEL  /iot/devices/<ip>  → Remove device             │
    │  ├── POST /iot/alert         → Send alert to all devices │
    │  ├── POST /iot/alert/clear   → Clear all device alerts   │
    │  ├── GET  /iot/alert/history → Alert history             │
    │  ├── POST /iot/test/<ip>     → Test specific device      │
    │  ├── GET  /iot/arduino       → Download Arduino code     │
    │  ├── GET  /iot/esp8266       → Download ESP8266 code     │
    │  ├── GET  /iot/arduino/generate → Custom Arduino code    │
    │  ├── GET  /iot/esp8266/generate → Custom ESP8266 code    │
    │  └── GET  /iot/esp8266/cloud/generate → Cloud ESP code   │
    │                                                           │
    │  POST /iot/trigger-from-prediction → Auto IoT trigger    │
    └──────────────────────────────────────────────────────────┘

                                                                        Page 81

Prediction Endpoint Implementation:
The /predict endpoint accepts earthquake parameters and returns an
AI-enhanced risk assessment:

    @app.route('/predict', methods=['POST'])
    def predict():
        data = request.get_json()

        # Extract parameters
        magnitude = data.get('magnitude', 7.0)
        depth = data.get('depth', 10)
        latitude = data.get('latitude', 0)
        longitude = data.get('longitude', 90)

        # Create seismic pattern (24×32 matrix)
        input_data = create_seismic_pattern(
            magnitude, depth, latitude, longitude
        )

        # Model inference
        prediction = model.predict(
            input_data.reshape(1, 24, 32),
            verbose=0
        )
        raw_probability = float(prediction[0][0])

        # Physics-based adjustment
        depth_factor = max(0, 1 - depth / 300)
        mag_factor = min(1, (magnitude - 5) / 4)
        ocean_factor = 0.8 if (latitude < 0 or ...) else 0.3
        adjusted_prob = 0.4 * raw_probability + \
                       0.6 * (depth_factor * mag_factor * ocean_factor)

The adjusted probability combines the model's learned representation
(40%) with physics-based heuristics (60%), providing a balanced
assessment that leverages both AI pattern recognition and domain
knowledge.

Live Data Integration:
The /live-data endpoint fetches real-time earthquake data from USGS,
runs model predictions on each event, and returns enriched data with
AI-assessed risk levels:

    @app.route('/live-data')
    def get_live_data():
        # Fetch real-time earthquakes from USGS
        response = requests.get(USGS_API_URL, params={...}, timeout=15)
        data = response.json()
        # Process each earthquake through the model
        for feature in data['features']:
            # ... extract parameters, predict, assess ...
        return jsonify(enriched_data)


6.9  MODULE I: IoT HARDWARE INTEGRATION
     (iot/ — 3 Arduino/C++ programs)
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 82

Purpose:
Three hardware firmware programs enable physical alert delivery through
Arduino UNO microcontrollers and ESP8266 WiFi modules.

                              [Figure 6.9]
    ┌─────────────────────────────────────────────────────────────┐
    │          ARDUINO + ESP8266 CIRCUIT DIAGRAM                   │
    │                                                              │
    │  ┌──────────────────────┐      ┌──────────────────────────┐ │
    │  │     ARDUINO UNO      │      │       ESP8266            │ │
    │  │                      │      │                          │ │
    │  │  Pin 12 (RS) ───────────→ LCD Pin RS                   │ │
    │  │  Pin 11 (EN) ───────────→ LCD Pin EN                   │ │
    │  │  Pin 5  (D4) ───────────→ LCD Pin D4                   │ │
    │  │  Pin 4  (D5) ───────────→ LCD Pin D5                   │ │
    │  │  Pin 3  (D6) ───────────→ LCD Pin D6                   │ │
    │  │  Pin 2  (D7) ───────────→ LCD Pin D7                   │ │
    │  │                      │      │                          │ │
    │  │  Pin 8  ─────────────────→ Buzzer (+)                  │ │
    │  │                      │      │                          │ │
    │  │  Pin 7  (SoftSerial  │      │                          │ │
    │  │   TX) ──[1kΩ]──┬─────────→ RX                         │ │
    │  │                │     │      │                          │ │
    │  │            [2kΩ]     │      │                          │ │
    │  │                │     │      │                          │ │
    │  │               GND    │      │                          │ │
    │  │                      │      │                          │ │
    │  │  Pin 6  (SoftSerial  │      │                          │ │
    │  │   RX) ◄──────────────────── TX                        │ │
    │  │                      │      │                          │ │
    │  │  5V ────────────────────→ Vin (with regulator)        │ │
    │  │  GND ───────────────────→ GND                         │ │
    │  └──────────────────────┘      └──────────────────────────┘ │
    │                                                              │
    │  Note: 1kΩ/2kΩ voltage divider for 5V→3.3V level shift     │
    └─────────────────────────────────────────────────────────────┘

      Figure 6.9: Arduino + ESP8266 circuit connections

                                                                        Page 83

Table 6.6: IoT Alert Levels and Buzzer Patterns

┌──────────┬─────────────────┬──────────────────────────────────────────┐
│ Level    │ LCD Display     │ Buzzer Pattern                          │
├──────────┼─────────────────┼──────────────────────────────────────────┤
│ NONE     │ "System Normal" │ Silent                                  │
├──────────┼─────────────────┼──────────────────────────────────────────┤
│ WATCH    │ "WATCH: Monitor"│ 2 short beeps every 10 seconds          │
├──────────┼─────────────────┼──────────────────────────────────────────┤
│ ADVISORY │ "ADVISORY: Prep"│ 3 beeps every 5 seconds                 │
├──────────┼─────────────────┼──────────────────────────────────────────┤
│ WARNING  │ "⚠ WARNING ⚠"  │ Continuous rapid tone (200ms on/off)    │
├──────────┼─────────────────┼──────────────────────────────────────────┤
│ CRITICAL │ "!! EVACUATE !!"│ Continuous solid tone with brief pauses │
└──────────┴─────────────────┴──────────────────────────────────────────┘

Communication Modes:

Mode 1 — WiFi HTTP Server (esp8266_wifi.ino):
The ESP8266 runs an HTTP server on port 80 with three endpoints:
- POST /alert: Receives alert data as JSON, forwards to Arduino
- POST /clear: Clears current alert
- POST /test: Tests device connectivity

The cloud server pushes alerts by making HTTP POST requests to each
registered device's IP address. This mode requires the ESP8266 to
have a publicly reachable IP address (or be on the same local network
as the server).

Mode 2 — Cloud Polling (esp8266_cloud.ino):
The ESP8266 periodically (every 5 seconds) polls the server endpoint
/iot/cloud/poll via HTTP GET. If an alert is pending, the server
responds with alert data; otherwise, it returns an empty response.

This mode solves the NAT/firewall problem: the ESP8266 initiates all
connections (outbound GET requests), which is always allowed through
NAT gateways, firewalls, and residential routers. No inbound port
forwarding or dynamic DNS is required.

    // From esp8266_cloud.ino
    void checkForAlerts() {
        HTTPClient http;
        http.begin(client, serverURL + "/iot/cloud/poll");
        int httpCode = http.GET();
        if (httpCode == 200) {
            String payload = http.getString();
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);
            if (doc["has_alert"]) {
                String level = doc["level"];
                String message = doc["message"];
                sendToArduino(level, message);
            }
        }
        http.end();
    }

                                                                        Page 84

6.10  MODULE J: UTILITY MODULES
      (src/utils/ — config_loader.py, logger.py, data_helpers.py)
────────────────────────────────────────────────────────────────────────────────

Three utility modules provide cross-cutting infrastructure services:

(1) config_loader.py: Loads and parses the YAML configuration file
    (config/config.yaml), providing a centralized configuration
    management system. All configurable parameters — API URLs, region
    boundaries, model hyperparameters, alert thresholds, system
    intervals — are externalized in YAML rather than hard-coded.

(2) logger.py: Configures the Loguru logging framework with:
    - Console output (INFO level) for operator monitoring
    - File output (logs/app.log, DEBUG level) for debugging
    - 100 MB rotation to prevent disk exhaustion
    - 30-day retention for log files
    - Compressed archive of rotated logs

    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add("logs/app.log",
               rotation="100 MB",
               retention="30 days",
               level="DEBUG",
               compression="zip")

(3) data_helpers.py: Provides utility functions for:
    - Downloading historical tsunami databases from NOAA NGDC
    - Generating synthetic training samples with configurable positive
      class ratio (default: 5% positive, 95% negative)
    - Creating sample datasets of 1,000 samples for development

Design Decisions:
(1) YAML configuration was chosen over environment variables or JSON
    because YAML supports comments (essential for documenting
    configuration choices) and nested structures (grouping related
    parameters under logical keys).
(2) Loguru was selected over Python's built-in logging module for its
    simpler API, automatic exception formatting, and native file
    rotation and compression support.

