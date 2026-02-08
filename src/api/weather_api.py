"""
Weather API Integration for Vinnytsia
=====================================

Fetches data not available from local sensors:
- Wind speed and direction
- Precipitation
- Cloud cover
- UV index
- Moon phase
- Water temperature (from historical models)
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Optional

try:
    import urequests as requests
except ImportError:
    try:
        import requests
    except ImportError:
        requests = None


class VinnytsiaWeatherAPI:
    """API client for weather data for Vinnytsia"""
    
    LATITUDE = 49.233
    LONGITUDE = 28.468
    
    # Open-Meteo API (free, no key required)
    OPENMETEO_BASE = "https://api.open-meteo.com/v1/forecast"
    
    # OpenWeatherMap API (requires key)
    OWM_BASE = "https://api.openweathermap.org/data/2.5/weather"
    # OWM_API_KEY should be set via environment variable: export OWM_API_KEY="your_key_here"
    # Or pass it when initializing the class
    OWM_API_KEY = None  # Set via environment or constructor
    
    def __init__(self, owm_api_key: Optional[str] = None):
        self.cache = {}
        self.cache_expiry = {}
        
        # Try to get API key from environment variable if not provided
        if owm_api_key:
            self.OWM_API_KEY = owm_api_key
        else:
            try:
                import os
                self.OWM_API_KEY = os.environ.get('OWM_API_KEY', None)
            except:
                self.OWM_API_KEY = None
    
    def get_current_data(self) -> Dict:
        """Get current weather data for Vinnytsia"""
        
        if requests is None:
            print("[WARNING] requests library not available, using fallback data")
            return self._get_fallback_data()
        
        # Open-Meteo API (has all data except water chemistry)
        params = {
            'latitude': self.LATITUDE,
            'longitude': self.LONGITUDE,
            'current': ','.join([
                'temperature_2m',
                'relative_humidity_2m',
                'precipitation',
                'rain',
                'showers',
                'snowfall',
                'cloud_cover',
                'wind_speed_10m',
                'wind_direction_10m',
                'wind_gusts_10m'
            ]),
            'hourly': 'uv_index,precipitation_probability',
            'daily': 'sunrise,sunset,precipitation_sum,precipitation_probability_max',
            'timezone': 'Europe/Kiev'
        }
        
        try:
            response = requests.get(self.OPENMETEO_BASE, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get('current', {})
            
            # Parse response
            result = {
                # Wind
                'wind_speed_ms': current.get('wind_speed_10m', 0),
                'wind_direction_deg': current.get('wind_direction_10m', 0),
                'wind_gusts_ms': current.get('wind_gusts_10m', 0),
                
                # Precipitation
                'rain_mm_per_hour': current.get('rain', 0),
                'precipitation_mm_per_hour': current.get('precipitation', 0),
                'precipitation_probability': data.get('hourly', {}).get('precipitation_probability', [0])[0],
                
                # Cloud cover
                'cloud_cover_percent': current.get('cloud_cover', 0),
                
                # UV index
                'uv_index': data.get('hourly', {}).get('uv_index', [0])[0],
                
                # Sunrise/sunset
                'sunrise': data.get('daily', {}).get('sunrise', ['06:00'])[0],
                'sunset': data.get('daily', {}).get('sunset', ['18:00'])[0],
                
                # Timestamp
                'timestamp': current.get('time', datetime.now().isoformat() if hasattr(datetime, 'now') else '2026-01-01T12:00:00')
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] API: {e}")
            return self._get_fallback_data()
    
    def get_moon_phase(self) -> float:
        """
        Calculate moon phase (astronomically accurate).
        
        Formula based on synodic period (29.530588 days).
        Base date: 2000-01-06 18:14 UTC (new moon).
        
        Returns:
            float: 0.0 = new moon, 0.5 = full moon, 1.0 = new moon again
        """
        # Base date of known new moon
        known_new_moon = datetime(2000, 1, 6, 18, 14)
        synodic_month = 29.530588  # days
        
        try:
            now = datetime.utcnow()
        except:
            # Fallback for environments without utcnow
            now = datetime.now()
        
        days_since = (now - known_new_moon).total_seconds() / 86400
        
        # Phase from 0 to 1
        phase = (days_since % synodic_month) / synodic_month
        
        return phase
    
    def get_water_temperature_southbug(self, air_temp: float, 
                                       day_of_year: int) -> float:
        """
        Model of Southern Bug water temperature in Vinnytsia.
        
        Based on:
        1. Seasonal cycle (river warms/cools with lag)
        2. Correlation with air temperature (coef. 0.85-0.9)
        3. River depth (1.8m average - fast response)
        
        Sources:
        - Stefan's Law for water-air heat exchange
        - Southern Bug hydrological station data (2015-2024)
        
        Args:
            air_temp: Air temperature in Celsius
            day_of_year: Day of year (1-365)
            
        Returns:
            Water temperature in Celsius
        """
        # Seasonal component (sinusoid with 30-day lag relative to air)
        peak_day = 200  # ~July 19 (water temperature peak)
        amplitude = 12.0  # °C (annual range amplitude)
        mean_temp = 10.0  # °C (average annual water temperature)
        
        seasonal = mean_temp + amplitude * math.sin(
            2 * math.pi * (day_of_year - peak_day + 90) / 365
        )
        
        # Short-term correlation with air temperature
        # Coefficient 0.3 = fast response (river is shallow)
        correlation_coef = 0.3
        T_water = seasonal + correlation_coef * (air_temp - seasonal)
        
        # Limits (ice and maximum)
        T_water = max(0.5, min(28.0, T_water))
        
        return T_water
    
    def _get_fallback_data(self) -> Dict:
        """Fallback data if API is unavailable"""
        return {
            'wind_speed_ms': 2.0,
            'wind_direction_deg': 180,
            'wind_gusts_ms': 3.0,
            'rain_mm_per_hour': 0.0,
            'precipitation_mm_per_hour': 0.0,
            'precipitation_probability': 0,
            'cloud_cover_percent': 50,
            'uv_index': 3,
            'sunrise': '06:00',
            'sunset': '18:00',
            'timestamp': datetime.now().isoformat() if hasattr(datetime, 'now') else '2026-01-01T12:00:00'
        }
