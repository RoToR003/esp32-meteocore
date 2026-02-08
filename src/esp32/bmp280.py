"""
BMP280 Pressure and Temperature Sensor Driver
==============================================

Digital barometric pressure sensor for ESP32-S3 meteo station.

Features:
- I2C interface (0x76 or 0x77)
- Pressure: 300-1100 hPa
- Temperature: -40 to +85°C
- High accuracy pressure measurement
- MicroPython compatible

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] BMP280: {message}")
    except:
        pass


class BMP280Sensor:
    """
    BMP280 sensor driver for MicroPython.
    
    Provides pressure and temperature readings.
    Compatible with existing BME280 interface for drop-in replacement.
    """
    
    def __init__(self, i2c, address=0x76):
        """
        Initialize BMP280 sensor.
        
        Args:
            i2c: I2C bus object (machine.I2C)
            address: I2C address (default 0x76, alternative 0x77)
        """
        self.i2c = i2c
        self.address = address
        self._bmp = None
        
        try:
            # Try to import BMP280 library for MicroPython
            import bmp280
            self._bmp = bmp280.BMP280(i2c=i2c, addr=address)
            log(f"BMP280 initialized at address 0x{address:02x}")
        except ImportError:
            log("BMP280 library not found. Install micropython-bmp280", "WARNING")
        except Exception as e:
            log(f"Failed to initialize BMP280: {e}", "ERROR")
    
    def read(self):
        """
        Read sensor data.
        
        Returns:
            Dictionary with temperature (°C), pressure (hPa), humidity (None)
        """
        if self._bmp is None:
            log("BMP280 not initialized", "WARNING")
            return {
                'temperature': None,
                'humidity': None,
                'pressure': None
            }
        
        try:
            # Read temperature and pressure
            temperature = self._bmp.temperature
            pressure = self._bmp.pressure / 100.0  # Convert Pa to hPa
            
            return {
                'temperature': round(temperature, 2),
                'humidity': None,  # BMP280 doesn't measure humidity
                'pressure': round(pressure, 2)
            }
        except Exception as e:
            log(f"Error reading BMP280: {e}", "ERROR")
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
