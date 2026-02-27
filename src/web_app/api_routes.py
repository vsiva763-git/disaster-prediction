"""
REST API Routes
Provides RESTful API endpoints for tsunami warning system
"""

from flask import Blueprint, jsonify, request
from loguru import logger
from datetime import datetime
import threading

from ..inference_engine import RealTimeInferenceEngine

api_bp = Blueprint('api', __name__)

# Global inference engine instance
inference_engine = None
engine_lock = threading.Lock()


def get_inference_engine():
    """Get or create inference engine instance"""
    global inference_engine
    
    with engine_lock:
        if inference_engine is None:
            logger.info("Initializing inference engine...")
            inference_engine = RealTimeInferenceEngine()
        return inference_engine


@api_bp.route('/status', methods=['GET'])
def get_system_status():
    """
    Get current system status
    
    Returns:
        JSON with system status information
    """
    try:
        engine = get_inference_engine()
        status = engine.get_current_status()
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/current-assessment', methods=['GET'])
def get_current_assessment():
    """
    Get current tsunami risk assessment
    
    Returns:
        JSON with latest assessment
    """
    try:
        engine = get_inference_engine()
        assessment = engine.current_assessment
        
        if assessment is None:
            return jsonify({
                'success': True,
                'data': {
                    'message': 'No assessment available yet',
                    'run_check': True
                }
            }), 200
        
        return jsonify({
            'success': True,
            'data': assessment
        }), 200
    except Exception as e:
        logger.error(f"Error getting current assessment: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/run-check', methods=['POST'])
def run_manual_check():
    """
    Manually trigger tsunami risk check
    
    Returns:
        JSON with assessment results
    """
    try:
        engine = get_inference_engine()
        
        logger.info("Manual tsunami check triggered")
        assessment = engine.run_tsunami_check()
        
        return jsonify({
            'success': True,
            'data': assessment
        }), 200
    except Exception as e:
        logger.error(f"Error running manual check: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitoring/start', methods=['POST'])
def start_monitoring():
    """
    Start real-time monitoring
    
    Request body:
        {
            "interval_seconds": 300  (optional, default 300)
        }
    
    Returns:
        JSON with success status
    """
    try:
        data = request.get_json() or {}
        interval = data.get('interval_seconds', 300)
        
        engine = get_inference_engine()
        engine.start_monitoring(interval_seconds=interval)
        
        return jsonify({
            'success': True,
            'message': f'Monitoring started with {interval}s interval',
            'data': {
                'interval_seconds': interval
            }
        }), 200
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """
    Stop real-time monitoring
    
    Returns:
        JSON with success status
    """
    try:
        engine = get_inference_engine()
        engine.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped'
        }), 200
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/earthquake/recent', methods=['GET'])
def get_recent_earthquakes():
    """
    Get recent earthquakes from USGS
    
    Query parameters:
        hours: Lookback period (default 24)
        min_magnitude: Minimum magnitude (default 5.5)
    
    Returns:
        JSON with earthquake data
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        min_mag = request.args.get('min_magnitude', default=5.5, type=float)
        
        engine = get_inference_engine()
        earthquakes = engine.usgs_collector.fetch_recent_earthquakes(hours=hours)
        
        if earthquakes.empty:
            return jsonify({
                'success': True,
                'data': {
                    'count': 0,
                    'earthquakes': []
                }
            }), 200
        
        # Filter by magnitude
        earthquakes = earthquakes[earthquakes['magnitude'] >= min_mag]
        
        # Convert to JSON-serializable format
        eq_list = earthquakes.to_dict('records')
        for eq in eq_list:
            if 'time' in eq and hasattr(eq['time'], 'isoformat'):
                eq['time'] = eq['time'].isoformat()
        
        return jsonify({
            'success': True,
            'data': {
                'count': len(eq_list),
                'earthquakes': eq_list
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching earthquakes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/ocean/conditions', methods=['GET'])
def get_ocean_conditions():
    """
    Get current ocean conditions
    
    Returns:
        JSON with ocean data from tides and buoys
    """
    try:
        engine = get_inference_engine()
        
        # Fetch tide data
        tide_data = engine.noaa_tides_collector.fetch_all_stations(hours=6)
        
        # Fetch buoy data
        buoy_data = engine.noaa_buoys_collector.fetch_all_buoys()
        
        # Analyze conditions
        conditions = engine._analyze_ocean_conditions(tide_data, buoy_data)
        
        # Format response
        tide_summary = {}
        for station_id, df in tide_data.items():
            if not df.empty:
                tide_summary[station_id] = {
                    'latest_reading': df.iloc[-1].to_dict(),
                    'anomaly_score': engine.noaa_tides_collector.calculate_sea_level_anomaly(df)
                }
        
        buoy_summary = {}
        for station_id, df in buoy_data.items():
            if not df.empty:
                buoy_summary[station_id] = {
                    'latest_reading': df.iloc[-1].to_dict(),
                    'tsunami_signature': engine.noaa_buoys_collector.detect_tsunami_signature(df)
                }
        
        return jsonify({
            'success': True,
            'data': {
                'conditions': conditions,
                'tide_stations': tide_summary,
                'buoy_stations': buoy_summary
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching ocean conditions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/advisories/incois', methods=['GET'])
def get_incois_advisories():
    """
    Get current INCOIS advisories
    
    Returns:
        JSON with INCOIS advisory data
    """
    try:
        engine = get_inference_engine()
        advisories = engine.incois_collector.fetch_current_advisories()
        risk_info = engine.incois_collector.get_india_specific_risk()
        
        return jsonify({
            'success': True,
            'data': {
                'advisories': advisories,
                'risk_assessment': risk_info
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching INCOIS advisories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/alert-history', methods=['GET'])
def get_alert_history():
    """
    Get alert history
    
    Query parameters:
        hours: Lookback period (default 24)
    
    Returns:
        JSON with historical alerts
    """
    try:
        hours = request.args.get('hours', default=24, type=int)
        
        engine = get_inference_engine()
        history = engine.risk_assessor.get_alert_history(hours=hours)
        
        return jsonify({
            'success': True,
            'data': {
                'count': len(history),
                'alerts': history
            }
        }), 200
    except Exception as e:
        logger.error(f"Error fetching alert history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """
    Get model information
    
    Returns:
        JSON with model details
    """
    try:
        engine = get_inference_engine()
        
        info = {
            'model_loaded': engine.model.model is not None,
            'architecture': 'CNN-LSTM Multi-modal',
            'input_features': engine.config['model']['input_features'],
            'thresholds': engine.config['model']['thresholds']
        }
        
        if engine.model.model is not None:
            info['model_summary'] = engine.model.get_model_summary()
        
        return jsonify({
            'success': True,
            'data': info
        }), 200
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def register_api_routes(app):
    """
    Register API routes with Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(api_bp, url_prefix='/api')
    logger.success("API routes registered")
