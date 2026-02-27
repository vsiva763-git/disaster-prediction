"""
Data Preprocessor
Prepares and transforms raw data for model input
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
from pathlib import Path


class DataPreprocessor:
    """Preprocesses raw data for tsunami prediction model"""
    
    def __init__(self, config: Dict):
        """
        Initialize data preprocessor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config['model']
        self.input_config = self.config['input_features']
        self.temporal_window = self.input_config['temporal_window']
        
        # Scalers for different data types
        self.earthquake_scaler = StandardScaler()
        self.ocean_scaler = StandardScaler()
        self.spatial_scaler = MinMaxScaler()
        
        self.is_fitted = False
    
    def preprocess_earthquake_data(self, 
                                  df: pd.DataFrame,
                                  temporal_window: Optional[int] = None) -> np.ndarray:
        """
        Preprocess earthquake data into model input format
        
        Args:
            df: DataFrame with earthquake data
            temporal_window: Hours of historical data to include
            
        Returns:
            Preprocessed array (timesteps, num_earthquakes, features)
        """
        if df.empty:
            print("Empty earthquake dataframe")
            return np.zeros((1, 10, 4))  # Default empty array
        
        temporal_window = temporal_window or self.temporal_window
        
        # Extract relevant features
        features = self.input_config['earthquake']
        earthquake_features = df[features].values
        
        # Scale features
        if self.is_fitted:
            earthquake_features = self.earthquake_scaler.transform(earthquake_features)
        else:
            earthquake_features = self.earthquake_scaler.fit_transform(earthquake_features)
        
        # Create temporal sequences
        sequences = self._create_temporal_sequences(
            earthquake_features,
            df['time'].values if 'time' in df.columns else None,
            temporal_window
        )
        
        return sequences
    
    def preprocess_ocean_data(self,
                             tide_data: Dict[str, pd.DataFrame],
                             buoy_data: Dict[str, pd.DataFrame],
                             temporal_window: Optional[int] = None) -> np.ndarray:
        """
        Preprocess ocean condition data
        
        Args:
            tide_data: Dictionary of tidal dataframes by station
            buoy_data: Dictionary of buoy dataframes by station
            temporal_window: Hours of historical data
            
        Returns:
            Preprocessed array (timesteps, num_locations, features)
        """
        temporal_window = temporal_window or self.temporal_window
        
        # Combine tide and buoy data
        all_features = []
        
        for station_id, tide_df in tide_data.items():
            if tide_df.empty:
                continue
            
            # Extract tide features
            tide_features = self._extract_tide_features(tide_df)
            all_features.append(tide_features)
        
        for station_id, buoy_df in buoy_data.items():
            if buoy_df.empty:
                continue
            
            # Extract buoy features
            buoy_features = self._extract_buoy_features(buoy_df)
            all_features.append(buoy_features)
        
        if not all_features:
            print("No ocean data available")
            return np.zeros((1, 5, 3))  # Default empty array
        
        # Stack and scale features
        ocean_features = np.vstack(all_features)
        
        if self.is_fitted:
            ocean_features = self.ocean_scaler.transform(ocean_features)
        else:
            ocean_features = self.ocean_scaler.fit_transform(ocean_features)
        
        # Reshape to (timesteps, locations, features)
        # Simplified: use most recent readings
        sequences = ocean_features.reshape(1, -1, ocean_features.shape[-1])
        
        return sequences
    
    def preprocess_spatial_data(self,
                               bathymetry_data,
                               earthquake_location: Tuple[float, float],
                               grid_size: Tuple[int, int] = (64, 64)) -> np.ndarray:
        """
        Preprocess spatial/bathymetry data
        
        Args:
            bathymetry_data: Bathymetry dataset (xarray)
            earthquake_location: (latitude, longitude) of earthquake epicenter
            grid_size: Output grid dimensions
            
        Returns:
            Preprocessed array (height, width, channels)
        """
        try:
            lat, lon = earthquake_location
            
            # Extract local region around earthquake
            lat_range = 10  # degrees
            lon_range = 10
            
            # Subset bathymetry data
            if bathymetry_data is not None:
                local_bathy = bathymetry_data.sel(
                    lat=slice(lat - lat_range, lat + lat_range),
                    lon=slice(lon - lon_range, lon + lon_range)
                )['elevation'].values
            else:
                local_bathy = np.random.uniform(-5000, -100, grid_size)
            
            # Resize to standard grid
            from scipy.ndimage import zoom
            zoom_factors = (
                grid_size[0] / local_bathy.shape[0],
                grid_size[1] / local_bathy.shape[1]
            )
            resized_bathy = zoom(local_bathy, zoom_factors, order=1)
            
            # Calculate distance to epicenter for each grid cell
            lats = np.linspace(lat - lat_range, lat + lat_range, grid_size[0])
            lons = np.linspace(lon - lon_range, lon + lon_range, grid_size[1])
            lat_grid, lon_grid = np.meshgrid(lats, lons, indexing='ij')
            
            distance_grid = np.sqrt(
                (lat_grid - lat)**2 + (lon_grid - lon)**2
            )
            
            # Stack channels: [bathymetry, distance_to_epicenter]
            spatial_features = np.stack([resized_bathy, distance_grid], axis=-1)
            
            # Scale
            original_shape = spatial_features.shape
            spatial_features = spatial_features.reshape(-1, original_shape[-1])
            
            if self.is_fitted:
                spatial_features = self.spatial_scaler.transform(spatial_features)
            else:
                spatial_features = self.spatial_scaler.fit_transform(spatial_features)
            
            spatial_features = spatial_features.reshape(original_shape)
            
            return spatial_features
            
        except Exception as e:
            print(f"Error preprocessing spatial data: {e}")
            # Return default grid
            return np.zeros((*grid_size, 2))
    
    def _extract_tide_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features from tide data"""
        features = []
        
        if 'water_level' in df.columns:
            features.append(df['water_level'].mean())
            features.append(df['water_level'].std())
            
            # Rate of change
            if len(df) > 1:
                df = df.sort_values('time')
                rate = df['water_level'].diff().mean()
                features.append(rate)
            else:
                features.append(0.0)
        else:
            features = [0.0, 0.0, 0.0]
        
        return np.array(features)
    
    def _extract_buoy_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features from buoy data"""
        features = []
        
        if 'wave_height' in df.columns:
            features.append(df['wave_height'].mean())
            features.append(df['wave_height'].max())
        else:
            features.extend([0.0, 0.0])
        
        if 'dominant_period' in df.columns:
            features.append(df['dominant_period'].mean())
        else:
            features.append(0.0)
        
        return np.array(features)
    
    def _create_temporal_sequences(self,
                                  features: np.ndarray,
                                  timestamps: Optional[np.ndarray],
                                  window_hours: int) -> np.ndarray:
        """
        Create temporal sequences from features
        
        Args:
            features: Feature array
            timestamps: Time stamps for each feature
            window_hours: Temporal window size
            
        Returns:
            Sequenced array
        """
        # Simplified: return most recent data in sequence format
        # In production, implement proper temporal windowing
        
        max_events = 10  # Maximum events to include
        if len(features) > max_events:
            features = features[-max_events:]
        elif len(features) < max_events:
            # Pad with zeros
            padding = np.zeros((max_events - len(features), features.shape[1]))
            features = np.vstack([padding, features])
        
        # Reshape to (1, timesteps, features) for single sample
        return features.reshape(1, features.shape[0], features.shape[1])
    
    def create_training_labels(self, 
                              tsunami_occurred: bool,
                              tsunami_intensity: str = 'none') -> Tuple:
        """
        Create training labels for model
        
        Args:
            tsunami_occurred: Whether tsunami occurred
            tsunami_intensity: Intensity level (none, low, medium, high)
            
        Returns:
            Tuple of (risk_probability, confidence, risk_class)
        """
        # Risk probability
        risk_prob = 1.0 if tsunami_occurred else 0.0
        
        # Confidence (simplified - could be based on data quality)
        confidence = 0.9
        
        # Risk class (one-hot encoded)
        intensity_map = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        class_idx = intensity_map.get(tsunami_intensity, 0)
        risk_class = np.zeros(4)
        risk_class[class_idx] = 1.0
        
        return (
            np.array([[risk_prob]]),
            np.array([[confidence]]),
            np.array([risk_class])
        )
    
    def save_scalers(self, save_dir: str):
        """Save fitted scalers"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.earthquake_scaler, save_path / 'earthquake_scaler.pkl')
        joblib.dump(self.ocean_scaler, save_path / 'ocean_scaler.pkl')
        joblib.dump(self.spatial_scaler, save_path / 'spatial_scaler.pkl')
        
        print(f"Scalers saved to {save_dir}")
    
    def load_scalers(self, save_dir: str):
        """Load fitted scalers"""
        save_path = Path(save_dir)
        
        self.earthquake_scaler = joblib.load(save_path / 'earthquake_scaler.pkl')
        self.ocean_scaler = joblib.load(save_path / 'ocean_scaler.pkl')
        self.spatial_scaler = joblib.load(save_path / 'spatial_scaler.pkl')
        
        self.is_fitted = True
        print(f"Scalers loaded from {save_dir}")
