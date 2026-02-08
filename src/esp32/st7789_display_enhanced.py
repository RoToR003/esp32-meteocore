"""
Enhanced MeteoDisplay - Multi-Screen Display Manager
====================================================

Provides advanced display features:
- 4 screens: Main, Details, Pressure Graph, Fishing Forecast
- Header/Body/Footer layout
- Large vector fonts for temperature
- Weather icons
- Progress bars
- Pressure graphs

Uses display_wrapper for hardware abstraction.

Author: ESP32-MeteoCore Project
"""

from .fonts import draw_temperature, draw_large_number, FONT_LARGE
from .graphics import GraphicsHelper, get_color_for_battery, get_color_for_temperature


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] DISPLAY_ENHANCED: {message}")
    except:
        pass


# RGB565 Colors
COLOR_BLACK = 0x0000
COLOR_WHITE = 0xFFFF
COLOR_RED = 0xF800
COLOR_GREEN = 0x07E0
COLOR_BLUE = 0x001F
COLOR_YELLOW = 0xFFE0
COLOR_CYAN = 0x07FF
COLOR_MAGENTA = 0xF81F
COLOR_ORANGE = 0xFC00
COLOR_GRAY = 0x8410
COLOR_DARK_BLUE = 0x0010


class MeteoDisplayEnhanced:
    """
    Enhanced multi-screen display manager.
    
    Screens:
    1. Main - Temperature, humidity, pressure with large fonts
    2. Details - Extended data (dew point, external temp, altitude)
    3. Pressure Graph - 24-hour pressure trend
    4. Fishing - Fishing forecast with KIAR%
    """
    
    def __init__(self, display, width=240, height=320):
        """
        Initialize enhanced display.
        
        Args:
            display: Display wrapper instance (from display_wrapper)
            width: Display width
            height: Display height
        """
        self.display = display
        self.width = width
        self.height = height
        
        # Layout zones
        self.header_height = 40
        self.footer_height = 40
        self.body_height = height - self.header_height - self.footer_height
        
        # Current screen
        self.current_screen = 0  # 0=Main, 1=Details, 2=Graph, 3=Fishing
        self.screen_count = 4
        
        # Graphics helper
        self.graphics = GraphicsHelper()
        
        # Brightness
        self.brightness = 100
        
        log(f"Enhanced display initialized: {width}x{height}")
    
    def clear(self, color=COLOR_BLACK):
        """Clear entire display."""
        self.display.fill(color)
    
    def draw_header(self, title, battery_percent=None):
        """
        Draw header section.
        
        Args:
            title: Header title text
            battery_percent: Battery percentage (optional)
        """
        # Background
        self.display.fill_rect(0, 0, self.width, self.header_height, COLOR_DARK_BLUE)
        
        # Title
        self.display.text(title, 10, 12, COLOR_WHITE)
        
        # Battery indicator
        if battery_percent is not None:
            battery_color = get_color_for_battery(battery_percent)
            battery_x = self.width - 50
            battery_y = 10
            self.graphics.draw_battery(
                self.display, battery_x, battery_y, 40, 20, 
                battery_percent, battery_color
            )
    
    def draw_footer(self, text, page_indicator=True):
        """
        Draw footer section.
        
        Args:
            text: Footer text
            page_indicator: Show page indicator dots
        """
        footer_y = self.height - self.footer_height
        
        # Background
        self.display.fill_rect(0, footer_y, self.width, self.footer_height, COLOR_DARK_BLUE)
        
        # Text
        self.display.text(text, 10, footer_y + 12, COLOR_WHITE)
        
        # Page indicator
        if page_indicator:
            indicator_x = self.width - 60
            indicator_y = footer_y + 18
            dot_spacing = 12
            
            for i in range(self.screen_count):
                dot_color = COLOR_WHITE if i == self.current_screen else COLOR_GRAY
                self.display.fill_rect(
                    indicator_x + i * dot_spacing, indicator_y,
                    8, 8, dot_color
                )
    
    def show_main_screen(self, data):
        """
        Display main screen with large temperature.
        
        Args:
            data: Dict with keys: temperature, humidity, pressure_mslp, battery
        """
        # Clear
        self.clear()
        
        # Header
        self.draw_header("METEO STATION", data.get('battery'))
        
        # Body area
        body_y = self.header_height
        
        # Large temperature in center
        temp = data.get('temperature', 0)
        temp_color = get_color_for_temperature(temp)
        
        # Draw temperature (centered)
        temp_scale = 4
        temp_y = body_y + 40
        temp_x = (self.width - 100) // 2  # Approximate centering
        draw_temperature(self.display, temp, temp_x, temp_y, temp_scale, temp_color)
        
        # Weather icon below temperature
        icon_y = temp_y + 80
        icon_x = self.width // 2
        
        # Simple weather determination
        humidity = data.get('humidity', 50)
        if humidity > 80:
            # Rainy
            cloud_x = icon_x - 20
            self.graphics.draw_cloud(self.display, cloud_x, icon_y, 40, COLOR_GRAY)
            self.graphics.draw_rain(self.display, cloud_x, icon_y + 20, 40, 20, 3, COLOR_CYAN)
        elif humidity > 60:
            # Cloudy
            self.graphics.draw_cloud(self.display, icon_x - 20, icon_y, 40, COLOR_GRAY)
        else:
            # Sunny
            self.graphics.draw_sun(self.display, icon_x, icon_y + 10, 12, COLOR_YELLOW)
        
        # Humidity and pressure below
        info_y = icon_y + 50
        
        # Humidity
        humidity_text = f"Humidity: {humidity:.0f}%"
        self.display.text(humidity_text, 20, info_y, COLOR_CYAN)
        
        # Pressure
        pressure = data.get('pressure_mslp', 1013)
        pressure_text = f"Pressure: {pressure:.0f} hPa"
        self.display.text(pressure_text, 20, info_y + 20, COLOR_GREEN)
        
        # Pressure trend
        trend = data.get('pressure_trend', 0)
        trend_text = "Trend: "
        if trend > 1:
            trend_text += "Rising"
            trend_direction = 'up'
        elif trend < -1:
            trend_text += "Falling"
            trend_direction = 'down'
        else:
            trend_text += "Stable"
            trend_direction = 'flat'
        
        self.display.text(trend_text, 20, info_y + 40, COLOR_YELLOW)
        
        # Draw trend arrow
        arrow_x = 180
        arrow_y = info_y + 45
        self.graphics.draw_trend_arrow(
            self.display, arrow_x, arrow_y, 6, trend_direction, COLOR_YELLOW
        )
        
        # Footer
        forecast = data.get('forecast', 'Unknown')
        self.draw_footer(forecast)
        
        log("Main screen displayed")
    
    def show_details_screen(self, data):
        """
        Display details screen with extended data.
        
        Args:
            data: Dict with extended sensor data
        """
        # Clear
        self.clear()
        
        # Header
        self.draw_header("DETAILS", data.get('battery'))
        
        # Body
        y = self.header_height + 20
        line_height = 25
        
        # Temperature (both sensors)
        temp = data.get('temperature', 0)
        self.display.text(f"Air Temp: {temp:.1f}C", 20, y, COLOR_YELLOW)
        y += line_height
        
        # External temperature
        if 'temperature_water' in data and data['temperature_water'] is not None:
            ext_temp = data['temperature_water']
            self.display.text(f"Water Temp: {ext_temp:.1f}C", 20, y, COLOR_CYAN)
            y += line_height
        
        # Dew point (calculate using simplified approximation)
        # Note: This is a basic approximation accurate to ±1°C
        # For better accuracy, use Magnus formula: Td = (b*α)/(a-α) where α = ln(RH/100) + aT/(b+T)
        humidity = data.get('humidity', 50)
        dew_point = temp - ((100 - humidity) / 5.0)  # Simple approximation
        self.display.text(f"Dew Point: {dew_point:.1f}C", 20, y, COLOR_CYAN)
        y += line_height
        
        # Station pressure
        if 'pressure_station' in data:
            station_p = data['pressure_station']
            self.display.text(f"Station P: {station_p:.1f} hPa", 20, y, COLOR_GREEN)
            y += line_height
        
        # MSLP
        pressure = data.get('pressure_mslp', 1013)
        self.display.text(f"MSLP: {pressure:.1f} hPa", 20, y, COLOR_GREEN)
        y += line_height
        
        # Altitude (calculated from pressure)
        altitude = 44330 * (1 - (data.get('pressure_station', 1013) / 1013.25) ** 0.1903)
        self.display.text(f"Altitude: {altitude:.0f} m", 20, y, COLOR_MAGENTA)
        y += line_height
        
        # Timestamp
        if 'timestamp' in data:
            import time
            try:
                t = time.localtime(data['timestamp'])
                time_str = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
                self.display.text(f"Time: {time_str}", 20, y, COLOR_GRAY)
            except:
                pass
        
        # Footer
        self.draw_footer("Extended Data")
        
        log("Details screen displayed")
    
    def show_pressure_graph_screen(self, data, pressure_history):
        """
        Display pressure graph screen.
        
        Args:
            data: Current data dict
            pressure_history: PressureHistory instance
        """
        # Clear
        self.clear()
        
        # Header
        self.draw_header("PRESSURE TREND", data.get('battery'))
        
        # Body
        graph_margin = 20
        graph_x = graph_margin
        graph_y = self.header_height + 40
        graph_width = self.width - 2 * graph_margin
        graph_height = 120
        
        # Get pressure data
        if pressure_history and len(pressure_history) > 0:
            history_values = pressure_history.get_pressures()
            
            # Draw graph
            self.graphics.draw_pressure_graph(
                self.display,
                graph_x, graph_y,
                graph_width, graph_height,
                history_values,
                COLOR_YELLOW,
                COLOR_BLACK
            )
            
            # Show min/max
            min_p, max_p = pressure_history.get_min_max()
            if min_p and max_p:
                info_y = graph_y + graph_height + 20
                self.display.text(f"Min: {min_p:.1f} hPa", graph_x, info_y, COLOR_CYAN)
                self.display.text(f"Max: {max_p:.1f} hPa", graph_x, info_y + 20, COLOR_CYAN)
                
                # Current
                current_p = history_values[-1] if history_values else 0
                self.display.text(f"Now: {current_p:.1f} hPa", graph_x, info_y + 40, COLOR_GREEN)
                
                # Trend
                trend = pressure_history.get_trend()
                trend_text = f"3h: {trend:+.1f} hPa"
                self.display.text(trend_text, graph_x, info_y + 60, COLOR_YELLOW)
        else:
            # No data
            no_data_y = graph_y + graph_height // 2
            self.display.text("No pressure history", graph_x + 20, no_data_y, COLOR_GRAY)
            self.display.text("Data collection in progress", graph_x + 10, no_data_y + 20, COLOR_GRAY)
        
        # Footer
        self.draw_footer("24h History")
        
        log("Pressure graph screen displayed")
    
    def show_fishing_screen(self, data):
        """
        Display fishing forecast screen.
        
        Args:
            data: Dict with fishing data
        """
        # Clear
        self.clear()
        
        # Header
        self.draw_header("FISHING FORECAST", data.get('battery'))
        
        # Body
        y = self.header_height + 30
        line_height = 30
        
        # Fish icon
        fish_x = self.width // 2
        fish_y = y + 20
        self.graphics.draw_fish(self.display, fish_x, fish_y, 20, COLOR_CYAN)
        y += 60
        
        # KIAR % (if available)
        fish_activity = data.get('fish_activity', 'Unknown')
        kiar_value = data.get('kiar_percent', 0)
        
        if isinstance(kiar_value, (int, float)) and kiar_value > 0:
            # Show KIAR percentage
            kiar_text = f"KIAR: {kiar_value:.0f}%"
            self.display.text(kiar_text, 60, y, COLOR_YELLOW)
            
            # Progress bar for KIAR
            bar_x = 40
            bar_y = y + 25
            bar_width = self.width - 80
            bar_height = 20
            
            # Color based on KIAR value
            if kiar_value > 70:
                bar_color = COLOR_GREEN
            elif kiar_value > 40:
                bar_color = COLOR_YELLOW
            else:
                bar_color = COLOR_RED
            
            self.graphics.draw_progress_bar(
                self.display, bar_x, bar_y, bar_width, bar_height,
                kiar_value, COLOR_GRAY, bar_color
            )
            
            y += 50
        
        # Activity level
        activity_text = f"Activity: {fish_activity}"
        self.display.text(activity_text, 40, y, COLOR_CYAN)
        y += line_height
        
        # Water temperature
        if 'temperature_water' in data and data['temperature_water'] is not None:
            water_temp = data['temperature_water']
            water_text = f"Water: {water_temp:.1f}C"
            self.display.text(water_text, 40, y, COLOR_CYAN)
            y += line_height
        
        # Pressure trend influence
        trend = data.get('pressure_trend', 0)
        if trend > 1:
            trend_text = "Pressure rising: Good"
            trend_color = COLOR_GREEN
        elif trend < -1:
            trend_text = "Pressure falling: Poor"
            trend_color = COLOR_RED
        else:
            trend_text = "Pressure stable: Fair"
            trend_color = COLOR_YELLOW
        
        self.display.text(trend_text, 30, y, trend_color)
        
        # Footer
        self.draw_footer("Southern Bug River")
        
        log("Fishing screen displayed")
    
    def show_data(self, data, pressure_history=None):
        """
        Display current screen based on current_screen index.
        
        Args:
            data: Data dictionary
            pressure_history: PressureHistory instance (optional)
        """
        if self.current_screen == 0:
            self.show_main_screen(data)
        elif self.current_screen == 1:
            self.show_details_screen(data)
        elif self.current_screen == 2:
            self.show_pressure_graph_screen(data, pressure_history)
        elif self.current_screen == 3:
            self.show_fishing_screen(data)
        else:
            # Default to main
            self.show_main_screen(data)
    
    def next_screen(self):
        """Switch to next screen."""
        self.current_screen = (self.current_screen + 1) % self.screen_count
        log(f"Switched to screen {self.current_screen}")
    
    def previous_screen(self):
        """Switch to previous screen."""
        self.current_screen = (self.current_screen - 1) % self.screen_count
        log(f"Switched to screen {self.current_screen}")
    
    def set_brightness(self, percent):
        """
        Set backlight brightness.
        
        Args:
            percent: Brightness level (0-100)
        """
        self.brightness = max(0, min(100, percent))
        if hasattr(self.display, 'set_brightness'):
            self.display.set_brightness(self.brightness)
        log(f"Brightness set to {self.brightness}%")
    
    def display_off(self):
        """Turn off display (for sleep mode)."""
        self.set_brightness(0)
        log("Display off")
    
    def display_on(self):
        """Wake up display."""
        self.set_brightness(self.brightness)
        log("Display on")
