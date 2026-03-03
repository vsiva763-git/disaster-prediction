
================================================================================
CHAPTER 5    CORE ALGORITHMS AND LOGIC
================================================================================
                                                                        Page 54

5.1  ALGORITHM 1: BINARY FOCAL LOSS FUNCTION
────────────────────────────────────────────────────────────────────────────────

Purpose:
Binary Focal Loss addresses the extreme class imbalance in tsunami
datasets where tsunamigenic events constitute less than 5% of all
significant earthquakes. Standard cross-entropy loss assigns equal
importance to all samples, causing the model to be dominated by the
overwhelming majority of easy negative examples. Focal Loss introduces
a modulating factor that down-weights well-classified examples and
focuses training on hard, misclassified samples [Lin et al., 2017].

Mathematical Formulation:

For a binary classification task, let y ∈ {0, 1} be the ground truth
label and p ∈ [0, 1] be the model's predicted probability for the
positive class. Define:

    p_t = p     if y = 1
    p_t = 1-p   if y = 0

The standard Binary Cross-Entropy (BCE) loss is:
    BCE(p_t) = -log(p_t)

Focal Loss modifies this by introducing two parameters:
    FL(p_t) = -α_t × (1 - p_t)^γ × log(p_t)

where:
- α_t (alpha): Class balancing factor. Set to α = 0.25 for the
  positive class and (1-α) = 0.75 for the negative class. This
  compensates for the lower prevalence of positive (tsunami) samples.
- γ (gamma): Focusing parameter. Set to γ = 2.0. This determines how
  aggressively well-classified examples are down-weighted.

                                                                        Page 55

The modulating factor (1 - p_t)^γ has the following effect:
- For a well-classified positive example (p_t → 1.0):
  (1 - p_t)^γ → 0, making the loss contribution nearly zero.
- For a misclassified positive example (p_t → 0.0):
  (1 - p_t)^γ → 1, preserving the full loss contribution.

This focusing mechanism ensures that the model's gradient updates are
dominated by hard, informative examples rather than the abundant easy
negatives that constitute >95% of the training data.

Pseudocode:

    ALGORITHM: BINARY_FOCAL_LOSS
    INPUT:  y_true (ground truth labels, shape [batch_size])
            y_pred (predicted probabilities, shape [batch_size])
            gamma  (focusing parameter, default 2.0)
            alpha  (balancing parameter, default 0.25)
    OUTPUT: loss (scalar loss value)

    1.  epsilon ← machine_epsilon    // ~1e-7
    2.  y_pred ← CLIP(y_pred, epsilon, 1 - epsilon)   // prevent log(0)
    3.
    4.  // Compute standard cross-entropy
    5.  cross_entropy ← -y_true × LOG(y_pred)
    6.                   - (1 - y_true) × LOG(1 - y_pred)
    7.
    8.  // Compute focal modulation weight
    9.  focal_weight ← y_true × alpha × (1 - y_pred)^gamma
    10.                + (1 - y_true) × (1 - alpha) × y_pred^gamma
    11.
    12. // Apply focal weight to cross-entropy
    13. focal_loss ← focal_weight × cross_entropy
    14.
    15. // Reduce to scalar
    16. loss ← MEAN(focal_loss)
    17.
    18. RETURN loss

Time Complexity: O(n) where n is the batch size — identical to standard
cross-entropy loss. The additional element-wise exponentiation and
multiplication do not change the asymptotic complexity.

Space Complexity: O(n) for intermediate tensors (cross_entropy,
focal_weight, focal_loss).


5.2  ALGORITHM 2: HAVERSINE DISTANCE CALCULATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 56

Purpose:
The Haversine formula calculates the great-circle distance between two
points on the Earth's surface, given their latitudes and longitudes.
This is used throughout the system for: (a) calculating the distance
from an earthquake epicenter to India's coastline; (b) estimating
tsunami arrival times based on distance and propagation speed; and
(c) determining which coastal regions are within the impact radius of
a tsunamigenic earthquake.

Mathematical Formulation:

Given two points with coordinates (φ₁, λ₁) and (φ₂, λ₂) in radians:

    a = sin²(Δφ/2) + cos(φ₁) × cos(φ₂) × sin²(Δλ/2)

    c = 2 × arcsin(√a)

    d = R × c

where:
- Δφ = φ₂ - φ₁ (difference in latitude)
- Δλ = λ₂ - λ₁ (difference in longitude)
- R = 6,371 km (Earth's mean radius)
- d = distance between the two points along the great circle

                                                                        Page 57

Pseudocode:

    ALGORITHM: HAVERSINE_DISTANCE
    INPUT:  lat1, lon1 (coordinates of point 1 in degrees)
            lat2, lon2 (coordinates of point 2 in degrees)
    OUTPUT: distance (great-circle distance in kilometers)

    1.  R ← 6371                           // Earth radius in km
    2.  φ₁ ← RADIANS(lat1)
    3.  λ₁ ← RADIANS(lon1)
    4.  φ₂ ← RADIANS(lat2)
    5.  λ₂ ← RADIANS(lon2)
    6.  Δφ ← φ₂ - φ₁
    7.  Δλ ← λ₂ - λ₁
    8.  a ← sin²(Δφ / 2) + cos(φ₁) × cos(φ₂) × sin²(Δλ / 2)
    9.  c ← 2 × arcsin(√a)
    10. distance ← R × c
    11. RETURN distance

Implementation (from src/filtering/india_impact_filter.py):

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(np.radians,
                                      [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + \
            np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

Time Complexity: O(1) — constant time for a single distance
calculation. Trigonometric functions are computed in constant time.

Space Complexity: O(1) — requires only scalar intermediate variables.

Accuracy: The Haversine formula assumes a perfectly spherical Earth,
introducing a maximum error of approximately 0.3% compared with the
Vincenty formula for an oblate spheroid. This level of accuracy is
more than sufficient for tsunami warning purposes, where the relevant
distances span hundreds to thousands of kilometers.


5.3  ALGORITHM 3: INDIA RISK SCORE COMPUTATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 58

Purpose:
The India Risk Score is a composite metric that combines the AI model's
raw prediction probability with four geographic and geophysical factors
to produce a single scalar assessment of tsunami risk to India. This
score determines the alert level and drives the decision to issue
warnings.

Mathematical Formulation:

    IRS = w₁ × model_risk + w₂ × location_threat +
          w₃ × distance_factor + w₄ × propagation_factor +
          w₅ × depth_factor

where:
- w₁ = 0.35 (model prediction weight)
- w₂ = 0.25 (location threat weight)
- w₃ = 0.20 (distance factor weight)
- w₄ = 0.10 (propagation direction weight)
- w₅ = 0.10 (earthquake depth weight)
- Σwᵢ = 1.00

Each factor is normalized to the range [0, 1]:

model_risk:       Raw sigmoid output of the CNN-LSTM model.
location_threat:  1.0 if epicenter is in Andaman subduction zone,
                  0.8 if in Makran zone, 0.5 if in other critical
                  zones, 0.0 otherwise.
distance_factor:  1 - (distance / critical_radius). Normalized so
                  that 0 km distance → 1.0, and distances ≥ 3000 km
                  → 0.0.
propagation:      1.0 for M≥8.0 (omnidirectional), 0.8 for M≥7.0,
                  scaled by distance for smaller events.
depth_factor:     Based on magnitude-depth matrix (see Table 5.1).

                                                                        Page 59

Table 5.1: Tsunami Capability Assessment Matrix

┌───────────────────┬──────────────────────────────────────────────────┐
│ Magnitude Range   │ Depth < 40km │ Depth 40-70km │ Depth 70-100km  │
│                   │              │               │ Depth > 100km   │
├───────────────────┼──────────────┼───────────────┼─────────────────┤
│ M ≥ 7.5           │ 1.0          │ 1.0           │ 0.7 / 0.3      │
├───────────────────┼──────────────┼───────────────┼─────────────────┤
│ M 7.0 – 7.5       │ 1.0          │ 0.6           │ 0.2 / 0.0      │
├───────────────────┼──────────────┼───────────────┼─────────────────┤
│ M 6.5 – 7.0       │ 0.8          │ 0.4           │ 0.1 / 0.0      │
├───────────────────┼──────────────┼───────────────┼─────────────────┤
│ M < 6.5            │ 0.3          │ 0.1           │ 0.0 / 0.0      │
└───────────────────┴──────────────┴───────────────┴─────────────────┘

Note: Shallow-focus, large-magnitude earthquakes receive the highest
depth factor because they are most likely to displace the water column
vertically — the primary mechanism for tsunami generation.

Pseudocode:

    ALGORITHM: INDIA_RISK_SCORE
    INPUT:  model_risk (float, 0-1)
            earthquake_data (dict: magnitude, depth, lat, lon)
            critical_zones (dict)
            india_coastline (dict)
    OUTPUT: india_risk_score (float, 0-1)
            risk_level (string: HIGH/MEDIUM/LOW/NONE)
            affected_regions (list of strings)

    1.  location_threat ← EVALUATE_LOCATION(lat, lon, critical_zones)
    2.  distance ← MIN(HAVERSINE(lat, lon, region) for region in coastline)
    3.  distance_factor ← MAX(0, 1 - distance / 3000)
    4.  propagation ← EVALUATE_PROPAGATION(lat, lon, magnitude)
    5.  depth_factor ← ASSESS_DEPTH(depth, magnitude)
    6.
    7.  IRS ← 0.35 × model_risk + 0.25 × location_threat
    8.       + 0.20 × distance_factor + 0.10 × propagation
    9.       + 0.10 × depth_factor
    10.
    11. IF IRS ≥ 0.75 THEN risk_level ← "HIGH"
    12. ELSE IF IRS ≥ 0.50 THEN risk_level ← "MEDIUM"
    13. ELSE IF IRS ≥ 0.25 THEN risk_level ← "LOW"
    14. ELSE risk_level ← "NONE"
    15.
    16. affected ← IDENTIFY_AFFECTED_REGIONS(lat, lon, magnitude)
    17. RETURN (IRS, risk_level, affected)

Time Complexity: O(k) where k is the number of coastal regions (3 in
the current configuration: west coast, east coast, Andaman/Nicobar).

Space Complexity: O(k) for storing affected region identifiers.

                                                                        Page 60

5.4  ALGORITHM 4: SEISMIC PATTERN SYNTHESIS
────────────────────────────────────────────────────────────────────────────────

Purpose:
In the standalone deployment mode (app.py), real-time earthquake data
from the USGS API consists of a single set of parameters (magnitude,
depth, latitude, longitude) rather than a 24-timestep sequence. The
seismic pattern synthesis algorithm converts these scalar parameters
into a 24×32 input matrix compatible with the CNN-LSTM model by
generating synthetic temporal evolution features using sinusoidal
modulation.

Mathematical Formulation:
For timestep t ∈ {0, 1, ..., 23} and base features [M, D, lat, lon]:

    feature[t][0] = M × sin(2π × t / 24)           // magnitude temporal
    feature[t][1] = D × cos(2π × t / 24)           // depth temporal
    feature[t][2] = lat + 0.1 × sin(2π × t / 12)   // latitude variation
    feature[t][3] = lon + 0.1 × cos(2π × t / 12)   // longitude variation
    feature[t][4..31] = f(M, D, lat, lon, t)        // derived features

Pseudocode:

    ALGORITHM: CREATE_SEISMIC_PATTERN
    INPUT:  magnitude (float), depth (float)
            latitude (float), longitude (float)
    OUTPUT: pattern (ndarray, shape [24, 32])

    1.  pattern ← ZEROS(24, 32)
    2.  mag_factor ← magnitude / 10.0
    3.  depth_factor ← MIN(depth, 700) / 700.0
    4.
    5.  FOR t ← 0 TO 23:
    6.      time_factor ← sin(2π × t / 24)
    7.      pattern[t][0] ← magnitude × time_factor
    8.      pattern[t][1] ← depth_factor × cos(2π × t / 24)
    9.      pattern[t][2] ← latitude / 90.0
    10.     pattern[t][3] ← longitude / 180.0
    11.     pattern[t][4] ← mag_factor × (1 + 0.1 × time_factor)
    12.     pattern[t][5] ← depth_factor × (1 - 0.05 × time_factor)
    13.     // ... remaining features filled with derived values
    14.     pattern[t][31] ← mag_factor × depth_factor × time_factor
    15. END FOR
    16.
    17. RETURN pattern

                                                                        Page 61

Design Rationale:
The sinusoidal modulation serves two purposes. First, it creates
variation across timesteps to provide meaningful input to the LSTM
layers, which would otherwise receive identical values at each timestep
(since a single earthquake provides only one set of parameters).
Second, the sinusoidal waveforms loosely model the fact that seismic
signals exhibit temporal evolution — P-waves arrive first, followed by
S-waves and surface waves, with amplitude changing over time.

This approach is an engineering compromise: it enables the pre-trained
CNN-LSTM model to be used in the standalone deployment mode without
requiring access to the full data collection pipeline. The physics-
based adjustment applied after model prediction (40% model + 60%
physics) compensates for any information loss in the synthetic pattern.

Time Complexity: O(T × F) where T = 24 (timesteps) and F = 32
(features), yielding O(768) — effectively constant time.


5.5  ALGORITHM 5: TSUNAMI ARRIVAL TIME ESTIMATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 62

Purpose:
When a tsunami threat is confirmed, estimating arrival times at
specific coastal locations enables evacuation planning. The algorithm
calculates the estimated time for tsunami waves to travel from the
earthquake epicenter to each affected Indian coastal region.

Mathematical Formulation:

    travel_time = distance / tsunami_speed

where:
- distance: Haversine great-circle distance (km) from epicenter to
  coastal region center
- tsunami_speed: 700 km/h (average deep-ocean tsunami propagation
  speed, derived from c = √(gh) at h ≈ 4000m depth)

The arrival time is then:
    arrival = earthquake_time + travel_time

Region center coordinates used for calculation:

    West Coast:        (15.0°N, 73.0°E)   // Goa/Karnataka coast
    East Coast:        (13.0°N, 80.0°E)   // Tamil Nadu/Andhra coast
    Andaman & Nicobar: (11.0°N, 92.5°E)   // Port Blair

Pseudocode:

    ALGORITHM: ESTIMATE_ARRIVAL_TIMES
    INPUT:  earthquake_data (dict: lat, lon, magnitude, time)
            affected_regions (list of region names)
    OUTPUT: arrival_times (dict: region → formatted UTC time)

    1.  tsunami_speed ← 700   // km/h
    2.  eq_time ← PARSE_TIME(earthquake_data.time)
    3.  region_coords ← {
    4.      'west_coast': (15.0, 73.0),
    5.      'east_coast': (13.0, 80.0),
    6.      'andaman_nicobar': (11.0, 92.5)
    7.  }
    8.
    9.  FOR EACH region IN affected_regions:
    10.     IF region IN region_coords:
    11.         (reg_lat, reg_lon) ← region_coords[region]
    12.         distance ← HAVERSINE(eq_lat, eq_lon, reg_lat, reg_lon)
    13.         travel_hours ← distance / tsunami_speed
    14.         arrival ← eq_time + TIMEDELTA(hours=travel_hours)
    15.         arrival_times[region] ← FORMAT(arrival, '%Y-%m-%d %H:%M UTC')
    16. RETURN arrival_times

Time Complexity: O(k) where k is the number of affected regions.

Limitation: This estimation assumes constant deep-ocean wave speed
and does not account for bathymetric variations, refraction, or
coastal shoaling, which can alter actual arrival times by 10–30%.

                                                                        Page 63

5.6  ALGORITHM 6: WAVE ANOMALY DETECTION
────────────────────────────────────────────────────────────────────────────────

Purpose:
This algorithm analyzes real-time wave buoy data to detect signatures
characteristic of tsunami waves. Tsunamis differ from wind-generated
waves in period (>10 minutes vs. 5–15 seconds), rate of height change,
and trend patterns. The algorithm checks four independent indicators
and returns a composite detection result.

Pseudocode:

    ALGORITHM: DETECT_TSUNAMI_SIGNATURE
    INPUT:  wave_data (DataFrame: WVHT, DPD, MWD, timestamps)
    OUTPUT: result (dict: detected, indicators)

    1.  indicators ← []
    2.  detected ← FALSE
    3.
    4.  // Check 1: Long-period waves (tsunami period > 10 minutes)
    5.  IF MAX(wave_data.DPD) > 600 THEN
    6.      indicators.APPEND('long_period_waves')
    7.      detected ← TRUE
    8.
    9.  // Check 2: Rapid wave height changes (> 0.5m between readings)
    10. height_change ← MAX(ABS(DIFF(wave_data.WVHT)))
    11. IF height_change > 0.5 THEN
    12.     indicators.APPEND('rapid_height_change')
    13.     detected ← TRUE
    14.
    15. // Check 3: Abnormal absolute wave height (> 3 meters)
    16. IF MAX(wave_data.WVHT) > 3.0 THEN
    17.     indicators.APPEND('abnormal_wave_height')
    18.     detected ← TRUE
    19.
    20. // Check 4: Monotonically increasing wave height trend
    21. recent ← TAIL(wave_data.WVHT, 10)
    22. IF IS_MONOTONIC_INCREASING(recent)
    23.    AND recent[LAST] - recent[FIRST] > 0.5 THEN
    24.     indicators.APPEND('increasing_trend')
    25.     detected ← TRUE
    26.
    27. RETURN {detected: detected, indicators: indicators}

Time Complexity: O(n) where n is the number of observations in the
wave dataset (typically 50–200 recent readings).


5.7  COMPLEXITY ANALYSIS SUMMARY
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 64

Table 5.2: Algorithm Complexity Summary

┌───────────────────────────────────┬──────────┬──────────┬──────────────┐
│ Algorithm                         │ Time     │ Space    │ Notes        │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Binary Focal Loss                 │ O(n)     │ O(n)     │ n=batch size │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Haversine Distance                │ O(1)     │ O(1)     │ Constant     │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ India Risk Score                  │ O(k)     │ O(k)     │ k=3 regions  │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Seismic Pattern Synthesis         │ O(T×F)   │ O(T×F)   │ T=24, F=32   │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Arrival Time Estimation           │ O(k)     │ O(k)     │ k=3 regions  │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Wave Anomaly Detection            │ O(n)     │ O(1)     │ n=wave obs.  │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ CNN-LSTM Forward Pass             │ O(P)     │ O(P)     │ P=~350K      │
│ (inference)                       │          │          │ parameters   │
├───────────────────────────────────┼──────────┼──────────┼──────────────┤
│ Complete Prediction Pipeline      │ O(P+k+n) │ O(P)     │ Dominated by │
│                                   │          │          │ model params │
└───────────────────────────────────┴──────────┴──────────┴──────────────┘

The complete prediction pipeline is dominated by the CNN-LSTM forward
pass, which involves approximately 350,000 multiply-accumulate
operations. On modern hardware (Intel i5 or equivalent), this executes
in under 200 milliseconds without GPU acceleration. The geographic
filtering and risk score computation add negligible overhead.

