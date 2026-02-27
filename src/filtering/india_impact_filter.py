"""
India Impact Filter
Determines if detected tsunami poses risk to India
"""

import numpy as np
from typing import Dict, Tuple, List
from loguru import logger


class IndiaImpactFilter:
    """
    Filters tsunami alerts to determine India-specific impact
    
    Evaluates:
    - Epicenter location and proximity to Indian coast
    - Wave propagation direction
    - Ocean depth and coastal amplification
    - Historical patterns of Indian Ocean tsunamis
    """
    
    def __init__(self, config: Dict):
        """
        Initialize India impact filter
        
        Args:
            config: Configuration dictionary with India region settings
        """
        self.config = config
        self.india_region = config['india_region']
        self.critical_radius_km = self.india_region['critical_radius_km']
        
        # Indian coastline regions
        self.coastline_regions = self.india_region['coastline']
        
        # Define critical earthquake zones that affect India
        self.critical_zones = {
            'andaman_subduction': {
                'lat_range': (0, 15),
                'lon_range': (90, 100),
                'threat_level': 'critical'
            },
            'makran_subduction': {
                'lat_range': (20, 27),
                'lon_range': (60, 68),
                'threat_level': 'high'
            },
            'sumatra_subduction': {
                'lat_range': (-10, 5),
                'lon_range': (90, 105),
                'threat_level': 'medium'
            },
            'arabian_sea': {
                'lat_range': (10, 25),
                'lon_range': (60, 75),
                'threat_level': 'medium'
            }
        }
    
    def assess_india_risk(self, 
                         earthquake_data: Dict,
                         model_prediction: Dict) -> Dict:
        """
        Assess if tsunami poses risk to India
        
        Args:
            earthquake_data: Dictionary with earthquake information
                {latitude, longitude, magnitude, depth, time}
            model_prediction: Model output
                {risk_probability, confidence, risk_class}
        
        Returns:
            Dictionary with India-specific risk assessment
        """
        lat = earthquake_data['latitude']
        lon = earthquake_data['longitude']
        magnitude = earthquake_data['magnitude']
        depth = earthquake_data['depth']
        
        # Step 1: Check if model detected tsunami risk
        model_risk = model_prediction['risk_probability']
        
        if model_risk < 0.25:
            return self._create_no_risk_response(
                "Model prediction below threshold",
                model_prediction
            )
        
        # Step 2: Evaluate location threat level
        location_threat = self._evaluate_location_threat(lat, lon)
        
        if location_threat['threat_level'] == 'none':
            return self._create_no_risk_response(
                "Epicenter outside critical zones for India",
                model_prediction
            )
        
        # Step 3: Calculate distance to Indian coast
        distance_to_coast = self._calculate_distance_to_india(lat, lon)
        
        if distance_to_coast > self.critical_radius_km:
            return self._create_no_risk_response(
                f"Epicenter too distant ({distance_to_coast:.0f} km)",
                model_prediction
            )
        
        # Step 4: Evaluate wave propagation direction
        propagation_risk = self._evaluate_propagation_direction(
            lat, lon, magnitude
        )
        
        # Step 5: Assess depth and tsunami generation potential
        depth_factor = self._assess_depth_factor(depth, magnitude)
        
        # Step 6: Identify affected regions
        affected_regions = self._identify_affected_regions(
            lat, lon, magnitude, propagation_risk
        )
        
        # Step 7: Calculate final India risk score
        india_risk_score = self._calculate_india_risk_score(
            model_risk=model_risk,
            location_threat=location_threat['threat_weight'],
            distance_factor=self._normalize_distance(distance_to_coast),
            propagation_factor=propagation_risk,
            depth_factor=depth_factor
        )
        
        # Step 8: Determine risk level
        risk_level = self._determine_risk_level(india_risk_score)
        
        return {
            'india_at_risk': india_risk_score > 0.3,
            'india_risk_score': india_risk_score,
            'risk_level': risk_level,
            'affected_regions': affected_regions,
            'distance_to_coast_km': distance_to_coast,
            'location_threat': location_threat['threat_level'],
            'propagation_favorable': propagation_risk > 0.5,
            'depth_favorable': depth_factor > 0.5,
            'model_confidence': model_prediction['confidence'],
            'reasoning': self._generate_reasoning(
                india_risk_score,
                location_threat,
                distance_to_coast,
                affected_regions
            )
        }
    
    def _evaluate_location_threat(self, lat: float, lon: float) -> Dict:
        """Evaluate threat level based on earthquake location"""
        for zone_name, zone_info in self.critical_zones.items():
            lat_min, lat_max = zone_info['lat_range']
            lon_min, lon_max = zone_info['lon_range']
            
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                threat_weights = {
                    'critical': 1.0,
                    'high': 0.8,
                    'medium': 0.5
                }
                return {
                    'zone': zone_name,
                    'threat_level': zone_info['threat_level'],
                    'threat_weight': threat_weights[zone_info['threat_level']]
                }
        
        return {
            'zone': 'none',
            'threat_level': 'none',
            'threat_weight': 0.0
        }
    
    def _calculate_distance_to_india(self, lat: float, lon: float) -> float:
        """Calculate minimum distance to Indian coastline"""
        min_distance = float('inf')
        
        for region_name, bounds in self.coastline_regions.items():
            # Calculate distance to center of coastal region
            lat_center = (bounds['min_lat'] + bounds['max_lat']) / 2
            lon_center = (bounds['min_lon'] + bounds['max_lon']) / 2
            
            distance = self._haversine_distance(lat, lon, lat_center, lon_center)
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _evaluate_propagation_direction(self, lat: float, lon: float, 
                                       magnitude: float) -> float:
        """
        Evaluate if wave propagation direction favors India impact
        Returns value between 0 and 1
        """
        # Simplified: assumes waves propagate in all directions
        # For more accuracy, would use tsunami propagation models
        
        # Check if epicenter is positioned to send waves toward India
        india_center_lat = 20.0
        india_center_lon = 77.0
        
        # Calculate bearing from epicenter to India
        bearing = self._calculate_bearing(lat, lon, india_center_lat, india_center_lon)
        
        # Stronger earthquakes have more omnidirectional propagation
        if magnitude >= 8.0:
            return 1.0  # Major tsunamis affect large areas
        elif magnitude >= 7.0:
            return 0.8
        else:
            # For smaller earthquakes, direction matters more
            # Simplified: assume favorable if generally toward India
            distance = self._haversine_distance(lat, lon, india_center_lat, india_center_lon)
            if distance < 1000:
                return 0.9
            else:
                return 0.5
    
    def _calculate_bearing(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate bearing from point 1 to point 2"""
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlon = lon2 - lon1
        x = np.sin(dlon) * np.cos(lat2)
        y = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
        
        bearing = np.arctan2(x, y)
        bearing = np.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    def _assess_depth_factor(self, depth: float, magnitude: float) -> float:
        """
        Assess tsunami generation potential based on depth
        Returns value between 0 and 1
        """
        # Shallow earthquakes more likely to generate tsunamis
        if magnitude >= 7.5:
            if depth < 70:
                return 1.0
            elif depth < 100:
                return 0.7
            else:
                return 0.3
        elif magnitude >= 7.0:
            if depth < 50:
                return 1.0
            elif depth < 70:
                return 0.6
            else:
                return 0.2
        else:
            if depth < 40:
                return 0.8
            elif depth < 60:
                return 0.4
            else:
                return 0.1
    
    def _identify_affected_regions(self, lat: float, lon: float, 
                                   magnitude: float, 
                                   propagation_risk: float) -> List[str]:
        """Identify which Indian coastal regions are affected"""
        affected = []
        
        if propagation_risk < 0.3:
            return affected
        
        # Calculate distance to each region
        for region_name, bounds in self.coastline_regions.items():
            lat_center = (bounds['min_lat'] + bounds['max_lat']) / 2
            lon_center = (bounds['min_lon'] + bounds['max_lon']) / 2
            
            distance = self._haversine_distance(lat, lon, lat_center, lon_center)
            
            # Impact radius based on magnitude
            if magnitude >= 8.5:
                impact_radius = 4000
            elif magnitude >= 8.0:
                impact_radius = 3000
            elif magnitude >= 7.5:
                impact_radius = 2000
            elif magnitude >= 7.0:
                impact_radius = 1500
            else:
                impact_radius = 1000
            
            if distance <= impact_radius:
                affected.append(region_name)
        
        return affected
    
    def _normalize_distance(self, distance: float) -> float:
        """Normalize distance to factor between 0 and 1"""
        # Closer = higher risk
        if distance <= 500:
            return 1.0
        elif distance <= 1000:
            return 0.8
        elif distance <= 2000:
            return 0.6
        elif distance <= 3000:
            return 0.4
        else:
            return 0.2
    
    def _calculate_india_risk_score(self, model_risk: float,
                                    location_threat: float,
                                    distance_factor: float,
                                    propagation_factor: float,
                                    depth_factor: float) -> float:
        """Calculate overall India risk score"""
        # Weighted combination of factors
        weights = {
            'model': 0.35,
            'location': 0.25,
            'distance': 0.20,
            'propagation': 0.10,
            'depth': 0.10
        }
        
        score = (
            model_risk * weights['model'] +
            location_threat * weights['location'] +
            distance_factor * weights['distance'] +
            propagation_factor * weights['propagation'] +
            depth_factor * weights['depth']
        )
        
        return np.clip(score, 0.0, 1.0)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine categorical risk level"""
        thresholds = self.config['model']['thresholds']
        
        if risk_score >= thresholds['high_risk']:
            return 'HIGH'
        elif risk_score >= thresholds['medium_risk']:
            return 'MEDIUM'
        elif risk_score >= thresholds['low_risk']:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _generate_reasoning(self, risk_score: float, location_threat: Dict,
                           distance: float, affected_regions: List[str]) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        reasons.append(f"India risk score: {risk_score:.2f}")
        reasons.append(f"Epicenter in {location_threat['zone']} zone ({location_threat['threat_level']} threat)")
        reasons.append(f"Distance to Indian coast: {distance:.0f} km")
        
        if affected_regions:
            regions_str = ', '.join(affected_regions)
            reasons.append(f"Potentially affected regions: {regions_str}")
        else:
            reasons.append("No Indian coastal regions directly threatened")
        
        return " | ".join(reasons)
    
    def _create_no_risk_response(self, reason: str, model_prediction: Dict) -> Dict:
        """Create response for no India risk"""
        return {
            'india_at_risk': False,
            'india_risk_score': 0.0,
            'risk_level': 'NONE',
            'affected_regions': [],
            'distance_to_coast_km': None,
            'location_threat': 'none',
            'propagation_favorable': False,
            'depth_favorable': False,
            'model_confidence': model_prediction.get('confidence', 0.0),
            'reasoning': reason
        }
