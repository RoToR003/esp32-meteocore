"""
Physical Constants for Meteorology and Hydrobiology
===================================================

Unified constants from both meteorological and fishing modules.
Compatible with both CPython and MicroPython.
"""

try:
    from micropython import const
    MICROPYTHON = True
except ImportError:
    # For CPython compatibility
    def const(x):
        return x
    MICROPYTHON = False


class PhysicalConstants:
    """
    Physical constants for meteorological and hydrological calculations.
    Merged from both meteo_core.py and fishing.py.
    """
    
    # ========================================================================
    # ATMOSPHERIC CONSTANTS
    # ========================================================================
    
    # Gas constants
    R = const(287)  # Gas constant for dry air, J/(kg·K)
    g = const(9.81)  # Gravitational acceleration, m/s² (UNIFIED - was duplicated)
    cp = const(1005)  # Specific heat capacity at constant pressure, J/(kg·K)
    cv = const(718)  # Specific heat capacity at constant volume, J/(kg·K)
    gamma = const(1.4)  # Adiabatic index
    L = const(2500000)  # Specific heat of vaporization, J/kg (2.5e6)
    
    # Psychrometric constants
    A = 0.000662  # Psychrometric coefficient
    
    # Vertical gradients
    GAMMA_DRY = 1.0  # Dry adiabatic lapse rate, °C/100m
    GAMMA_WET = 0.5  # Saturated adiabatic lapse rate, °C/100m
    GAMMA_NORMAL = 0.6  # Normal temperature lapse rate, °C/100m
    
    # Standard conditions
    P0_HPA = 1013.25  # Standard atmospheric pressure, hPa
    P0_MMHG = const(760)  # Standard pressure, mmHg
    T0_CELSIUS = const(15)  # Standard temperature, °C
    T0_KELVIN = 273.15  # Absolute zero offset
    
    # Empirical coefficients
    BARIC_STEP_COEF = const(8000)  # For baric step calculations
    CONDENSATION_COEF = const(122)  # Condensation level coefficient, m/°C
    CONDENSATION_HEIGHT_COEF = const(122)  # Alternative name for same coefficient
    
    # ========================================================================
    # LOCATION-SPECIFIC: VINNYTSIA, UKRAINE
    # ========================================================================
    
    # Geographic coordinates
    LATITUDE = 49.233  # degrees North
    LONGITUDE = 28.468  # degrees East
    ELEVATION = const(305)  # meters above sea level (CORRECTED from 262m)
    TIMEZONE = 'Europe/Kiev'
    
    # Climate of Vinnytsia (continental, temperate)
    # Average annual temperature: +7.3°C
    # Average annual precipitation: 595 mm
    # Average station pressure at 305m: 975-980 hPa
    # MSLP: 1010-1020 hPa (reduced to sea level)
    
    # Barometric formula correction for Vinnytsia (305m)
    # At T=15°C: p_station ≈ 976 hPa -> MSLP ≈ 1013 hPa
    # Correction coefficient: 1.038 (instead of universal)
    VINNYTSIA_MSLP_CORRECTION = 1.038
    
    # ========================================================================
    # SOUTHERN BUG RIVER (CENTER OF VINNYTSIA)
    # ========================================================================
    
    RIVER_NAME = "Південний Буг"
    RIVER_WIDTH = 80.0  # meters (in city center)
    RIVER_DEPTH_AVERAGE = 1.8  # meters (average depth)
    RIVER_DEPTH_MAX = 4.5  # meters (maximum depth)
    RIVER_CURRENT_SPEED = 0.3  # m/s (average current speed)
    RIVER_SUBSTRATE = "змішаний"  # sand, silt, stone
    
    # Thermal characteristics of the river
    RIVER_THERMAL_INERTIA = 0.12  # For river (fast response to weather)
    RIVER_TEMP_AMPLITUDE_SUMMER = 8.0  # °C (daily temperature range in summer)
    RIVER_TEMP_AMPLITUDE_WINTER = 2.0  # °C (lower amplitude in winter)
    
    # Ice regime of Southern Bug in Vinnytsia
    ICE_FORMATION_TEMP = -5.0  # °C (average temperature for ice formation)
    ICE_BREAKUP_TEMP = 3.0  # °C (average temperature for ice breakup)
    ICE_COVER_DAYS_AVG = 80  # days (average ice cover duration)
    
    # ========================================================================
    # WATER CHEMISTRY OF SOUTHERN BUG (GEO VINNYTSIA DATA)
    # ========================================================================
    
    WATER_PH_AVERAGE = 7.8  # slightly alkaline (typically 7.5-8.2)
    WATER_PH_MIN = 7.2
    WATER_PH_MAX = 8.5
    WATER_HARDNESS = 4.5  # mg-eq/L (moderately hard)
    WATER_OXYGEN_SATURATION_SUMMER = 7.5  # mg/L (decreases in summer)
    WATER_OXYGEN_SATURATION_WINTER = 12.0  # mg/L (increases in winter)
    WATER_TURBIDITY = "середня"  # NTU 10-25 (depends on flood)
    
    # Anthropogenic pollution (city center)
    POLLUTION_FACTOR = 1.2  # Pollution coefficient (1.0 = clean, >1.0 = polluted)
    EUTROPHICATION_LEVEL = "помірна"  # Eutrophication from urban runoff
    
    EMA_ALPHA = 0.3  # Exponential smoothing coefficient for sensor noise (0.1 - very smooth, 1.0 - no smoothing)
    
    # Barometric changes
    BAROMETRIC_CRITICAL_CHANGE = 2.5  # Critical pressure change, mmHg/hour
    
    # ========================================================================
    # WATER PROPERTIES
    # ========================================================================
    
    # Physical properties of water
    WATER_DENSITY = const(1000)  # kg/m³
    WATER_HEAT_CAPACITY = const(4186)  # J/(kg·°C)
    WATER_PRESSURE_PER_METER = const(76)  # mmHg per 1 meter of depth
    
    # Gas exchange in water
    HENRY_CONSTANT_O2 = 1.3e-3  # mol/(L·atm) at 25°C
    O2_DIFFUSION_COEF = 2.0e-9  # m²/s
    
    # Optical properties
    WATER_ALBEDO = 0.06
    LIGHT_EXTINCTION_CLEAR = 0.1  # m⁻¹ for clear water
    LIGHT_EXTINCTION_TURBID = 5.0  # m⁻¹ for turbid water
    
    # ========================================================================
    # BIOLOGICAL CONSTANTS
    # ========================================================================
    
    # Temperature dependence
    Q10_FISH = 2.2  # Van't Hoff temperature coefficient for fish
    
    # Thermal inertia of water bodies
    THERMAL_INERTIA_SHALLOW = 0.15  # Shallow water
    THERMAL_INERTIA_MEDIUM = 0.08   # Medium depth
    THERMAL_INERTIA_DEEP = 0.05     # Deep water
    
    # Wind and aeration
    AERATION_COEFFICIENT = 0.001  # Wind aeration coefficient
    WIND_TURBULENCE_COEF = 0.001  # Wind turbulence coefficient

    # ========================================================================
    # ESP32-S3 HARDWARE CONFIGURATION
    # ========================================================================

    # Display ST7789 (SPI)
    DISPLAY_WIDTH = const(240)   # Pixels (2.0" display)
    DISPLAY_HEIGHT = const(320)  # Pixels (2.0" display, 240×320)
    DISPLAY_SCK = const(14)
    DISPLAY_MOSI = const(13)
    DISPLAY_RST = const(12)
    DISPLAY_DC = const(11)
    DISPLAY_BLK = const(10)  # PWM for brightness
    DISPLAY_CS = const(9)    # Chip Select (optional, not used)
    DISPLAY_ROTATION = 0  # 0, 90, 180, 270
    
    # Display zones (240×320 layout)
    HEADER_HEIGHT = 40    # Top status bar
    BODY_HEIGHT = 240     # Main data area
    FOOTER_HEIGHT = 40    # Bottom forecast

    # Sensors I2C
    SENSOR_SDA = const(4)
    SENSOR_SCL = const(5)
    SENSOR_FREQ = const(100000)  # 100 kHz

    # DHT22 simulation for Wokwi (separate GPIO to avoid I2C conflict)
    DHT22_SIM_PIN = const(6)  # GPIO 6 for DHT22 in Wokwi mode

    # AHT20 (replacing BME280 for humidity!)
    AHT20_ADDRESS = const(0x38)

    # BMP280 (pressure only)
    BMP280_ADDRESS = const(0x76)  # or 0x77

    # DS18B20 (1-Wire temperature sensor)
    DS18B20_PIN = const(15)  # GPIO 15 for 1-Wire bus
    DS18B20_ENABLED = True

    # IR Receiver HX1838 (or compatible VS1838B)
    IR_PIN = const(1)  # RTC GPIO for wake_on_ext0

    # Battery ADC (2×18650 Li-Ion cells in series)
    BAT_ADC_PIN = const(2)
    BAT_VOLTAGE_DIVIDER = 2.0  # 100kΩ/100kΩ voltage divider
    BAT_VOLTAGE_MAX = 8.4      # Fully charged (2×4.2V)
    BAT_VOLTAGE_MIN = 6.0      # Empty (2×3.0V, cutoff)
    BAT_VOLTAGE_NOMINAL = 7.4  # Nominal (2×3.7V)
    BAT_FULL = 8.4             # Alias for backward compatibility
    BAT_EMPTY = 6.0            # Alias for backward compatibility
    
    # Battery thresholds
    BATTERY_LOW_PERCENT = 20    # Show low battery warning
    BATTERY_CRITICAL_PERCENT = 10 # Enter power saving mode

    # ========================================================================
    # DEEP SLEEP CONFIGURATION
    # ========================================================================

    # Wake intervals
    SLEEP_DURATION_NORMAL = const(3600)  # 1 hour (hourly updates)
    SLEEP_DURATION_SHORT = const(300)    # 5 min (for testing)
    SLEEP_DURATION_IR_DISPLAY = const(15)  # 15 sec (after IR wake)
    SLEEP_DURATION_LOW_BATTERY = const(7200) # 2 hours (conserve power)

    # Wake reasons (for detection)
    WAKE_REASON_COLD_BOOT = 0
    WAKE_REASON_TIMER = 1
    WAKE_REASON_IR_REMOTE = 2

    # WiFi settings
    WIFI_SSID = "YOUR_WIFI_SSID"        # Replace with your WiFi name
    WIFI_PASSWORD = "YOUR_WIFI_PASSWORD" # Replace with your WiFi password
    WIFI_TIMEOUT = const(15)             # Connection timeout (seconds)
    WIFI_BURST_MODE = True               # Turn off after API call

    # NTP settings for Vinnytsia
    NTP_SERVER = "ua.pool.ntp.org"
    NTP_TIMEZONE_OFFSET = 2  # UTC+2 (winter) / UTC+3 (summer DST)

    # ========================================================================
    # POWER MANAGEMENT
    # ========================================================================

    # Target current consumption
    CURRENT_DEEPSLEEP = 0.03  # mA (30 µA)
    CURRENT_ACTIVE_AVG = 1.2  # mA (average per hour)
    CURRENT_IR_WAKE = 35.0  # mA (display + sensors, no WiFi)

    # Battery capacity
    BATTERY_CAPACITY = 5400  # mAh (2x 2700 in parallel)
    ESTIMATED_RUNTIME_DAYS = 180  # ~6 months
    
    # ========================================================================
    # BAROMETRIC CONSTANTS
    # ========================================================================
    
    # Standard atmosphere
    PRESSURE_SEA_LEVEL = 1013.25    # hPa (standard sea level pressure)
    TEMPERATURE_STANDARD = 15.0     # °C (ISA standard temperature)
    LAPSE_RATE = 0.0065             # K/m (temperature lapse rate)
    
    # Gas constants (refined values)
    GAS_CONSTANT_DRY_AIR = 287.05   # J/(kg·K)
    GAS_CONSTANT_WATER_VAPOR = 461.5 # J/(kg·K)
    SPECIFIC_HEAT_AIR = 1005.0      # J/(kg·K)
    
    # Gravity
    GRAVITY = 9.80665               # m/s² (standard gravity)
    
    # Molar masses
    MOLAR_MASS_DRY_AIR = 0.0289644  # kg/mol
    MOLAR_MASS_WATER = 0.018016     # kg/mol
    
    # ========================================================================
    # FISHING FORECAST CONSTANTS
    # ========================================================================
    
    # Pressure change thresholds (hPa per hour)
    PRESSURE_CHANGE_STABLE = 0.5    # Stable weather
    PRESSURE_CHANGE_RISING = 1.5    # Rising pressure (good fishing)
    PRESSURE_CHANGE_FALLING = -1.5  # Falling pressure (bad fishing)
    
    # Optimal fishing conditions
    OPTIMAL_TEMP_MIN = 15.0         # °C
    OPTIMAL_TEMP_MAX = 25.0         # °C
    OPTIMAL_PRESSURE_MIN = 1005.0   # hPa
    OPTIMAL_PRESSURE_MAX = 1020.0   # hPa
    OPTIMAL_WIND_MAX = 5.0          # m/s
    
    # Water temperature thresholds (South Bug River, Vinnytsia)
    WATER_TEMP_WINTER = 1.0     # °C (January average)
    WATER_TEMP_SUMMER = 24.0    # °C (July peak)
    WATER_TEMP_FREEZE = 0.0     # °C (ice formation)
    
    # ========================================================================
    # DATA LOGGING
    # ========================================================================
    
    LOG_INTERVAL = const(3600)      # Log data every hour
    MAX_LOG_ENTRIES = const(168)    # 7 days of hourly data
    
    # NVS (Non-Volatile Storage) keys
    NVS_NAMESPACE = "meteocore"
    NVS_KEY_PRESSURE_HISTORY = "press_hist"
    NVS_KEY_BATTERY_CALIBRATION = "bat_cal"
    NVS_KEY_BOOT_COUNT = "boot_count"
    
    # ========================================================================
    # DEBUG CONFIGURATION
    # ========================================================================
    
    DEBUG_MODE = True               # Enable debug logging
    DEBUG_UART_BAUD = 115200        # Serial console baud rate
    
    # Sensor read retries
    SENSOR_READ_RETRIES = 3         # Number of retries for failed reads
    SENSOR_READ_DELAY = 100         # ms between retries
    
    # IR remote commands (customize for your remote!)
    IR_PROTOCOL = "NEC"             # Most common IR protocol
    IR_CMD_WAKE = 0x45              # Power button
    IR_CMD_NEXT = 0x46              # Next screen
    IR_CMD_PREV = 0x47              # Previous screen
    IR_CMD_BRIGHTNESS_UP = 0x48     # Increase brightness
    IR_CMD_BRIGHTNESS_DOWN = 0x49   # Decrease brightness


# For backward compatibility
g = PhysicalConstants.g
R = PhysicalConstants.R
cp = PhysicalConstants.cp
cv = PhysicalConstants.cv
gamma = PhysicalConstants.gamma
L = PhysicalConstants.L
