"""
Flask Application Factory
Creates and configures Flask app
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from loguru import logger
import sys
from datetime import datetime

# Configure loguru
logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("logs/app.log", rotation="100 MB", retention="30 days", level="DEBUG")

socketio = SocketIO()


def create_app(config_path='config/config.yaml'):
    """
    Create Flask application
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'tsunami-warning-system-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    
    # Enable CORS for API access and Railway healthchecks
    # Allow all origins for /api endpoints and healthcheck.railway.app for /health
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/health": {"origins": "*"}})

    socketio.init_app(app, cors_allowed_origins="*")
    
    logger.success("Flask application created successfully")
    
    return app
