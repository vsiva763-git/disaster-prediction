"""
Bathymetry Data Loader
Loads and processes ocean bathymetry data from GEBCO or other sources
"""

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from typing import Dict, Tuple, Optional
from loguru import logger


class BathymetryLoader:
    """Loads and processes bathymetry (ocean depth) data"""
    
    def __init__(self, config: Dict, data_dir: str = "data/raw"):
        """
        Initialize Bathymetry loader
        
        Args:
            config: Configuration dictionary
            data_dir: Directory containing bathymetry files
        """
        self.config = config
        self.data_dir = Path(data_dir)
        self.bathymetry_data = None
        self.india_region = config['india_region']
    
    def load_gebco_data(self, file_path: Optional[str] = None) -> xr.Dataset:
        """
        Load GEBCO bathymetry data from NetCDF file
        
        Args:
            file_path: Path to GEBCO NetCDF file
            
        Returns:
            xarray Dataset with bathymetry data
        """
        try:
            if file_path is None:
                # Look for GEBCO file in data directory
                gebco_files = list(self.data_dir.glob("GEBCO*.nc"))
                if not gebco_files:
                    logger.warning("No GEBCO bathymetry file found")
                    return self._create_dummy_bathymetry()
                file_path = gebco_files[0]
            
            logger.info(f"Loading bathymetry data from {file_path}...")
            ds = xr.open_dataset(file_path)
            
            # Extract Indian Ocean region
            ds = self._extract_indian_ocean_region(ds)
            
            self.bathymetry_data = ds
            logger.success("Bathymetry data loaded successfully")
            return ds
            
        except Exception as e:
            logger.error(f"Failed to load bathymetry data: {e}")
            return self._create_dummy_bathymetry()
    
    def _extract_indian_ocean_region(self, ds: xr.Dataset) -> xr.Dataset:
        """
        Extract Indian Ocean region from global dataset
        
        Args:
            ds: Global bathymetry dataset
            
        Returns:
            Subset for Indian Ocean region
        """
        # Define Indian Ocean bounding box
        lat_min, lat_max = -20, 30
        lon_min, lon_max = 40, 110
        
        # Select region (variable names may differ)
        if 'lat' in ds.dims and 'lon' in ds.dims:
            ds = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
        elif 'latitude' in ds.dims and 'longitude' in ds.dims:
            ds = ds.sel(latitude=slice(lat_min, lat_max), longitude=slice(lon_min, lon_max))
        
        return ds
    
    def _create_dummy_bathymetry(self) -> xr.Dataset:
        """
        Create dummy bathymetry data for testing
        
        Returns:
            Synthetic bathymetry dataset
        """
        logger.warning("Creating dummy bathymetry data for testing")
        
        lat = np.linspace(-20, 30, 100)
        lon = np.linspace(40, 110, 140)
        
        # Create synthetic depth data (negative values for ocean)
        depth = np.random.uniform(-5000, -100, (len(lat), len(lon)))
        
        ds = xr.Dataset(
            {
                'elevation': (['lat', 'lon'], depth)
            },
            coords={
                'lat': lat,
                'lon': lon
            }
        )
        
        return ds
    
    def get_depth_at_location(self, latitude: float, longitude: float) -> float:
        """
        Get bathymetry depth at specific coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Depth in meters (negative for below sea level)
        """
        if self.bathymetry_data is None:
            self.load_gebco_data()
        
        try:
            # Find nearest point
            depth = self.bathymetry_data.sel(
                lat=latitude, 
                lon=longitude, 
                method='nearest'
            )['elevation'].values
            
            return float(depth)
        except Exception as e:
            logger.error(f"Failed to get depth at ({latitude}, {longitude}): {e}")
            return -3000.0  # Default depth
    
    def calculate_distance_to_coast(self, latitude: float, longitude: float) -> float:
        """
        Calculate approximate distance to nearest coast
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Distance to coast in km
        """
        if self.bathymetry_data is None:
            self.load_gebco_data()
        
        try:
            # Simplified calculation - find nearest positive elevation (land)
            # In production, use proper coastline dataset
            
            # For now, estimate based on region
            coastline_regions = self.india_region['coastline']
            
            min_distance = float('inf')
            for region_name, bounds in coastline_regions.items():
                # Calculate distance to region boundary
                lat_center = (bounds['min_lat'] + bounds['max_lat']) / 2
                lon_center = (bounds['min_lon'] + bounds['max_lon']) / 2
                
                distance = self._haversine_distance(
                    latitude, longitude, lat_center, lon_center
                )
                min_distance = min(min_distance, distance)
            
            return min_distance
            
        except Exception as e:
            logger.error(f"Failed to calculate distance to coast: {e}")
            return 100.0  # Default distance
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def extract_features(self, latitude: float, longitude: float) -> Dict[str, float]:
        """
        Extract bathymetry-related features for a location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary of bathymetry features
        """
        return {
            'bathymetry': self.get_depth_at_location(latitude, longitude),
            'distance_to_coast': self.calculate_distance_to_coast(latitude, longitude),
            'is_deep_ocean': self.get_depth_at_location(latitude, longitude) < -4000
        }
