"""
Main Entry Point
Runs the Tsunami Early Warning System web application
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.web_app import create_app
from src.web_app.app import socketio
from src.utils import setup_logger
from loguru import logger


def main():
    """Main function to run the web application"""
    
    parser = argparse.ArgumentParser(
        description='Tsunami Early Warning System for India'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logger(level=log_level)
    
    logger.info("=" * 60)
    logger.info("🌊 TSUNAMI EARLY WARNING SYSTEM - INDIA")
    logger.info("=" * 60)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Debug: {args.debug}")
    logger.info(f"Config: {args.config}")
    logger.info("=" * 60)
    
    # Create Flask app
    app = create_app(config_path=args.config)
    
    # Run with SocketIO support
    try:
        logger.success("Starting web server...")
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
