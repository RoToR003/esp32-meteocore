"""
ESP32 Sensor Drivers
===================

Hardware drivers for BME280, BMP180, and BH1750 sensors.
Compatible with MicroPython on ESP32.
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] SENSORS: {message}")
    except:
        pass


class BME280Sensor:
    """
    Driver for BME280 sensor (temperature, humidity, pressure).
    
    BME280 is a combined digital humidity, pressure and temperature sensor.
    Communication via I2C interface.
    """
    
    def __init__(self, i2c, address=0x76):
        """
        Initialize BME280 sensor.
        
        Args:
            i2c: I2C bus object (machine.I2C)
            address: I2C address (default 0x76, alternative 0x77)
        """
        self.i2c = i2c
        self.address = address
        self._bme = None
        
        try:
            # Try to import BME280 library for MicroPython
            import bme280
            self._bme = bme280.BME280(i2c=i2c, address=address)
            log(f"BME280 initialized at address 0x{address:02x}")
        except ImportError:
            log("BME280 library not found. Install micropython-bme280", "WARNING")
        except Exception as e:
            log(f"Failed to initialize BME280: {e}", "ERROR")
    
    def read(self):
        """
        Read sensor data.
        
        Returns:
            Dictionary with temperature (°C), humidity (%), pressure (hPa)
            Returns None values if sensor not available
        """
        if self._bme is None:
            log("BME280 not initialized", "WARNING")
            return {
                'temperature': None,
                'humidity': None,
                'pressure': None
            }
        
        try:
            # Read raw values
            temp_str, pressure_str, humidity_str = self._bme.values
            
            # Parse values (format: "25.0C", "1013.25hPa", "60.0%")
            temperature = float(temp_str.replace('C', ''))
            pressure = float(pressure_str.replace('hPa', ''))
            humidity = float(humidity_str.replace('%', ''))
            
            return {
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'pressure': round(pressure, 2)
            }
        except Exception as e:
            log(f"Error reading BME280: {e}", "ERROR")
            return {
                'temperature': None,
                'humidity': None,
                'pressure': None
            }
    
    def read_temperature(self):
        """Read temperature only (°C)."""
        data = self.read()
        return data['temperature']
    
    def read_humidity(self):
        """Read humidity only (%)."""
        data = self.read()
        return data['humidity']
    
    def read_pressure(self):
        """Read pressure only (hPa)."""
        data = self.read()
        return data['pressure']


class BMP180Sensor:
    """
    Driver for BMP180 sensor (temperature, pressure).
    
    BMP180 is a digital pressure sensor (no humidity).
    Communication via I2C interface.
    """
    
    def __init__(self, i2c, address=0x77):
        """
        Initialize BMP180 sensor.
        
        Args:
            i2c: I2C bus object (machine.I2C)
            address: I2C address (default 0x77)
        """
        self.i2c = i2c
        self.address = address
        self._bmp = None
        
        try:
            # Try to import BMP180 library for MicroPython
            import bmp180
            self._bmp = bmp180.BMP180(i2c)
            self._bmp.oversample_sett = 2
            log(f"BMP180 initialized at address 0x{address:02x}")
        except ImportError:
            log("BMP180 library not found. Install micropython-bmp180", "WARNING")
        except Exception as e:
            log(f"Failed to initialize BMP180: {e}", "ERROR")
    
    def read(self):
        """
        Read sensor data.
        
        Returns:
            Dictionary with temperature (°C), pressure (hPa), humidity (always None)
        """
        if self._bmp is None:
            log("BMP180 not initialized", "WARNING")
            return {
                'temperature': None,
                'humidity': None,
                'pressure': None
            }
        
        try:
            temperature = self._bmp.temperature
            pressure = self._bmp.pressure / 100.0  # Convert Pa to hPa
            
            return {
                'temperature': round(temperature, 2),
                'humidity': None,  # BMP180 doesn't measure humidity
                'pressure': round(pressure, 2)
            }
        except Exception as e:
            log(f"Error reading BMP180: {e}", "ERROR")
            return {
                'temperature': None,
                'humidity': None,
                'pressure': None
            }
    
    def read_temperature(self):
        """Read temperature only (°C)."""
        data = self.read()
        return data['temperature']
    
    def read_pressure(self):
        """Read pressure only (hPa)."""
        data = self.read()
        return data['pressure']


class LightSensor:
    """
    Driver for BH1750 light sensor (illuminance).
    
    BH1750 is a digital ambient light sensor with I2C interface.
    Measures illuminance in lux (0-65535 lux range).
    """
    
    # BH1750 I2C commands
    POWER_DOWN = 0x00
    POWER_ON = 0x01
    RESET = 0x07
    CONTINUOUS_HIGH_RES_MODE = 0x10
    
    def __init__(self, i2c, address=0x23):
        """
        Initialize BH1750 light sensor.
        
        Args:
            i2c: I2C bus object (machine.I2C)
            address: I2C address (default 0x23, alternative 0x5C)
        """
        self.i2c = i2c
        self.address = address
        
        try:
            # Power on and set to continuous high resolution mode
            self.i2c.writeto(self.address, bytes([self.POWER_ON]))
            self.i2c.writeto(self.address, bytes([self.CONTINUOUS_HIGH_RES_MODE]))
            log(f"BH1750 initialized at address 0x{address:02x}")
        except Exception as e:
            log(f"Failed to initialize BH1750: {e}", "ERROR")
    
    def read_lux(self):
        """
        Read illuminance in lux.
        
        Returns:
            Illuminance in lux (float), or None if error
        """
        try:
            # Read 2 bytes
            data = self.i2c.readfrom(self.address, 2)
            
            # Convert to lux
            # Formula: (high_byte << 8 | low_byte) / 1.2
            lux = ((data[0] << 8) | data[1]) / 1.2
            
            return round(lux, 1)
        except Exception as e:
            log(f"Error reading BH1750: {e}", "ERROR")
            return None
    
    def read(self):
        """
        Read sensor data in standard format.
        
        Returns:
            Dictionary with illuminance (lux)
        """
        return {
            'illuminance': self.read_lux()
        }


class MockSensor:
    """
    Mock sensor for testing without hardware.
    Returns simulated values.
    """
    
    def __init__(self):
        """Initialize mock sensor."""
        log("Mock sensor initialized (for testing only)", "WARNING")
        self._counter = 0
    
    def read(self):
        """
        Return simulated sensor data.
        
        Returns:
            Dictionary with simulated temperature, humidity, pressure
        """
        import math
        
        # Simulate daily temperature variation
        self._counter += 1
        hour_of_day = (self._counter % 24)
        
        # Temperature: 15-25°C with daily cycle
        temperature = 20 + 5 * math.sin(hour_of_day * 3.14159 / 12)
        
        # Humidity: 50-80% with inverse daily cycle
        humidity = 65 - 15 * math.sin(hour_of_day * 3.14159 / 12)
        
        # Pressure: around 1013 hPa with small variations
        pressure = 1013 + 3 * math.sin(hour_of_day * 3.14159 / 24)
        
        return {
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'pressure': round(pressure, 2)
        }
    
    def read_lux(self):
        """Return simulated illuminance."""
        import math
        hour_of_day = (self._counter % 24)
        
        # Daylight: 0 at night, up to 50000 lux at noon
        if 6 <= hour_of_day <= 18:
            lux = 25000 + 25000 * math.sin((hour_of_day - 6) * 3.14159 / 12)
        else:
            lux = 0
        
        return round(lux, 1)
