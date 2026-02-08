"""
Personal Weather Station for Vinnytsia with Fishing Forecast for Southern Bug
==============================================================================

A complete example demonstrating the integration of:
- Local sensors (BME280, BH1750)
- API data (Open-Meteo)
- Precise barometric calculations for Vinnytsia (305m elevation)
- Fish bite forecast for Southern Bug river species

This station is calibrated specifically for:
- Location: Vinnytsia, Ukraine (49.233°N, 28.468°E)
- Elevation: 305 meters above sea level
- Water body: Southern Bug River (city center)
- Purpose: Personal fishing forecast station
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime

# Try to import ESP32 modules, fall back to mock implementations
try:
    from machine import I2C, Pin
    ESP32_AVAILABLE = True
except ImportError:
    ESP32_AVAILABLE = False
    print("[INFO] Running in simulation mode (no ESP32 hardware)")

from src.esp32.sensors import BME280Sensor, LightSensor
from src.api.weather_api import VinnytsiaWeatherAPI
from src.meteo.forecast import WeatherForecastSystem
from src.meteo.barometric import adjust_pressure_to_sea_level_precise
from src.fishing.activity import FishBiteForecastSystem
from src.fishing.profiles import FishSpecies


class VinnytsiaWeatherStation:
    """Personal weather station for Vinnytsia with fishing forecast"""
    
    def __init__(self):
        """Initialize the station"""
        print("="*80)
        print("PERSONAL WEATHER STATION VINNYTSIA")
        print("Location: Southern Bug River, city center")
        print("="*80)
        
        # Initialize sensors
        if ESP32_AVAILABLE:
            i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
            self.bme280 = BME280Sensor(i2c)
            self.light_sensor = LightSensor(i2c)
        else:
            # Mock sensors for testing
            self.bme280 = self._create_mock_bme280()
            self.light_sensor = self._create_mock_light()
        
        # API client
        self.api = VinnytsiaWeatherAPI()
        
        # Forecast systems
        self.weather_system = WeatherForecastSystem()
        
        # Fish forecast systems for different species
        self.pike_forecast = FishBiteForecastSystem(FishSpecies.SOUTHBUG_PIKE)
        self.zander_forecast = FishBiteForecastSystem(FishSpecies.SOUTHBUG_ZANDER)
        self.bream_forecast = FishBiteForecastSystem(FishSpecies.SOUTHBUG_BREAM)
        
        print("[INFO] Station initialized successfully")
    
    def _create_mock_bme280(self):
        """Create mock BME280 sensor for testing"""
        class MockBME280:
            def read(self):
                return {
                    'temperature': 18.5,
                    'pressure': 976.5,  # Station pressure at 305m
                    'humidity': 65.0
                }
        return MockBME280()
    
    def _create_mock_light(self):
        """Create mock light sensor for testing"""
        class MockLight:
            def read_lux(self):
                hour = datetime.now().hour
                # Simulate daylight cycle
                if 6 <= hour <= 18:
                    return 5000 + (hour - 12) ** 2 * 500
                else:
                    return 50
        return MockLight()
    
    def read_sensors(self):
        """Read all local sensors"""
        local_data = self.bme280.read()
        illuminance = self.light_sensor.read_lux()
        
        return {
            'temperature': local_data['temperature'],
            'pressure': local_data['pressure'],
            'humidity': local_data['humidity'],
            'illuminance': illuminance
        }
    
    def get_precise_mslp(self, station_pressure, temperature, humidity):
        """
        Calculate precise mean sea level pressure for Vinnytsia.
        Uses humidity-aware barometric formula.
        """
        return adjust_pressure_to_sea_level_precise(
            station_pressure,
            temperature,
            humidity,
            elevation=305
        )
    
    def get_water_temperature(self, air_temp):
        """Get Southern Bug water temperature"""
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        return self.api.get_water_temperature_southbug(air_temp, day_of_year)
    
    def prepare_fishing_conditions(self, sensor_data, api_data, water_temp, moon_phase):
        """Prepare conditions dictionary for fishing forecast"""
        now = datetime.now()
        
        conditions = {
            # Local sensors
            'air_temp_celsius': sensor_data['temperature'],
            'pressure_mmHg': sensor_data['pressure_mslp'] * 0.750062,  # hPa -> mmHg
            'pressure_change_3h_mmHg': 0,  # TODO: store history
            'humidity_percent': sensor_data['humidity'],
            'illuminance_lux': sensor_data['illuminance'],
            
            # API data
            'wind_speed_ms': api_data['wind_speed_ms'],
            'rain_mm_per_hour': api_data['rain_mm_per_hour'],
            'cloud_cover_percent': api_data['cloud_cover_percent'],
            'uv_index': api_data['uv_index'],
            
            # Astronomy
            'moon_phase': moon_phase,
            'hour_of_day': now.hour + now.minute / 60.0,
            'day_of_year': now.timetuple().tm_yday,
            
            # Southern Bug River
            'water_temp_celsius': water_temp,
            'river_current_speed': 0.3,  # m/s (typical for city center)
            'turbidity_ntu': 15.0,  # NTU (moderate)
            'pH': 7.8,  # Southern Bug is slightly alkaline
            
            # Hydrochemistry (typical values)
            'dissolved_oxygen_mg_l': None  # Will be calculated automatically
        }
        
        return conditions
    
    def print_weather_conditions(self, sensor_data, api_data, water_temp, moon_phase):
        """Print current weather conditions"""
        print("\n🌤️  WEATHER CONDITIONS:")
        print("-"*80)
        print(f"Air temperature: {sensor_data['temperature']:.1f}°C")
        print(f"Water temperature: {water_temp:.1f}°C")
        print(f"Pressure (MSLP): {sensor_data['pressure_mslp']:.1f} hPa")
        print(f"Humidity: {sensor_data['humidity']:.0f}%")
        print(f"Wind: {api_data['wind_speed_ms']:.1f} m/s")
        print(f"Illuminance: {sensor_data['illuminance']:.0f} lux")
        print(f"Moon phase: {moon_phase*100:.0f}%")
        print(f"Cloud cover: {api_data['cloud_cover_percent']:.0f}%")
        print(f"UV index: {api_data['uv_index']}")
    
    def print_fishing_forecast(self, conditions):
        """Print fishing forecast for different species"""
        print("\n🎣 FISHING FORECAST FOR SOUTHERN BUG:")
        print("-"*80)
        
        # Pike forecast
        pike_result = self.pike_forecast.calculate_KIAR(conditions)
        print(f"\n🐟 PIKE: {pike_result['KIAR_percent']:.1f}%")
        print(f"   {pike_result['recommendation']}")
        
        # Zander forecast
        zander_result = self.zander_forecast.calculate_KIAR(conditions)
        print(f"\n🐟 ZANDER: {zander_result['KIAR_percent']:.1f}%")
        print(f"   {zander_result['recommendation']}")
        
        # Bream forecast
        bream_result = self.bream_forecast.calculate_KIAR(conditions)
        print(f"\n🐟 BREAM: {bream_result['KIAR_percent']:.1f}%")
        print(f"   {bream_result['recommendation']}")
    
    def run_once(self):
        """Run one measurement cycle"""
        print("\n" + "="*80)
        print("PERSONAL WEATHER STATION VINNYTSIA")
        print("Location: Southern Bug River, city center")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. Read local sensors
        sensor_data = self.read_sensors()
        
        # 2. Get API data
        api_data = self.api.get_current_data()
        moon_phase = self.api.get_moon_phase()
        
        # 3. Calculate precise MSLP for Vinnytsia (305m)
        sensor_data['pressure_mslp'] = self.get_precise_mslp(
            sensor_data['pressure'],
            sensor_data['temperature'],
            sensor_data['humidity']
        )
        
        # 4. Calculate Southern Bug water temperature
        water_temp = self.get_water_temperature(sensor_data['temperature'])
        
        # 5. Print weather conditions
        self.print_weather_conditions(sensor_data, api_data, water_temp, moon_phase)
        
        # 6. Prepare conditions for fishing forecast
        conditions = self.prepare_fishing_conditions(
            sensor_data, api_data, water_temp, moon_phase
        )
        
        # 7. Print fishing forecast
        self.print_fishing_forecast(conditions)
        
        print("\n" + "="*80)
    
    def main_loop(self, interval_seconds=300):
        """
        Main loop - runs continuously
        
        Args:
            interval_seconds: Time between measurements (default: 5 minutes)
        """
        while True:
            try:
                self.run_once()
                print(f"\nNext update in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\n[INFO] Station stopped by user")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)


def main():
    """Main entry point"""
    station = VinnytsiaWeatherStation()
    
    # Run once for testing, or uncomment main_loop for continuous operation
    station.run_once()
    
    # For continuous operation:
    # station.main_loop(interval_seconds=300)


if __name__ == "__main__":
    main()
