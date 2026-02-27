"""
Configuration Loader
Load and validate configuration
"""

import yaml
from pathlib import Path
from typing import Dict
from loguru import logger


def load_config(config_path: str = 'config/config.yaml') -> Dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate configuration
        _validate_config(config)
        
        logger.success(f"Configuration loaded from {config_path}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def _validate_config(config: Dict):
    """
    Validate configuration structure
    
    Args:
        config: Configuration dictionary
    """
    required_sections = ['apis', 'india_region', 'model', 'data']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate API configurations
    required_apis = ['usgs_earthquake', 'noaa_tides', 'noaa_buoys', 'incois']
    for api in required_apis:
        if api not in config['apis']:
            logger.warning(f"Missing API configuration: {api}")
    
    # Validate model configuration
    if 'architecture' not in config['model']:
        raise ValueError("Missing model architecture configuration")
    
    if 'input_features' not in config['model']:
        raise ValueError("Missing model input features configuration")
    
    logger.info("Configuration validation passed")


def save_config(config: Dict, config_path: str = 'config/config.yaml'):
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        logger.success(f"Configuration saved to {config_path}")
        
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        raise
