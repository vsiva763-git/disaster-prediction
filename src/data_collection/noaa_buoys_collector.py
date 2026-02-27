"""
NOAA Buoys Data Collector
Fetches real-time wave height and ocean state data from NOAA NDBC
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import StringIO
from loguru import logger


class NOAABuoysCollector:
    """Collects wave and ocean data from NOAA NDBC buoys"""
    
    def __init__(self, config: Dict):
        """
        Initialize NOAA Buoys collector
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config['apis']['noaa_buoys']
        self.base_url = self.config['base_url']
        self.stations = self.config['stations']
    
    def fetch_buoy_data(self, station_id: str, data_type: str = 'spec') -> pd.DataFrame:
        """
        Fetch real-time buoy data
        
        Args:
            station_id: Buoy station identifier
            data_type: Type of data ('spec' for wave spectra, 'txt' for standard met)
            
        Returns:
            DataFrame with buoy measurements
        """
        try:
            # NOAA NDBC provides data in text format
            url = f"{self.base_url}/{station_id}.{data_type}"
            
            logger.info(f"Fetching buoy data from station {station_id}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the fixed-width text format
            lines = response.text.strip().split('\n')
            
            if len(lines) < 3:
                logger.warning(f"Insufficient data from buoy {station_id}")
                return pd.DataFrame()
            
            # First line is header, second line is units
            header = lines[0].split()
            data_lines = lines[2:]
            
            records = []
            for line in data_lines:
                values = line.split()
                if len(values) < len(header):
                    continue
                
                try:
                    # Parse timestamp
                    year, month, day, hour, minute = map(int, values[:5])
                    timestamp = datetime(year, month, day, hour, minute)
                    
                    # Parse wave data
                    record = {
                        'station_id': station_id,
                        'time': timestamp,
                        'wave_height': float(values[5]) if values[5] != 'MM' else None,
                        'dominant_period': float(values[6]) if values[6] != 'MM' else None,
                        'average_period': float(values[7]) if values[7] != 'MM' else None,
                        'wave_direction': float(values[8]) if len(values) > 8 and values[8] != 'MM' else None,
                    }
                    records.append(record)
                except (ValueError, IndexError):
                    continue
            
            if not records:
                logger.warning(f"No valid records from buoy {station_id}")
                return pd.DataFrame()
            
            df = pd.DataFrame(records)
            # Filter recent data only (last 48 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=48)
            df = df[df['time'] >= cutoff_time]
            
            logger.success(f"Fetched {len(df)} buoy readings from station {station_id}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch buoy data for station {station_id}: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing buoy data: {e}")
            return pd.DataFrame()
    
    def fetch_all_buoys(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from all configured buoy stations
        
        Returns:
            Dictionary mapping station IDs to DataFrames
        """
        all_data = {}
        for station_id in self.stations:
            df = self.fetch_buoy_data(station_id)
            if not df.empty:
                all_data[station_id] = df
        
        logger.info(f"Collected data from {len(all_data)} buoy stations")
        return all_data
    
    def analyze_wave_patterns(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze wave patterns for tsunami indicators
        
        Args:
            df: DataFrame with buoy data
            
        Returns:
            Dictionary with wave pattern metrics
        """
        if df.empty:
            return {}
        
        df = df.sort_values('time')
        
        metrics = {
            'mean_wave_height': df['wave_height'].mean(),
            'max_wave_height': df['wave_height'].max(),
            'wave_height_std': df['wave_height'].std(),
            'mean_period': df['dominant_period'].mean(),
            'period_variability': df['dominant_period'].std(),
        }
        
        # Calculate rate of change in wave height
        df['wave_height_change'] = df['wave_height'].diff()
        df['time_diff'] = df['time'].diff().dt.total_seconds() / 3600  # hours
        df['wave_height_rate'] = df['wave_height_change'] / df['time_diff']
        
        metrics['max_wave_height_rate'] = df['wave_height_rate'].abs().max()
        metrics['recent_trend'] = df['wave_height'].iloc[-10:].mean() - df['wave_height'].iloc[:10].mean()
        
        return metrics
    
    def detect_tsunami_signature(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Detect potential tsunami signatures in wave data
        
        Args:
            df: DataFrame with buoy data
            
        Returns:
            Dictionary with detection results
        """
        if df.empty or len(df) < 10:
            return {'detected': False, 'confidence': 0.0}
        
        metrics = self.analyze_wave_patterns(df)
        
        # Tsunami wave characteristics:
        # - Long period waves (10-60 minutes)
        # - Rapid changes in wave height
        # - Unusual wave patterns
        
        indicators = []
        
        # Check for long period waves
        if metrics.get('mean_period', 0) > 600:  # > 10 minutes
            indicators.append('long_period')
        
        # Check for rapid wave height changes
        if metrics.get('max_wave_height_rate', 0) > 0.5:  # > 0.5m per hour
            indicators.append('rapid_change')
        
        # Check for abnormal wave heights
        if metrics.get('max_wave_height', 0) > 3.0:
            indicators.append('high_waves')
        
        # Check for increasing trend
        if metrics.get('recent_trend', 0) > 0.5:
            indicators.append('increasing_trend')
        
        detected = len(indicators) >= 2
        confidence = len(indicators) / 4.0
        
        return {
            'detected': detected,
            'confidence': confidence,
            'indicators': indicators,
            'metrics': metrics
        }
