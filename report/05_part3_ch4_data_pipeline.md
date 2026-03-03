
================================================================================
CHAPTER 4    DATA SOURCES AND DATA PIPELINE
================================================================================
                                                                        Page 41

4.1  DATA COLLECTION STRATEGY
────────────────────────────────────────────────────────────────────────────────

The data collection strategy implements the "zero-cost infrastructure"
principle by exclusively utilizing free public APIs and open datasets.
Five collectors operate independently, each implementing standardized
error handling with retry logic (3 attempts), timeout management (30
seconds per request), and fallback data generation when external
services are unavailable.

Table 4.1: Data Sources and Collection Methods

┌──────────────┬───────────────┬────────────────┬──────────────────────┐
│ Source        │ Module        │ Data Type      │ Method               │
├──────────────┼───────────────┼────────────────┼──────────────────────┤
│ USGS         │ usgs_         │ Real-time      │ REST API (GeoJSON)   │
│              │ collector.py  │ earthquakes    │ region/magnitude/    │
│              │               │                │ time filtering       │
├──────────────┼───────────────┼────────────────┼──────────────────────┤
│ NOAA Tides   │ noaa_tides_   │ Sea level /    │ REST API (JSON)      │
│              │ collector.py  │ water levels   │ 6-minute intervals   │
│              │               │                │ rolling statistics   │
├──────────────┼───────────────┼────────────────┼──────────────────────┤
│ NOAA NDBC    │ noaa_buoys_   │ Wave height,   │ Text file parsing    │
│              │ collector.py  │ period,        │ from buoy stations   │
│              │               │ direction      │ 23001, 23009         │
├──────────────┼───────────────┼────────────────┼──────────────────────┤
│ INCOIS       │ incois_       │ Official       │ REST API for         │
│              │ collector.py  │ tsunami        │ advisories and       │
│              │               │ advisories     │ historical events    │
├──────────────┼───────────────┼────────────────┼──────────────────────┤
│ GEBCO        │ bathymetry_   │ Ocean floor    │ NetCDF file via      │
│              │ loader.py     │ depth data     │ xarray with dummy    │
│              │               │                │ fallback             │
└──────────────┴───────────────┴────────────────┴──────────────────────┘

                                                                        Page 42

                              [Figure 4.1]
    ┌─────────────────────────────────────────────────────────────┐
    │           DATA COLLECTION PIPELINE FLOW DIAGRAM             │
    │                                                              │
    │  ┌────────────────────────────────────────────────────────┐ │
    │  │              External Public APIs                      │ │
    │  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │ │
    │  │  │USGS  │ │NOAA  │ │NOAA  │ │INCOIS│ │GEBCO │        │ │
    │  │  │API   │ │Tides │ │NDBC  │ │API   │ │NetCDF│        │ │
    │  │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘        │ │
    │  └─────┼────────┼────────┼────────┼────────┼─────────────┘ │
    │        ↓        ↓        ↓        ↓        ↓               │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │           Collector Modules (Python)                 │   │
    │  │  HTTP GET → Parse Response → Validate → DataFrame   │   │
    │  │  Error?  → Retry (×3) → Timeout? → Fallback Data   │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        ↓                                    │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │           Data Validation & Cleaning                 │   │
    │  │  • Remove NaN/null values                           │   │
    │  │  • Filter by region bounding box                    │   │
    │  │  • Filter by magnitude threshold (≥5.5)             │   │
    │  │  • Convert timestamps to UTC                        │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        ↓                                    │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │           Feature Extraction                         │   │
    │  │  • 28 earthquake features → padded to 32            │   │
    │  │  • Tide: mean, std, rate-of-change                  │   │
    │  │  • Buoy: mean/max wave height, period               │   │
    │  │  • Spatial: bathymetry grid + distance channel       │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        ↓                                    │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │           Normalization & Windowing                   │   │
    │  │  • StandardScaler (earthquake/ocean features)        │   │
    │  │  • MinMaxScaler (spatial features)                   │   │
    │  │  • Create 24-timestep temporal windows               │   │
    │  │  • Zero-pad if insufficient data                    │   │
    │  └─────────────────────┬───────────────────────────────┘   │
    │                        ↓                                    │
    │              [ 24 × 32 Feature Matrix ]                     │
    │                 Ready for Model Input                       │
    └─────────────────────────────────────────────────────────────┘

        Figure 4.1: Data collection pipeline flow diagram


4.2  USGS EARTHQUAKE DATA COLLECTOR
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 43

The USGSEarthquakeCollector class (src/data_collection/usgs_collector.py,
126 lines) fetches real-time earthquake data from the USGS Earthquake
Hazards Program Federal Earthquake Data Network (FDSN) web service.

Design:
The collector constructs a parameterized URL to the USGS earthquake
query API with the following parameters:
- format: geojson (GeoJSON geographic data format)
- minmagnitude: 5.5 (minimum magnitude threshold from config)
- minlatitude/maxlatitude: -20/30 (Indian Ocean bounding box)
- minlongitude/maxlongitude: 40/110
- starttime: current time minus lookback period (configurable, default
  24 hours)
- orderby: time (most recent first)

The GeoJSON response is parsed to extract earthquake features into a
Pandas DataFrame with columns: id, magnitude, depth, latitude,
longitude, time, place, tsunami (USGS tsunami flag), and url.

Key Implementation Detail — The collector performs coordinate extraction
from the GeoJSON "geometry" object, where coordinates are stored as
[longitude, latitude, depth] — note the non-intuitive longitude-first
ordering mandated by the GeoJSON specification (RFC 7946).

    # From usgs_collector.py — coordinate extraction
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        earthquake = {
            'id': feature['id'],
            'magnitude': feature['properties']['mag'],
            'latitude': coords[1],     # GeoJSON: [lon, lat, depth]
            'longitude': coords[0],
            'depth': coords[2],
            'time': pd.to_datetime(
                feature['properties']['time'], unit='ms'
            ),
            'place': feature['properties']['place'],
            'tsunami': feature['properties']['tsunami']
        }

                                                                        Page 44

Error Handling: The collector implements a three-tier error handling
strategy: (1) HTTP request exceptions (ConnectionError, Timeout) trigger
up to three retries with exponential backoff; (2) JSON parsing errors
are caught and logged; (3) if all retries fail, the collector returns an
empty DataFrame rather than raising an exception, allowing the system
to continue operating with other data sources.

Fallback Data Generation: If the USGS API is unreachable, the system
can generate simulated earthquake data for demonstration and testing
purposes. The fallback generates a DataFrame with plausible earthquake
parameters within the Indian Ocean region, enabling system testing
without live API access.


4.3  NOAA TIDES AND CURRENTS COLLECTOR
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 45

The NOAATidesCollector class (src/data_collection/noaa_tides_collector.py,
168 lines) retrieves water level measurements from the NOAA Center for
Operational Oceanographic Products and Services (CO-OPS) API. Water
level data is critical for tsunami detection because tsunami waves
produce characteristic sea level anomalies — rapid, sustained changes
in water level that differ from normal tidal patterns.

The collector queries the NOAA Tides API with the following parameters:
- product: water_level
- datum: MLLW (Mean Lower Low Water — a tidal datum reference)
- units: metric (centimeters converted to meters)
- time_zone: gmt (UTC)
- format: json
- application: tsunami_warning (application identifier for NOAA)
- begin_date / end_date: configurable lookback period (default 6 hours)

The API returns water level readings at 6-minute intervals for each
queried station. The collector processes these readings into Pandas
DataFrames with columns: timestamp, water_level, quality_flag.

Sea Level Anomaly Detection:
The most significant algorithmic component of this module is the sea
level anomaly detection function, which implements statistical analysis
of water level time series:

    def calculate_sea_level_anomaly(self, data):
        """Detect anomalous sea level changes using rolling statistics"""
        # Calculate rolling mean and standard deviation
        window_size = 10  # 10 readings = 60 minutes
        rolling_mean = data['water_level'].rolling(window=window_size).mean()
        rolling_std = data['water_level'].rolling(window=window_size).std()

        # Z-score anomaly detection
        z_scores = (data['water_level'] - rolling_mean) / rolling_std

        # Flag anomalies where |z-score| > 3.0
        anomaly_score = z_scores.abs().max()

        return anomaly_score

                                                                        Page 46

The anomaly detection uses a rolling window of 10 observations (60
minutes at 6-minute intervals) to establish a local baseline, then
computes z-scores for each observation relative to this baseline. An
observation with |z-score| > 3.0 (more than three standard deviations
from the local mean) is flagged as anomalous. This approach is robust
to normal tidal variation because the rolling window captures the local
tidal trend, and only deviations exceeding three sigma — which occur by
chance less than 0.3% of the time — trigger an anomaly flag.


4.4  NOAA NDBC BUOY DATA COLLECTOR
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 47

The NOAABuoysCollector class (src/data_collection/noaa_buoys_collector.py,
196 lines) retrieves real-time wave observation data from the NOAA
National Data Buoy Center (NDBC). Unlike the Tides collector which uses
a JSON REST API, the NDBC provides data in fixed-width text format —
requiring different parsing logic.

Two buoy stations are configured for the Indian Ocean:
- Station 23001: Located in the Arabian Sea, monitoring wave conditions
  relevant to India's western coastline.
- Station 23009: Located in the Bay of Bengal, monitoring conditions
  relevant to India's eastern coastline and the Andaman Islands.

The collector downloads real-time data files from the NDBC URL pattern:
    https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt

Each file contains columnar data with headers defining measurement
fields. The relevant parameters extracted are:
- WVHT: Significant wave height (meters)
- DPD: Dominant wave period (seconds)
- MWD: Mean wave direction (degrees from true north)
- PRES: Atmospheric pressure (hPa)
- ATMP: Air temperature (°C)
- WTMP: Water temperature (°C)

                                                                        Page 48

Tsunami Signature Detection:
The module implements a tsunami signature detection algorithm that
analyzes wave characteristics for patterns indicative of tsunami waves:

    def detect_tsunami_signature(self, data):
        """Detect potential tsunami signatures in wave data"""
        indicators = []
        detected = False

        if not data.empty:
            # Check 1: Long-period waves (tsunami periods > 10 minutes)
            if 'DPD' in data.columns:
                long_period = data['DPD'].max() > 600  # > 10 min
                if long_period:
                    indicators.append('long_period_waves')
                    detected = True

            # Check 2: Rapid wave height changes
            if 'WVHT' in data.columns:
                height_change = data['WVHT'].diff().abs().max()
                if height_change > 0.5:  # > 0.5m change
                    indicators.append('rapid_height_change')
                    detected = True

                # Check 3: Abnormal wave height
                if data['WVHT'].max() > 3.0:  # > 3 meters
                    indicators.append('abnormal_wave_height')
                    detected = True

                # Check 4: Increasing trend
                recent = data['WVHT'].tail(10)
                if recent.is_monotonic_increasing and \
                   recent.iloc[-1] - recent.iloc[0] > 0.5:
                    indicators.append('increasing_trend')
                    detected = True

        return {'detected': detected, 'indicators': indicators}

This multi-criteria approach reduces false positives by requiring that
wave characteristics match known tsunami signatures rather than relying
on any single measurement. True tsunamis exhibit a distinctive
combination of long period (>10 minutes, compared with typical wind
waves at 5–15 seconds), sustained height increase, and rapid change
rates — patterns that rarely occur simultaneously under normal
oceanographic conditions.


4.5  INCOIS ADVISORY COLLECTOR
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 49

The INCOISCollector class (src/data_collection/incois_collector.py, 139
lines) interfaces with the Indian National Centre for Ocean Information
Services (INCOIS) to retrieve official tsunami advisories for the Indian
Ocean. INCOIS is India's designated National Tsunami Warning Centre,
mandated by the Government of India to issue tsunami bulletins for the
Indian coast.

The collector queries two endpoints:
(1) /advisories: Current active tsunami advisories and bulletins
(2) /events: Historical tsunami events database

Each advisory contains: advisory level (WATCH, ADVISORY, WARNING),
issue time, expiry time, affected regions, earthquake parameters, and
recommended actions. These advisories serve as a validation signal —
when INCOIS has issued an official advisory, the system's assessment
should reflect at least the same alert level.

The collector implements graceful degradation: if the INCOIS API is
unreachable (which is common due to intermittent availability of the
service), the assessment pipeline continues without official advisory
data, relying instead on model predictions and geographic filtering.


4.6  GEBCO BATHYMETRY LOADER
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 50

The BathymetryLoader class (src/data_collection/bathymetry_loader.py,
203 lines) loads and processes ocean depth data from the General
Bathymetric Chart of the Oceans (GEBCO) dataset. Bathymetry data is
essential for tsunami propagation modeling because tsunami speed is
directly proportional to the square root of ocean depth (c = √(gh)),
and coastal amplification depends on the slope of the continental shelf.

The loader supports two modes of operation:

Mode 1 — Full GEBCO Data: Loads the GEBCO_2023 global bathymetric grid
from a NetCDF file using the xarray library. The dataset provides ocean
depth at 15 arc-second resolution (approximately 450 meters at the
equator), organized as a 2D grid indexed by latitude and longitude.

    def load_gebco_data(self, filepath=None):
        """Load GEBCO bathymetry data"""
        if filepath and os.path.exists(filepath):
            self.bathymetry_data = xr.open_dataset(filepath)
            logger.success("GEBCO data loaded successfully")
        else:
            logger.warning("GEBCO data not found, using dummy data")
            self._generate_dummy_bathymetry()

Mode 2 — Dummy Fallback: When the full GEBCO dataset (approximately
7.5 GB) is unavailable, the loader generates a simplified bathymetric
grid covering the Indian Ocean region using mathematical approximation.
The dummy grid provides approximate depth values based on distance from
known continental shelf boundaries, enabling system testing and
demonstration without the full dataset.

The BathymetryLoader provides two key functions used by the prediction
pipeline:
(1) extract_region(lat, lon, size): Extracts a spatial grid of
    bathymetric data centered on an earthquake epicenter, used as
    spatial input to the multi-modal CNN-LSTM model.
(2) get_depth_at_point(lat, lon): Returns the ocean depth at a
    specific coordinate, used for tsunami speed estimation.


4.7  DATA PREPROCESSING AND TRANSFORMATION
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 51

The DataPreprocessor class (src/models/data_preprocessor.py, 299 lines)
transforms raw sensor data into the normalized, structured format
required by the CNN-LSTM model. The preprocessing pipeline performs
four key transformations:

Transformation 1 — Feature Extraction:
Earthquake features (4 base features: magnitude, depth, latitude,
longitude) are expanded to include derived features such as depth-to-
magnitude ratio, distance-to-coast approximation, and logarithmic
magnitude. Ocean features are extracted from tide data (mean water
level, standard deviation, rate of change) and buoy data (mean wave
height, maximum wave height, dominant period). The total feature count
is 32, combining earthquake, ocean, and derived features.

Transformation 2 — Normalization:
Two scikit-learn scalers are fitted during training and applied during
inference:
- StandardScaler: Applied to earthquake and ocean features, transforming
  each feature to zero mean and unit variance. This is appropriate for
  features with approximately Gaussian distributions.
- MinMaxScaler: Applied to spatial (bathymetry) features, scaling values
  to the [0, 1] range. This is appropriate for bounded features where
  relative magnitude matters.

Transformation 3 — Temporal Windowing:
Features are organized into temporal windows of 24 timesteps. For
training data from historical databases, this represents 24 consecutive
observations. For real-time inference, the most recent 24 observations
are used, with zero-padding applied if insufficient data is available.

Transformation 4 — Missing Data Handling:
Missing values are imputed using zero-padding for temporal sequences
(filling missing timesteps with zeros) and mean imputation for
individual feature values. This conservative imputation strategy avoids
introducing bias while ensuring that the fixed-size input matrix
required by the CNN-LSTM model is always provided.

                                                                        Page 52

Table 4.2: 32 Input Feature Descriptions

┌────┬──────────────────────────┬────────┬──────────────────────────────┐
│ #  │ Feature Name             │ Type   │ Description                  │
├────┼──────────────────────────┼────────┼──────────────────────────────┤
│ 1  │ magnitude                │ Seismic│ Earthquake magnitude (Mw)    │
│ 2  │ depth_km                 │ Seismic│ Hypocenter depth (km)        │
│ 3  │ latitude                 │ Seismic│ Epicenter latitude (°)       │
│ 4  │ longitude                │ Seismic│ Epicenter longitude (°)      │
│ 5  │ log_magnitude            │ Derived│ log10(magnitude)             │
│ 6  │ depth_mag_ratio          │ Derived│ depth / magnitude            │
│ 7  │ dist_to_coast            │ Derived│ Approx. distance to coast(km)│
│ 8  │ is_shallow               │ Derived│ 1 if depth < 70km, else 0   │
│ 9  │ is_submarine             │ Derived│ 1 if under ocean, else 0    │
│ 10 │ magnitude_class          │ Derived│ Encoded mag class (0-4)     │
│ 11 │ sea_level_mean           │ Ocean  │ Mean water level (m)         │
│ 12 │ sea_level_std            │ Ocean  │ Water level std deviation    │
│ 13 │ sea_level_rate           │ Ocean  │ Rate of change (m/hr)        │
│ 14 │ sea_level_anomaly        │ Ocean  │ Z-score anomaly metric       │
│ 15 │ wave_height_mean         │ Ocean  │ Significant wave height (m)  │
│ 16 │ wave_height_max          │ Ocean  │ Maximum wave height (m)      │
│ 17 │ wave_period_dominant     │ Ocean  │ Dominant wave period (s)     │
│ 18 │ wave_direction           │ Ocean  │ Mean wave direction (°)      │
│ 19 │ pressure                 │ Ocean  │ Atmospheric pressure (hPa)   │
│ 20 │ water_temp               │ Ocean  │ Sea surface temperature (°C) │
│ 21 │ sin_latitude             │ Spatial│ sin(latitude_rad)            │
│ 22 │ cos_latitude             │ Spatial│ cos(latitude_rad)            │
│ 23 │ sin_longitude            │ Spatial│ sin(longitude_rad)           │
│ 24 │ cos_longitude            │ Spatial│ cos(longitude_rad)           │
│ 25 │ bathymetry_mean          │ Spatial│ Mean depth in region (m)     │
│ 26 │ bathymetry_std           │ Spatial│ Depth variation in region    │
│ 27 │ shelf_slope              │ Spatial│ Continental shelf gradient   │
│ 28 │ time_since_last_eq       │ Temp.  │ Seconds since previous event │
│ 29 │ cumulative_energy        │ Temp.  │ Cumulative seismic energy    │
│ 30 │ swarm_indicator          │ Temp.  │ Earthquake swarm flag        │
│ 31 │ tidal_phase              │ Temp.  │ Current tidal phase (0-1)    │
│ 32 │ reserved                 │ Pad    │ Reserved for future features │
└────┴──────────────────────────┴────────┴──────────────────────────────┘

                              [Figure 4.5]
    ┌─────────────────────────────────────────────────────────────┐
    │              24 × 32 FEATURE MATRIX STRUCTURE               │
    │                                                              │
    │           Features →  (32 columns)                           │
    │     T   ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐                    │
    │     i t₁│M │D │La│Lo│Se│Wv│Ba│..│..│Pd│ ← Seismic+Ocean   │
    │     m   ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤    features at     │
    │     e t₂│  │  │  │  │  │  │  │  │  │  │    each timestep   │
    │     s   ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤                    │
    │     t t₃│  │  │  │  │  │  │  │  │  │  │                    │
    │     e   ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤                    │
    │     p . │  │  │  │  │  │  │  │  │  │  │                    │
    │     s . │  │  │  │  │  │  │  │  │  │  │                    │
    │     ↓   ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤                    │
    │      t₂₄│  │  │  │  │  │  │  │  │  │  │ ← Most recent     │
    │  (24)   └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘                    │
    │                                                              │
    │  Total input: 24 timesteps × 32 features = 768 values       │
    └─────────────────────────────────────────────────────────────┘

       Figure 4.5: 24×32 feature matrix structure fed to model

                                                                        Page 53

4.8  DATA SCHEMA AND STORAGE DESIGN
────────────────────────────────────────────────────────────────────────────────

The system operates primarily with in-memory data structures, as the
real-time nature of the application requires low-latency access to the
most recent observations. The key data structures are:

(1) Earthquake DataFrame: Pandas DataFrame with columns [id, magnitude,
    depth, latitude, longitude, time, place, tsunami, url]. Stored
    in memory for the most recent 24-hour window.

(2) Tide Data Dictionary: Dict[str, DataFrame] mapping station IDs to
    DataFrames with columns [timestamp, water_level, quality_flag].
    Each station stores up to 6 hours of 6-minute interval readings.

(3) Buoy Data Dictionary: Dict[str, DataFrame] mapping station IDs to
    DataFrames with columns [timestamp, WVHT, DPD, MWD, PRES, ATMP,
    WTMP]. Recent observations per station.

(4) Assessment History: List[Dict] storing the last N risk assessments,
    each containing full earthquake information, model predictions,
    filter results, and recommendations.

(5) IoT Device Registry: Dict[str, Dict] mapping device IP addresses
    to device metadata (registration time, last heartbeat, device type,
    firmware version).

(6) Cloud Alert State: Dict storing the current alert state for cloud
    polling IoT devices, including alert level, message, timestamp,
    and auto-clear flag.

Persistent storage is used only for:
- Trained model weights (models/best_model.keras, 2.1 MB)
- Scaler parameters (models/scalers/, joblib-serialized)
- Model metadata (models/model_metadata.json)
- Application logs (logs/app.log, with 100 MB rotation and 30-day
  retention via Loguru)
- Configuration file (config/config.yaml)

