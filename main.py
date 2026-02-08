"""
ESP32-S3 Autonomous Meteo Station - Main Script
================================================

Hardware:
- YD-ESP32-S3 (N16R8)
- ST7789 1.28" Display
- AHT20 (Temp/Humidity)
- BMP280 (Pressure)
- DS18B20 (External Temp, 1-Wire)
- HX1838 IR Receiver (VS1838B compatible)
- 2x18650 Battery

Modes:
1. Cold Boot: WiFi sync, NTP, first data
2. Timer Wake: Hourly update (WiFi ON)
3. IR Wake: Display last data (WiFi OFF)

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] MAIN: {message}")
    except:
        pass


def init_hardware():
    """Initialize all hardware components."""
    
    print("=" * 50)
    print("ESP32-S3 METEO STATION - INIT")
    print("=" * 50)
    
    try:
        from machine import I2C, Pin
        from src.core.constants import PhysicalConstants as PC
        from src.core.wokwi_detect import get_environment, log_environment
        from src.esp32.power_manager import PowerManager
        from src.esp32.aht20 import AHT20
        from src.esp32.bmp280 import BMP280Sensor
        from src.esp32.display_wrapper import get_display
        from src.esp32.st7789_display_enhanced import MeteoDisplayEnhanced
        from src.esp32.ds18b20 import DS18B20
        from src.esp32.pressure_history import PressureHistory
        
        # Detect environment (Wokwi vs hardware)
        env = get_environment()
        log_environment()
        
        # I2C bus
        i2c = I2C(
            0,
            scl=Pin(PC.SENSOR_SCL),
            sda=Pin(PC.SENSOR_SDA),
            freq=PC.SENSOR_FREQ
        )
        
        log(f"I2C devices found: {[hex(x) for x in i2c.scan()]}")
        
        # Sensors - with DHT22 fallback for Wokwi
        if env['platform'] == 'wokwi':
            # Wokwi: Use DHT22 on I2C pins as AHT20 simulation
            log("Wokwi mode: Using DHT22 for AHT20 simulation")
            aht20_pin = Pin(PC.SENSOR_SDA)  # DHT22 connected to SDA pin
            aht20 = AHT20(i2c=i2c, pin=aht20_pin)
        else:
            # Real hardware: Use AHT20
            aht20 = AHT20(i2c=i2c)
        
        bmp280 = BMP280Sensor(i2c)
        
        # DS18B20 external temperature sensor
        ds18b20 = None
        if PC.DS18B20_ENABLED:
            try:
                ds18b20 = DS18B20(Pin(PC.DS18B20_PIN))
                log("DS18B20 external temperature sensor initialized")
            except Exception as e:
                log(f"DS18B20 init failed: {e}", "WARNING")
        
        # Display - auto-detect ST7789/ILI9341/Mock
        display_driver = get_display(width=PC.DISPLAY_WIDTH, height=PC.DISPLAY_HEIGHT)
        display = MeteoDisplayEnhanced(display_driver, PC.DISPLAY_WIDTH, PC.DISPLAY_HEIGHT)
        
        # Power manager
        power = PowerManager()
        
        # Pressure history
        pressure_history = PressureHistory(max_size=24)
        pressure_history.load_from_nvs()  # Load from NVS if available
        
        return {
            'i2c': i2c,
            'aht20': aht20,
            'bmp280': bmp280,
            'ds18b20': ds18b20,
            'display': display,
            'power': power,
            'pressure_history': pressure_history,
            'environment': env
        }
    except Exception as e:
        log(f"Error initializing hardware: {e}", "ERROR")
        import sys
        sys.print_exception(e)
        return None


def read_sensors(hw):
    """Read all sensors and return data."""
    
    try:
        from src.meteo.barometric import adjust_pressure_to_sea_level_precise
        from src.core.constants import PhysicalConstants as PC
        import time
        
        # AHT20 (temp + humidity)
        aht_data = hw['aht20'].read()
        
        # BMP280 (pressure + temp)
        bmp_data = hw['bmp280'].read()
        
        # Average temperature from both sensors
        temp_avg = (aht_data['temperature'] + bmp_data['temperature']) / 2
        
        # Water temperature (DS18B20) - for fishing forecast!
        water_temp = None
        if hw.get('ds18b20'):
            try:
                ext_data = hw['ds18b20'].read()
                water_temp = ext_data.get('temperature_external')
                log(f"DS18B20 Water: {water_temp}°C")
            except Exception as e:
                log(f"DS18B20 read error: {e}", "WARNING")
        
        # Precise MSLP calculation
        pressure_mslp = adjust_pressure_to_sea_level_precise(
            bmp_data['pressure'],
            temp_avg,
            aht_data['humidity'],
            elevation=PC.ELEVATION
        )
        
        # Add to pressure history
        if hw.get('pressure_history'):
            hw['pressure_history'].add(pressure_mslp, time.time())
            hw['pressure_history'].save_to_nvs()
            log(f"Pressure history: {hw['pressure_history']}")
        
        # Battery
        battery_percent = hw['power'].get_battery_percent()
        
        return {
            'temperature': temp_avg,
            'humidity': aht_data['humidity'],
            'pressure_station': bmp_data['pressure'],
            'pressure_mslp': pressure_mslp,
            'pressure_trend': hw.get('pressure_history').get_trend() if hw.get('pressure_history') else 0,
            'temperature_water': water_temp,  # Renamed from temperature_external
            'battery': battery_percent,
            'timestamp': time.time()
        }
    except Exception as e:
        log(f"Error reading sensors: {e}", "ERROR")
        return None


def mode_cold_boot(hw):
    """Cold boot mode: Full initialization with WiFi."""
    
    log("COLD BOOT MODE")
    
    try:
        import time
        from src.core.constants import PhysicalConstants as PC
        
        # Show "Booting..." on display
        hw['display'].clear()
        hw['display'].display.text("METEO STATION", 60, 140, 0xFFFF)
        hw['display'].display.text("Booting...", 70, 160, 0x07E0)
        
        # Read sensors
        data = read_sensors(hw)
        
        if data:
            # WiFi burst: Sync time + weather
            def wifi_task():
                try:
                    # NTP sync (ntptime uses ua.pool.ntp.org by default for Ukraine)
                    import ntptime
                    ntptime.settime()
                    log(f"NTP time synced: {time.localtime()}")
                    
                    # Get weather forecast (optional, if API available)
                    # from src.api.weather_api import VinnytsiaWeatherAPI
                    # api = VinnytsiaWeatherAPI()
                    # api_data = api.get_current_data()
                    
                    return {'synced': True}
                except Exception as e:
                    log(f"WiFi task error: {e}", "ERROR")
                    return None
            
            api_data = hw['power'].wifi_burst(wifi_task, timeout=15)
            
            # Display data with enhanced display
            display_data = {
                **data,
                'forecast': 'Initialized',
                'fish_activity': 'Unknown'
            }
            
            hw['display'].show_data(display_data, hw.get('pressure_history'))
            time.sleep(5)
        
        # Enter deep sleep (1 hour)
        hw['display'].display_off()
        hw['power'].enter_deep_sleep(PC.SLEEP_DURATION_NORMAL)
        
    except Exception as e:
        log(f"Error in cold boot mode: {e}", "ERROR")
        import sys
        sys.print_exception(e)


def mode_timer_wake(hw):
    """Timer wake mode: Hourly update with WiFi."""
    
    log("TIMER WAKE MODE (Hourly)")
    
    try:
        import time
        from src.core.constants import PhysicalConstants as PC
        
        # Read sensors
        data = read_sensors(hw)
        
        if data:
            # WiFi burst: Update weather
            def wifi_task():
                try:
                    # Get weather forecast (optional)
                    # from src.api.weather_api import VinnytsiaWeatherAPI
                    # api = VinnytsiaWeatherAPI()
                    # api_data = api.get_current_data()
                    
                    return {'updated': True}
                except Exception as e:
                    log(f"WiFi task error: {e}", "ERROR")
                    return None
            
            api_data = hw['power'].wifi_burst(wifi_task, timeout=10)
            
            # Display with enhanced display
            hw['display'].display_on()
            display_data = {
                **data,
                'forecast': 'Updated',
                'fish_activity': 'Good'
            }
            hw['display'].show_data(display_data, hw.get('pressure_history'))
            time.sleep(5)
        
        # Sleep
        hw['display'].display_off()
        hw['power'].enter_deep_sleep(PC.SLEEP_DURATION_NORMAL)
        
    except Exception as e:
        log(f"Error in timer wake mode: {e}", "ERROR")
        import sys
        sys.print_exception(e)


def mode_ir_wake(hw):
    """IR wake mode: Display without WiFi."""
    
    log("IR WAKE MODE (Display Only)")
    
    try:
        import time
        from src.core.constants import PhysicalConstants as PC
        
        # Read sensors (local only)
        data = read_sensors(hw)
        
        if data:
            # Display with enhanced display
            hw['display'].display_on()
            display_data = {
                **data,
                'forecast': 'Cached',
                'fish_activity': 'Cached'
            }
            hw['display'].show_data(display_data, hw.get('pressure_history'))
            
            # Keep display on for 15 sec
            time.sleep(PC.SLEEP_DURATION_IR_DISPLAY)
        
        # Sleep
        hw['display'].display_off()
        hw['power'].enter_deep_sleep(PC.SLEEP_DURATION_NORMAL)
        
    except Exception as e:
        log(f"Error in IR wake mode: {e}", "ERROR")
        import sys
        sys.print_exception(e)


def main():
    """Main entry point."""
    
    try:
        import machine
        
        # Initialize hardware
        hw = init_hardware()
        
        if not hw:
            log("Hardware initialization failed", "ERROR")
            # Emergency sleep (prevent boot loop)
            machine.deepsleep(60000)  # 1 min
            return
        
        # Detect wake reason
        wake_reason = hw['power'].wake_reason
        
        log(f"Wake reason: {wake_reason}")
        
        # Route to appropriate mode
        if wake_reason == 0:  # Cold boot
            mode_cold_boot(hw)
        
        elif wake_reason == 1:  # Timer wake
            mode_timer_wake(hw)
        
        elif wake_reason == 2:  # IR wake
            mode_ir_wake(hw)
    
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        import sys
        sys.print_exception(e)
        
        # Emergency sleep (prevent boot loop)
        try:
            import machine
            machine.deepsleep(60000)  # 1 min
        except:
            pass


# Run
if __name__ == "__main__":
    main()
