"""
ST7789 TFT Display Driver for ESP32-S3
=======================================

Optimized for 1.28" and 1.69" round/square displays.

Features:
- SPI interface
- Hardware scrolling
- Low memory usage (no framebuffer)
- PWM backlight control
- MicroPython compatible

Dependencies:
- st7789py library (install: mpremote mip install github:russhughes/st7789py_mpy)

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] DISPLAY: {message}")
    except:
        pass


class MeteoDisplay:
    """
    High-level display manager for meteo station.
    """
    
    def __init__(self, width=240, height=320):
        """
        Initialize ST7789 display.
        
        Args:
            width: Display width (240 for 2.0" display)
            height: Display height (320 for 2.0" display)
        """
        try:
            from machine import Pin, SPI, PWM
            from ..core.constants import PhysicalConstants as PC
            
            # SPI setup
            self.spi = SPI(
                2,  # SPI2
                baudrate=40_000_000,  # 40 MHz
                polarity=0,
                phase=0,
                sck=Pin(PC.DISPLAY_SCK),
                mosi=Pin(PC.DISPLAY_MOSI)
            )
            
            # Display pins
            self.rst = Pin(PC.DISPLAY_RST, Pin.OUT)
            self.dc = Pin(PC.DISPLAY_DC, Pin.OUT)
            
            # Backlight PWM
            self.backlight = PWM(Pin(PC.DISPLAY_BLK), freq=1000)
            
            # Initialize ST7789
            try:
                import st7789
                self.display = st7789.ST7789(
                    self.spi,
                    width,
                    height,
                    reset=self.rst,
                    dc=self.dc,
                    rotation=PC.DISPLAY_ROTATION
                )
                self.st7789 = st7789
                log("ST7789 initialized successfully")
            except ImportError:
                log("st7789 library not found. Display will not work.", "WARNING")
                self.display = None
                self.st7789 = None
            
            self.width = width
            self.height = height
            
            # Clear screen
            if self.display:
                self.clear()
                self.set_brightness(100)
        
        except Exception as e:
            log(f"Error initializing display: {e}", "ERROR")
            self.display = None
            self.st7789 = None
    
    def set_brightness(self, percent):
        """
        Set backlight brightness (0-100%).
        
        Args:
            percent: Brightness level
        """
        try:
            duty = int((percent / 100.0) * 1023)
            self.backlight.duty(duty)
        except Exception as e:
            log(f"Error setting brightness: {e}", "ERROR")
    
    def clear(self):
        """Clear display to black."""
        try:
            if self.display and self.st7789:
                self.display.fill(self.st7789.BLACK)
        except Exception as e:
            log(f"Error clearing display: {e}", "ERROR")
    
    def display_off(self):
        """Turn off display (sleep + backlight off)."""
        try:
            self.set_brightness(0)
            if self.display:
                # Put display in sleep mode (optional, saves power)
                # self.display.sleep_mode(True)  # Uncomment if supported
                pass
            log("Display off")
        except Exception as e:
            log(f"Error turning off display: {e}", "ERROR")
    
    def display_on(self):
        """Wake up display."""
        try:
            if self.display:
                # Wake display from sleep mode
                # self.display.sleep_mode(False)  # Uncomment if supported
                pass
            self.set_brightness(100)
            log("Display on")
        except Exception as e:
            log(f"Error turning on display: {e}", "ERROR")
    
    def show_meteo_data(self, data):
        """
        Display meteorological data on screen.
        
        Args:
            data: Dictionary with keys:
                - temperature: float
                - humidity: float
                - pressure: float (hPa)
                - temperature_water: float (optional)
                - forecast: str
                - fish_activity: str (optional)
                - battery: float (%)
        """
        try:
            if not self.display or not self.st7789:
                log("Display not initialized", "WARNING")
                return
            
            # Clear
            self.clear()
            
            y_offset = 10
            line_height = 30
            
            # Temperature
            if 'temperature' in data:
                temp = data['temperature']
                text = f"Temp: {temp:.1f}C"
                self.display.text(text, 10, y_offset, self.st7789.YELLOW)
                y_offset += line_height
            
            # Humidity
            if 'humidity' in data:
                humidity = data['humidity']
                text = f"Humidity: {humidity:.1f}%"
                self.display.text(text, 10, y_offset, self.st7789.CYAN)
                y_offset += line_height
            
            # Pressure
            if 'pressure_mslp' in data:
                pressure = data['pressure_mslp']
                text = f"Press: {pressure:.1f} hPa"
                self.display.text(text, 10, y_offset, self.st7789.GREEN)
                y_offset += line_height
            elif 'pressure' in data:
                pressure = data['pressure']
                text = f"Press: {pressure:.1f} hPa"
                self.display.text(text, 10, y_offset, self.st7789.GREEN)
                y_offset += line_height
            
            # Water temperature (DS18B20)
            if data.get('temperature_water') is not None:
                water_temp = data['temperature_water']
                text = f"Water: {water_temp:.1f}C"
                self.display.text(text, 10, y_offset, self.st7789.CYAN)
                y_offset += line_height
            elif data.get('temperature_external') is not None:
                # Backward compatibility
                ext_temp = data['temperature_external']
                text = f"Water: {ext_temp:.1f}C"
                self.display.text(text, 10, y_offset, self.st7789.CYAN)
                y_offset += line_height
            
            # Battery
            if 'battery' in data:
                battery = data['battery']
                color = self.st7789.GREEN if battery > 20 else self.st7789.RED
                text = f"Battery: {battery:.0f}%"
                self.display.text(text, 10, y_offset, color)
                y_offset += line_height
            
            # Forecast
            if 'forecast' in data:
                forecast = data['forecast']
                # Truncate if too long
                if len(forecast) > 20:
                    forecast = forecast[:20]
                text = f"Forecast: {forecast}"
                self.display.text(text, 10, y_offset, self.st7789.YELLOW)
                y_offset += line_height
            
            # Fish activity
            if 'fish_activity' in data:
                fish = data['fish_activity']
                text = f"Fish: {fish}"
                self.display.text(text, 10, y_offset, self.st7789.MAGENTA)
            
            log("Meteo data displayed")
        
        except Exception as e:
            log(f"Error showing meteo data: {e}", "ERROR")
