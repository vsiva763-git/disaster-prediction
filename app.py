#!/usr/bin/env python3
"""
Flask API for Tsunami Detection Model
REST API endpoint for real-time tsunami prediction
"""

from flask import Flask, request, jsonify, send_file, make_response, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
from pathlib import Path
import logging
from datetime import datetime, timedelta
import requests as http_requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model
MODEL_CANDIDATES = [
    Path('./models/tsunami_detection_binary_focal.keras'),
    Path('./models/best_model.keras'),
]
METADATA_PATH = Path('./models/model_metadata.json')
loaded_model_path = None

try:
    model = None
    for candidate in MODEL_CANDIDATES:
        if not candidate.exists():
            continue

        try:
            # Load model weights only (without custom loss function)
            # This bypasses the custom loss deserialization issue
            model = tf.keras.models.load_model(str(candidate), compile=False)
            # Compile with standard binary crossentropy for inference
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            loaded_model_path = candidate
            logger.info(f"✓ Model loaded from {candidate} (weights only, compiled with binary_crossentropy)")
            break
        except Exception as load_error:
            logger.warning(f"Could not load model from {candidate}: {load_error}")

    if model is None:
        tried = ', '.join(str(path) for path in MODEL_CANDIDATES)
        raise FileNotFoundError(f"No loadable model found. Tried: {tried}")
except Exception as e:
    logger.error(f"✗ Failed to load model: {e}")
    model = None

# Load metadata
try:
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
    logger.info(f"✓ Metadata loaded from {METADATA_PATH}")
except Exception as e:
    logger.error(f"✗ Failed to load metadata: {e}")
    metadata = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_type': metadata.get('model_type') if metadata else None
    }), 200


@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def serve_dashboard():
    """Serve the live dashboard with Indian Ocean data"""
    try:
        response = make_response(render_template('index_live.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        return jsonify({'error': 'Dashboard not found'}), 404


@app.route('/summary', methods=['GET'])
def serve_summary():
    """Serve a lightweight summary page"""
    try:
        response = make_response(render_template('summary.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error serving summary: {e}")
        return jsonify({'error': 'Summary page not found'}), 404


@app.route('/iot', methods=['GET'])
def serve_iot_dashboard():
    """Serve the IoT Alert System dashboard"""
    try:
        response = make_response(render_template('iot_dashboard.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        logger.info("IoT dashboard requested")
        return response
    except Exception as e:
        logger.error(f"Error serving IoT dashboard: {e}")
        return jsonify({'error': 'IoT dashboard not found'}), 404


@app.route('/test-data', methods=['GET'])
def get_test_data():
    """
    Return test earthquake data for demonstration
    Shows how the system responds to real earthquake scenarios
    """
    return jsonify({
        'success': True,
        'region': 'Indian Ocean',
        'time_range': {
            'start': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
            'end': datetime.utcnow().isoformat()
        },
        'total_earthquakes': 3,
        'earthquakes': [
            {
                'magnitude': 6.8,
                'location': 'Off West Coast of Sumatra',
                'latitude': 0.5,
                'longitude': 95.2,
                'depth': 45,
                'time': (datetime.utcnow() - timedelta(hours=2)).timestamp() * 1000,
                'url': 'https://earthquake.usgs.gov/earthquakes/events/',
                'tsunami_probability': 0.75,
                'tsunami_risk': 'HIGH'
            },
            {
                'magnitude': 5.9,
                'location': 'Bay of Bengal',
                'latitude': 10.2,
                'longitude': 86.5,
                'depth': 32,
                'time': (datetime.utcnow() - timedelta(hours=6)).timestamp() * 1000,
                'url': 'https://earthquake.usgs.gov/earthquakes/events/',
                'tsunami_probability': 0.38,
                'tsunami_risk': 'MODERATE'
            },
            {
                'magnitude': 5.2,
                'location': 'Andaman Sea',
                'latitude': 8.5,
                'longitude': 94.3,
                'depth': 28,
                'time': (datetime.utcnow() - timedelta(hours=12)).timestamp() * 1000,
                'url': 'https://earthquake.usgs.gov/earthquakes/events/',
                'tsunami_probability': 0.15,
                'tsunami_risk': 'LOW'
            }
        ],
        'predictions': [],
        'high_risk_count': 1,
        'alerts_triggered': 1
    }), 200


@app.route('/live-data', methods=['GET'])
def get_live_data():
    """
    Fetch live seismic data from Indian Ocean region and predict tsunami risk
    Data source: USGS Earthquake API
    """
    try:
        # Indian Ocean region coordinates (approximate bounding box)
        # Latitude: -40 to 30, Longitude: 40 to 120
        min_lat, max_lat = -40, 30
        min_lon, max_lon = 40, 120
        
        # Get earthquakes from last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # USGS Earthquake API
        usgs_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'minlatitude': min_lat,
            'maxlatitude': max_lat,
            'minlongitude': min_lon,
            'maxlongitude': max_lon,
            'minmagnitude': 4.0,  # Only significant earthquakes
            'orderby': 'time-asc'
        }
        
        response = http_requests.get(usgs_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        earthquakes = []
        predictions = []
        
        for feature in data.get('features', [])[:10]:  # Limit to 10 most recent
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            # Extract earthquake info
            eq_info = {
                'id': feature.get('id'),
                'magnitude': props.get('mag'),
                'location': props.get('place'),
                'time': props.get('time'),
                'latitude': coords[1],
                'longitude': coords[0],
                'depth': coords[2],
                'url': props.get('url')
            }
            
            # Convert earthquake data to model input format
            # Create synthetic seismic pattern based on earthquake parameters
            seismic_data = create_seismic_pattern(
                magnitude=eq_info['magnitude'],
                depth=eq_info['depth'],
                latitude=eq_info['latitude'],
                longitude=eq_info['longitude']
            )
            
            # Make prediction
            if model is not None:
                input_data = np.expand_dims(seismic_data, axis=0)
                prediction = model.predict(input_data, verbose=0)
                probability = float(prediction[0][0])
                
                eq_info['tsunami_probability'] = probability
                eq_info['tsunami_risk'] = 'HIGH' if probability > 0.5 else 'MODERATE' if probability > 0.2 else 'LOW'
                eq_info['alert'] = probability > 0.1
                
                predictions.append({
                    'earthquake': eq_info,
                    'prediction': {
                        'probability': probability,
                        'risk_level': eq_info['tsunami_risk'],
                        'alert': eq_info['alert']
                    }
                })
            
            earthquakes.append(eq_info)
        
        return jsonify({
            'success': True,
            'region': 'Indian Ocean',
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'total_earthquakes': len(earthquakes),
            'earthquakes': earthquakes,
            'predictions': predictions,
            'high_risk_count': sum(1 for p in predictions if p['prediction']['risk_level'] == 'HIGH'),
            'alerts_triggered': sum(1 for p in predictions if p['prediction']['alert'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching live data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch live seismic data'
        }), 500


@app.route('/wave-data', methods=['GET'])
def get_wave_data():
    """
    Fetch real-time ocean wave and water level data from monitoring stations
    Data sources: IOC Sea Level stations, NOAA DART buoys
    """
    try:
        # Define monitoring stations with IOC codes
        stations = {
            'arabian': {
                'name': 'Arabian Sea',
                'stations': [
                    {'id': 'okha', 'ioc_code': 'okha', 'lat': 22.47, 'lon': 69.07, 'name': 'Okha, India'},
                    {'id': 'mumbai', 'ioc_code': 'bomb', 'lat': 18.95, 'lon': 72.82, 'name': 'Mumbai, India'},
                ]
            },
            'bengal': {
                'name': 'Bay of Bengal',
                'stations': [
                    {'id': 'chennai', 'ioc_code': 'ched', 'lat': 13.10, 'lon': 80.30, 'name': 'Chennai, India'},
                    {'id': 'vizag', 'ioc_code': 'visa', 'lat': 17.68, 'lon': 83.28, 'name': 'Visakhapatnam, India'},
                ]
            },
            'andaman': {
                'name': 'Andaman Sea',
                'stations': [
                    {'id': 'portblair', 'ioc_code': 'port', 'lat': 11.66, 'lon': 92.73, 'name': 'Port Blair, India'},
                    {'id': 'phuket', 'ioc_code': 'phuk', 'lat': 7.89, 'lon': 98.39, 'name': 'Phuket, Thailand'},
                ]
            }
        }
        
        wave_data = {}
        
        for region_key, region_info in stations.items():
            region_readings = []
            
            for station in region_info['stations']:
                try:
                    # Try IOC Sea Level Monitoring API
                    ioc_code = station.get('ioc_code', '').upper()
                    
                    # IOC API endpoint - last 1 hour of data
                    ioc_url = f"http://www.ioc-sealevelmonitoring.org/service.php"
                    params = {
                        'code': ioc_code,
                        'period': 0.04  # Last ~1 hour (0.04 days)
                    }
                    
                    response = http_requests.get(ioc_url, params=params, timeout=10)
                    
                    if response.status_code == 200 and len(response.text) > 100:
                        # Parse IOC CSV data
                        lines = response.text.strip().split('\n')
                        readings = []
                        
                        # Skip header lines and parse data
                        data_started = False
                        for line in lines:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            if 'slevel' in line.lower() or 'time' in line.lower():
                                data_started = True
                                continue
                            if data_started:
                                parts = line.split(',')
                                if len(parts) >= 2:
                                    try:
                                        # Format: timestamp, water_level, ...
                                        timestamp = parts[0].strip()
                                        water_level = float(parts[1].strip())
                                        
                                        # Convert to meters and add offset for visualization
                                        water_level_m = water_level / 100.0  # cm to meters
                                        water_level_m += 5.0  # Add baseline for positive display
                                        
                                        readings.append({
                                            'time': timestamp,
                                            'value': round(water_level_m, 3),
                                            'quality': 'verified'
                                        })
                                    except (ValueError, IndexError):
                                        continue
                        
                        if len(readings) >= 5:  # Need at least 5 readings
                            # Take last 10 readings
                            readings = readings[-10:]
                            
                            region_readings.append({
                                'station_id': station['id'],
                                'station_name': station['name'],
                                'location': {'lat': station['lat'], 'lon': station['lon']},
                                'readings': readings,
                                'source': 'IOC Sea Level Station',
                                'data_type': 'sea_level',
                                'unit': 'meters',
                                'real_data': True
                            })
                            logger.info(f"✓ Real-time data from {station['name']} ({ioc_code}): {len(readings)} readings")
                            continue
                    
                except Exception as e:
                    logger.debug(f"IOC data unavailable for {station['name']}: {e}")
                
                # Try NDBC/DART buoys for backup
                try:
                    # Map regions to nearby DART buoys
                    dart_buoys = {
                        'bengal': '23401',  # Bay of Bengal DART
                        'andaman': '23401'  # Also covers Andaman
                    }
                    
                    if region_key in dart_buoys:
                        buoy_id = dart_buoys[region_key]
                        dart_url = f"https://www.ndbc.noaa.gov/data/realtime2/{buoy_id}.txt"
                        
                        response = http_requests.get(dart_url, timeout=8)
                        
                        if response.status_code == 200:
                            lines = response.text.strip().split('\n')
                            readings = []
                            
                            # Parse NDBC format (first 2 lines are headers)
                            for line in lines[2:12]:  # Get 10 readings
                                parts = line.split()
                                if len(parts) >= 5:
                                    try:
                                        # NDBC format: YY MM DD hh mm WDIR WSPD GST WVHT ...
                                        year, month, day, hour, minute = parts[0:5]
                                        
                                        # Construct timestamp
                                        timestamp = f"20{year}-{month}-{day} {hour}:{minute}"
                                        
                                        # Get wave height if available (usually column 8)
                                        wave_height = float(parts[8]) if len(parts) > 8 and parts[8] != 'MM' else 5.0
                                        
                                        readings.append({
                                            'time': timestamp,
                                            'value': round(wave_height, 2),
                                            'quality': 'measured'
                                        })
                                    except (ValueError, IndexError):
                                        continue
                            
                            if len(readings) >= 5:
                                region_readings.append({
                                    'station_id': f'dart_{buoy_id}',
                                    'station_name': f'DART Buoy {buoy_id}',
                                    'location': {'lat': station['lat'], 'lon': station['lon']},
                                    'readings': readings[-10:],
                                    'source': 'NOAA DART Buoy',
                                    'data_type': 'wave_height',
                                    'unit': 'meters',
                                    'real_data': True
                                })
                                logger.info(f"✓ Real-time DART data from buoy {buoy_id}: {len(readings)} readings")
                                continue
                
                except Exception as e:
                    logger.debug(f"DART data unavailable: {e}")
                
                # If no real data available, generate realistic fallback
                logger.info(f"Using simulated data for {station['name']}")
                current_time = datetime.utcnow()
                readings = []
                
                regional_params = {
                    'arabian': {'baseline': 4.2, 'tide_amp': 1.8, 'wave_amp': 0.6},
                    'bengal': {'baseline': 4.8, 'tide_amp': 2.2, 'wave_amp': 0.8},
                    'andaman': {'baseline': 3.9, 'tide_amp': 1.6, 'wave_amp': 0.7}
                }
                
                params = regional_params[region_key]
                
                for i in range(10):
                    time_offset = current_time - timedelta(minutes=6 * (9 - i))
                    tide = params['baseline'] + params['tide_amp'] * np.sin(2 * np.pi * time_offset.hour / 12)
                    wave = params['wave_amp'] * np.sin(2 * np.pi * i / 3) * (0.8 + 0.2 * np.random.rand())
                    noise = np.random.randn() * 0.1
                    water_level = tide + wave + noise
                    
                    readings.append({
                        'time': time_offset.strftime('%Y-%m-%d %H:%M'),
                        'value': round(water_level, 2),
                        'quality': 'estimated'
                    })
                
                region_readings.append({
                    'station_id': station['id'],
                    'station_name': station['name'],
                    'location': {'lat': station['lat'], 'lon': station['lon']},
                    'readings': readings,
                    'source': 'Simulated (No real-time station)',
                    'data_type': 'water_level',
                    'unit': 'meters',
                    'real_data': False
                })
            
            wave_data[region_key] = {
                'region': region_info['name'],
                'stations': region_readings,
                'last_update': datetime.utcnow().isoformat()
            }
        
        return jsonify({
            'success': True,
            'wave_data': wave_data,
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Real-time data from IOC sea level stations and NOAA DART buoys'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching wave data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to fetch wave data'
        }), 500


# ============== IoT Alert System Endpoints ==============

# Store for registered IoT devices and alert history
iot_devices = []
iot_alert_history = []

# Cloud alert state (for ESP8266 polling)
cloud_alert_state = {
    'active': False,
    'level': 0,
    'message': '',
    'timestamp': None,
    'source': None
}

@app.route('/iot/cloud/poll', methods=['GET'])
def poll_cloud_alert():
    """
    ESP8266 polls this endpoint to get current alert state.
    This enables cloud-to-device communication without direct connection.
    """
    device_id = request.args.get('device', 'unknown')
    
    # Log device check-in
    logger.info(f"Device poll: {device_id}")
    
    return jsonify({
        'active': cloud_alert_state['active'],
        'level': cloud_alert_state['level'],
        'message': cloud_alert_state['message'],
        'timestamp': cloud_alert_state['timestamp']
    }), 200


@app.route('/iot/cloud/alert', methods=['POST'])
def set_cloud_alert():
    """
    Set alert state that ESP8266 devices will poll.
    """
    try:
        data = request.get_json()
        
        level = data.get('level', 1)
        message = data.get('message', 'Alert')
        
        cloud_alert_state['active'] = True
        cloud_alert_state['level'] = level
        cloud_alert_state['message'] = message
        cloud_alert_state['timestamp'] = datetime.utcnow().isoformat()
        cloud_alert_state['source'] = 'manual'
        
        # Add to history
        iot_alert_history.append({
            'type': 'cloud_alert',
            'level': level,
            'message': message,
            'timestamp': cloud_alert_state['timestamp']
        })
        
        return jsonify({
            'success': True,
            'message': 'Cloud alert set - devices will receive on next poll',
            'state': cloud_alert_state
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/iot/cloud/clear', methods=['POST', 'GET'])
def clear_cloud_alert():
    """Clear the cloud alert state."""
    cloud_alert_state['active'] = False
    cloud_alert_state['level'] = 0
    cloud_alert_state['message'] = ''
    cloud_alert_state['timestamp'] = datetime.utcnow().isoformat()
    
    return jsonify({
        'success': True,
        'message': 'Cloud alert cleared'
    }), 200


@app.route('/iot/cloud/status', methods=['GET'])
def cloud_alert_status():
    """Get current cloud alert status."""
    return jsonify(cloud_alert_state), 200


@app.route('/iot/devices', methods=['GET'])
def get_iot_devices():
    """Get list of registered IoT devices"""
    return jsonify({
        'success': True,
        'devices': iot_devices,
        'count': len(iot_devices)
    }), 200


@app.route('/iot/devices', methods=['POST'])
def register_iot_device():
    """Register a new IoT device"""
    try:
        data = request.get_json()
        
        if not data or 'ip' not in data:
            return jsonify({'error': 'IP address required'}), 400
        
        device = {
            'id': len(iot_devices) + 1,
            'name': data.get('name', f"Device_{len(iot_devices) + 1}"),
            'ip': data['ip'],
            'registered_at': datetime.utcnow().isoformat(),
            'last_seen': None,
            'online': False
        }
        
        # Check if device already exists
        existing = next((d for d in iot_devices if d['ip'] == data['ip']), None)
        if existing:
            return jsonify({'error': 'Device already registered', 'device': existing}), 409
        
        iot_devices.append(device)
        logger.info(f"IoT device registered: {device['name']} ({device['ip']})")
        
        return jsonify({
            'success': True,
            'message': 'Device registered',
            'device': device
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/iot/devices/<device_ip>', methods=['DELETE'])
def remove_iot_device(device_ip):
    """Remove an IoT device"""
    global iot_devices
    
    iot_devices = [d for d in iot_devices if d['ip'] != device_ip]
    
    return jsonify({
        'success': True,
        'message': f'Device {device_ip} removed'
    }), 200


@app.route('/iot/alert', methods=['POST'])
def send_iot_alert():
    """Send alert to IoT devices and log it"""
    try:
        data = request.get_json()
        
        level = data.get('level', 1)
        message = data.get('message', 'Alert')
        devices = data.get('devices', [])
        earthquake_info = data.get('earthquake', None)
        
        # Log the alert
        alert_record = {
            'id': len(iot_alert_history) + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'level_name': ['NONE', 'WATCH', 'ADVISORY', 'WARNING', 'CRITICAL'][min(level, 4)],
            'message': message,
            'devices_targeted': devices,
            'earthquake': earthquake_info
        }
        
        iot_alert_history.append(alert_record)
        
        # Send to each device via HTTP
        results = []
        for device_ip in devices:
            try:
                response = http_requests.post(
                    f'http://{device_ip}/alert',
                    json={
                        'level': level,
                        'message': message,
                        'earthquake': str(earthquake_info) if earthquake_info else 'Manual alert'
                    },
                    timeout=5
                )
                results.append({
                    'ip': device_ip,
                    'success': response.status_code == 200,
                    'status_code': response.status_code
                })
            except Exception as e:
                results.append({
                    'ip': device_ip,
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"IoT alert sent: Level {level} - {message} to {len(devices)} devices")
        
        return jsonify({
            'success': True,
            'alert': alert_record,
            'device_results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending IoT alert: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/iot/alert/clear', methods=['POST'])
def clear_iot_alerts():
    """Clear alerts on all registered devices"""
    try:
        data = request.get_json() or {}
        devices = data.get('devices', [d['ip'] for d in iot_devices])
        
        results = []
        for device_ip in devices:
            try:
                response = http_requests.post(
                    f'http://{device_ip}/clear',
                    timeout=5
                )
                results.append({
                    'ip': device_ip,
                    'success': response.status_code == 200
                })
            except Exception as e:
                results.append({
                    'ip': device_ip,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': 'Clear command sent',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/iot/alert/history', methods=['GET'])
def get_alert_history():
    """Get IoT alert history"""
    limit = request.args.get('limit', 50, type=int)
    
    return jsonify({
        'success': True,
        'alerts': iot_alert_history[-limit:][::-1],  # Most recent first
        'total': len(iot_alert_history)
    }), 200


@app.route('/iot/test/<device_ip>', methods=['POST'])
def test_iot_device(device_ip):
    """Send test command to a specific device"""
    try:
        response = http_requests.post(
            f'http://{device_ip}/test',
            timeout=5
        )
        
        return jsonify({
            'success': response.status_code == 200,
            'device_ip': device_ip,
            'response': response.text
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'device_ip': device_ip,
            'error': str(e)
        }), 500


@app.route('/iot/arduino', methods=['GET'])
def download_arduino_code():
    """Download Arduino UNO code for LCD and Buzzer"""
    try:
        return send_file(
            'iot/arduino_uno_lcd_buzzer/arduino_uno_lcd_buzzer.ino',
            mimetype='text/plain',
            as_attachment=True,
            download_name='arduino_uno_lcd_buzzer.ino'
        )
    except Exception as e:
        return jsonify({'error': f'Arduino code not found: {e}'}), 404


@app.route('/iot/esp8266', methods=['GET'])
def download_esp8266_code():
    """Download ESP8266 WiFi module code"""
    try:
        return send_file(
            'iot/esp8266_wifi/esp8266_wifi.ino',
            mimetype='text/plain',
            as_attachment=True,
            download_name='esp8266_wifi.ino'
        )
    except Exception as e:
        return jsonify({'error': f'ESP8266 code not found: {e}'}), 404


@app.route('/iot/arduino/generate', methods=['GET'])
def generate_arduino_code():
    """Generate Arduino code with custom pin configuration"""
    # Get pin values from query parameters
    lcd_rs = request.args.get('lcdRs', '12')
    lcd_en = request.args.get('lcdEn', '11')
    lcd_d4 = request.args.get('lcdD4', '5')
    lcd_d5 = request.args.get('lcdD5', '4')
    lcd_d6 = request.args.get('lcdD6', '3')
    lcd_d7 = request.args.get('lcdD7', '2')
    buzzer = request.args.get('buzzer', '8')
    esp_rx = request.args.get('espRx', '6')
    esp_tx = request.args.get('espTx', '7')
    
    arduino_code = f'''/*
 * Arduino UNO Tsunami Alert System
 * LCD Display + Buzzer Alert
 * 
 * Custom Pin Configuration - Generated from IoT Dashboard
 * 
 * Hardware Connections:
 * LCD RS  -> Arduino Pin {lcd_rs}
 * LCD EN  -> Arduino Pin {lcd_en}
 * LCD D4  -> Arduino Pin {lcd_d4}
 * LCD D5  -> Arduino Pin {lcd_d5}
 * LCD D6  -> Arduino Pin {lcd_d6}
 * LCD D7  -> Arduino Pin {lcd_d7}
 * LCD VSS -> GND
 * LCD VDD -> 5V
 * LCD V0  -> Potentiometer (contrast)
 * LCD RW  -> GND
 * LCD A   -> 5V (backlight)
 * LCD K   -> GND (backlight)
 * 
 * Buzzer  -> Arduino Pin {buzzer}
 * ESP8266 TX -> Arduino Pin {esp_rx} (via voltage divider)
 * Arduino Pin {esp_tx} -> ESP8266 RX
 */

#include <LiquidCrystal.h>
#include <SoftwareSerial.h>

// Pin Configuration
#define LCD_RS {lcd_rs}
#define LCD_EN {lcd_en}
#define LCD_D4 {lcd_d4}
#define LCD_D5 {lcd_d5}
#define LCD_D6 {lcd_d6}
#define LCD_D7 {lcd_d7}
#define BUZZER_PIN {buzzer}
#define ESP_RX_PIN {esp_rx}
#define ESP_TX_PIN {esp_tx}

// Initialize LCD (RS, EN, D4, D5, D6, D7)
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

// Software Serial for ESP8266 communication
SoftwareSerial espSerial(ESP_RX_PIN, ESP_TX_PIN);

// Alert levels
#define ALERT_NONE 0
#define ALERT_WATCH 1
#define ALERT_ADVISORY 2
#define ALERT_WARNING 3
#define ALERT_CRITICAL 4

int currentAlertLevel = ALERT_NONE;
unsigned long lastBuzzerTime = 0;
bool buzzerState = false;
String lastMessage = "";

// Buzzer patterns (on_time, off_time in ms)
const int PATTERN_WATCH[] = {{200, 2000}};
const int PATTERN_ADVISORY[] = {{300, 1000}};
const int PATTERN_WARNING[] = {{500, 500}};
const int PATTERN_CRITICAL[] = {{100, 100}};

void setup() {{
    Serial.begin(9600);
    espSerial.begin(9600);
    
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    
    lcd.begin(16, 2);
    lcd.clear();
    
    // Startup display
    lcd.setCursor(0, 0);
    lcd.print("Tsunami Alert");
    lcd.setCursor(0, 1);
    lcd.print("System Ready");
    
    // Startup beep
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    
    Serial.println("Arduino Tsunami Alert System Ready");
}}

void loop() {{
    // Check for data from ESP8266
    if (espSerial.available()) {{
        String data = espSerial.readStringUntil('\\n');
        data.trim();
        if (data.length() > 0) {{
            processAlert(data);
        }}
    }}
    
    // Handle buzzer based on alert level
    handleBuzzer();
}}

void processAlert(String data) {{
    Serial.println("Received: " + data);
    
    // Parse format: "LEVEL:message" or "CLEAR"
    if (data == "CLEAR") {{
        clearAlert();
        return;
    }}
    
    int colonIndex = data.indexOf(':');
    if (colonIndex > 0) {{
        int level = data.substring(0, colonIndex).toInt();
        String message = data.substring(colonIndex + 1);
        
        setAlert(level, message);
    }}
}}

void setAlert(int level, String message) {{
    currentAlertLevel = level;
    lastMessage = message;
    
    lcd.clear();
    
    // First row: Alert level
    lcd.setCursor(0, 0);
    switch(level) {{
        case ALERT_WATCH:
            lcd.print("! TSUNAMI WATCH");
            break;
        case ALERT_ADVISORY:
            lcd.print("! ADVISORY !");
            break;
        case ALERT_WARNING:
            lcd.print("!! WARNING !!");
            break;
        case ALERT_CRITICAL:
            lcd.print("!!! EVACUATE !!!");
            break;
        default:
            lcd.print("ALERT");
    }}
    
    // Second row: Message (scrolling if needed)
    lcd.setCursor(0, 1);
    if (message.length() <= 16) {{
        lcd.print(message);
    }} else {{
        lcd.print(message.substring(0, 16));
    }}
    
    Serial.println("Alert set: Level " + String(level) + " - " + message);
}}

void clearAlert() {{
    currentAlertLevel = ALERT_NONE;
    lastMessage = "";
    
    digitalWrite(BUZZER_PIN, LOW);
    buzzerState = false;
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("System Normal");
    lcd.setCursor(0, 1);
    lcd.print("Monitoring...");
    
    Serial.println("Alert cleared");
}}

void handleBuzzer() {{
    if (currentAlertLevel == ALERT_NONE) {{
        digitalWrite(BUZZER_PIN, LOW);
        return;
    }}
    
    unsigned long currentTime = millis();
    int onTime, offTime;
    
    switch(currentAlertLevel) {{
        case ALERT_WATCH:
            onTime = PATTERN_WATCH[0];
            offTime = PATTERN_WATCH[1];
            break;
        case ALERT_ADVISORY:
            onTime = PATTERN_ADVISORY[0];
            offTime = PATTERN_ADVISORY[1];
            break;
        case ALERT_WARNING:
            onTime = PATTERN_WARNING[0];
            offTime = PATTERN_WARNING[1];
            break;
        case ALERT_CRITICAL:
            onTime = PATTERN_CRITICAL[0];
            offTime = PATTERN_CRITICAL[1];
            break;
        default:
            return;
    }}
    
    int interval = buzzerState ? onTime : offTime;
    
    if (currentTime - lastBuzzerTime >= interval) {{
        buzzerState = !buzzerState;
        digitalWrite(BUZZER_PIN, buzzerState ? HIGH : LOW);
        lastBuzzerTime = currentTime;
    }}
}}
'''
    
    from io import BytesIO
    buffer = BytesIO(arduino_code.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/plain',
        as_attachment=True,
        download_name='arduino_uno_tsunami_alert.ino'
    )


@app.route('/iot/esp8266/generate', methods=['GET'])
def generate_esp8266_code():
    """Generate ESP8266 code with custom WiFi configuration"""
    ssid = request.args.get('ssid', 'YOUR_WIFI_SSID')
    password = request.args.get('password', 'YOUR_WIFI_PASSWORD')
    device_name = request.args.get('deviceName', 'TsunamiAlert_01')
    
    esp_code = f'''/*
 * ESP8266 Tsunami Alert Receiver
 * Receives alerts via WiFi and forwards to Arduino UNO
 * 
 * Custom Configuration - Generated from IoT Dashboard
 * Device Name: {device_name}
 * 
 * Hardware Connections:
 * ESP8266 VCC  -> 3.3V (NOT 5V!)
 * ESP8266 GND  -> GND
 * ESP8266 TX   -> Arduino RX Pin (via voltage divider: 1K + 2K)
 * ESP8266 RX   -> Arduino TX Pin
 * ESP8266 CH_PD -> 3.3V (Enable)
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "{ssid}";
const char* password = "{password}";

// Device Configuration
const char* deviceName = "{device_name}";

// Web Server on port 80
ESP8266WebServer server(80);

// Status
bool alertActive = false;
int currentLevel = 0;
String currentMessage = "";
unsigned long lastHeartbeat = 0;

void setup() {{
    Serial.begin(9600);
    delay(1000);
    
    Serial.println("\\n\\nTsunami Alert Receiver Starting...");
    Serial.print("Device: ");
    Serial.println(deviceName);
    
    // Connect to WiFi
    WiFi.hostname(deviceName);
    WiFi.begin(ssid, password);
    
    Serial.print("Connecting to WiFi");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {{
        delay(500);
        Serial.print(".");
        attempts++;
    }}
    
    if (WiFi.status() == WL_CONNECTED) {{
        Serial.println("\\nConnected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    }} else {{
        Serial.println("\\nFailed to connect! Restarting...");
        delay(5000);
        ESP.restart();
    }}
    
    // Setup HTTP endpoints
    server.on("/", HTTP_GET, handleRoot);
    server.on("/alert", HTTP_POST, handleAlert);
    server.on("/alert", HTTP_GET, handleAlertGet);
    server.on("/clear", HTTP_POST, handleClear);
    server.on("/clear", HTTP_GET, handleClearGet);
    server.on("/status", HTTP_GET, handleStatus);
    server.on("/test", HTTP_POST, handleTest);
    server.on("/test", HTTP_GET, handleTestGet);
    
    server.begin();
    Serial.println("HTTP server started");
    
    // Send ready signal to Arduino
    Serial.println("READY");
}}

void loop() {{
    server.handleClient();
    
    // Heartbeat every 30 seconds
    if (millis() - lastHeartbeat > 30000) {{
        lastHeartbeat = millis();
        if (WiFi.status() != WL_CONNECTED) {{
            Serial.println("WiFi disconnected! Reconnecting...");
            WiFi.reconnect();
        }}
    }}
}}

void handleRoot() {{
    String html = "<html><head><title>" + String(deviceName) + "</title>";
    html += "<style>body{{font-family:Arial;padding:20px;background:#1a1a2e;color:#fff;}}";
    html += ".status{{padding:20px;border-radius:10px;margin:10px 0;}}";
    html += ".ok{{background:#2d5a27;}}.alert{{background:#8b0000;}}</style></head>";
    html += "<body><h1>Tsunami Alert Receiver</h1>";
    html += "<p>Device: " + String(deviceName) + "</p>";
    html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
    html += "<div class='status " + String(alertActive ? "alert" : "ok") + "'>";
    html += alertActive ? "ALERT ACTIVE - Level " + String(currentLevel) : "System Normal";
    html += "</div>";
    html += "<h3>Endpoints:</h3><ul>";
    html += "<li>POST /alert - Send alert (level, message)</li>";
    html += "<li>POST /clear - Clear alert</li>";
    html += "<li>GET /status - Get current status</li>";
    html += "<li>POST /test - Test connection</li>";
    html += "</ul></body></html>";
    server.send(200, "text/html", html);
}}

void handleAlert() {{
    if (server.hasArg("plain")) {{
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, server.arg("plain"));
        
        if (!error) {{
            int level = doc["level"] | 1;
            const char* message = doc["message"] | "Alert";
            
            currentLevel = level;
            currentMessage = String(message);
            alertActive = true;
            
            // Forward to Arduino via Serial
            String alertData = String(level) + ":" + currentMessage;
            Serial.println(alertData);
            
            server.send(200, "application/json", "{{\\"success\\":true,\\"level\\":" + String(level) + "}}");
        }} else {{
            server.send(400, "application/json", "{{\\"error\\":\\"Invalid JSON\\"}}");
        }}
    }} else {{
        server.send(400, "application/json", "{{\\"error\\":\\"No data received\\"}}");
    }}
}}

void handleAlertGet() {{
    int level = server.arg("level").toInt();
    String message = server.arg("message");
    
    if (level > 0) {{
        currentLevel = level;
        currentMessage = message.length() > 0 ? message : "Alert";
        alertActive = true;
        
        String alertData = String(level) + ":" + currentMessage;
        Serial.println(alertData);
        
        server.send(200, "application/json", "{{\\"success\\":true,\\"level\\":" + String(level) + "}}");
    }} else {{
        server.send(400, "application/json", "{{\\"error\\":\\"Invalid level\\"}}");
    }}
}}

void handleClear() {{
    alertActive = false;
    currentLevel = 0;
    currentMessage = "";
    
    Serial.println("CLEAR");
    
    server.send(200, "application/json", "{{\\"success\\":true,\\"message\\":\\"Alert cleared\\"}}");
}}

void handleClearGet() {{
    handleClear();
}}

void handleStatus() {{
    String json = "{{";
    json += "\\"device\\":\\"" + String(deviceName) + "\\",";
    json += "\\"ip\\":\\"" + WiFi.localIP().toString() + "\\",";
    json += "\\"rssi\\":" + String(WiFi.RSSI()) + ",";
    json += "\\"alertActive\\":" + String(alertActive ? "true" : "false") + ",";
    json += "\\"level\\":" + String(currentLevel) + ",";
    json += "\\"message\\":\\"" + currentMessage + "\\"";
    json += "}}";
    
    server.send(200, "application/json", json);
}}

void handleTest() {{
    Serial.println("TEST");
    server.send(200, "application/json", "{{\\"success\\":true,\\"message\\":\\"Test signal sent\\"}}");
}}

void handleTestGet() {{
    handleTest();
}}
'''
    
    from io import BytesIO
    buffer = BytesIO(esp_code.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/plain',
        as_attachment=True,
        download_name='esp8266_tsunami_alert.ino'
    )


@app.route('/iot/esp8266/cloud/generate', methods=['GET'])
def generate_esp8266_cloud_code():
    """Generate ESP8266 code for CLOUD mode (polling-based)"""
    ssid = request.args.get('ssid', 'YOUR_WIFI_SSID')
    password = request.args.get('password', 'YOUR_WIFI_PASSWORD')
    device_name = request.args.get('deviceName', 'TsunamiAlert_01')
    server_url = request.args.get('serverUrl', 'https://your-server.com')
    poll_interval = request.args.get('pollInterval', '5000')
    
    esp_code = f'''/*
 * ESP8266 Cloud Tsunami Alert Receiver
 * 
 * CLOUD MODE - Polls server for alerts
 * Works with cloud deployments (Codespace, Heroku, Railway, etc.)
 * 
 * Generated Configuration:
 * - Device: {device_name}
 * - Server: {server_url}
 * - Poll Interval: {poll_interval}ms
 * 
 * Hardware Connections:
 * ESP8266 VCC  -> 3.3V
 * ESP8266 GND  -> GND
 * ESP8266 TX   -> Arduino Pin 6 (SoftwareSerial RX)
 * ESP8266 RX   -> Arduino Pin 7 (through voltage divider)
 * ESP8266 CH_PD -> 3.3V
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

// ============ CONFIGURATION ============
const char* ssid = "{ssid}";
const char* password = "{password}";
const char* serverUrl = "{server_url}";
const char* deviceName = "{device_name}";
const unsigned long POLL_INTERVAL = {poll_interval};
// ========================================

WiFiClientSecure wifiClient;
HTTPClient http;

bool lastAlertState = false;
int lastAlertLevel = 0;
String lastMessage = "";
unsigned long lastPollTime = 0;
unsigned long lastHeartbeat = 0;

void setup() {{
    Serial.begin(9600);
    delay(1000);
    
    Serial.println("\\n================================");
    Serial.println("Tsunami Alert - CLOUD MODE");
    Serial.println("================================");
    Serial.print("Device: ");
    Serial.println(deviceName);
    Serial.print("Server: ");
    Serial.println(serverUrl);
    
    // Allow insecure connections for testing
    wifiClient.setInsecure();
    
    connectWiFi();
    
    Serial.println("\\nSystem ready - polling for alerts...");
    Serial.println("READY");
}}

void loop() {{
    if (WiFi.status() != WL_CONNECTED) {{
        Serial.println("WiFi lost - reconnecting...");
        connectWiFi();
    }}
    
    unsigned long currentTime = millis();
    if (currentTime - lastPollTime >= POLL_INTERVAL) {{
        lastPollTime = currentTime;
        pollServer();
    }}
    
    if (currentTime - lastHeartbeat >= 30000) {{
        lastHeartbeat = currentTime;
        Serial.println("HEARTBEAT");
    }}
}}

void connectWiFi() {{
    WiFi.hostname(deviceName);
    WiFi.begin(ssid, password);
    
    Serial.print("Connecting to WiFi");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {{
        delay(500);
        Serial.print(".");
        attempts++;
    }}
    
    if (WiFi.status() == WL_CONNECTED) {{
        Serial.println("\\nConnected!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        Serial.print("RSSI: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
    }} else {{
        Serial.println("\\nWiFi failed! Restarting...");
        delay(5000);
        ESP.restart();
    }}
}}

void pollServer() {{
    String url = String(serverUrl) + "/iot/cloud/poll?device=" + String(deviceName);
    
    http.begin(wifiClient, url);
    http.setTimeout(10000);
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    http.addHeader("User-Agent", "ESP8266-TsunamiAlert");
    
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {{
        String payload = http.getString();
        
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {{
            bool alertActive = doc["active"] | false;
            int level = doc["level"] | 0;
            const char* message = doc["message"] | "";
            
            if (alertActive && (!lastAlertState || level != lastAlertLevel)) {{
                // New alert
                String alertCmd = "ALERT:" + String(level) + ":" + String(message);
                Serial.println(alertCmd);
                
                lastAlertState = true;
                lastAlertLevel = level;
                lastMessage = String(message);
            }}
            else if (!alertActive && lastAlertState) {{
                // Alert cleared
                Serial.println("CLEAR");
                
                lastAlertState = false;
                lastAlertLevel = 0;
                lastMessage = "";
            }}
        }} else {{
            Serial.print("JSON error: ");
            Serial.println(error.c_str());
        }}
    }} else if (httpCode > 0) {{
        Serial.print("HTTP ");
        Serial.println(httpCode);
    }} else {{
        Serial.print("Error: ");
        Serial.println(http.errorToString(httpCode));
    }}
    
    http.end();
}}
'''
    
    from io import BytesIO
    buffer = BytesIO(esp_code.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/plain',
        as_attachment=True,
        download_name='esp8266_cloud_tsunami_alert.ino'
    )


@app.route('/iot/trigger-from-prediction', methods=['POST'])
def trigger_iot_from_prediction():
    """
    Automatically trigger IoT alerts based on earthquake prediction
    This is called internally when a high-risk earthquake is detected
    """
    try:
        data = request.get_json()
        
        magnitude = data.get('magnitude', 0)
        probability = data.get('probability', 0)
        location = data.get('location', 'Unknown')
        
        # Determine alert level based on probability
        if probability > 0.9:
            level = 4  # CRITICAL
        elif probability > 0.75:
            level = 3  # WARNING
        elif probability > 0.5:
            level = 2  # ADVISORY
        elif probability > 0.3:
            level = 1  # WATCH
        else:
            return jsonify({
                'success': True,
                'message': 'Risk too low for alert',
                'probability': probability
            }), 200
        
        # Send to all registered devices
        message = f"M{magnitude:.1f} {location} {probability*100:.0f}%"
        
        device_ips = [d['ip'] for d in iot_devices]
        
        if not device_ips:
            return jsonify({
                'success': True,
                'message': 'No devices registered',
                'alert_level': level
            }), 200
        
        # Send alerts
        results = []
        for device_ip in device_ips:
            try:
                response = http_requests.post(
                    f'http://{device_ip}/alert',
                    json={
                        'level': level,
                        'message': message,
                        'earthquake': f"M{magnitude} at {location}"
                    },
                    timeout=5
                )
                results.append({
                    'ip': device_ip,
                    'success': response.status_code == 200
                })
            except:
                results.append({
                    'ip': device_ip,
                    'success': False
                })
        
        # Log alert
        iot_alert_history.append({
            'id': len(iot_alert_history) + 1,
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'level_name': ['NONE', 'WATCH', 'ADVISORY', 'WARNING', 'CRITICAL'][level],
            'message': message,
            'devices_targeted': device_ips,
            'earthquake': data,
            'triggered_by': 'automatic_prediction'
        })
        
        logger.info(f"Auto IoT alert triggered: Level {level} - {message}")
        
        return jsonify({
            'success': True,
            'alert_level': level,
            'message': message,
            'devices_alerted': len([r for r in results if r['success']]),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error triggering IoT alert: {e}")
        return jsonify({'error': str(e)}), 500


# ============== End IoT Alert System ==============


def create_seismic_pattern(magnitude, depth, latitude, longitude):
    """
    Create synthetic seismic pattern for model input based on earthquake parameters
    Returns (24, 32) shaped array representing seismic features over time
    
    Parameters:
    - magnitude: Earthquake magnitude (Richter scale)
    - depth: Earthquake depth (km)
    - latitude: Earthquake latitude
    - longitude: Earthquake longitude
    """
    # Initialize pattern
    pattern = np.zeros((24, 32))
    
    # Magnitude affects amplitude (higher magnitude = higher amplitude)
    magnitude_factor = magnitude / 10.0
    
    # Depth affects pattern (shallow = more surface impact)
    depth_factor = max(0.1, 1.0 - (depth / 700.0))  # 700km max depth
    
    # Create time-varying pattern
    for t in range(24):
        # Create frequency components (32 features)
        for f in range(32):
            # Base signal with magnitude influence
            base = magnitude_factor * depth_factor
            
            # Add time evolution (tsunami waves build up)
            time_evolution = np.sin(t * np.pi / 24) * (t / 24)
            
            # Add frequency components
            freq_component = np.cos(2 * np.pi * f / 32)
            
            # Combine factors with some randomness
            pattern[t, f] = base * (0.3 + 0.5 * time_evolution + 0.2 * freq_component)
            pattern[t, f] += np.random.randn() * 0.05  # Small noise
    
    # Normalize to reasonable range
    pattern = np.clip(pattern, 0, 1.0)
    
    return pattern


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict tsunami probability from seismic parameters OR raw data
    
    Accepts two formats:
    1. Seismic parameters: {magnitude, depth, latitude, longitude}
    2. Raw model data: {data: [[24 timesteps x 32 features]]}
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        request_data = request.get_json()
        
        # Check if this is a seismic parameter request
        if 'magnitude' in request_data:
            magnitude = float(request_data.get('magnitude', 7.0))
            depth = float(request_data.get('depth', 30))
            latitude = float(request_data.get('latitude', 0))
            longitude = float(request_data.get('longitude', 0))
            
            # Generate synthetic seismic pattern based on parameters
            input_data = create_seismic_pattern(magnitude, depth, latitude, longitude)
            input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension
            
            # Make prediction
            predictions = model.predict(input_data, verbose=0)
            probability = float(predictions[0][0])
            
            # Adjust probability based on actual seismic science
            # Tsunamis are more likely with: shallow depth (<70km), high magnitude (>7.0), ocean location
            
            # Depth factor: shallow = more dangerous
            depth_factor = 1.0 if depth < 50 else (0.7 if depth < 100 else 0.3)
            
            # Magnitude factor: exponential increase with magnitude
            mag_factor = min(1.0, (magnitude - 5.5) / 3.5) if magnitude > 5.5 else 0.0
            
            # Location factor: check if oceanic region (rough check for Indian Ocean)
            ocean_factor = 0.9 if (70 < longitude < 100 and -10 < latitude < 25) else 0.5
            
            # Combine factors with model prediction
            adjusted_probability = probability * 0.4 + (depth_factor * mag_factor * ocean_factor) * 0.6
            adjusted_probability = max(0.0, min(1.0, adjusted_probability))
            
            # Determine alert level
            if adjusted_probability > 0.9:
                alert_level = 4
                interpretation = "CRITICAL - Immediate evacuation recommended"
            elif adjusted_probability > 0.75:
                alert_level = 3
                interpretation = "WARNING - High tsunami risk"
            elif adjusted_probability > 0.5:
                alert_level = 2
                interpretation = "ADVISORY - Significant tsunami possible"
            elif adjusted_probability > 0.3:
                alert_level = 1
                interpretation = "WATCH - Tsunami possible, monitor situation"
            else:
                alert_level = 0
                interpretation = "LOW RISK - No significant tsunami expected"
            
            # Also set cloud alert if risk is significant
            if alert_level >= 2:
                cloud_alert_state['active'] = True
                cloud_alert_state['level'] = alert_level
                cloud_alert_state['message'] = f"M{magnitude} at {depth}km - {interpretation}"
                cloud_alert_state['timestamp'] = datetime.utcnow().isoformat()
                cloud_alert_state['source'] = 'ai_prediction'
            
            return jsonify({
                'success': True,
                'prediction': {
                    'tsunami_probability': adjusted_probability,
                    'raw_model_probability': probability,
                    'alert_level': alert_level,
                    'interpretation': interpretation
                },
                'input': {
                    'magnitude': magnitude,
                    'depth': depth,
                    'latitude': latitude,
                    'longitude': longitude
                },
                'factors': {
                    'depth_factor': depth_factor,
                    'magnitude_factor': mag_factor,
                    'ocean_factor': ocean_factor
                },
                'cloud_alert_triggered': alert_level >= 2
            }), 200
            
        # Original raw data format
        elif 'data' in request_data:
            input_data = np.array(request_data['data'], dtype=np.float32)
            threshold = request_data.get('threshold', 0.1)
            
            if input_data.ndim == 2:
                input_data = np.expand_dims(input_data, axis=0)
            elif input_data.ndim != 3:
                return jsonify({'error': f'Invalid input shape'}), 400
            
            if input_data.shape[1:] != (24, 32):
                return jsonify({'error': f'Expected (24, 32), got {input_data.shape[1:]}'}), 400
            
            predictions = model.predict(input_data, verbose=0)
            probabilities = predictions.flatten().tolist()
            alerts = [float(p > threshold) for p in probabilities]
            
            return jsonify({
                'success': True,
                'probabilities': probabilities,
                'alerts': alerts,
                'threshold': threshold
            }), 200
        else:
            return jsonify({'error': 'Missing required fields'}), 400
            
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/model-info', methods=['GET'])
def model_info():
    """Get model information and performance metrics"""
    if metadata is None:
        return jsonify({'error': 'Metadata not available'}), 500
    
    return jsonify({
        'model': metadata,
        'endpoints': {
            'predict': '/predict (POST)',
            'health': '/health (GET)',
            'model_info': '/model-info (GET)'
        }
    }), 200


@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction for multiple samples
    
    Expected input:
    {
        "samples": [
            [[timestep1_features], ...],
            [[timestep1_features], ...],
            ...
        ],
        "threshold": 0.1
    }
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        request_data = request.get_json()
        
        if 'samples' not in request_data:
            return jsonify({'error': 'Missing "samples" field'}), 400
        
        # Parse batch
        samples = np.array(request_data['samples'], dtype=np.float32)
        threshold = request_data.get('threshold', 0.1)
        
        # Validate shape
        if samples.shape[1:] != (24, 32):
            return jsonify({'error': f'Expected features (24, 32) per sample, got {samples.shape[1:]}'}), 400
        
        # Batch predict
        predictions = model.predict(samples, verbose=0)
        probabilities = predictions.flatten().tolist()
        alerts = [float(p > threshold) for p in probabilities]
        
        return jsonify({
            'success': True,
            'batch_size': len(samples),
            'probabilities': probabilities,
            'alerts': alerts,
            'alert_count': sum(alerts),
            'alert_rate': f"{100 * sum(alerts) / len(alerts):.2f}%",
            'threshold': threshold
        }), 200
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/predict',
            '/batch-predict',
            '/model-info'
        ]
    }), 404


if __name__ == '__main__':
    import os
    logger.info("Starting Tsunami Detection API...")
    logger.info("Available endpoints:")
    logger.info("  - GET  /health")
    logger.info("  - POST /predict")
    logger.info("  - POST /batch-predict")
    logger.info("  - GET  /model-info")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
