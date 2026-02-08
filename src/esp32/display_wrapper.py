"""
Display Wrapper - Unified Interface for ST7789 and ILI9341
===========================================================

Provides a single interface that works with:
- ST7789 (real hardware)
- ILI9341 (Wokwi simulation)
- Mock display (fallback for testing)

Auto-detects available display driver and creates appropriate instance.

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] DISPLAY_WRAPPER: {message}")
    except:
        pass


def draw_circle_bresenham(display, x0, y0, radius, color, fill=False):
    """
    Draw circle using Bresenham's algorithm.
    
    Helper function used by both ST7789 and ILI9341 displays.
    
    Args:
        display: Display object with line() and pixel() methods
        x0, y0: Center coordinates
        radius: Circle radius
        color: Color value
        fill: Whether to fill the circle
    """
    x = radius
    y = 0
    err = 0
    
    while x >= y:
        if fill:
            display.line(x0 - x, y0 + y, x0 + x, y0 + y, color)
            display.line(x0 - x, y0 - y, x0 + x, y0 - y, color)
            display.line(x0 - y, y0 + x, x0 + y, y0 + x, color)
            display.line(x0 - y, y0 - x, x0 + y, y0 - x, color)
        else:
            display.pixel(x0 + x, y0 + y, color)
            display.pixel(x0 + y, y0 + x, color)
            display.pixel(x0 - y, y0 + x, color)
            display.pixel(x0 - x, y0 + y, color)
            display.pixel(x0 - x, y0 - y, color)
            display.pixel(x0 - y, y0 - x, color)
            display.pixel(x0 + y, y0 - x, color)
            display.pixel(x0 + x, y0 - y, color)
        
        y += 1
        err += 1 + 2*y
        if 2*(err-x) + 1 > 0:
            x -= 1
            err += 1 - 2*x


class DisplayInterface:
    """
    Base interface for all display implementations.
    Defines common methods that all displays must support.
    """
    
    def fill(self, color):
        """Fill entire display with color."""
        raise NotImplementedError
    
    def pixel(self, x, y, color):
        """Set a single pixel."""
        raise NotImplementedError
    
    def line(self, x1, y1, x2, y2, color):
        """Draw a line."""
        raise NotImplementedError
    
    def rect(self, x, y, w, h, color):
        """Draw a rectangle outline."""
        raise NotImplementedError
    
    def fill_rect(self, x, y, w, h, color):
        """Draw a filled rectangle."""
        raise NotImplementedError
    
    def circle(self, x, y, r, color, fill=False):
        """Draw a circle."""
        raise NotImplementedError
    
    def text(self, text, x, y, color):
        """Draw text."""
        raise NotImplementedError
    
    def show(self):
        """Update display (for buffered displays)."""
        pass


class ST7789Display(DisplayInterface):
    """
    ST7789 display wrapper for real hardware.
    """
    
    def __init__(self, width, height):
        """Initialize ST7789 display."""
        from machine import Pin, SPI, PWM
        from ..core.constants import PhysicalConstants as PC
        import st7789
        
        # SPI setup
        self.spi = SPI(
            2,
            baudrate=40_000_000,
            polarity=0,
            phase=0,
            sck=Pin(PC.DISPLAY_SCK),
            mosi=Pin(PC.DISPLAY_MOSI)
        )
        
        # Display pins
        rst = Pin(PC.DISPLAY_RST, Pin.OUT)
        dc = Pin(PC.DISPLAY_DC, Pin.OUT)
        
        # Backlight PWM
        self.backlight = PWM(Pin(PC.DISPLAY_BLK), freq=1000)
        
        # Initialize display
        self.display = st7789.ST7789(
            self.spi,
            width,
            height,
            reset=rst,
            dc=dc,
            rotation=PC.DISPLAY_ROTATION
        )
        
        self.st7789 = st7789
        self.width = width
        self.height = height
        
        log("ST7789 display initialized")
    
    def fill(self, color):
        self.display.fill(color)
    
    def pixel(self, x, y, color):
        self.display.pixel(x, y, color)
    
    def line(self, x1, y1, x2, y2, color):
        self.display.line(x1, y1, x2, y2, color)
    
    def rect(self, x, y, w, h, color):
        self.display.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        self.display.fill_rect(x, y, w, h, color)
    
    def circle(self, x, y, r, color, fill=False):
        # ST7789 might not have circle method, use helper
        if hasattr(self.display, 'circle'):
            self.display.circle(x, y, r, color, fill)
        else:
            draw_circle_bresenham(self.display, x, y, r, color, fill)
    
    def text(self, text, x, y, color):
        self.display.text(text, x, y, color)
    
    def set_brightness(self, percent):
        """Set backlight brightness (0-100%)."""
        duty = int((percent / 100.0) * 1023)
        self.backlight.duty(duty)


class ILI9341Display(DisplayInterface):
    """
    ILI9341 display wrapper for Wokwi simulation.
    """
    
    def __init__(self, width, height):
        """Initialize ILI9341 display."""
        from machine import Pin, SPI
        from ..core.constants import PhysicalConstants as PC
        import ili9341
        
        # SPI setup
        self.spi = SPI(
            2,
            baudrate=40_000_000,
            polarity=0,
            phase=0,
            sck=Pin(PC.DISPLAY_SCK),
            mosi=Pin(PC.DISPLAY_MOSI)
        )
        
        # Display pins
        rst = Pin(PC.DISPLAY_RST, Pin.OUT)
        dc = Pin(PC.DISPLAY_DC, Pin.OUT)
        cs = Pin(PC.DISPLAY_CS, Pin.OUT) if hasattr(PC, 'DISPLAY_CS') else None
        
        # Initialize display
        if cs:
            self.display = ili9341.ILI9341(
                self.spi,
                width,
                height,
                reset=rst,
                dc=dc,
                cs=cs,
                rotation=PC.DISPLAY_ROTATION
            )
        else:
            self.display = ili9341.ILI9341(
                self.spi,
                width,
                height,
                reset=rst,
                dc=dc,
                rotation=PC.DISPLAY_ROTATION
            )
        
        self.ili9341 = ili9341
        self.width = width
        self.height = height
        
        # Try backlight if available
        try:
            from machine import PWM
            self.backlight = PWM(Pin(PC.DISPLAY_BLK), freq=1000)
        except:
            self.backlight = None
        
        log("ILI9341 display initialized (Wokwi)")
    
    def fill(self, color):
        self.display.fill(color)
    
    def pixel(self, x, y, color):
        self.display.pixel(x, y, color)
    
    def line(self, x1, y1, x2, y2, color):
        self.display.line(x1, y1, x2, y2, color)
    
    def rect(self, x, y, w, h, color):
        self.display.rect(x, y, w, h, color)
    
    def fill_rect(self, x, y, w, h, color):
        self.display.fill_rect(x, y, w, h, color)
    
    def circle(self, x, y, r, color, fill=False):
        if hasattr(self.display, 'circle'):
            self.display.circle(x, y, r, color, fill)
        else:
            draw_circle_bresenham(self.display, x, y, r, color, fill)
    
    def text(self, text, x, y, color):
        self.display.text(text, x, y, color)
    
    def set_brightness(self, percent):
        """Set backlight brightness (0-100%)."""
        if self.backlight:
            duty = int((percent / 100.0) * 1023)
            self.backlight.duty(duty)


class MockDisplay(DisplayInterface):
    """
    Mock display for testing without hardware.
    Just logs operations.
    """
    
    def __init__(self, width, height):
        """Initialize mock display."""
        self.width = width
        self.height = height
        log("Mock display initialized (no hardware)")
    
    def fill(self, color):
        pass
    
    def pixel(self, x, y, color):
        pass
    
    def line(self, x1, y1, x2, y2, color):
        pass
    
    def rect(self, x, y, w, h, color):
        pass
    
    def fill_rect(self, x, y, w, h, color):
        pass
    
    def circle(self, x, y, r, color, fill=False):
        pass
    
    def text(self, text, x, y, color):
        log(f"TEXT: '{text}' at ({x}, {y})")
    
    def set_brightness(self, percent):
        log(f"BRIGHTNESS: {percent}%")


def get_display(width=240, height=320):
    """
    Auto-detect and initialize display.
    
    Tries in order:
    1. ST7789 (real hardware)
    2. ILI9341 (Wokwi simulation)
    3. Mock display (fallback)
    
    Args:
        width: Display width in pixels
        height: Display height in pixels
    
    Returns:
        DisplayInterface: Initialized display instance
    """
    # Try ST7789 first (real hardware)
    try:
        import st7789
        log("Found st7789 library, using ST7789 display")
        return ST7789Display(width, height)
    except ImportError:
        log("st7789 not available", "DEBUG")
    except Exception as e:
        log(f"ST7789 init failed: {e}", "WARNING")
    
    # Try ILI9341 (Wokwi)
    try:
        import ili9341
        log("Found ili9341 library, using ILI9341 display (Wokwi)")
        return ILI9341Display(width, height)
    except ImportError:
        log("ili9341 not available", "DEBUG")
    except Exception as e:
        log(f"ILI9341 init failed: {e}", "WARNING")
    
    # Fallback to mock
    log("No display hardware found, using mock display", "WARNING")
    return MockDisplay(width, height)
