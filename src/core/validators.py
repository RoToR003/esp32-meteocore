"""
Input Data Validation
=====================

Validators for meteorological and fishing prediction data.
"""

from typing import Dict, Any, Optional


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class DataValidator:
    """Validator for meteorological and fishing data."""
    
    @staticmethod
    def validate_temperature(temp: float, min_val: float = -50, max_val: float = 60) -> float:
        """
        Validate temperature value.
        
        Args:
            temp: Temperature in Celsius
            min_val: Minimum allowed temperature
            max_val: Maximum allowed temperature
            
        Returns:
            Validated temperature
            
        Raises:
            ValidationError: If temperature is invalid
        """
        if not isinstance(temp, (int, float)):
            raise ValidationError(f"Temperature must be numeric, got {type(temp).__name__}")
        
        if not min_val <= temp <= max_val:
            raise ValidationError(f"Temperature {temp}°C out of range [{min_val}, {max_val}]")
        
        return float(temp)
    
    @staticmethod
    def validate_pressure(pressure: float, min_val: float = 900, max_val: float = 1100) -> float:
        """
        Validate atmospheric pressure value.
        
        Args:
            pressure: Pressure in hPa
            min_val: Minimum allowed pressure
            max_val: Maximum allowed pressure
            
        Returns:
            Validated pressure
            
        Raises:
            ValidationError: If pressure is invalid
        """
        if not isinstance(pressure, (int, float)):
            raise ValidationError(f"Pressure must be numeric, got {type(pressure).__name__}")
        
        if not min_val <= pressure <= max_val:
            raise ValidationError(f"Pressure {pressure} hPa out of range [{min_val}, {max_val}]")
        
        return float(pressure)
    
    @staticmethod
    def validate_humidity(humidity: float, min_val: float = 0, max_val: float = 100) -> float:
        """
        Validate relative humidity value.
        
        Args:
            humidity: Relative humidity in percent
            min_val: Minimum allowed humidity
            max_val: Maximum allowed humidity
            
        Returns:
            Validated humidity
            
        Raises:
            ValidationError: If humidity is invalid
        """
        if not isinstance(humidity, (int, float)):
            raise ValidationError(f"Humidity must be numeric, got {type(humidity).__name__}")
        
        if not min_val <= humidity <= max_val:
            raise ValidationError(f"Humidity {humidity}% out of range [{min_val}, {max_val}]")
        
        return float(humidity)
    
    @staticmethod
    def validate_wind_speed(wind_speed: float, min_val: float = 0, max_val: float = 100) -> float:
        """
        Validate wind speed value.
        
        Args:
            wind_speed: Wind speed in m/s
            min_val: Minimum allowed wind speed
            max_val: Maximum allowed wind speed
            
        Returns:
            Validated wind speed
            
        Raises:
            ValidationError: If wind speed is invalid
        """
        if not isinstance(wind_speed, (int, float)):
            raise ValidationError(f"Wind speed must be numeric, got {type(wind_speed).__name__}")
        
        if not min_val <= wind_speed <= max_val:
            raise ValidationError(f"Wind speed {wind_speed} m/s out of range [{min_val}, {max_val}]")
        
        return float(wind_speed)
    
    @staticmethod
    def validate_illuminance(illuminance: float, min_val: float = 0, max_val: float = 200000) -> float:
        """
        Validate illuminance value.
        
        Args:
            illuminance: Illuminance in lux
            min_val: Minimum allowed illuminance
            max_val: Maximum allowed illuminance (200000 lux ~ bright sunlight)
            
        Returns:
            Validated illuminance
            
        Raises:
            ValidationError: If illuminance is invalid
        """
        if not isinstance(illuminance, (int, float)):
            raise ValidationError(f"Illuminance must be numeric, got {type(illuminance).__name__}")
        
        if not min_val <= illuminance <= max_val:
            raise ValidationError(f"Illuminance {illuminance} lux out of range [{min_val}, {max_val}]")
        
        return float(illuminance)
    
    @staticmethod
    def validate_water_temp(water_temp: float, min_val: float = 0, max_val: float = 40) -> float:
        """
        Validate water temperature value.
        
        Args:
            water_temp: Water temperature in Celsius
            min_val: Minimum allowed water temperature
            max_val: Maximum allowed water temperature
            
        Returns:
            Validated water temperature
            
        Raises:
            ValidationError: If water temperature is invalid
        """
        if not isinstance(water_temp, (int, float)):
            raise ValidationError(f"Water temperature must be numeric, got {type(water_temp).__name__}")
        
        if not min_val <= water_temp <= max_val:
            raise ValidationError(f"Water temperature {water_temp}°C out of range [{min_val}, {max_val}]")
        
        return float(water_temp)
    
    @staticmethod
    def validate_sensor_data(data: Dict[str, Any]) -> Dict[str, float]:
        """
        Validate sensor data dictionary.
        
        Args:
            data: Dictionary with sensor readings
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: If any sensor data is invalid
        """
        validated = {}
        
        if 'temperature' in data:
            validated['temperature'] = DataValidator.validate_temperature(data['temperature'])
        
        if 'pressure' in data:
            validated['pressure'] = DataValidator.validate_pressure(data['pressure'])
        
        if 'humidity' in data:
            validated['humidity'] = DataValidator.validate_humidity(data['humidity'])
        
        if 'wind_speed' in data:
            validated['wind_speed'] = DataValidator.validate_wind_speed(data['wind_speed'])
        
        if 'illuminance' in data:
            validated['illuminance'] = DataValidator.validate_illuminance(data['illuminance'])
        
        if 'water_temp' in data or 'water_temp_celsius' in data:
            key = 'water_temp' if 'water_temp' in data else 'water_temp_celsius'
            validated['water_temp_celsius'] = DataValidator.validate_water_temp(data[key])
        
        return validated
    
    @staticmethod
    def validate_conditions(conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate weather conditions dictionary.
        
        Args:
            conditions: Dictionary with weather conditions
            
        Returns:
            Validated conditions dictionary
            
        Raises:
            ValidationError: If any condition is invalid
        """
        validated = {}
        
        # Validate required fields
        required_fields = []
        for field in required_fields:
            if field not in conditions:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate each field if present
        if 'temperature' in conditions or 'temp_celsius' in conditions:
            key = 'temperature' if 'temperature' in conditions else 'temp_celsius'
            validated['temp_celsius'] = DataValidator.validate_temperature(conditions[key])
        
        if 'pressure' in conditions or 'pressure_hpa' in conditions:
            key = 'pressure' if 'pressure' in conditions else 'pressure_hpa'
            validated['pressure_hpa'] = DataValidator.validate_pressure(conditions[key])
        
        if 'humidity' in conditions:
            validated['humidity'] = DataValidator.validate_humidity(conditions['humidity'])
        
        if 'wind_speed' in conditions:
            validated['wind_speed'] = DataValidator.validate_wind_speed(conditions['wind_speed'])
        
        if 'water_temp_celsius' in conditions:
            validated['water_temp_celsius'] = DataValidator.validate_water_temp(conditions['water_temp_celsius'])
        
        if 'illuminance_lux' in conditions:
            validated['illuminance_lux'] = DataValidator.validate_illuminance(conditions['illuminance_lux'])
        
        # Copy other fields as-is
        for key, value in conditions.items():
            if key not in validated:
                validated[key] = value
        
        return validated
