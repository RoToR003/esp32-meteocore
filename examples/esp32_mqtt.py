"""
ESP32 with MQTT Integration
===========================

ESP32 operation with WiFi and MQTT publishing.
Reads sensors, generates forecasts, and publishes to MQTT broker.

Hardware requirements:
  - ESP32 board with WiFi
  - BME280 sensor (I2C)
  - BH1750 light sensor (I2C) - optional

Configuration:
  Edit the WIFI_SSID, WIFI_PASSWORD, and MQTT_BROKER variables below.
"""

try:
    import machine
    import time
    MICROPYTHON = True
except ImportError:
    import time
    MICROPYTHON = False
    print("Warning: Running on CPython, hardware features disabled")

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.esp32.sensors import BME280Sensor, LightSensor, MockSensor
from src.esp32.wifi_manager import WiFiManager
from src.esp32.mqtt_client import MQTTClient
from src.esp32.display import Display
from src.meteo.barometric import adjust_pressure_to_sea_level
from src.meteo.psychrometry import dew_point, humidity_deficit
from src.fishing.activity import FishBiteForecastSystem


# ============================================================================
# CONFIGURATION - Edit these values for your setup
# ============================================================================

WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

MQTT_BROKER = "mqtt.example.com"  # or IP address like "192.168.1.100"
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if your broker requires authentication
MQTT_PASSWORD = None

MQTT_TOPIC_WEATHER = "home/meteo/weather"
MQTT_TOPIC_FISHING = "home/meteo/fishing"
MQTT_TOPIC_SENSORS = "home/meteo/sensors"

UPDATE_INTERVAL = 300  # Seconds between readings (5 minutes)

# ============================================================================


def log(message):
    """Simple logging."""
    print(f"[ESP32-MQTT] {message}")


def connect_wifi(wifi_manager):
    """Connect to WiFi network."""
    log("Connecting to WiFi...")
    
    max_retries = 3
    for attempt in range(max_retries):
        if wifi_manager.connect(WIFI_SSID, WIFI_PASSWORD, timeout=15):
            ip = wifi_manager.get_ip()
            log(f"Connected! IP: {ip}")
            return True
        else:
            log(f"Connection attempt {attempt + 1}/{max_retries} failed")
            time.sleep(5)
    
    log("Failed to connect to WiFi")
    return False


def connect_mqtt(mqtt_client):
    """Connect to MQTT broker."""
    log(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        if mqtt_client.connect(MQTT_USERNAME, MQTT_PASSWORD):
            log("Connected to MQTT broker")
            return True
        else:
            log(f"Connection attempt {attempt + 1}/{max_retries} failed")
            time.sleep(5)
    
    log("Failed to connect to MQTT broker")
    return False


def main():
    """Main application loop."""
    log("ESP32-MeteoCore with MQTT Starting...")
    log("=" * 50)
    
    # Initialize I2C bus
    if MICROPYTHON:
        try:
            i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=100000)
            log("I2C initialized")
            devices = i2c.scan()
            if devices:
                log(f"Found I2C devices: {[hex(d) for d in devices]}")
        except Exception as e:
            log(f"I2C init error: {e}")
            i2c = None
    else:
        i2c = None
    
    # Initialize sensors
    if i2c:
        bme = BME280Sensor(i2c)
        light = LightSensor(i2c)
    else:
        log("Using mock sensors")
        bme = MockSensor()
        light = MockSensor()
    
    display = Display("console")
    
    # Initialize WiFi
    wifi = WiFiManager()
    if not connect_wifi(wifi):
        log("ERROR: Cannot continue without WiFi")
        return
    
    # Initialize MQTT
    mqtt = MQTTClient(MQTT_BROKER, MQTT_PORT)
    if not connect_mqtt(mqtt):
        log("ERROR: Cannot continue without MQTT")
        return
    
    # Initialize fish forecast system
    fish_system = FishBiteForecastSystem()
    
    log("System initialized, starting main loop")
    log("Press Ctrl+C to stop")
    log("=" * 50)
    
    iteration = 0
    last_wifi_check = time.time()
    
    try:
        while True:
            iteration += 1
            log(f"\n--- Iteration {iteration} ---")
            
            # Check WiFi connection (every minute)
            if time.time() - last_wifi_check > 60:
                if not wifi.is_connected():
                    log("WiFi connection lost, reconnecting...")
                    if not connect_wifi(wifi):
                        log("WiFi reconnection failed, waiting...")
                        time.sleep(60)
                        continue
                    if not connect_mqtt(mqtt):
                        log("MQTT reconnection failed, waiting...")
                        time.sleep(60)
                        continue
                last_wifi_check = time.time()
            
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
            
            log(f"T={weather_data['temperature']:.1f}°C, "
                f"H={weather_data['humidity']:.0f}%, "
                f"P={weather_data['pressure']:.1f}hPa")
            
            # Calculate derived values
            pressure_mslp = adjust_pressure_to_sea_level(
                weather_data['pressure'],
                weather_data['temperature']
            )
            
            dewpoint = dew_point(
                weather_data['temperature'],
                weather_data['humidity']
            )
            
            # Publish raw sensor data
            sensor_payload = {
                'temperature': round(weather_data['temperature'], 2),
                'humidity': round(weather_data['humidity'], 2),
                'pressure': round(weather_data['pressure'], 2),
                'pressure_mslp': round(pressure_mslp, 2),
                'illuminance': round(illuminance, 1) if illuminance else None
            }
            
            if mqtt.publish_sensor_data(sensor_payload, MQTT_TOPIC_SENSORS):
                log("Sensor data published to MQTT")
            
            # Publish weather data
            weather_payload = {
                'temperature': round(weather_data['temperature'], 2),
                'humidity': round(weather_data['humidity'], 2),
                'pressure_mslp': round(pressure_mslp, 2),
                'dew_point': round(dewpoint, 2)
            }
            
            if mqtt.publish_weather(weather_payload, MQTT_TOPIC_WEATHER):
                log("Weather data published to MQTT")
            
            # Calculate and publish fish activity
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
                'pressure_change_3h': 0.0,
                'water_temp_celsius': weather_data['temperature'] - 2.0,
                'dissolved_O2_mg_per_L': 8.0,
                'illuminance_lux': illuminance if illuminance else 5000.0,
                'wind_speed_m_s': 2.0,
                'moon_phase': 0.5,
                'time_of_day': hour,
                'month': month,
                'is_raining': False,
                'cloud_cover_percent': 50
            }
            
            fish_result = fish_system.calculate_KIAR(conditions)
            
            if 'error' not in fish_result:
                fishing_payload = {
                    'KIAR_percent': round(fish_result['KIAR_percent'], 1),
                    'rating': fish_result['rating'],
                    'recommendation': fish_result['recommendation']
                }
                
                if mqtt.publish_fishing(fishing_payload, MQTT_TOPIC_FISHING):
                    log(f"Fishing data published: {fish_result['KIAR_percent']:.1f}% - {fish_result['rating']}")
            
            # Wait before next reading
            log(f"Waiting {UPDATE_INTERVAL}s until next reading...")
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        log("\nStopped by user")
    except Exception as e:
        log(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log("Shutting down...")
        mqtt.disconnect()
        wifi.disconnect()


if __name__ == "__main__":
    main()
