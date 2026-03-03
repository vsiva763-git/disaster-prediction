
================================================================================
                          PART IV — RESULTS AND ANALYSIS
================================================================================


================================================================================
CHAPTER 9    EXPERIMENTAL RESULTS AND PERFORMANCE EVALUATION
================================================================================
                                                                        Page 100

This chapter presents the experimental results of the India-Specific
Tsunami Early Warning System, including model training performance,
classification metrics, real-time system evaluation, and comparative
analysis.


9.1  MODEL TRAINING RESULTS
────────────────────────────────────────────────────────────────────────────────

The CNN-LSTM binary model was trained on the Kaggle GPU platform
(Tesla T4 × 2) using the following dataset configuration:

Table 9.1: Training Dataset Characteristics

┌────────────────────────────┬──────────────────────────────────────────┐
│ Parameter                  │ Value                                    │
├────────────────────────────┼──────────────────────────────────────────┤
│ Total Samples              │ 8,000                                    │
├────────────────────────────┼──────────────────────────────────────────┤
│ Positive Samples (Tsunami) │ 3,182 (39.78%)                           │
├────────────────────────────┼──────────────────────────────────────────┤
│ Negative Samples (No Tsun.)│ 4,818 (60.22%)                           │
├────────────────────────────┼──────────────────────────────────────────┤
│ Training Set (80%)         │ 6,400 samples                            │
├────────────────────────────┼──────────────────────────────────────────┤
│ Validation Set (20%)       │ 1,600 samples                            │
├────────────────────────────┼──────────────────────────────────────────┤
│ Input Dimensions           │ (24, 32) — 24 timesteps × 32 features   │
├────────────────────────────┼──────────────────────────────────────────┤
│ Class Ratio                │ 1:1.51 (mild imbalance)                  │
├────────────────────────────┼──────────────────────────────────────────┤
│ Training Duration          │ 8 epochs (early stopped at epoch 8)      │
├────────────────────────────┼──────────────────────────────────────────┤
│ Best Epoch                 │ 8 (highest val_auc)                      │
├────────────────────────────┼──────────────────────────────────────────┤
│ Final Learning Rate        │ 0.0005 (no reduction triggered)          │
└────────────────────────────┴──────────────────────────────────────────┘

                                                                        Page 101

9.1.1  Training Convergence

The model converged rapidly, achieving near-perfect validation metrics
within 8 epochs. The following table presents the per-epoch training
progression (data from model_metadata.json):

Table 9.2: Per-Epoch Training Metrics

┌───────┬───────────┬───────────┬────────────┬────────────┬─────────────┐
│ Epoch │ Train Loss│ Val Loss  │ Train Acc  │ Val Acc    │ Val AUC     │
├───────┼───────────┼───────────┼────────────┼────────────┼─────────────┤
│ 1     │ 0.2481    │ 0.0832    │ 91.23%     │ 96.44%     │ 0.9891      │
│ 2     │ 0.0614    │ 0.0501    │ 97.55%     │ 97.81%     │ 0.9956      │
│ 3     │ 0.0389    │ 0.0398    │ 98.42%     │ 98.12%     │ 0.9972      │
│ 4     │ 0.0287    │ 0.0321    │ 98.89%     │ 98.56%     │ 0.9983      │
│ 5     │ 0.0219    │ 0.0275    │ 99.14%     │ 98.69%     │ 0.9989      │
│ 6     │ 0.0178    │ 0.0246    │ 99.33%     │ 98.75%     │ 0.9993      │
│ 7     │ 0.0142    │ 0.0221    │ 99.52%     │ 98.81%     │ 0.9996      │
│ 8     │ 0.0117    │ 0.0198    │ 99.64%     │ 98.94%     │ 0.9998      │
└───────┴───────────┴───────────┴────────────┴────────────┴─────────────┘

                              [Figure 9.1]
    Training & Validation Loss Over Epochs

    Loss
    0.25 ┤
         │ ■
    0.20 ┤ │
         │ │  □
    0.15 ┤ │     □
         │ │
    0.10 ┤ │         ■
         │ │  ■      □     □
    0.05 ┤ │     ■      ■     ■     □     □
         │ │        □      □     ■     ■     ■
    0.00 ┤ └──────────────────────────────────────→ Epoch
         0    1    2    3    4    5    6    7    8

    ■ = Training Loss,  □ = Validation Loss

    Figure 9.1: Training and validation loss convergence

                                                                        Page 102

                              [Figure 9.2]
    Training & Validation Accuracy Over Epochs

    Accuracy (%)
    100  ┤                              ■─────■────■────■
         │                     ■─────■                      □────□
      99 ┤              ■─────                         □
         │         ■                         □────□
      98 ┤    ■                    □────□
         │              □────□
      97 ┤    □
         │
      96 ┤ □
         │
      95 ┤
         │
      94 ┤
         │
      93 ┤
         │
      92 ┤
         │ ■
      91 ┤ └──────────────────────────────────────→ Epoch
         0    1    2    3    4    5    6    7    8

    ■ = Training Accuracy,  □ = Validation Accuracy

    Figure 9.2: Training and validation accuracy progression


9.2  CLASSIFICATION METRICS ON TEST SET
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 103

Table 9.3: Test Set Classification Performance

┌─────────────────────────────┬────────────────────────────────────────┐
│ Metric                      │ Value                                  │
├─────────────────────────────┼────────────────────────────────────────┤
│ Test Accuracy               │ 100.00%                                │
├─────────────────────────────┼────────────────────────────────────────┤
│ Test AUC (ROC)              │ 1.0000                                 │
├─────────────────────────────┼────────────────────────────────────────┤
│ Test Recall (Sensitivity)   │ 100.00%                                │
├─────────────────────────────┼────────────────────────────────────────┤
│ Test Precision              │ 100.00%                                │
├─────────────────────────────┼────────────────────────────────────────┤
│ Test Specificity            │ 100.00%                                │
├─────────────────────────────┼────────────────────────────────────────┤
│ F1-Score                    │ 1.0000                                 │
├─────────────────────────────┼────────────────────────────────────────┤
│ Classification Threshold    │ 0.10                                   │
├─────────────────────────────┼────────────────────────────────────────┤
│ Model Parameters            │ ~350,000                               │
├─────────────────────────────┼────────────────────────────────────────┤
│ Model File Size             │ 2.1 MB                                 │
├─────────────────────────────┼────────────────────────────────────────┤
│ Validation Accuracy         │ 98.94%                                 │
├─────────────────────────────┼────────────────────────────────────────┤
│ Validation AUC              │ 0.9998                                 │
├─────────────────────────────┼────────────────────────────────────────┤
│ Validation Recall           │ 97.23%                                 │
└─────────────────────────────┴────────────────────────────────────────┘

9.2.1  Confusion Matrix

Table 9.4: Confusion Matrix (Test Set at Threshold = 0.10)

┌─────────────────────┬─────────────────────┬─────────────────────┐
│ Predicted →         │ Predicted Negative  │ Predicted Positive  │
│ Actual ↓            │ (No Tsunami)        │ (Tsunami)           │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ Actual Negative     │ TN = 964            │ FP = 0              │
│ (No Tsunami)        │                     │                     │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ Actual Positive     │ FN = 0              │ TP = 636            │
│ (Tsunami)           │                     │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘

    Total Test Samples:    1,600
    True Positives:        636  (all tsunamigenic events correctly identified)
    True Negatives:        964  (all non-tsunamigenic events correctly rejected)
    False Positives:       0    (no false alarms)
    False Negatives:       0    (no missed tsunamis)

                                                                        Page 104

9.2.2  ROC Curve Analysis

                              [Figure 9.3]
    ROC Curve (AUC = 1.0000)

    TPR (Sensitivity)
    1.0  ┤ ■──────────────────────────────────────
         │ │
    0.9  ┤ │
         │ │
    0.8  ┤ │
         │ │
    0.7  ┤ │
         │ │
    0.6  ┤ │
         │ │
    0.5  ┤ │
         │ │
    0.4  ┤ │
         │ │
    0.3  ┤ │
         │ │
    0.2  ┤ │
         │ │
    0.1  ┤ │
         │ │
    0.0  ┤ └──────────────────────────────────────→ FPR
         0.0  0.1  0.2  0.3  0.4  0.5  0.6  0.7  0.8  0.9  1.0

    Figure 9.3: ROC curve showing perfect discrimination (AUC = 1.0)

    The ROC curve hugs the upper-left corner, indicating that the model
    achieves 100% sensitivity at 0% false positive rate across all
    threshold values. The Area Under Curve (AUC) of 1.0 represents
    theoretically perfect binary discrimination.

9.2.3  Threshold Analysis
The model uses a threshold of 0.10 (rather than the standard 0.50)
for binary classification. This lowered threshold was selected to
maximize recall for tsunami detection — a domain where false negatives
(missed tsunamis) carry catastrophically higher cost than false
positives (false alarms).

    Decision rule:  ŷ = 1 if sigmoid(output) ≥ 0.10, else ŷ = 0

With AUC = 1.0, all positive samples have predicted probabilities > 0.10
and all negative samples have predicted probabilities < 0.10, so the
threshold could be set anywhere in the separation gap without affecting
classification performance on this test set.

                                                                        Page 105

9.3  FOCAL LOSS EFFECTIVENESS
────────────────────────────────────────────────────────────────────────────────

Binary Focal Loss (γ=2.0, α=0.25) was employed to handle the mild class
imbalance (39.78% positive, 60.22% negative). Its effectiveness can be
quantified by comparing with standard Binary Cross-Entropy:

Table 9.5: Focal Loss vs Binary Cross-Entropy Comparison

┌──────────────────────────┬──────────────┬──────────────────────────────┐
│ Metric                   │ Focal Loss   │ Binary Cross-Entropy (est.) │
├──────────────────────────┼──────────────┼──────────────────────────────┤
│ Convergence Epochs       │ 8            │ 12–15 (estimated)            │
├──────────────────────────┼──────────────┼──────────────────────────────┤
│ Final Train Loss         │ 0.0117       │ ~0.03–0.05                   │
├──────────────────────────┼──────────────┼──────────────────────────────┤
│ Minority Class Recall    │ 100.00%      │ ~95–98% (estimated)          │
├──────────────────────────┼──────────────┼──────────────────────────────┤
│ Gradient Stability       │ High         │ Moderate                     │
├──────────────────────────┼──────────────┼──────────────────────────────┤
│ Hard Example Focus       │ Strong (γ=2) │ None                         │
└──────────────────────────┴──────────────┴──────────────────────────────┘

The Focal Loss modulating factor $(1 - p_t)^\gamma$ with $\gamma = 2.0$
effectively down-weights easy-to-classify examples. For a well-classified
negative sample with $p_t = 0.95$:

    Focal weight: $(1 - 0.95)^2 = 0.0025$

This reduces the contribution of easy negatives by a factor of 400,
allowing the model to focus training signal on the harder, more
informative examples near the decision boundary.


9.4  FEATURE IMPORTANCE ANALYSIS
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 106

Table 9.6: Feature Importance Ranking (from model_metadata.json)

┌──────┬────────────────────────────┬──────────────────────────────────────┐
│ Rank │ Feature                    │ Importance Score                     │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 1    │ Magnitude                  │ 0.3215 (highest)                     │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 2    │ Depth                      │ 0.2847                               │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 3    │ Distance to subduction zone│ 0.1893                               │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 4    │ Latitude                   │ 0.0812                               │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 5    │ Longitude                  │ 0.0645                               │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 6    │ Ocean depth (bathymetry)   │ 0.0340                               │
├──────┼────────────────────────────┼──────────────────────────────────────┤
│ 7    │ Historical frequency       │ 0.0248                               │
└──────┴────────────────────────────┴──────────────────────────────────────┘

The feature importance analysis confirms domain expectations:
(1) Magnitude is the strongest predictor, consistent with the known
    physical relationship between earthquake magnitude and tsunami
    generation potential.
(2) Depth is the second most important feature, reflecting the
    geological principle that shallow earthquakes (< 70 km) are far
    more likely to displace water vertically and generate tsunamis.
(3) Distance to subduction zone captures the geological understanding
    that tsunamigenic earthquakes overwhelmingly occur along subduction
    zone boundaries.
(4) Geographic coordinates (latitude, longitude) capture region-specific
    patterns in tsunamigenesis.

                                                                        Page 107

9.5  REAL-TIME SYSTEM PERFORMANCE
────────────────────────────────────────────────────────────────────────────────

Table 9.7: System Response Times (Measured on Railway Deployment)

┌───────────────────────────────┬───────────────────────────────────────────┐
│ Operation                     │ Latency                                   │
├───────────────────────────────┼───────────────────────────────────────────┤
│ /health endpoint              │ < 50 ms                                   │
├───────────────────────────────┼───────────────────────────────────────────┤
│ /predict (single inference)   │ 100–300 ms                                │
├───────────────────────────────┼───────────────────────────────────────────┤
│ /batch-predict (10 events)    │ 500–1,200 ms                              │
├───────────────────────────────┼───────────────────────────────────────────┤
│ /live-data (USGS fetch + AI)  │ 2–5 seconds                               │
├───────────────────────────────┼───────────────────────────────────────────┤
│ /wave-data (NOAA fetch)       │ 1–3 seconds                               │
├───────────────────────────────┼───────────────────────────────────────────┤
│ Model loading (cold start)    │ 3–8 seconds                               │
├───────────────────────────────┼───────────────────────────────────────────┤
│ IoT cloud polling cycle       │ < 100 ms (server-side)                    │
├───────────────────────────────┼───────────────────────────────────────────┤
│ End-to-end alert delivery     │ 5–15 seconds (earthquake → IoT buzzer)    │
│ (monitoring mode)             │                                           │
├───────────────────────────────┼───────────────────────────────────────────┤
│ Dashboard refresh             │ 30 seconds (configurable)                 │
└───────────────────────────────┴───────────────────────────────────────────┘

9.5.1  India Impact Filter Performance
The India Impact Filter's hierarchical multi-step evaluation provides
efficient processing:

Table 9.8: India Filter Processing Stages (10,000 Test Events)

┌───────────────────────────┬──────────┬───────────────────────────────────┐
│ Stage                     │ Events   │ Percentage Filtered               │
│                           │ Passing  │                                   │
├───────────────────────────┼──────────┼───────────────────────────────────┤
│ Stage 1: Model threshold  │ 4,200    │ 58% rejected (low probability)   │
│ (pred ≥ 0.25)            │          │                                   │
├───────────────────────────┼──────────┼───────────────────────────────────┤
│ Stage 2: Critical zone    │ 1,680    │ 60% of remaining rejected        │
│ check                     │          │ (outside zones)                   │
├───────────────────────────┼──────────┼───────────────────────────────────┤
│ Stage 3: Distance check   │ 840      │ 50% of remaining rejected        │
│ (≤ 3000 km)              │          │ (too far from India)              │
├───────────────────────────┼──────────┼───────────────────────────────────┤
│ Stage 4: Full assessment  │ 840      │ 8.4% proceed to full assessment  │
└───────────────────────────┴──────────┴───────────────────────────────────┘

This cascading filter design reduces computational load by 91.6%,
preventing unnecessary risk assessments for events that clearly do
not affect India.

                                                                        Page 108

9.6  SYSTEM SCENARIO EVALUATION
────────────────────────────────────────────────────────────────────────────────

Five representative earthquake scenarios were evaluated through the
complete prediction pipeline:

Table 9.9: End-to-End Scenario Evaluation Results

┌────┬────────────────────┬──────┬───────┬────────┬────────┬──────────┐
│ #  │ Scenario           │ Mag  │ Depth │ Model  │ Adj.   │ Risk     │
│    │                    │ (Mw) │ (km)  │ Prob.  │ Prob.  │ Level    │
├────┼────────────────────┼──────┼───────┼────────┼────────┼──────────┤
│ 1  │ Andaman M7.5       │ 7.5  │ 10    │ 0.94   │ 0.87   │ HIGH     │
│    │ (3.3°N, 95.8°E)    │      │       │        │        │          │
├────┼────────────────────┼──────┼───────┼────────┼────────┼──────────┤
│ 2  │ Makran M6.8        │ 6.8  │ 45    │ 0.71   │ 0.58   │ MEDIUM   │
│    │ (25.1°N, 63.2°E)   │      │       │        │        │          │
├────┼────────────────────┼──────┼───────┼────────┼────────┼──────────┤
│ 3  │ Deep Interior M5.2 │ 5.2  │ 120   │ 0.05   │ 0.02   │ MINIMAL  │
│    │ (28.5°N, 77.0°E)   │      │       │        │        │          │
├────┼────────────────────┼──────┼───────┼────────┼────────┼──────────┤
│ 4  │ Pacific M8.0       │ 8.0  │ 15    │ 0.96   │ 0.35   │ LOW      │
│    │ (40.5°N, 143.0°E)  │      │       │        │        │ (not     │
│    │                    │      │       │        │        │ India)   │
├────┼────────────────────┼──────┼───────┼────────┼────────┼──────────┤
│ 5  │ Weak Coastal M4.5  │ 4.5  │ 80    │ 0.02   │ 0.01   │ MINIMAL  │
│    │ (13.0°N, 80.3°E)   │      │       │        │        │          │
└────┴────────────────────┴──────┴───────┴────────┴────────┴──────────┘

Analysis:
(1) Scenario 1 (Andaman M7.5, shallow): Both raw and adjusted
    probabilities are high because the earthquake characteristics
    match historical tsunamigenic profiles (high magnitude, shallow
    depth, subduction zone location). Risk level: HIGH.

(2) Scenario 2 (Makran M6.8, moderate depth): The model assigns
    moderate probability; physics-based adjustment reduces it slightly
    due to the 45-km depth. Risk level: MEDIUM, reflecting genuine
    threat from the Makran subduction zone.

(3) Scenario 3 (Deep Interior M5.2): Very low probability from both
    model and physics components. The earthquake is too small (M5.2)
    and too deep (120 km) to generate a tsunami. Risk level: MINIMAL.

(4) Scenario 4 (Pacific M8.0): High raw model probability (0.96)
    because the earthquake has strong tsunamigenic characteristics.
    However, the adjusted probability (0.35) is significantly reduced
    by the India Impact Filter, which correctly identifies that a
    Pacific earthquake at 143°E does not threaten India. Risk level:
    LOW (classified as not India-relevant).

(5) Scenario 5 (Weak Coastal M4.5): Very low probabilities across
    all components. An M4.5 earthquake is below the tsunamigenic
    threshold regardless of location. Risk level: MINIMAL.

                                                                        Page 109

9.7  WEB DASHBOARD EVALUATION
────────────────────────────────────────────────────────────────────────────────

The web-based live dashboard (index_live.html) provides real-time
visualization of earthquake data and tsunami risk assessments. Key
interface components evaluated:

Table 9.10: Dashboard Components and Functionality

┌───────────────────────────┬──────────────────────────────────────────────┐
│ Component                 │ Functionality                                │
├───────────────────────────┼──────────────────────────────────────────────┤
│ Interactive Map (Leaflet) │ Displays earthquake epicenters with color-   │
│                           │ coded risk markers. Red=HIGH, Orange=MEDIUM, │
│                           │ Yellow=LOW, Green=MINIMAL. Clickable popups  │
│                           │ show detailed earthquake parameters.         │
├───────────────────────────┼──────────────────────────────────────────────┤
│ Alert Banner              │ Top-of-page alert with color-coded           │
│                           │ background. Displays current system status   │
│                           │ and most recent alert level.                 │
├───────────────────────────┼──────────────────────────────────────────────┤
│ Statistics Panel          │ Displays system metrics: total earthquakes,  │
│                           │ tsunamigenic events, average magnitude,      │
│                           │ data freshness.                              │
├───────────────────────────┼──────────────────────────────────────────────┤
│ Recent Earthquakes Table  │ Sortable table of recent seismic events with │
│                           │ magnitude, depth, location, time, and AI     │
│                           │ risk assessment.                             │
├───────────────────────────┼──────────────────────────────────────────────┤
│ Wave Animation Canvas     │ HTML5 Canvas-based real-time wave simulation │
│                           │ showing wave propagation from epicenter.     │
├───────────────────────────┼──────────────────────────────────────────────┤
│ IoT Device Manager        │ Lists registered devices, enables manual     │
│                           │ test alerts, shows device connectivity.      │
└───────────────────────────┴──────────────────────────────────────────────┘

[Figure 9.7: Screenshot description — The live dashboard showing an
interactive Leaflet map of the Indian Ocean region with multiple
colored earthquake markers, a green "No Active Threat" banner at the
top, statistics panel on the left showing 47 earthquakes detected and
0 tsunami warnings, and a recent earthquakes table at the bottom with
sortable columns.]


9.8  LIMITATIONS OF RESULTS
────────────────────────────────────────────────────────────────────────────────

While the model achieves perfect classification on the test set, several
limitations must be acknowledged:

(1) Synthetic Training Data: The dataset is partially synthetic
    (generated using data_helpers.py), which may not capture the full
    complexity of real-world seismic patterns. Perfect test metrics may
    not generalize to unseen real-world events.

(2) Limited Real-World Validation: No real tsunami event has occurred
    in the Indian Ocean during the system's deployment period to
    validate detection in a true emergency scenario.

(3) Overfitting Risk: Perfect test metrics (100% across all measures)
    may indicate overfitting to the training data distribution, despite
    Focal Loss and Dropout regularization.

(4) Distribution Shift: The model was trained on data with specific
    magnitude, depth, and location distributions. Earthquakes with
    parameters outside these distributions may produce unreliable
    predictions.

(5) External API Dependency: Real-time performance depends on USGS,
    NOAA, and INCOIS API availability. Service outages or rate limiting
    could degrade system capability.

