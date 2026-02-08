# ESP32-MeteoCore

**Professional Weather Forecasting and Fish Activity Prediction System for ESP32**

A modular, scientifically accurate system for weather forecasting and fish bite prediction, designed to run on ESP32 microcontrollers with MicroPython, while maintaining full compatibility with standard Python for development and testing.

## 🌟 Features

### Weather Forecasting
- **Professional meteorological calculations** based on scientific formulas
- Barometric pressure analysis and sea level adjustment
- Psychrometric calculations (humidity, dew point, condensation level)
- Synoptic analysis with pressure tendency detection
- Statistical forecasting models
- Hazardous weather detection (thunderstorms, fog, frost)
- Zambretti forecaster for long-range predictions

### Fish Activity Prediction
- **KIAR (Comprehensive Fish Activity Index)** calculation
- Species-specific profiles (pike, perch, carp, catfish, and more)
- Multi-factor analysis:
  - Water temperature and oxygen levels
  - Atmospheric pressure changes
  - Light conditions and moon phases
  - Time of day and seasonal patterns
  - Weather conditions
- Scientific basis using Van't Hoff equation for cold-blooded animals

### ESP32 Hardware Support
- **BME280/BMP180/BMP280** sensor drivers (temperature, humidity, pressure)
- **AHT20** sensor driver (temperature, humidity) for ESP32-S3
- **BH1750** light sensor support
- **ST7789** TFT display driver (1.28"/1.69" with PWM backlight)
- **WiFi** connection management with auto-reconnect and burst mode
- **Deep Sleep** power management with wake-on-timer and wake-on-IR
- **Battery monitoring** via ADC with voltage divider
- **MQTT** integration for IoT platforms
- **Display** drivers (SSD1306 OLED, LCD1602, ST7789 TFT)
- Mock sensors for testing without hardware

## 📁 Project Structure

```
esp32-meteocore/
├── README.md                   # This file
├── requirements.txt            # CPython dependencies
├── requirements-esp32.txt      # MicroPython dependencies
├── main.py                     # ⭐ ESP32-S3 autonomous station entry point
├── boot.py                     # ⭐ Boot configuration
├── src/
│   ├── core/                   # Core utilities
│   │   ├── constants.py        # Physical constants (⭐ ESP32-S3 config added)
│   │   ├── calculations.py     # Math functions (numpy-free)
│   │   └── validators.py       # Input validation
│   ├── meteo/                  # Weather forecasting
│   │   ├── forecast.py         # Main forecast system
│   │   ├── synoptic.py         # Synoptic analysis
│   │   ├── barometric.py       # Pressure calculations
│   │   └── psychrometry.py     # Humidity calculations
│   ├── fishing/                # Fish activity prediction
│   │   ├── activity.py         # KIAR calculation
│   │   ├── profiles.py         # Fish species profiles
│   │   ├── chemistry.py        # Water chemistry
│   │   └── pressure_analyzer.py # ⭐ Simplified pressure trend analysis
│   ├── esp32/                  # ESP32 hardware drivers
│   │   ├── sensors.py          # BME280, BH1750 drivers
│   │   ├── aht20.py            # ⭐ AHT20 temperature/humidity driver
│   │   ├── bmp280.py           # ⭐ BMP280 pressure sensor driver
│   │   ├── st7789_display.py   # ⭐ ST7789 TFT display driver
│   │   ├── power_manager.py    # ⭐ Deep Sleep and battery management
│   │   ├── memory_optimizer.py # ⭐ RAM optimization utilities
│   │   ├── wifi_manager.py     # WiFi management
│   │   ├── mqtt_client.py      # MQTT client
│   │   └── display.py          # Display drivers
│   └── utils/
│       └── data_generator.py   # Weather data generator
├── examples/
│   ├── demo_meteo.py           # Weather forecast demo
│   ├── demo_fishing.py         # Fish prediction demo
│   ├── esp32_standalone.py     # Standalone ESP32 operation
│   ├── esp32_mqtt.py           # ESP32 with MQTT
│   └── esp32s3_station_demo.py # ⭐ ESP32-S3 autonomous station demo
├── tests/
│   ├── test_calculations.py    # Unit tests
│   └── ...
└── docs/
    ├── FISHING_BITE_FORECAST_RESEARCH.md
    └── meteorology_professional_guide.md
```

## 🚀 Quick Start

### Installation for Development (CPython)

```bash
# Clone the repository
git clone https://github.com/RoToR003/esp32-meteocore.git
cd esp32-meteocore

# Install dependencies
pip install -r requirements.txt

# Run weather forecast demo
python examples/demo_meteo.py

# Run fishing prediction demo
python examples/demo_fishing.py
```

### Installation for ESP32 (MicroPython)

1. **Flash MicroPython to ESP32**
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-micropython.bin
   ```

2. **Upload the project**
   ```bash
   # Using ampy or rshell
   ampy --port /dev/ttyUSB0 put src /
   ```

3. **Install MicroPython libraries**
   ```python
   import upip
   upip.install('micropython-bme280')
   upip.install('micropython-umqtt.simple')
   ```

4. **Run standalone example**
   ```python
   import esp32_standalone
   ```

## 🔋 ESP32-S3 Autonomous Station Mode

### Overview
Transform your ESP32-S3 into an **autonomous meteo station** with ultra-low power consumption for 6-month battery operation!

### Features
- ✅ **Deep Sleep Mode**: Wakes once per hour for updates (~30 µA consumption)
- ✅ **IR Remote Wake**: View data instantly without WiFi
- ✅ **ST7789 Display**: 1.28" or 1.69" IPS TFT with PWM brightness
- ✅ **Battery Powered**: 2×18650 cells (~5400 mAh capacity)
- ✅ **WiFi Burst Mode**: Connect only for 10-15 seconds to save power
- ✅ **Memory Optimized**: No numpy/pandas, minimal RAM usage
- ✅ **Smart Sensors**: AHT20 (temp/humidity) + BMP280 (pressure)

### Hardware Requirements

**MCU:** YD-ESP32-S3 (N16R8)
- 16MB Flash, 8MB PSRAM
- MicroPython firmware
- Deep Sleep with RTC GPIO support

**Display:** ST7789 (1.28" or 1.69" IPS TFT)
```python
# SPI Interface
SCK  = GPIO 14
MOSI = GPIO 13
RST  = GPIO 12
DC   = GPIO 11
BLK  = GPIO 10  # PWM for brightness
```

**Sensors (I2C):**
```python
# AHT20 (Temperature/Humidity)
# BMP280 (Pressure/Temperature)
SDA = GPIO 4
SCL = GPIO 5
```

**IR Receiver:** VS1838B
```python
IR_PIN = GPIO 1  # RTC GPIO for wake_on_ext0
```

**Battery Monitoring:**
```python
BAT_ADC = GPIO 2  # Voltage divider 100kΩ/100kΩ
```

**Power Supply:**
- 2×18650 cells in parallel (~5400 mAh)
- TP4056 USB-C charging module
- MT3608 Step-Up converter (4.5V → 5V)

### Operating Modes

#### 1. Cold Boot (First Start)
```
1. Initialize peripherals (I2C, SPI, Display)
2. Connect WiFi (from saved networks)
3. NTP time synchronization
4. Fetch weather forecast from API
5. Read sensors (AHT20 + BMP280)
6. Save data to NVS (Non-Volatile Storage)
7. Enter Deep Sleep (1 hour)
```

#### 2. Timer Wake (Every Hour)
```
1. Wake from Deep Sleep (timer)
2. Turn on WiFi (10-15 seconds only!)
3. Read sensors
4. Update weather forecast
5. Analyze pressure trend (last 6-12 hours)
6. Update display (5 seconds)
7. Turn off WiFi
8. Enter Deep Sleep (1 hour)
```

#### 3. IR Wake (Remote Button Press)
```
1. Wake from Deep Sleep (IR signal)
2. NO WiFi activation (saves power)
3. Read sensors (local data only)
4. Display last cached forecast
5. Keep backlight on (15 seconds)
6. Enter Deep Sleep (1 hour)
```

### Power Consumption

**Deep Sleep Mode:**
- ESP32-S3: ~10-20 µA
- AHT20: 0.25 µA (standby)
- BMP280: 0.1 µA (sleep)
- Display: 0 mA (backlight off)
- **Total: ~20-30 µA**

**Active Mode (Timer Wake):**
- ESP32-S3 + WiFi: ~200 mA (10 sec)
- Sensor reading: ~5 mA (1 sec)
- Display: ~30 mA (5 sec)
- **Average: ~1.2 mAh per hour**

**Battery Life:**
- Capacity: 5400 mAh (2×18650)
- Consumption: 1.2 mA/hour (average)
- **Runtime: ~4500 hours (6 months!)** 🔋

### Installation

1. **Flash MicroPython to ESP32-S3**
   ```bash
   esptool.py --chip esp32s3 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32s3 --port /dev/ttyUSB0 write_flash -z 0 ESP32_GENERIC_S3-20240602-v1.23.0.bin
   ```

2. **Install required MicroPython libraries**
   ```bash
   # Connect to ESP32-S3
   mpremote connect /dev/ttyUSB0
   
   # Install ST7789 display driver
   mpremote mip install github:russhughes/st7789py_mpy
   
   # Install sensor libraries
   mpremote mip install ahtx0
   mpremote mip install bmp280
   ```

3. **Upload the project**
   ```bash
   # Upload all source files
   mpremote cp -r src/ :
   mpremote cp main.py :
   mpremote cp boot.py :
   ```

4. **Configure WiFi**
   Edit WiFi credentials before uploading or use the interactive setup.

5. **Run**
   ```bash
   # The station will auto-start from main.py
   # Or run manually:
   mpremote run main.py
   ```

### Usage Example

```python
# Run the autonomous station demo
python examples/esp32s3_station_demo.py
```

The demo demonstrates:
- Sensor initialization and reading
- Display functionality
- Power management
- Memory optimization
- Fishing forecast analysis

### Wiring Diagram

```
ESP32-S3          Connections
--------          -----------
GPIO 14   ---->   ST7789 SCK
GPIO 13   ---->   ST7789 MOSI
GPIO 12   ---->   ST7789 RST
GPIO 11   ---->   ST7789 DC
GPIO 10   ---->   ST7789 BLK
GPIO 4    ---->   I2C SDA (AHT20, BMP280)
GPIO 5    ---->   I2C SCL (AHT20, BMP280)
GPIO 1    ---->   VS1838B IR Receiver
GPIO 2    ---->   Battery ADC (via divider)
```

### Configuration

All ESP32-S3 settings are in `src/core/constants.py`:

```python
# Deep Sleep settings
SLEEP_DURATION_NORMAL = 3600  # 1 hour (seconds)
SLEEP_DURATION_SHORT = 300    # 5 min (for testing)
SLEEP_DURATION_IR_DISPLAY = 15  # 15 sec (after IR wake)

# Display settings
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240  # or 280 for 1.69"
DISPLAY_ROTATION = 0  # 0, 90, 180, 270

# Battery thresholds
BAT_FULL = 4.2   # Volts (100%)
BAT_EMPTY = 3.2  # Volts (0%)
```

### Fishing Forecast

The autonomous station includes a simplified pressure analyzer for fishing predictions:

```python
from src.fishing.pressure_analyzer import analyze_pressure_trend

# Pressure history (hourly readings)
pressures = [1013.2, 1012.8, 1012.5, 1012.0, 1011.5, 1011.0]

result = analyze_pressure_trend(pressures)
# Result:
# {
#     'delta_6h': -2.2,
#     'trend': 'falling',
#     'fishing_status': '🎣 ВІДМІННО (хижак)',
#     'recommendation': 'Тиск падає - жор хижаків!'
# }
```

**Pressure Logic:**
- ΔP < -2 hPa/6h: Falling → Excellent for predators
- ΔP > +2 hPa/6h: Rising → Reduced activity
- |ΔP| < 2 hPa/6h: Stable → Normal activity

## 📊 Usage Examples

### Weather Forecasting

```python
from src.meteo.forecast import WeatherForecastSystem

# Initialize system
forecast = WeatherForecastSystem()

# Load historical data
forecast.load_weather_data("weather_log.json")

# Get current conditions
current = forecast.get_current_conditions()
print(f"Temperature: {current['temperature']}°C")
print(f"Pressure: {current['pressure']} hPa")
print(f"Dew Point: {current['dew_point']}°C")

# Generate forecast
nowcast = forecast.generate_nowcast()
print(f"Forecast: {nowcast['forecast']}")
```

### Fish Activity Prediction

```python
from src.fishing.activity import FishBiteForecastSystem

# Initialize system
fish_system = FishBiteForecastSystem()

# Define conditions
conditions = {
    'water_temp_celsius': 18.0,
    'pressure_hpa': 1015.0,
    'pressure_change_3h': 2.0,  # Rising pressure
    'dissolved_O2_mg_per_L': 8.5,
    'illuminance_lux': 5000.0,
    'time_of_day': 7,  # 7 AM
    'month': 6  # June
}

# Calculate KIAR
result = fish_system.calculate_KIAR(conditions)
print(f"Fish Activity: {result['KIAR_percent']}%")
print(f"Rating: {result['rating']}")
print(f"Recommendation: {result['recommendation']}")
```

### ESP32 Standalone Operation

```python
from machine import I2C, Pin
from src.esp32.sensors import BME280Sensor
from src.meteo.barometric import adjust_pressure_to_sea_level

# Initialize I2C and sensor
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = BME280Sensor(i2c)

# Read sensor
data = sensor.read()
print(f"Temperature: {data['temperature']}°C")
print(f"Pressure: {data['pressure']} hPa")

# Adjust to sea level
pressure_mslp = adjust_pressure_to_sea_level(
    data['pressure'], 
    data['temperature']
)
print(f"Sea Level Pressure: {pressure_mslp} hPa")
```

## 🔌 Hardware Connections

### BME280 Sensor (I2C)
```
ESP32        BME280
-----        ------
3.3V    -->  VCC
GND     -->  GND
GPIO21  -->  SDA
GPIO22  -->  SCL
```

### BH1750 Light Sensor (I2C)
```
ESP32        BH1750
-----        ------
3.3V    -->  VCC
GND     -->  GND
GPIO21  -->  SDA
GPIO22  -->  SCL
```

### SSD1306 OLED Display (I2C)
```
ESP32        SSD1306
-----        -------
3.3V    -->  VCC
GND     -->  GND
GPIO21  -->  SDA
GPIO22  -->  SCL
```

## 📖 API Documentation

### Core Modules

#### Constants (`src/core/constants.py`)
Physical constants for meteorological and hydrological calculations.

```python
from src.core.constants import PhysicalConstants

# Access constants
print(PhysicalConstants.P0_HPA)  # Standard pressure: 1013.25 hPa
print(PhysicalConstants.ELEVATION)  # Default elevation: 262m
```

#### Calculations (`src/core/calculations.py`)
Numpy-free mathematical functions for MicroPython compatibility.

```python
from src.core.calculations import mean, std_dev, exponential_smoothing

data = [20.0, 21.0, 20.5, 22.0]
avg = mean(data)  # 20.875
std = std_dev(data)  # ~0.76
```

#### Validators (`src/core/validators.py`)
Input data validation for sensor readings.

```python
from src.core.validators import DataValidator

data = {'temperature': 25.0, 'humidity': 60.0}
validated = DataValidator.validate_sensor_data(data)
```

### Meteorological Modules

#### Barometric (`src/meteo/barometric.py`)
Atmospheric pressure calculations.

```python
from src.meteo.barometric import adjust_pressure_to_sea_level

# Adjust station pressure to sea level
mslp = adjust_pressure_to_sea_level(1000.0, 20.0)
```

#### Psychrometry (`src/meteo/psychrometry.py`)
Humidity and water vapor calculations.

```python
from src.meteo.psychrometry import dew_point, humidity_deficit

dp = dew_point(25.0, 60.0)  # Temperature, humidity
deficit = humidity_deficit(25.0, 60.0)
```

## 🧪 Testing

Run unit tests:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_calculations.py

# Run with verbose output
python -m pytest -v tests/
```

## 🔧 Configuration

### WiFi Configuration (ESP32)
Edit `examples/esp32_mqtt.py`:

```python
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
```

### MQTT Configuration
```python
MQTT_BROKER = "mqtt.example.com"
MQTT_PORT = 1883
MQTT_TOPIC_WEATHER = "home/meteo/weather"
MQTT_TOPIC_FISHING = "home/meteo/fishing"
```

### Location Configuration
Edit `src/core/constants.py`:

```python
class PhysicalConstants:
    ELEVATION = 262  # Your elevation in meters
```

## 📈 KIAR Interpretation

| KIAR % | Rating | Description |
|--------|--------|-------------|
| 80-100% | Excellent | Best fishing conditions |
| 60-80% | Very Good | High fish activity expected |
| 40-60% | Good | Moderate activity, good chances |
| 20-40% | Fair | Low activity, patience required |
| 0-20% | Poor | Unfavorable conditions |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Based on professional meteorological formulas and scientific research
- Fish activity models derived from ichthyology studies
- Designed for the ESP32 community

## 📚 References

- See `docs/meteorology_professional_guide.md` for detailed meteorological formulas
- See `docs/FISHING_BITE_FORECAST_RESEARCH.md` for fish prediction methodology

## 🐛 Troubleshooting

### "Module not found" errors on ESP32
- Ensure all files are uploaded to the ESP32
- Check that MicroPython libraries are installed

### Sensor not detected
- Check I2C connections (SDA, SCL, VCC, GND)
- Verify I2C address with `i2c.scan()`
- Common addresses: BME280 (0x76/0x77), BH1750 (0x23/0x5C)

### WiFi connection fails
- Check SSID and password
- Ensure ESP32 is within range
- Verify 2.4GHz network (ESP32 doesn't support 5GHz)

## 📞 Support

For issues and questions:
- GitHub Issues: [https://github.com/RoToR003/esp32-meteocore/issues](https://github.com/RoToR003/esp32-meteocore/issues)

---

**Version:** 2.0.0  
**Last Updated:** 2026  
**Author:** ESP32-MeteoCore Team
