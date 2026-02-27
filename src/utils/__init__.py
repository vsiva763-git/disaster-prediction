"""
Utilities Module
Helper functions and utilities
"""

from .logger import setup_logger
from .config_loader import load_config


def download_global_tsunami_data(*args, **kwargs):
	from .data_helpers import download_global_tsunami_data as _download_global_tsunami_data
	return _download_global_tsunami_data(*args, **kwargs)

__all__ = ['setup_logger', 'load_config', 'download_global_tsunami_data']
