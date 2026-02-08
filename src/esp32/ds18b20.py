"""
DS18B20 Temperature Sensor Driver
==================================

External temperature sensor using 1-Wire protocol.

Features:
- 1-Wire interface (GPIO 15)
- Temperature: -55 to +125°C (±0.5°C)
- Unique 64-bit ROM ID for multiple sensors
- MicroPython compatible

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] DS18B20: {message}")
    except:
        pass


class DS18B20:
    """
    DS18B20 sensor driver for MicroPython.
    
    Provides external temperature readings via 1-Wire protocol.
    """
    
    def __init__(self, pin):
        """
        Initialize DS18B20 sensor.
        
        Args:
            pin: GPIO Pin object configured for 1-Wire bus
        """
        self.pin = pin
        self.ow = None
        self.ds = None
        self.roms = []
        
        try:
            # Import 1-Wire libraries
            import onewire
            import ds18x20
            
            # Initialize 1-Wire bus
            self.ow = onewire.OneWire(self.pin)
            self.ds = ds18x20.DS18X20(self.ow)
            
            # Scan for devices
            self.roms = self.ds.scan()
            
            if not self.roms:
                log("No DS18B20 sensors found on 1-Wire bus", "WARNING")
                raise RuntimeError("No DS18B20 sensors found")
            
            log(f"Found {len(self.roms)} DS18B20 sensor(s)")
            for i, rom in enumerate(self.roms):
                rom_id = ''.join('%02X' % b for b in rom)
                log(f"Sensor {i}: {rom_id}")
            
        except ImportError as e:
            log(f"Failed to import 1-Wire libraries: {e}", "ERROR")
            raise
        except Exception as e:
            log(f"Failed to initialize DS18B20: {e}", "ERROR")
            raise
    
    def read(self):
        """
        Read temperature from DS18B20 sensor.
        
        Returns:
            dict: {'temperature_external': float, 'sensor_id': str}
        
        Raises:
            RuntimeError: If sensor not initialized or read fails
        """
        if not self.ds or not self.roms:
            log("DS18B20 not initialized", "ERROR")
            raise RuntimeError("DS18B20 not initialized")
        
        try:
            # Convert temperature (initiate conversion)
            self.ds.convert_temp()
            
            # Wait for conversion (750ms for 12-bit resolution)
            try:
                import time
                time.sleep_ms(750)
            except:
                import time as time_module
                time_module.sleep(0.75)
            
            # Read temperature from first sensor
            rom = self.roms[0]
            temperature = self.ds.read_temp(rom)
            
            # Format ROM ID as hex string
            rom_id = ''.join('%02X' % b for b in rom)
            
            return {
                'temperature_external': round(temperature, 2),
                'sensor_id': rom_id
            }
            
        except Exception as e:
            log(f"Error reading DS18B20: {e}", "ERROR")
            raise RuntimeError(f"Failed to read DS18B20: {e}")
    
    def read_temperature(self):
        """Read temperature only (°C)."""
        data = self.read()
        return data['temperature_external']
    
    def get_sensor_count(self):
        """Get number of connected DS18B20 sensors."""
        return len(self.roms)
    
    def read_all(self):
        """
        Read temperature from all connected sensors.
        
        Returns:
            list: List of dicts with temperature and sensor_id for each sensor
        """
        if not self.ds or not self.roms:
            log("DS18B20 not initialized", "ERROR")
            raise RuntimeError("DS18B20 not initialized")
        
        try:
            # Convert temperature for all sensors
            self.ds.convert_temp()
            
            # Wait for conversion
            try:
                import time
                time.sleep_ms(750)
            except:
                import time as time_module
                time_module.sleep(0.75)
            
            # Read all sensors
            results = []
            for rom in self.roms:
                temperature = self.ds.read_temp(rom)
                rom_id = ''.join('%02X' % b for b in rom)
                results.append({
                    'temperature_external': round(temperature, 2),
                    'sensor_id': rom_id
                })
            
            return results
            
        except Exception as e:
            log(f"Error reading DS18B20 sensors: {e}", "ERROR")
            raise RuntimeError(f"Failed to read DS18B20 sensors: {e}")
