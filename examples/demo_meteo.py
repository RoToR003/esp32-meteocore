"""
Weather Forecasting Demo
========================

Demonstration of the weather forecasting module.
Works on both CPython and MicroPython.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.meteo.forecast import WeatherForecastSystem
from src.core.validators import DataValidator


def demo_weather_forecast():
    """Demonstrate weather forecasting capabilities."""
    print("=" * 70)
    print("ESP32-MeteoCore - Weather Forecasting Demo")
    print("=" * 70)
    print()
    
    # Initialize forecast system
    print("Initializing weather forecast system...")
    forecast_system = WeatherForecastSystem()
    
    # Try to load weather data from file
    if forecast_system.load_weather_data("weather_log.json"):
        print("Weather data loaded successfully")
        print()
        
        # Get current conditions
        print("Current Weather Conditions:")
        print("-" * 70)
        current = forecast_system.get_current_conditions()
        if current:
            print(f"Temperature:        {current['temperature']}°C")
            print(f"Pressure:           {current['pressure']} hPa")
            print(f"Humidity:           {current['humidity']}%")
            print(f"Dew Point:          {current['dew_point']}°C")
            print(f"Dew Point Deficit:  {current['dew_point_deficit']}°C")
            print(f"Condensation Level: {current['condensation_level']} m")
            print(f"Air Density:        {current['air_density']} kg/m³")
        print()
        
        # Analyze trends
        print("Weather Trends:")
        print("-" * 70)
        trends = forecast_system.analyze_trends()
        if 'error' not in trends:
            print(f"Pressure Trend:     {trends.get('pressure_trend', 'N/A')}")
            print(f"Temperature Trend:  {trends.get('temperature_trend', 'N/A')}")
            print(f"Humidity Trend:     {trends.get('humidity_trend', 'N/A')}")
        print()
        
        # Generate nowcast
        print("Current Weather Analysis (Nowcast):")
        print("-" * 70)
        nowcast = forecast_system.generate_nowcast()
        if 'forecast' in nowcast:
            print(f"Forecast:           {nowcast['forecast']}")
            print(f"Confidence:         {nowcast.get('confidence', 'N/A')}")
            if 'warnings' in nowcast:
                print(f"Warnings:           {nowcast['warnings']}")
        print()
        
        # Generate forecast
        print("Weather Forecast (3 hours ahead):")
        print("-" * 70)
        forecast = forecast_system.generate_forecast(hours_ahead=3)
        if 'summary' in forecast:
            print(forecast['summary'])
        
    else:
        print("Could not load weather data file.")
        print("Generating simulated data...")
        print()
        
        # Demonstrate with simulated data
        simulated_conditions = {
            'temperature': 22.5,
            'humidity': 65.0,
            'pressure': 1013.0
        }
        
        # Validate input
        try:
            validated = DataValidator.validate_sensor_data(simulated_conditions)
            print(f"Input data validated: {validated}")
        except Exception as e:
            print(f"Validation error: {e}")
            return
        
        print()
        print("Simulated Sensor Data:")
        print(f"  Temperature: {simulated_conditions['temperature']}°C")
        print(f"  Humidity:    {simulated_conditions['humidity']}%")
        print(f"  Pressure:    {simulated_conditions['pressure']} hPa")
        print()
        print("Note: For full forecast functionality, provide weather_log.json file")
        print("You can generate it using: python src/utils/data_generator.py")
    
    print()
    print("=" * 70)
    print("Demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo_weather_forecast()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
