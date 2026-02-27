"""
Real-time Monitoring Script
Run standalone tsunami monitoring
"""

import sys
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.inference_engine import RealTimeInferenceEngine
from src.utils import setup_logger
from loguru import logger


def main():
    """Main monitoring function"""
    
    parser = argparse.ArgumentParser(
        description='Real-time Tsunami Monitoring'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='models/best_model.keras',
        help='Path to trained model'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Monitoring interval in seconds (default: 300)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run check once and exit'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level='INFO')
    
    logger.info("=" * 60)
    logger.info("🌊 TSUNAMI REAL-TIME MONITORING")
    logger.info("=" * 60)
    
    # Initialize inference engine
    logger.info("Initializing inference engine...")
    engine = RealTimeInferenceEngine(
        config_path=args.config,
        model_path=args.model
    )
    
    if args.once:
        # Run single check
        logger.info("Running single tsunami check...")
        assessment = engine.run_tsunami_check()
        
        if assessment:
            logger.info("\n" + "=" * 60)
            logger.info("ASSESSMENT RESULTS")
            logger.info("=" * 60)
            logger.info(f"Alert Level: {assessment['alert_level']}")
            logger.info(f"India at Risk: {assessment['india_at_risk']}")
            logger.info(f"Risk Score: {assessment.get('india_risk_score', 0):.3f}")
            logger.info(f"Message: {assessment['alert_message']}")
            logger.info("=" * 60)
        else:
            logger.warning("No assessment generated")
    else:
        # Start continuous monitoring
        logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            engine.start_monitoring(interval_seconds=args.interval)
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\nStopping monitoring...")
            engine.stop_monitoring()
            logger.success("Monitoring stopped")


if __name__ == '__main__':
    main()
