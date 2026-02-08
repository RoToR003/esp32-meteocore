"""
AHT20 Temperature and Humidity Sensor Driver
=============================================

Replacement for BME280 (humidity part) on ESP32-S3 meteo station.

Features:
- I2C interface (0x38)
- Temperature: -40 to +85°C (±0.3°C)
- Humidity: 0-100% RH (±2%)
- Lower power consumption than BME280
- DHT22 fallback for Wokwi simulation
- MicroPython compatible

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] AHT20: {message}")
    except:
        pass


class AHT20:
    """
    AHT20 sensor driver for MicroPython with DHT22 fallback.
    
    Supports:
    - AHT20 via I2C (real hardware)
    - DHT22 via GPIO (Wokwi simulation)
    - Mock mode (no hardware)
    
    Datasheet: http://www.aosong.com/userfiles/files/media/AHT20%20%E8%8B%B1%E6%96%87%E7%89%88%E8%AF%B4%E6%98%8E%E4%B9%A6.pdf
    """
    
    # I2C Address
    ADDRESS = 0x38
    
    # Commands
    CMD_INIT = bytearray([0xBE, 0x08, 0x00])
    CMD_TRIGGER = bytearray([0xAC, 0x33, 0x00])
    CMD_SOFTRESET = bytearray([0xBA])
    
    def __init__(self, i2c=None, pin=None, address=None):
        """
        Initialize AHT20 sensor with fallback support.
        
        Args:
            i2c: Initialized I2C bus (for AHT20)
            pin: GPIO Pin object (for DHT22 fallback)
            address: I2C address (default 0x38)
        """
        self.sensor_type = None
        self.sensor = None
        self.i2c = i2c
        self.address = address if address is not None else self.ADDRESS
        
        # Try AHT20 first (real hardware)
        if i2c is not None:
            try:
                devices = self.i2c.scan()
                if self.address in devices:
                    self._init_aht20()
                    return
                else:
                    log(f"AHT20 not found at 0x{self.address:02X}, trying DHT22 fallback", "INFO")
            except Exception as e:
                log(f"AHT20 init failed: {e}", "WARNING")
        
        # Try DHT22 fallback (Wokwi simulation)
        if pin is not None:
            try:
                self._init_dht22(pin)
                return
            except Exception as e:
                log(f"DHT22 init failed: {e}", "WARNING")
        
        # No hardware available - use mock
        log("No sensor hardware found, using MOCK mode", "WARNING")
        self.sensor_type = "MOCK"
    
    def _init_aht20(self):
        """Initialize AHT20 sensor."""
        try:
            import time
            time.sleep_ms(40)  # Wait for power-on
        except:
            import time as time_module
            time_module.sleep(0.04)
        
        self._initialize()
        self.sensor_type = "AHT20"
        log(f"AHT20 initialized at address 0x{self.address:02X}")
    
    def _init_dht22(self, pin):
        """
        Initialize DHT22 sensor (fallback for Wokwi).
        
        Args:
            pin: GPIO Pin object (DHT22 library handles pin configuration)
        """
        import dht
        self.sensor = dht.DHT22(pin)
        self.sensor_type = "DHT22"
        log("DHT22 initialized (Wokwi simulation mode)")
    
    def _initialize(self):
        """Initialize sensor (calibration)."""
        self.i2c.writeto(self.address, self.CMD_INIT)
        try:
            import time
            time.sleep_ms(10)
        except:
            import time as time_module
            time_module.sleep(0.01)
    
    def reset(self):
        """Soft reset sensor."""
        self.i2c.writeto(self.address, self.CMD_SOFTRESET)
        try:
            import time
            time.sleep_ms(20)
        except:
            import time as time_module
            time_module.sleep(0.02)
        self._initialize()
        log("AHT20 reset complete")
    
    def read(self):
        """
        Read temperature and humidity.
        
        Returns:
            dict: {'temperature': float, 'humidity': float}
        """
        if self.sensor_type == "AHT20":
            return self._read_aht20()
        elif self.sensor_type == "DHT22":
            return self._read_dht22()
        else:
            return self._read_mock()
    
    def _read_aht20(self):
        """Read from AHT20 sensor."""
        # Trigger measurement
        self.i2c.writeto(self.address, self.CMD_TRIGGER)
        try:
            import time
            time.sleep_ms(80)  # Wait for conversion
        except:
            import time as time_module
            time_module.sleep(0.08)
        
        # Read 6 bytes
        data = self.i2c.readfrom(self.address, 6)
        
        # Check busy bit
        if data[0] & 0x80:
            try:
                import time
                time.sleep_ms(10)
            except:
                import time as time_module
                time_module.sleep(0.01)
            data = self.i2c.readfrom(self.address, 6)
        
        # Parse humidity (20 bits)
        humidity_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        humidity = (humidity_raw / 1048576.0) * 100.0
        
        # Parse temperature (20 bits)
        temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        temperature = (temperature_raw / 1048576.0) * 200.0 - 50.0
        
        return {
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2)
        }
    
    def _read_dht22(self):
        """Read from DHT22 sensor (Wokwi simulation)."""
        try:
            self.sensor.measure()
            temperature = self.sensor.temperature()
            humidity = self.sensor.humidity()
            
            return {
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2)
            }
        except Exception as e:
            log(f"DHT22 read error: {e}", "ERROR")
            # Return mock data on error
            return self._read_mock()
    
    def _read_mock(self):
        """Return mock data (no hardware)."""
        return {
            'temperature': 22.5,
            'humidity': 65.0
        }
    
    def read_temperature(self):
        """Read temperature only (°C)."""
        return self.read()['temperature']
    
    def read_humidity(self):
        """Read humidity only (%)."""
        return self.read()['humidity']
