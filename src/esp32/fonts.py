"""
Vector Fonts for Large Display
================================

Provides vector-based fonts for displaying large digits and symbols.
Scalable without quality loss - perfect for temperature display.

Features:
- Large digits (0-9)
- Degree symbol (°)
- Letter C (for Celsius)
- Scalable to any size
- Low memory footprint

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] FONTS: {message}")
    except:
        pass


# Vector font data - each digit is defined as a list of line segments
# Format: [(x1, y1, x2, y2), ...] where coordinates are relative to 10x10 grid
FONT_LARGE = {
    '0': [
        # Outer rectangle
        (2, 0, 8, 0),   # Top
        (8, 0, 8, 10),  # Right
        (8, 10, 2, 10), # Bottom
        (2, 10, 2, 0),  # Left
        # Diagonal (to distinguish from 8)
        (2, 2, 8, 8),
    ],
    '1': [
        # Vertical line
        (5, 0, 5, 10),
        # Top hook
        (5, 0, 3, 2),
        # Bottom base
        (3, 10, 7, 10),
    ],
    '2': [
        # Top arc
        (2, 2, 2, 0),
        (2, 0, 8, 0),
        (8, 0, 8, 2),
        # Middle
        (8, 2, 2, 5),
        # Bottom
        (2, 5, 2, 10),
        (2, 10, 8, 10),
    ],
    '3': [
        # Top
        (2, 0, 8, 0),
        (8, 0, 8, 5),
        # Middle
        (8, 5, 4, 5),
        # Bottom
        (8, 5, 8, 10),
        (8, 10, 2, 10),
    ],
    '4': [
        # Left vertical
        (2, 0, 2, 6),
        # Horizontal
        (2, 6, 8, 6),
        # Right vertical
        (8, 0, 8, 10),
    ],
    '5': [
        # Top
        (8, 0, 2, 0),
        (2, 0, 2, 5),
        # Middle
        (2, 5, 8, 5),
        (8, 5, 8, 10),
        # Bottom
        (8, 10, 2, 10),
    ],
    '6': [
        # Top
        (8, 0, 2, 0),
        # Left
        (2, 0, 2, 10),
        # Bottom
        (2, 10, 8, 10),
        (8, 10, 8, 5),
        # Middle
        (8, 5, 2, 5),
    ],
    '7': [
        # Top
        (2, 0, 8, 0),
        # Diagonal
        (8, 0, 4, 10),
    ],
    '8': [
        # Top rectangle
        (2, 0, 8, 0),
        (8, 0, 8, 5),
        (8, 5, 2, 5),
        (2, 5, 2, 0),
        # Bottom rectangle
        (2, 5, 2, 10),
        (2, 10, 8, 10),
        (8, 10, 8, 5),
    ],
    '9': [
        # Top rectangle
        (2, 0, 8, 0),
        (8, 0, 8, 5),
        (8, 5, 2, 5),
        (2, 5, 2, 0),
        # Right vertical
        (8, 5, 8, 10),
        # Bottom
        (8, 10, 2, 10),
    ],
    '.': [
        # Small dot at bottom
        (4, 8, 6, 8),
        (6, 8, 6, 10),
        (6, 10, 4, 10),
        (4, 10, 4, 8),
    ],
    '-': [
        # Horizontal line in middle
        (2, 5, 8, 5),
    ],
    '°': [
        # Small circle at top
        (3, 1, 5, 1),
        (5, 1, 5, 3),
        (5, 3, 3, 3),
        (3, 3, 3, 1),
    ],
    'C': [
        # Arc shape
        (8, 2, 8, 0),
        (8, 0, 2, 0),
        (2, 0, 2, 10),
        (2, 10, 8, 10),
        (8, 10, 8, 8),
    ],
}


def draw_large_digit(display, digit, x, y, scale=1, color=0xFFFF):
    """
    Draw a large digit using vector font.
    
    Args:
        display: Display object with line() method
        digit: Character to draw ('0'-'9', '.', '-', '°', 'C')
        x: X coordinate (top-left)
        y: Y coordinate (top-left)
        scale: Scale factor (default 1, try 3-5 for large display)
        color: Color value (RGB565 format)
    """
    if digit not in FONT_LARGE:
        log(f"Character '{digit}' not in font", "WARNING")
        return
    
    # Get line segments for this digit
    segments = FONT_LARGE[digit]
    
    # Draw each line segment
    for segment in segments:
        x1, y1, x2, y2 = segment
        
        # Scale and offset coordinates
        x1_scaled = x + int(x1 * scale)
        y1_scaled = y + int(y1 * scale)
        x2_scaled = x + int(x2 * scale)
        y2_scaled = y + int(y2 * scale)
        
        # Draw line
        display.line(x1_scaled, y1_scaled, x2_scaled, y2_scaled, color)


def draw_large_number(display, number, x, y, scale=1, color=0xFFFF):
    """
    Draw a large number (integer or float) using vector font.
    
    Args:
        display: Display object with line() method
        number: Number to draw (int or float)
        x: X coordinate (top-left)
        y: Y coordinate (top-left)
        scale: Scale factor
        color: Color value
    
    Returns:
        int: Total width used in pixels
    """
    # Convert to string
    text = str(number)
    
    # Character spacing
    char_width = 10 * scale
    char_spacing = 2 * scale
    
    # Draw each character
    current_x = x
    for char in text:
        if char in FONT_LARGE:
            draw_large_digit(display, char, current_x, y, scale, color)
            
            # Special spacing for decimal point and degree
            if char in ['.', '°']:
                current_x += char_width // 2
            else:
                current_x += char_width + char_spacing
    
    return current_x - x


def draw_temperature(display, temp, x, y, scale=3, color=0xFFFF):
    """
    Draw temperature with °C symbol.
    
    Args:
        display: Display object
        temp: Temperature value (float)
        x: X coordinate
        y: Y coordinate
        scale: Scale factor
        color: Color value
    
    Returns:
        int: Total width used
    """
    # Format temperature
    temp_str = f"{temp:.1f}"
    
    # Draw number
    width = draw_large_number(display, temp_str, x, y, scale, color)
    
    # Draw degree symbol
    deg_x = x + width + (2 * scale)
    draw_large_digit(display, '°', deg_x, y, scale, color)
    
    # Draw C
    c_x = deg_x + (6 * scale)
    draw_large_digit(display, 'C', c_x, y, scale, color)
    
    return c_x + (10 * scale) - x


def get_text_width(text, scale=1):
    """
    Calculate width of text in pixels.
    
    Args:
        text: Text string
        scale: Scale factor
    
    Returns:
        int: Width in pixels
    """
    char_width = 10 * scale
    char_spacing = 2 * scale
    
    total_width = 0
    for char in text:
        if char in FONT_LARGE:
            if char in ['.', '°']:
                total_width += char_width // 2
            else:
                total_width += char_width + char_spacing
    
    return total_width


def get_digit_height(scale=1):
    """
    Get height of digit.
    
    Args:
        scale: Scale factor
    
    Returns:
        int: Height in pixels
    """
    return 10 * scale
