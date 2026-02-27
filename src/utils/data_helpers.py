"""
Data Helpers
Functions to download and prepare training data
"""

import requests
import pandas as pd
from pathlib import Path
from typing import Optional
from loguru import logger


def download_global_tsunami_data(output_dir: str = 'data/raw') -> bool:
    """
    Download global tsunami dataset from NOAA
    
    Args:
        output_dir: Directory to save downloaded data
        
    Returns:
        True if successful, False otherwise
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # NOAA NGDC Tsunami Database
    tsunami_url = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events"
    
    try:
        logger.info("Downloading global tsunami dataset from NOAA...")
        
        # Download tsunami events
        response = requests.get(tsunami_url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' in data:
            df = pd.DataFrame(data['items'])
            output_file = output_path / 'global_tsunami_events.csv'
            df.to_csv(output_file, index=False)
            logger.success(f"Downloaded {len(df)} tsunami events to {output_file}")
            return True
        else:
            logger.warning("No tsunami data found in response")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download tsunami data: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing tsunami data: {e}")
        return False


def create_sample_dataset(output_dir: str = 'data/raw', n_samples: int = 1000):
    """
    Create synthetic sample dataset for testing
    
    Args:
        output_dir: Directory to save data
        n_samples: Number of samples to create
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating synthetic dataset with {n_samples} samples...")
    
    # Generate synthetic tsunami events
    np.random.seed(42)
    
    data = {
        'event_id': [f'TSUNAMI_{i:05d}' for i in range(n_samples)],
        'date': [
            (datetime(2010, 1, 1) + timedelta(days=np.random.randint(0, 5000))).isoformat()
            for _ in range(n_samples)
        ],
        'latitude': np.random.uniform(-60, 60, n_samples),
        'longitude': np.random.uniform(-180, 180, n_samples),
        'magnitude': np.random.uniform(5.5, 9.5, n_samples),
        'depth': np.random.uniform(5, 100, n_samples),
        'tsunami_occurred': np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05]),
        'intensity': np.random.choice(['none', 'low', 'medium', 'high'], 
                                     size=n_samples, 
                                     p=[0.95, 0.03, 0.015, 0.005])
    }
    
    df = pd.DataFrame(data)
    
    # Adjust intensity for events without tsunami
    df.loc[df['tsunami_occurred'] == 0, 'intensity'] = 'none'
    
    output_file = output_path / 'global_tsunami_events.csv'
    df.to_csv(output_file, index=False)
    
    logger.success(f"Created synthetic dataset: {output_file}")


def download_gebco_bathymetry_info():
    """
    Provide information about downloading GEBCO bathymetry data
    """
    info = """
    GEBCO Bathymetry Data Download Instructions:
    
    1. Visit: https://www.gebco.net/data_and_products/gridded_bathymetry_data/
    
    2. Download the GEBCO Grid (NetCDF format)
       - Select region covering Indian Ocean (40°E to 110°E, 20°S to 30°N)
       - Choose appropriate resolution (15 arc-second recommended)
    
    3. Save the downloaded NetCDF file to: data/raw/
       - Filename should match pattern: GEBCO*.nc
    
    4. The system will automatically load bathymetry data on startup
    
    Alternative: The system can operate with synthetic bathymetry for testing
    """
    
    logger.info(info)
    return info


def prepare_training_data(raw_data_dir: str = 'data/raw',
                         processed_data_dir: str = 'data/processed') -> bool:
    """
    Prepare training data from raw datasets
    
    Args:
        raw_data_dir: Directory with raw data
        processed_data_dir: Directory for processed data
        
    Returns:
        True if successful
    """
    try:
        raw_path = Path(raw_data_dir)
        processed_path = Path(processed_data_dir)
        processed_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Preparing training data...")
        
        # Load global tsunami events
        tsunami_file = raw_path / 'global_tsunami_events.csv'
        
        if not tsunami_file.exists():
            logger.warning("Global tsunami events file not found, creating sample data...")
            create_sample_dataset(raw_data_dir)
        
        df = pd.read_csv(tsunami_file)
        
        # Data cleaning and preprocessing
        df = df.dropna(subset=['magnitude', 'depth', 'latitude', 'longitude'])
        
        # Filter relevant events (magnitude >= 5.5)
        df = df[df['magnitude'] >= 5.5]
        
        # Save processed data
        output_file = processed_path / 'processed_tsunami_events.csv'
        df.to_csv(output_file, index=False)
        
        logger.success(f"Processed {len(df)} events saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error preparing training data: {e}")
        return False
