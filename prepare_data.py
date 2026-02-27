"""
Data Preparation Script
Download and prepare training data
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import (
    setup_logger, 
    download_global_tsunami_data, 
    create_sample_dataset,
    prepare_training_data,
    download_gebco_bathymetry_info
)
from loguru import logger


def main():
    """Main data preparation function"""
    
    parser = argparse.ArgumentParser(
        description='Prepare Training Data for Tsunami Warning System'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download global tsunami data from NOAA'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create synthetic sample dataset'
    )
    parser.add_argument(
        '--prepare',
        action='store_true',
        help='Prepare and process training data'
    )
    parser.add_argument(
        '--bathymetry-info',
        action='store_true',
        help='Show bathymetry download instructions'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for data'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all preparation steps'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level='INFO')
    
    logger.info("=" * 60)
    logger.info("📊 DATA PREPARATION")
    logger.info("=" * 60)
    
    if args.all or args.bathymetry_info:
        logger.info("\n" + download_gebco_bathymetry_info())
    
    if args.all or args.download:
        logger.info("\nDownloading global tsunami data...")
        success = download_global_tsunami_data(args.output_dir)
        if not success:
            logger.warning("Download failed, will create sample data instead")
            args.sample = True
    
    if args.all or args.sample:
        logger.info("\nCreating synthetic sample dataset...")
        create_sample_dataset(args.output_dir, n_samples=1000)
    
    if args.all or args.prepare:
        logger.info("\nPreparing training data...")
        success = prepare_training_data(
            raw_data_dir=args.output_dir,
            processed_data_dir='data/processed'
        )
        if success:
            logger.success("Training data prepared successfully")
        else:
            logger.error("Failed to prepare training data")
    
    logger.success("\n" + "=" * 60)
    logger.success("✅ DATA PREPARATION COMPLETED")
    logger.success("=" * 60)


if __name__ == '__main__':
    main()
