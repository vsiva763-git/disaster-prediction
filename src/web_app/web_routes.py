"""
Web Interface Routes
Serves HTML dashboards and web interface
"""

from flask import Blueprint, render_template, send_from_directory
from loguru import logger
import os

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """
    Main dashboard page
    
    Returns:
        HTML dashboard
    """
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        # Return simple HTML if template not found
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tsunami Early Warning System - India</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    padding: 30px;
                }
                h1 {
                    color: #667eea;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }
                .status-card {
                    background: #f7fafc;
                    border-left: 4px solid #4299e1;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }
                .api-link {
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    margin: 10px 10px 10px 0;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }
                .api-link:hover {
                    background: #764ba2;
                }
                .feature-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .feature {
                    background: #edf2f7;
                    padding: 20px;
                    border-radius: 8px;
                    border-top: 3px solid #667eea;
                }
                .feature h3 {
                    color: #667eea;
                    margin-top: 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌊 Tsunami Early Warning System - India</h1>
                
                <div class="status-card">
                    <h2>System Status: ✅ Operational</h2>
                    <p>AI-powered tsunami monitoring and prediction for Indian coastlines</p>
                </div>
                
                <h2>API Endpoints</h2>
                <div>
                    <a href="/api/status" class="api-link">System Status</a>
                    <a href="/api/current-assessment" class="api-link">Current Assessment</a>
                    <a href="/api/earthquake/recent" class="api-link">Recent Earthquakes</a>
                    <a href="/api/ocean/conditions" class="api-link">Ocean Conditions</a>
                    <a href="/api/advisories/incois" class="api-link">INCOIS Advisories</a>
                    <a href="/api/alert-history" class="api-link">Alert History</a>
                    <a href="/api/model/info" class="api-link">Model Info</a>
                </div>
                
                <div class="feature-list">
                    <div class="feature">
                        <h3>🤖 AI-Powered Detection</h3>
                        <p>Multi-modal CNN-LSTM model trained on global tsunami data for accurate predictions</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🌍 Real-time Data</h3>
                        <p>Continuous monitoring via USGS earthquakes, NOAA ocean data, and INCOIS advisories</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🇮🇳 India-Specific</h3>
                        <p>Intelligent filtering ensures alerts only when India is at risk</p>
                    </div>
                    
                    <div class="feature">
                        <h3>📊 Comprehensive Analysis</h3>
                        <p>Analyzes earthquake magnitude, depth, location, ocean conditions, and bathymetry</p>
                    </div>
                    
                    <div class="feature">
                        <h3>⚡ Fast Response</h3>
                        <p>Real-time processing and immediate risk assessment</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🔓 Open Data</h3>
                        <p>Built entirely on free public APIs - no sensor infrastructure required</p>
                    </div>
                </div>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <h2>Quick Start</h2>
                    <pre style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto;">
# Start monitoring
curl -X POST http://localhost:5000/api/monitoring/start

# Run manual check
curl -X POST http://localhost:5000/api/monitoring/run-check

# Get current assessment
curl http://localhost:5000/api/current-assessment
                    </pre>
                </div>
            </div>
        </body>
        </html>
        """


@web_bp.route('/dashboard')
def dashboard():
    """Alternative dashboard route"""
    return index()


@web_bp.route('/docs')
def documentation():
    """API documentation page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation - Tsunami Warning System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 5px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #3498db; }
            .method { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
            .get { background: #2ecc71; color: white; }
            .post { background: #3498db; color: white; }
            code { background: #34495e; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌊 Tsunami Warning System API Documentation</h1>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/status</strong>
                <p>Get current system status and monitoring state</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/current-assessment</strong>
                <p>Get the latest tsunami risk assessment</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/run-check</strong>
                <p>Manually trigger a tsunami risk check</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/monitoring/start</strong>
                <p>Start real-time monitoring</p>
                <p>Body: <code>{"interval_seconds": 300}</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/monitoring/stop</strong>
                <p>Stop real-time monitoring</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/earthquake/recent</strong>
                <p>Get recent earthquakes</p>
                <p>Query params: <code>hours=24</code>, <code>min_magnitude=5.5</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/ocean/conditions</strong>
                <p>Get current ocean conditions from tides and buoys</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/advisories/incois</strong>
                <p>Get current INCOIS advisories</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/alert-history</strong>
                <p>Get alert history</p>
                <p>Query params: <code>hours=24</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/model/info</strong>
                <p>Get model architecture and configuration information</p>
            </div>
            
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """
