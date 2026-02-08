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
    
    def __init__(self, width=240, height=240):
        """
        Initialize ST7789 display.
        
        Args:
            width: Display width (240 for 1.28", 240 for 1.69")
            height: Display height (240 for 1.28", 280 for 1.69")
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
            log("Display off")
        except Exception as e:
            log(f"Error turning off display: {e}", "ERROR")
    
    def display_on(self):
        """Wake up display."""
        try:
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
                - forecast: str
                - battery: float (%)
        """
        try:
            if not self.display or not self.st7789:
                log("Display not initialized", "WARNING")
                return
            
            # Clear
            self.clear()
            
            # Battery
            battery = data.get('battery', 0)
            self.display.text(
                f"BAT: {battery:.0f}%",
                10, 10,
                self.st7789.WHITE
            )
            
            # Temperature
            temp = data.get('temperature', 0)
            self.display.text(
                f"T: {temp:.1f}C",
                10, 60,
                self.st7789.YELLOW
            )
            
            # External Temperature (DS18B20)
            y_offset = 90
            if data.get('temperature_external') is not None:
                ext_temp = data['temperature_external']
                self.display.text(
                    f"Out: {ext_temp:.1f}C",
                    10, y_offset,
                    self.st7789.YELLOW
                )
                y_offset += 30
            
            # Humidity
            humidity = data.get('humidity', 0)
            self.display.text(
                f"H: {humidity:.0f}%",
                10, y_offset,
                self.st7789.CYAN
            )
            y_offset += 30
            
            # Pressure
            pressure = data.get('pressure', 0)
            self.display.text(
                f"P: {pressure:.1f}hPa",
                10, y_offset,
                self.st7789.GREEN
            )
            
            # Forecast
            forecast = data.get('forecast', 'N/A')
            # Truncate if too long
            if len(forecast) > 20:
                forecast = forecast[:20]
            y_offset += 50
            self.display.text(
                forecast,
                10, y_offset,
                self.st7789.WHITE
            )
            
            log("Meteo data displayed")
        
        except Exception as e:
            log(f"Error showing meteo data: {e}", "ERROR")
