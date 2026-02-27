"""
Risk Assessor
Comprehensive risk assessment and alert generation
"""

from typing import Dict, List
from datetime import datetime, timedelta
from loguru import logger


class RiskAssessor:
    """
    Comprehensive tsunami risk assessment for India
    Generates alerts and advisories
    """
    
    def __init__(self, config: Dict):
        """
        Initialize risk assessor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.thresholds = config['model']['thresholds']
        self.alert_history = []
    
    def generate_comprehensive_assessment(self,
                                         earthquake_data: Dict,
                                         model_prediction: Dict,
                                         india_filter_result: Dict,
                                         ocean_conditions: Dict,
                                         incois_advisories: List[Dict]) -> Dict:
        """
        Generate comprehensive risk assessment
        
        Args:
            earthquake_data: Earthquake information
            model_prediction: Model predictions
            india_filter_result: India-specific filtering results
            ocean_conditions: Current ocean conditions
            incois_advisories: Official INCOIS advisories
            
        Returns:
            Comprehensive assessment dictionary
        """
        assessment_time = datetime.utcnow()
        
        # Determine overall alert level
        alert_level = self._determine_alert_level(
            india_filter_result,
            incois_advisories
        )
        
        # Generate alert message
        alert_message = self._generate_alert_message(
            alert_level,
            earthquake_data,
            india_filter_result
        )
        
        # Calculate estimated arrival times
        arrival_times = self._estimate_arrival_times(
            earthquake_data,
            india_filter_result['affected_regions']
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            alert_level,
            india_filter_result['affected_regions']
        )
        
        # Compile assessment
        assessment = {
            'assessment_id': self._generate_assessment_id(assessment_time),
            'timestamp': assessment_time.isoformat(),
            'alert_level': alert_level,
            'india_at_risk': india_filter_result['india_at_risk'],
            'india_risk_score': india_filter_result['india_risk_score'],
            'model_confidence': india_filter_result['model_confidence'],
            
            'earthquake_info': {
                'magnitude': earthquake_data['magnitude'],
                'depth_km': earthquake_data['depth'],
                'location': {
                    'latitude': earthquake_data['latitude'],
                    'longitude': earthquake_data['longitude']
                },
                'time': earthquake_data['time'],
                'place': earthquake_data.get('place', 'Unknown')
            },
            
            'affected_regions': india_filter_result['affected_regions'],
            'estimated_arrival_times': arrival_times,
            
            'ocean_conditions': {
                'sea_level_anomaly': ocean_conditions.get('sea_level_anomaly', 'normal'),
                'wave_height_anomaly': ocean_conditions.get('wave_height_anomaly', 'normal'),
                'buoy_indicators': ocean_conditions.get('tsunami_indicators', [])
            },
            
            'official_advisories': {
                'incois_status': self._parse_incois_status(incois_advisories),
                'active_warnings': len(incois_advisories)
            },
            
            'alert_message': alert_message,
            'recommendations': recommendations,
            
            'data_sources': {
                'earthquake': 'USGS Earthquake API',
                'ocean_data': ['NOAA Tides & Currents', 'NOAA NDBC Buoys'],
                'bathymetry': 'GEBCO',
                'official': 'INCOIS'
            },
            
            'system_status': {
                'model_operational': True,
                'data_freshness': 'current',
                'last_update': assessment_time.isoformat()
            }
        }
        
        # Store in history
        self.alert_history.append(assessment)
        
        logger.info(f"Generated assessment: {alert_level} alert")
        
        return assessment
    
    def _determine_alert_level(self, india_filter_result: Dict,
                               incois_advisories: List[Dict]) -> str:
        """Determine overall alert level"""
        
        # Check INCOIS official advisories first
        if incois_advisories:
            for advisory in incois_advisories:
                level = advisory.get('level', '').lower()
                if 'major' in level or 'warning' in level:
                    return 'WARNING'
                elif 'advisory' in level:
                    return 'ADVISORY'
                elif 'watch' in level:
                    return 'WATCH'
        
        # Use India risk assessment
        if not india_filter_result['india_at_risk']:
            return 'NONE'
        
        risk_level = india_filter_result['risk_level']
        
        if risk_level == 'HIGH':
            return 'WARNING'
        elif risk_level == 'MEDIUM':
            return 'ADVISORY'
        elif risk_level == 'LOW':
            return 'WATCH'
        else:
            return 'INFORMATION'
    
    def _generate_alert_message(self, alert_level: str,
                                earthquake_data: Dict,
                                india_filter_result: Dict) -> str:
        """Generate human-readable alert message"""
        
        magnitude = earthquake_data['magnitude']
        depth = earthquake_data['depth']
        place = earthquake_data.get('place', 'Unknown location')
        
        if alert_level == 'WARNING':
            message = (
                f"⚠️ TSUNAMI WARNING for Indian coast. "
                f"A magnitude {magnitude:.1f} earthquake at {depth:.0f}km depth "
                f"near {place} has generated tsunami waves. "
            )
            if india_filter_result['affected_regions']:
                regions = ', '.join(india_filter_result['affected_regions'])
                message += f"Affected regions: {regions}. "
            message += "Immediate evacuation of coastal areas recommended."
            
        elif alert_level == 'ADVISORY':
            message = (
                f"⚠️ TSUNAMI ADVISORY for Indian coast. "
                f"A magnitude {magnitude:.1f} earthquake at {depth:.0f}km depth "
                f"near {place} may generate tsunami waves. "
            )
            if india_filter_result['affected_regions']:
                regions = ', '.join(india_filter_result['affected_regions'])
                message += f"Monitor advisories for: {regions}. "
            message += "Stay alert and follow local authorities."
            
        elif alert_level == 'WATCH':
            message = (
                f"ℹ️ TSUNAMI WATCH. "
                f"A magnitude {magnitude:.1f} earthquake at {depth:.0f}km depth "
                f"near {place} detected. "
                f"Low risk to Indian coast but monitoring continues."
            )
            
        elif alert_level == 'INFORMATION':
            message = (
                f"ℹ️ INFORMATION: "
                f"Magnitude {magnitude:.1f} earthquake at {depth:.0f}km depth "
                f"near {place}. Minimal tsunami risk to India."
            )
            
        else:  # NONE
            message = (
                f"✓ NO THREAT to Indian coast from magnitude {magnitude:.1f} "
                f"earthquake near {place}."
            )
        
        return message
    
    def _estimate_arrival_times(self, earthquake_data: Dict,
                                affected_regions: List[str]) -> Dict[str, str]:
        """Estimate tsunami arrival times for affected regions"""
        
        if not affected_regions:
            return {}
        
        eq_time = earthquake_data.get('time')
        if isinstance(eq_time, str):
            eq_time = datetime.fromisoformat(eq_time.replace('Z', '+00:00'))
        
        arrival_times = {}
        
        # Simplified tsunami travel time estimation
        # Average tsunami speed: ~700 km/h in deep ocean
        tsunami_speed = 700  # km/h
        
        lat = earthquake_data['latitude']
        lon = earthquake_data['longitude']
        
        # Approximate distances to regions (simplified)
        region_coords = {
            'west_coast': (15.0, 73.0),
            'east_coast': (13.0, 80.0),
            'andaman_nicobar': (11.0, 92.5)
        }
        
        for region in affected_regions:
            if region in region_coords:
                reg_lat, reg_lon = region_coords[region]
                
                # Calculate approximate distance
                distance = self._haversine_distance(lat, lon, reg_lat, reg_lon)
                
                # Estimate travel time
                travel_hours = distance / tsunami_speed
                arrival_time = eq_time + timedelta(hours=travel_hours)
                
                arrival_times[region] = arrival_time.strftime('%Y-%m-%d %H:%M UTC')
        
        return arrival_times
    
    def _haversine_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
        import numpy as np
        R = 6371
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _generate_recommendations(self, alert_level: str,
                                  affected_regions: List[str]) -> List[str]:
        """Generate safety recommendations"""
        
        recommendations = []
        
        if alert_level == 'WARNING':
            recommendations = [
                "Evacuate coastal areas immediately",
                "Move to higher ground (at least 20 meters elevation)",
                "Stay away from beaches, harbors, and low-lying coastal areas",
                "Follow instructions from local disaster management authorities",
                "Do not return to coastal areas until all-clear is issued",
                "Monitor official channels for updates"
            ]
            
        elif alert_level == 'ADVISORY':
            recommendations = [
                "Stay away from beaches and coastal areas",
                "Be prepared to evacuate if conditions worsen",
                "Monitor tsunami warnings and updates",
                "Have emergency supplies ready",
                "Follow local authority instructions",
                "Avoid swimming or boating"
            ]
            
        elif alert_level == 'WATCH':
            recommendations = [
                "Stay informed about developing situation",
                "Be aware of tsunami warning signs",
                "Review evacuation routes",
                "Monitor official advisories",
                "Exercise normal caution near coastal areas"
            ]
            
        else:  # INFORMATION or NONE
            recommendations = [
                "No special action required",
                "Continue normal activities",
                "Stay informed through official channels"
            ]
        
        return recommendations
    
    def _parse_incois_status(self, advisories: List[Dict]) -> str:
        """Parse INCOIS advisory status"""
        if not advisories:
            return 'No active advisories'
        
        return f"{len(advisories)} active advisory(ies)"
    
    def _generate_assessment_id(self, timestamp: datetime) -> str:
        """Generate unique assessment ID"""
        return f"TSUNAMI_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get recent alert history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]
        
        return recent_alerts
