"""
NOAA Tides and Currents Data Collector
Fetches real-time sea level and tidal data from NOAA API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger


class NOAATidesCollector:
    """Collects tidal and sea level data from NOAA API"""
    
    def __init__(self, config: Dict):
        """
        Initialize NOAA Tides collector
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config['apis']['noaa_tides']
        self.base_url = self.config['base_url']
        
        # Indian Ocean coastal stations (examples - would need actual station IDs)
        self.indian_stations = [
            '9001234',  # Example: Arabian Sea station
            '9005678',  # Example: Bay of Bengal station
            '9009876',  # Example: Andaman Sea station
        ]
    
    def fetch_water_levels(self, 
                          station_id: str, 
                          hours: int = 24,
                          interval: str = '6') -> pd.DataFrame:
        """
        Fetch water level data for a specific station
        
        Args:
            station_id: NOAA station identifier
            hours: Lookback period in hours
            interval: Data interval in minutes ('h' for hourly, '6' for 6-min)
            
        Returns:
            DataFrame with water level data
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            params = {
                'begin_date': start_time.strftime('%Y%m%d %H:%M'),
                'end_date': end_time.strftime('%Y%m%d %H:%M'),
                'station': station_id,
                'product': self.config['product'],
                'datum': self.config['datum'],
                'units': self.config['units'],
                'time_zone': self.config['time_zone'],
                'format': self.config['format'],
                'application': self.config['application']
            }
            
            logger.info(f"Fetching water levels for station {station_id}...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or not data['data']:
                logger.warning(f"No data available for station {station_id}")
                return pd.DataFrame()
            
            records = []
            for entry in data['data']:
                records.append({
                    'station_id': station_id,
                    'time': pd.to_datetime(entry['t']),
                    'water_level': float(entry['v']),
                    'sigma': float(entry.get('s', 0)),
                    'flags': entry.get('f', ''),
                    'quality': entry.get('q', '')
                })
            
            df = pd.DataFrame(records)
            logger.success(f"Fetched {len(df)} water level readings for station {station_id}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch NOAA tides data for station {station_id}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing NOAA tides data: {e}")
            return pd.DataFrame()
    
    def fetch_all_stations(self, hours: int = 24) -> Dict[str, pd.DataFrame]:
        """
        Fetch water level data for all Indian Ocean stations
        
        Args:
            hours: Lookback period in hours
            
        Returns:
            Dictionary mapping station IDs to DataFrames
        """
        all_data = {}
        for station_id in self.indian_stations:
            df = self.fetch_water_levels(station_id, hours)
            if not df.empty:
                all_data[station_id] = df
        
        logger.info(f"Collected data from {len(all_data)} stations")
        return all_data
    
    def detect_anomalies(self, df: pd.DataFrame, threshold_std: float = 3.0) -> pd.DataFrame:
        """
        Detect anomalous sea level readings
        
        Args:
            df: DataFrame with water level data
            threshold_std: Number of standard deviations for anomaly detection
            
        Returns:
            DataFrame with anomaly flags
        """
        if df.empty or len(df) < 10:
            return df
        
        df = df.copy()
        
        # Calculate rolling statistics
        df['rolling_mean'] = df['water_level'].rolling(window=10, center=True).mean()
        df['rolling_std'] = df['water_level'].rolling(window=10, center=True).std()
        
        # Detect anomalies
        df['deviation'] = (df['water_level'] - df['rolling_mean']) / df['rolling_std']
        df['is_anomaly'] = df['deviation'].abs() > threshold_std
        
        anomaly_count = df['is_anomaly'].sum()
        if anomaly_count > 0:
            logger.warning(f"Detected {anomaly_count} anomalous water level readings")
        
        return df
    
    def calculate_sea_level_anomaly(self, df: pd.DataFrame) -> float:
        """
        Calculate overall sea level anomaly score
        
        Args:
            df: DataFrame with water level data
            
        Returns:
            Anomaly score (higher = more anomalous)
        """
        if df.empty or len(df) < 2:
            return 0.0
        
        # Calculate rate of change
        df = df.sort_values('time')
        df['rate_of_change'] = df['water_level'].diff() / df['time'].diff().dt.total_seconds()
        
        # Anomaly indicators
        max_rate = df['rate_of_change'].abs().max()
        std_dev = df['water_level'].std()
        range_val = df['water_level'].max() - df['water_level'].min()
        
        # Combine into anomaly score
        anomaly_score = (max_rate * 1000 + std_dev + range_val) / 3
        
        return anomaly_score
