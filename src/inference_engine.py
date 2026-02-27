"""
Real-time Inference System
Continuously monitors and predicts tsunami risk
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional
from loguru import logger
import yaml

from .data_collection import (
    USGSEarthquakeCollector,
    NOAATidesCollector,
    NOAABuoysCollector,
    INCOISCollector,
    BathymetryLoader
)
from .models import TsunamiPredictionBinaryModel as TsunamiPredictionModel, DataPreprocessor
from .filtering import IndiaImpactFilter, RiskAssessor


class RealTimeInferenceEngine:
    """
    Real-time tsunami monitoring and prediction engine
    Continuously fetches data and makes predictions
    """
    
    def __init__(self, config_path: str = 'config/config.yaml',
                 model_path: str = 'models/best_model.keras'):
        """
        Initialize inference engine
        
        Args:
            config_path: Path to configuration file
            model_path: Path to trained model
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.usgs_collector = USGSEarthquakeCollector(self.config)
        self.noaa_tides_collector = NOAATidesCollector(self.config)
        self.noaa_buoys_collector = NOAABuoysCollector(self.config)
        self.incois_collector = INCOISCollector(self.config)
        self.bathymetry_loader = BathymetryLoader(self.config)
        
        # Load bathymetry data
        logger.info("Loading bathymetry data...")
        self.bathymetry_loader.load_gebco_data()
        
        # Initialize model
        self.model = TsunamiPredictionModel(self.config)
        self.preprocessor = DataPreprocessor(self.config)
        
        # Load trained model
        try:
            self.model.load_model(model_path)
            self.preprocessor.load_scalers('models/scalers')
            logger.success("Model and scalers loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load model: {e}. Will need to train first.")
        
        # Initialize filtering and assessment
        self.india_filter = IndiaImpactFilter(self.config)
        self.risk_assessor = RiskAssessor(self.config)
        
        # Monitoring state
        self.is_running = False
        self.monitoring_thread = None
        self.current_assessment = None
        self.last_check_time = None
        self.check_interval = 300  # 5 minutes
    
    def start_monitoring(self, interval_seconds: int = 300):
        """
        Start real-time monitoring
        
        Args:
            interval_seconds: Check interval in seconds
        """
        if self.is_running:
            logger.warning("Monitoring already running")
            return
        
        self.check_interval = interval_seconds
        self.is_running = True
        
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.success(f"Real-time monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        logger.info("Monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                logger.info("Running tsunami check...")
                assessment = self.run_tsunami_check()
                
                if assessment and assessment['india_at_risk']:
                    logger.warning(f"⚠️ TSUNAMI RISK DETECTED: {assessment['alert_level']}")
                    self._handle_alert(assessment)
                else:
                    logger.info("✓ No tsunami threat detected")
                
                self.last_check_time = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next interval
            time.sleep(self.check_interval)
    
    def run_tsunami_check(self) -> Optional[Dict]:
        """
        Run complete tsunami check cycle
        
        Returns:
            Risk assessment dictionary or None
        """
        try:
            # Step 1: Fetch recent earthquakes
            logger.info("Fetching earthquake data...")
            earthquakes = self.usgs_collector.fetch_recent_earthquakes(hours=2)
            
            if earthquakes.empty:
                logger.info("No recent earthquakes detected")
                return self._create_no_threat_assessment()
            
            # Step 2: Check for significant earthquakes
            significant = earthquakes[earthquakes['magnitude'] >= 6.5]
            
            if significant.empty:
                logger.info("No significant earthquakes (M≥6.5)")
                return self._create_no_threat_assessment()
            
            logger.info(f"Found {len(significant)} significant earthquake(s)")
            
            # Step 3: Analyze most recent/significant earthquake
            latest_eq = significant.iloc[0]
            
            earthquake_data = {
                'id': latest_eq['id'],
                'magnitude': latest_eq['magnitude'],
                'depth': latest_eq['depth'],
                'latitude': latest_eq['latitude'],
                'longitude': latest_eq['longitude'],
                'time': latest_eq['time'].isoformat() if hasattr(latest_eq['time'], 'isoformat') else str(latest_eq['time']),
                'place': latest_eq['place']
            }
            
            logger.info(f"Analyzing earthquake: M{earthquake_data['magnitude']} at {earthquake_data['place']}")
            
            # Step 4: Fetch ocean conditions
            logger.info("Fetching ocean conditions...")
            tide_data = self.noaa_tides_collector.fetch_all_stations(hours=6)
            buoy_data = self.noaa_buoys_collector.fetch_all_buoys()
            
            # Analyze ocean conditions
            ocean_conditions = self._analyze_ocean_conditions(tide_data, buoy_data)
            
            # Step 5: Fetch INCOIS advisories
            logger.info("Checking INCOIS advisories...")
            incois_advisories = self.incois_collector.fetch_current_advisories()
            
            # Step 6: Prepare model inputs
            logger.info("Preprocessing data for model...")
            eq_input = self.preprocessor.preprocess_earthquake_data(
                earthquakes[earthquakes['magnitude'] >= 6.0]
            )
            ocean_input = self.preprocessor.preprocess_ocean_data(
                tide_data, buoy_data
            )
            spatial_input = self.preprocessor.preprocess_spatial_data(
                self.bathymetry_loader.bathymetry_data,
                (earthquake_data['latitude'], earthquake_data['longitude'])
            )
            
            # Reshape for single prediction
            eq_input = eq_input.reshape(1, *eq_input.shape[1:])
            ocean_input = ocean_input.reshape(1, *ocean_input.shape[1:])
            spatial_input = spatial_input.reshape(1, *spatial_input.shape)
            
            # Step 7: Run model prediction
            logger.info("Running model prediction...")
            risk_prob, confidence, risk_class = self.model.predict(
                eq_input, ocean_input, spatial_input
            )
            
            model_prediction = {
                'risk_probability': float(risk_prob[0][0]),
                'confidence': float(confidence[0][0]),
                'risk_class': risk_class[0].tolist()
            }
            
            logger.info(f"Model prediction: Risk={model_prediction['risk_probability']:.3f}, "
                       f"Confidence={model_prediction['confidence']:.3f}")
            
            # Step 8: Apply India-specific filter
            logger.info("Applying India impact filter...")
            india_filter_result = self.india_filter.assess_india_risk(
                earthquake_data, model_prediction
            )
            
            # Step 9: Generate comprehensive assessment
            logger.info("Generating risk assessment...")
            assessment = self.risk_assessor.generate_comprehensive_assessment(
                earthquake_data,
                model_prediction,
                india_filter_result,
                ocean_conditions,
                incois_advisories
            )
            
            self.current_assessment = assessment
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error during tsunami check: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _analyze_ocean_conditions(self, tide_data: Dict, buoy_data: Dict) -> Dict:
        """Analyze ocean conditions for anomalies"""
        conditions = {
            'sea_level_anomaly': 'normal',
            'wave_height_anomaly': 'normal',
            'tsunami_indicators': []
        }
        
        # Analyze tide data
        for station_id, df in tide_data.items():
            if not df.empty:
                anomaly_score = self.noaa_tides_collector.calculate_sea_level_anomaly(df)
                if anomaly_score > 2.0:
                    conditions['sea_level_anomaly'] = 'elevated'
                    conditions['tsunami_indicators'].append('sea_level_anomaly')
        
        # Analyze buoy data
        for station_id, df in buoy_data.items():
            if not df.empty:
                signature = self.noaa_buoys_collector.detect_tsunami_signature(df)
                if signature['detected']:
                    conditions['wave_height_anomaly'] = 'anomalous'
                    conditions['tsunami_indicators'].extend(signature['indicators'])
        
        return conditions
    
    def _create_no_threat_assessment(self) -> Dict:
        """Create assessment for no threat scenario"""
        return {
            'assessment_id': f"NO_THREAT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.utcnow().isoformat(),
            'alert_level': 'NONE',
            'india_at_risk': False,
            'india_risk_score': 0.0,
            'alert_message': '✓ No tsunami threat to Indian coast',
            'system_status': {
                'model_operational': True,
                'last_update': datetime.utcnow().isoformat()
            }
        }
    
    def _handle_alert(self, assessment: Dict):
        """Handle tsunami alert"""
        # In production, this would:
        # - Send notifications
        # - Update dashboards
        # - Alert authorities
        # - Trigger emergency protocols
        
        logger.critical(f"TSUNAMI ALERT: {assessment['alert_message']}")
        logger.critical(f"Risk Score: {assessment['india_risk_score']:.2f}")
        logger.critical(f"Affected Regions: {assessment['affected_regions']}")
    
    def get_current_status(self) -> Dict:
        """Get current system status"""
        return {
            'is_monitoring': self.is_running,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'check_interval_seconds': self.check_interval,
            'model_loaded': self.model.model is not None,
            'current_assessment': self.current_assessment,
            'system_time': datetime.utcnow().isoformat()
        }
