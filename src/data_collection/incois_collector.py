"""
INCOIS Data Collector
Fetches tsunami advisories and historical events from Indian National Centre for Ocean Information Services
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger


class INCOISCollector:
    """Collects tsunami advisories and event data from INCOIS"""
    
    def __init__(self, config: Dict):
        """
        Initialize INCOIS collector
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config['apis']['incois']
        self.base_url = self.config['base_url']
        self.advisory_endpoint = self.config['advisory_endpoint']
        self.event_endpoint = self.config['event_endpoint']
    
    def fetch_current_advisories(self) -> List[Dict]:
        """
        Fetch current tsunami advisories from INCOIS
        
        Returns:
            List of active advisory dictionaries
        """
        try:
            url = f"{self.base_url}{self.advisory_endpoint}"
            
            logger.info("Fetching current INCOIS advisories...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Note: INCOIS API format may vary - this is a template
            data = response.json()
            advisories = data.get('advisories', [])
            
            logger.success(f"Fetched {len(advisories)} INCOIS advisories")
            return advisories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch INCOIS advisories: {e}")
            # Return empty list on failure to allow system to continue
            return []
        except Exception as e:
            logger.error(f"Error processing INCOIS advisories: {e}")
            return []
    
    def fetch_historical_events(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch historical tsunami events from INCOIS
        
        Args:
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with historical tsunami events
        """
        try:
            url = f"{self.base_url}{self.event_endpoint}"
            
            params = {}
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            logger.info("Fetching INCOIS historical events...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            if not events:
                logger.warning("No historical events found")
                return pd.DataFrame()
            
            df = pd.DataFrame(events)
            logger.success(f"Fetched {len(df)} INCOIS historical events")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch INCOIS historical events: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing INCOIS historical events: {e}")
            return pd.DataFrame()
    
    def parse_advisory(self, advisory: Dict) -> Dict:
        """
        Parse and structure advisory information
        
        Args:
            advisory: Raw advisory dictionary
            
        Returns:
            Structured advisory information
        """
        return {
            'id': advisory.get('id', ''),
            'issue_time': advisory.get('issue_time', ''),
            'level': advisory.get('level', 'unknown'),
            'regions': advisory.get('affected_regions', []),
            'message': advisory.get('message', ''),
            'expected_arrival': advisory.get('expected_arrival', ''),
            'source': 'INCOIS'
        }
    
    def get_india_specific_risk(self) -> Dict[str, any]:
        """
        Get current India-specific tsunami risk assessment
        
        Returns:
            Dictionary with risk assessment
        """
        advisories = self.fetch_current_advisories()
        
        if not advisories:
            return {
                'risk_level': 'normal',
                'active_advisories': 0,
                'affected_regions': [],
                'last_update': datetime.utcnow().isoformat()
            }
        
        # Process advisories to determine overall risk
        risk_levels = {'watch': 1, 'advisory': 2, 'warning': 3, 'major_warning': 4}
        max_risk = 0
        affected_regions = set()
        
        for advisory in advisories:
            parsed = self.parse_advisory(advisory)
            level_value = risk_levels.get(parsed['level'], 0)
            max_risk = max(max_risk, level_value)
            affected_regions.update(parsed['regions'])
        
        risk_names = {0: 'normal', 1: 'watch', 2: 'advisory', 3: 'warning', 4: 'major_warning'}
        
        return {
            'risk_level': risk_names[max_risk],
            'active_advisories': len(advisories),
            'affected_regions': list(affected_regions),
            'last_update': datetime.utcnow().isoformat(),
            'advisories': [self.parse_advisory(adv) for adv in advisories]
        }
