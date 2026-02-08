"""
ESP32 Standalone Operation
==========================

Autonomous ESP32 operation with display output.
Reads sensors, generates forecasts, and displays results.

Hardware requirements:
  - ESP32 board
  - BME280 sensor (I2C)
  - BH1750 light sensor (I2C) - optional
  - SSD1306 OLED display (I2C) - optional
"""

try:
    import machine
    import time
    MICROPYTHON = True
except ImportError:
    # Running on CPython for testing
    import time
    MICROPYTHON = False
    print("Warning: Running on CPython, hardware features disabled")

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.esp32.sensors import BME280Sensor, LightSensor, MockSensor
from src.esp32.display import Display, SSD1306Display
from src.meteo.barometric import adjust_pressure_to_sea_level, celsius_to_kelvin
from src.meteo.psychrometry import dew_point, humidity_deficit
from src.fishing.activity import FishBiteForecastSystem, FishActivityCalculations
from src.core.constants import PhysicalConstants


def log(message):
    """Simple logging."""
    print(f"[ESP32] {message}")


def main():
    """Main application loop."""
    log("ESP32-MeteoCore Standalone Starting...")
    log("=" * 50)
    
    # Initialize I2C bus (if on MicroPython)
    if MICROPYTHON:
        try:
            i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=100000)
            log(f"I2C initialized")
            
            # Scan for devices
            devices = i2c.scan()
            if devices:
                log(f"Found I2C devices: {[hex(d) for d in devices]}")
            else:
                log("No I2C devices found")
        except Exception as e:
            log(f"I2C init error: {e}")
            i2c = None
    else:
        i2c = None
    
    # Initialize sensors
    if i2c:
        bme = BME280Sensor(i2c)
        light = LightSensor(i2c)
        try:
            display = SSD1306Display(i2c)
        except:
            log("OLED display not available, using console")
            display = Display("console")
    else:
        log("Using mock sensors (no hardware)")
        bme = MockSensor()
        light = MockSensor()
        display = Display("console")
    
    # Initialize fish forecast system
    fish_system = FishBiteForecastSystem()
    
    log("System initialized, starting main loop")
    log("Press Ctrl+C to stop")
    log("=" * 50)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            log(f"\n--- Iteration {iteration} ---")
            
            # Read sensors
            weather_data = bme.read()
            if hasattr(light, 'read_lux'):
                illuminance = light.read_lux()
            else:
                illuminance = light.read().get('illuminance', 0)
            
            if weather_data['temperature'] is None:
                log("Sensor read error, skipping iteration")
                time.sleep(60)
                continue
            
            # Log raw readings
            log(f"Temperature: {weather_data['temperature']}°C")
            log(f"Humidity:    {weather_data['humidity']}%")
            log(f"Pressure:    {weather_data['pressure']} hPa")
            if illuminance is not None:
                log(f"Light:       {illuminance} lux")
            
            # Calculate derived values
            pressure_mslp = adjust_pressure_to_sea_level(
                weather_data['pressure'],
                weather_data['temperature']
            )
            
            dewpoint = dew_point(
                weather_data['temperature'],
                weather_data['humidity']
            )
            
            hum_deficit = humidity_deficit(
                weather_data['temperature'],
                weather_data['humidity']
            )
            
            log(f"Pressure (sea level): {pressure_mslp:.1f} hPa")
            log(f"Dew point:            {dewpoint:.1f}°C")
            log(f"Humidity deficit:     {hum_deficit:.2f} hPa")
            
            # Prepare conditions for fishing forecast
            # Get current time
            if MICROPYTHON:
                try:
                    import utime
                    current_time = utime.localtime()
                    hour = current_time[3]
                    month = current_time[1]
                except:
                    hour = 12
                    month = 6
            else:
                from datetime import datetime
                now = datetime.now()
                hour = now.hour
                month = now.month
            
            conditions = {
                'temp_celsius': weather_data['temperature'],
                'pressure_hpa': pressure_mslp,
                'pressure_change_3h': 0.0,  # Would need history
                'water_temp_celsius': weather_data['temperature'] - 2.0,  # Estimate
                'dissolved_O2_mg_per_L': 8.0,  # Estimate
                'illuminance_lux': illuminance if illuminance else 5000.0,
                'wind_speed_m_s': 2.0,  # Default estimate
                'moon_phase': 0.5,  # Default
                'time_of_day': hour,
                'month': month,
                'is_raining': False,
                'cloud_cover_percent': 50
            }
            
            # Calculate fish activity
            log("Calculating fish activity...")
            fish_result = fish_system.calculate_KIAR(conditions)
            
            if 'error' not in fish_result:
                kiar = fish_result['KIAR_percent']
                rating = fish_result['rating']
                log(f"Fish Activity (KIAR): {kiar:.1f}% - {rating}")
            else:
                log(f"Fish calculation error: {fish_result['error']}")
                fish_result = {'KIAR_percent': 0, 'rating': 'Error'}
            
            # Update display
            display_data = {
                'temperature': weather_data['temperature'],
                'pressure': pressure_mslp,
                'humidity': weather_data['humidity'],
                'forecast': f"Dew: {dewpoint:.1f}C"
            }
            
            display.show_forecast(display_data, fish_result)
            
            # Wait before next reading (5 minutes)
            log("Waiting 5 minutes until next reading...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        log("\nStopped by user")
    except Exception as e:
        log(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log("Shutting down...")
        if display:
            display.clear()


if __name__ == "__main__":
    main()
