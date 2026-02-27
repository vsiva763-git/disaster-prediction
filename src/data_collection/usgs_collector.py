"""
USGS Earthquake Data Collector
Fetches real-time earthquake data from USGS API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger


class USGSEarthquakeCollector:
    """Collects earthquake data from USGS Earthquake API"""
    
    def __init__(self, config: Dict):
        """
        Initialize USGS collector
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config['apis']['usgs_earthquake']
        self.base_url = self.config['base_url']
        self.min_magnitude = self.config['min_magnitude']
        self.region = self.config['region']
        self.lookback_hours = self.config['lookback_hours']
        
    def fetch_recent_earthquakes(self, hours: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch recent earthquakes from USGS API
        
        Args:
            hours: Lookback period in hours (default from config)
            
        Returns:
            DataFrame with earthquake data
        """
        try:
            hours = hours or self.lookback_hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            params = {
                'format': self.config['format'],
                'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'minmagnitude': self.min_magnitude,
                'minlatitude': self.region['min_latitude'],
                'maxlatitude': self.region['max_latitude'],
                'minlongitude': self.region['min_longitude'],
                'maxlongitude': self.region['max_longitude']
            }
            
            logger.info(f"Fetching earthquakes from USGS (last {hours} hours)...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            features = data.get('features', [])
            
            if not features:
                logger.warning("No earthquakes found in specified region")
                return pd.DataFrame()
            
            earthquakes = []
            for feature in features:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                earthquakes.append({
                    'id': feature['id'],
                    'magnitude': props['mag'],
                    'depth': coords[2],  # km
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'time': datetime.fromtimestamp(props['time'] / 1000),
                    'place': props['place'],
                    'type': props['type'],
                    'tsunami': props.get('tsunami', 0),
                    'sig': props.get('sig', 0),
                    'url': props.get('url', '')
                })
            
            df = pd.DataFrame(earthquakes)
            logger.success(f"Fetched {len(df)} earthquakes from USGS")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch USGS data: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing USGS data: {e}")
            return pd.DataFrame()
    
    def get_significant_earthquakes(self, magnitude_threshold: float = 6.5) -> pd.DataFrame:
        """
        Get significant earthquakes above magnitude threshold
        
        Args:
            magnitude_threshold: Minimum magnitude to consider
            
        Returns:
            DataFrame with significant earthquakes
        """
        df = self.fetch_recent_earthquakes()
        if df.empty:
            return df
        
        significant = df[df['magnitude'] >= magnitude_threshold].copy()
        logger.info(f"Found {len(significant)} significant earthquakes (M≥{magnitude_threshold})")
        return significant
    
    def is_tsunami_capable(self, magnitude: float, depth: float) -> bool:
        """
        Determine if earthquake is tsunami-capable
        
        Args:
            magnitude: Earthquake magnitude
            depth: Earthquake depth in km
            
        Returns:
            True if earthquake could generate tsunami
        """
        # Tsunami potential criteria:
        # - Magnitude >= 6.5
        # - Shallow depth (< 70 km for strong earthquakes)
        # - Undersea location (checked separately)
        
        if magnitude >= 7.5:
            return depth < 100
        elif magnitude >= 7.0:
            return depth < 70
        elif magnitude >= 6.5:
            return depth < 50
        
        return False
