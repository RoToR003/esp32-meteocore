"""
Graphics Helper - Weather Icons, Graphs, and UI Elements
=========================================================

Provides graphics functions for enhanced display:
- Weather icons (sun, cloud, rain, snow)
- Progress bars (battery, etc.)
- Pressure graphs
- UI elements

All graphics are vector-based for scalability.

Author: ESP32-MeteoCore Project
"""

import math


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] GRAPHICS: {message}")
    except:
        pass


class GraphicsHelper:
    """
    Collection of graphics drawing functions.
    """
    
    @staticmethod
    def draw_sun(display, x, y, radius, color):
        """
        Draw sun icon (circle with rays).
        
        Args:
            display: Display object
            x, y: Center coordinates
            radius: Sun radius
            color: Color value
        """
        # Draw circle
        display.circle(x, y, radius, color, fill=True)
        
        # Draw 8 rays
        ray_length = radius + 8
        for angle in range(0, 360, 45):
            # Convert to radians
            rad = angle * 3.14159 / 180.0
            
            # Calculate ray start (on circle edge)
            x1 = int(x + radius * math.cos(rad))
            y1 = int(y + radius * math.sin(rad))
            
            # Calculate ray end
            x2 = int(x + ray_length * math.cos(rad))
            y2 = int(y + ray_length * math.sin(rad))
            
            # Draw ray
            display.line(x1, y1, x2, y2, color)
    
    @staticmethod
    def draw_cloud(display, x, y, width, color):
        """
        Draw cloud icon (3 overlapping circles).
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width: Cloud width
            color: Color value
        """
        # Calculate circle sizes
        r1 = width // 4
        r2 = width // 3
        r3 = width // 4
        
        # Draw 3 circles
        display.circle(x + r1, y + r1, r1, color, fill=True)
        display.circle(x + width // 2, y + r2, r2, color, fill=True)
        display.circle(x + width - r3, y + r3, r3, color, fill=True)
        
        # Draw base rectangle
        display.fill_rect(x, y + r2, width, r2, color)
    
    @staticmethod
    def draw_rain(display, x, y, width, height, drops, color):
        """
        Draw rain drops.
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width, height: Area size
            drops: Number of drops
            color: Color value
        """
        # Draw drops as small lines
        drop_spacing = width // max(drops, 1)
        
        for i in range(drops):
            drop_x = x + (i * drop_spacing) + (drop_spacing // 2)
            drop_y = y
            
            # Draw 2-3 drops vertically
            display.line(drop_x, drop_y, drop_x, drop_y + 4, color)
            display.line(drop_x, drop_y + 8, drop_x, drop_y + 12, color)
    
    @staticmethod
    def draw_snow(display, x, y, width, height, flakes, color):
        """
        Draw snowflakes.
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width, height: Area size
            flakes: Number of snowflakes
            color: Color value
        """
        # Draw snowflakes as small crosses
        flake_spacing = width // max(flakes, 1)
        
        for i in range(flakes):
            flake_x = x + (i * flake_spacing) + (flake_spacing // 2)
            flake_y = y + (height // 2)
            
            # Draw cross
            display.line(flake_x - 2, flake_y, flake_x + 2, flake_y, color)
            display.line(flake_x, flake_y - 2, flake_x, flake_y + 2, color)
    
    @staticmethod
    def draw_progress_bar(display, x, y, width, height, percent, color_empty, color_fill):
        """
        Draw progress bar.
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width, height: Bar size
            percent: Fill percentage (0-100)
            color_empty: Empty bar color
            color_fill: Fill color
        """
        # Clamp percent
        percent = max(0, min(100, percent))
        
        # Draw border
        display.rect(x, y, width, height, color_empty)
        
        # Calculate fill width
        fill_width = int((width - 4) * percent / 100)
        
        if fill_width > 0:
            # Draw fill
            display.fill_rect(x + 2, y + 2, fill_width, height - 4, color_fill)
    
    @staticmethod
    def draw_battery(display, x, y, width, height, percent, color):
        """
        Draw battery icon with level indicator.
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width, height: Battery size
            percent: Battery level (0-100)
            color: Color value (auto-adjusts shade for level)
        """
        # Draw battery body
        display.rect(x, y, width - 4, height, color)
        
        # Draw battery terminal (bump on right)
        terminal_width = 4
        terminal_height = height // 3
        terminal_y = y + (height - terminal_height) // 2
        display.fill_rect(x + width - 4, terminal_y, terminal_width, terminal_height, color)
        
        # Draw fill level
        if percent > 0:
            fill_width = int((width - 8) * percent / 100)
            if fill_width > 0:
                display.fill_rect(x + 2, y + 2, fill_width, height - 4, color)
    
    @staticmethod
    def draw_pressure_graph(display, x, y, width, height, history, color_line, color_bg):
        """
        Draw pressure trend graph.
        
        Args:
            display: Display object
            x, y: Top-left coordinates
            width, height: Graph size
            history: List of pressure values
            color_line: Line color
            color_bg: Background color
        """
        if not history or len(history) < 2:
            # Not enough data
            display.text("No data", x + 5, y + height // 2, color_line)
            return
        
        # Clear background
        display.fill_rect(x, y, width, height, color_bg)
        
        # Draw border
        display.rect(x, y, width, height, color_line)
        
        # Find min/max for scaling
        min_pressure = min(history)
        max_pressure = max(history)
        pressure_range = max_pressure - min_pressure
        
        if pressure_range < 0.1:
            # Almost flat, just draw a line
            mid_y = y + height // 2
            display.line(x, mid_y, x + width, mid_y, color_line)
            return
        
        # Calculate points
        points = []
        step_x = (width - 4) / max(len(history) - 1, 1)
        
        for i, pressure in enumerate(history):
            px = x + 2 + int(i * step_x)
            # Invert Y (top = high pressure)
            py = y + height - 2 - int((pressure - min_pressure) / pressure_range * (height - 4))
            points.append((px, py))
        
        # Draw lines connecting points
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            display.line(x1, y1, x2, y2, color_line)
        
        # Draw points
        for px, py in points:
            display.pixel(px, py, color_line)
            display.pixel(px + 1, py, color_line)
            display.pixel(px, py + 1, color_line)
            display.pixel(px + 1, py + 1, color_line)
    
    @staticmethod
    def draw_trend_arrow(display, x, y, size, direction, color):
        """
        Draw trend arrow (up, down, flat).
        
        Args:
            display: Display object
            x, y: Arrow tip coordinates
            size: Arrow size
            direction: 'up', 'down', or 'flat'
            color: Color value
        """
        if direction == 'up':
            # Upward arrow
            display.line(x, y, x - size, y + size, color)
            display.line(x, y, x + size, y + size, color)
            display.line(x, y, x, y + size * 2, color)
        
        elif direction == 'down':
            # Downward arrow
            display.line(x, y, x - size, y - size, color)
            display.line(x, y, x + size, y - size, color)
            display.line(x, y, x, y - size * 2, color)
        
        else:  # flat
            # Horizontal arrow
            display.line(x - size, y, x + size, y, color)
            display.line(x + size, y, x + size - 3, y - 3, color)
            display.line(x + size, y, x + size - 3, y + 3, color)
    
    @staticmethod
    def draw_fish(display, x, y, size, color):
        """
        Draw simple fish icon.
        
        Args:
            display: Display object
            x, y: Fish center
            size: Fish size
            color: Color value
        """
        # Body (oval)
        for i in range(size):
            offset = int(math.sqrt(size * size - (i - size // 2) ** 2))
            display.line(x - offset, y + i - size // 2, 
                        x + offset, y + i - size // 2, color)
        
        # Tail
        display.line(x - size, y, x - size - 5, y - 5, color)
        display.line(x - size, y, x - size - 5, y + 5, color)
        
        # Eye
        display.pixel(x + size // 3, y - size // 4, color)
    
    @staticmethod
    def draw_wifi_icon(display, x, y, size, strength, color):
        """
        Draw WiFi signal strength icon.
        
        Args:
            display: Display object
            x, y: Bottom-left coordinates
            size: Icon size
            strength: Signal strength 0-3 (0=no signal, 3=excellent)
            color: Color value
        """
        bar_width = size // 4
        bar_spacing = size // 5
        
        for i in range(4):
            bar_height = (i + 1) * size // 4
            bar_x = x + i * (bar_width + bar_spacing)
            bar_y = y - bar_height
            
            if i <= strength:
                display.fill_rect(bar_x, bar_y, bar_width, bar_height, color)
            else:
                display.rect(bar_x, bar_y, bar_width, bar_height, color)


def get_color_for_battery(percent):
    """
    Get appropriate color for battery level.
    
    Args:
        percent: Battery percentage (0-100)
    
    Returns:
        int: RGB565 color value
    """
    if percent > 60:
        return 0x07E0  # Green
    elif percent > 20:
        return 0xFFE0  # Yellow
    else:
        return 0xF800  # Red


def get_color_for_temperature(temp):
    """
    Get appropriate color for temperature.
    
    Args:
        temp: Temperature in Celsius
    
    Returns:
        int: RGB565 color value
    """
    if temp < 0:
        return 0x1CF   # Blue (cold)
    elif temp < 15:
        return 0x07FF  # Cyan (cool)
    elif temp < 25:
        return 0x07E0  # Green (comfortable)
    elif temp < 30:
        return 0xFFE0  # Yellow (warm)
    else:
        return 0xF800  # Red (hot)
