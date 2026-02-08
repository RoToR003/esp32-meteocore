"""
Display Output Handler for ESP32
================================

Handles output to various display types (OLED, LCD, etc.).
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] DISPLAY: {message}")
    except:
        pass


class Display:
    """
    Base display handler.
    Can be extended for specific display types (SSD1306 OLED, LCD1602, etc.).
    """
    
    def __init__(self, display_type="console"):
        """
        Initialize display.
        
        Args:
            display_type: Type of display ("console", "ssd1306", "lcd1602")
        """
        self.display_type = display_type
        self.display = None
        
        if display_type == "console":
            log("Using console output")
        else:
            log(f"Display type '{display_type}' not yet implemented", "WARNING")
    
    def clear(self):
        """Clear display."""
        if self.display_type == "console":
            print("\n" * 3)
    
    def show_text(self, text, x=0, y=0):
        """
        Show text on display.
        
        Args:
            text: Text to display
            x: X position (column)
            y: Y position (row)
        """
        if self.display_type == "console":
            print(f"{text}")
    
    def show_forecast(self, weather_data, fishing_data=None):
        """
        Display weather and fishing forecast.
        
        Args:
            weather_data: Dictionary with weather information
            fishing_data: Optional dictionary with fishing forecast
        """
        self.clear()
        
        # Weather display
        if 'temperature' in weather_data:
            temp = weather_data['temperature']
            self.show_text(f"Temp: {temp}°C")
        
        if 'pressure' in weather_data:
            press = weather_data['pressure']
            self.show_text(f"Press: {press} hPa")
        
        if 'humidity' in weather_data:
            hum = weather_data['humidity']
            self.show_text(f"Humidity: {hum}%")
        
        if 'forecast' in weather_data:
            forecast = weather_data['forecast']
            self.show_text(f"Forecast: {forecast}")
        
        # Fishing display
        if fishing_data and 'KIAR_percent' in fishing_data:
            kiar = fishing_data['KIAR_percent']
            self.show_text(f"Fish Activity: {kiar}%")
            
            if 'rating' in fishing_data:
                rating = fishing_data['rating']
                self.show_text(f"Rating: {rating}")


class SSD1306Display(Display):
    """
    SSD1306 OLED display driver (128x64 pixels).
    Commonly used with ESP32 via I2C.
    """
    
    def __init__(self, i2c, width=128, height=64, address=0x3C):
        """
        Initialize SSD1306 OLED display.
        
        Args:
            i2c: I2C bus object
            width: Display width in pixels (default 128)
            height: Display height in pixels (default 64)
            address: I2C address (default 0x3C)
        """
        super().__init__("ssd1306")
        
        try:
            import ssd1306
            self.display = ssd1306.SSD1306_I2C(width, height, i2c, address)
            self.width = width
            self.height = height
            log(f"SSD1306 OLED initialized ({width}x{height})")
            self.clear()
        except ImportError:
            log("ssd1306 library not found. Install micropython-ssd1306", "WARNING")
        except Exception as e:
            log(f"Failed to initialize SSD1306: {e}", "ERROR")
    
    def clear(self):
        """Clear OLED display."""
        if self.display:
            try:
                self.display.fill(0)
                self.display.show()
            except Exception as e:
                log(f"Error clearing display: {e}", "ERROR")
    
    def show_text(self, text, x=0, y=0):
        """
        Show text on OLED.
        
        Args:
            text: Text to display
            x: X position in pixels
            y: Y position in pixels
        """
        if self.display:
            try:
                self.display.text(str(text), x, y)
                self.display.show()
            except Exception as e:
                log(f"Error showing text: {e}", "ERROR")
    
    def show_forecast(self, weather_data, fishing_data=None):
        """
        Display weather and fishing forecast on OLED.
        
        Args:
            weather_data: Dictionary with weather information
            fishing_data: Optional dictionary with fishing forecast
        """
        if not self.display:
            return
        
        try:
            self.clear()
            
            line = 0
            
            # Weather data
            if 'temperature' in weather_data:
                temp = weather_data['temperature']
                self.display.text(f"T: {temp:.1f}C", 0, line * 10)
                line += 1
            
            if 'pressure' in weather_data:
                press = weather_data['pressure']
                self.display.text(f"P: {press:.0f}hPa", 0, line * 10)
                line += 1
            
            if 'humidity' in weather_data:
                hum = weather_data['humidity']
                self.display.text(f"H: {hum:.0f}%", 0, line * 10)
                line += 1
            
            # Fishing data
            if fishing_data and 'KIAR_percent' in fishing_data:
                line += 1  # Add spacing
                kiar = fishing_data['KIAR_percent']
                self.display.text(f"Fish: {kiar:.0f}%", 0, line * 10)
                line += 1
                
                if 'rating' in fishing_data:
                    rating = fishing_data['rating']
                    # Truncate long ratings
                    if len(rating) > 16:
                        rating = rating[:13] + "..."
                    self.display.text(rating, 0, line * 10)
            
            self.display.show()
            
        except Exception as e:
            log(f"Error displaying forecast: {e}", "ERROR")


class LCD1602Display(Display):
    """
    LCD1602 display driver (16x2 characters).
    Commonly used with ESP32 via I2C with PCF8574 I/O expander.
    """
    
    def __init__(self, i2c, address=0x27):
        """
        Initialize LCD1602 display.
        
        Args:
            i2c: I2C bus object
            address: I2C address of PCF8574 (default 0x27)
        """
        super().__init__("lcd1602")
        
        try:
            # Try to import LCD library for MicroPython
            from machine import I2C
            from lcd_api import LcdApi
            from i2c_lcd import I2cLcd
            
            self.display = I2cLcd(i2c, address, 2, 16)
            log("LCD1602 initialized")
            self.clear()
        except ImportError:
            log("LCD library not found", "WARNING")
        except Exception as e:
            log(f"Failed to initialize LCD1602: {e}", "ERROR")
    
    def clear(self):
        """Clear LCD display."""
        if self.display:
            try:
                self.display.clear()
            except Exception as e:
                log(f"Error clearing display: {e}", "ERROR")
    
    def show_text(self, text, x=0, y=0):
        """
        Show text on LCD.
        
        Args:
            text: Text to display
            x: X position (column 0-15)
            y: Y position (row 0-1)
        """
        if self.display:
            try:
                self.display.move_to(x, y)
                self.display.putstr(str(text))
            except Exception as e:
                log(f"Error showing text: {e}", "ERROR")
    
    def show_forecast(self, weather_data, fishing_data=None):
        """
        Display weather and fishing forecast on LCD.
        
        Args:
            weather_data: Dictionary with weather information
            fishing_data: Optional dictionary with fishing forecast
        """
        if not self.display:
            return
        
        try:
            self.clear()
            
            # Line 1: Temperature and Pressure
            line1 = ""
            if 'temperature' in weather_data:
                temp = weather_data['temperature']
                line1 += f"{temp:.1f}C "
            if 'pressure' in weather_data:
                press = weather_data['pressure']
                line1 += f"{press:.0f}hPa"
            
            # Line 2: Humidity or Fish Activity
            line2 = ""
            if fishing_data and 'KIAR_percent' in fishing_data:
                kiar = fishing_data['KIAR_percent']
                line2 = f"Fish: {kiar:.0f}%"
            elif 'humidity' in weather_data:
                hum = weather_data['humidity']
                line2 = f"Humidity: {hum:.0f}%"
            
            # Display
            self.show_text(line1[:16], 0, 0)
            self.show_text(line2[:16], 0, 1)
            
        except Exception as e:
            log(f"Error displaying forecast: {e}", "ERROR")
