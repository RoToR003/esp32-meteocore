"""
Pressure Trend Analyzer for Fishing Forecast
=============================================

Lightweight algorithm for RAM-limited ESP32-S3.

Logic:
- ΔP < -2 hPa/6h: Falling → Good for predators
- ΔP > +2 hPa/6h: Rising → Slowing activity
- |ΔP| < 2 hPa/6h: Stable → Normal activity

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] PRESSURE: {message}")
    except:
        pass


def analyze_pressure_trend(pressure_history):
    """
    Analyze pressure trend for fishing.
    
    Args:
        pressure_history: List of pressure readings (last 12 hours)
        
    Returns:
        dict: {
            'delta_6h': float,
            'trend': str ('falling', 'rising', 'stable'),
            'fishing_status': str,
            'recommendation': str
        }
    """
    
    if len(pressure_history) < 2:
        return {
            'delta_6h': 0.0,
            'trend': 'unknown',
            'fishing_status': 'Недостатньо даних',
            'recommendation': 'Збираємо історію...'
        }
    
    # Calculate delta (6 hours = 6 readings if hourly)
    if len(pressure_history) >= 7:
        delta_6h = pressure_history[-1] - pressure_history[-7]
    else:
        delta_6h = pressure_history[-1] - pressure_history[0]
    
    # Classify trend
    if delta_6h < -2.0:
        trend = 'falling'
        status = '🎣 ВІДМІННО (хижак)'
        recommendation = 'Тиск падає - жор хижаків!'
    elif delta_6h > 2.0:
        trend = 'rising'
        status = '😐 Слабка активність'
        recommendation = 'Тиск росте - риба пасивна'
    else:
        trend = 'stable'
        status = '✅ Добре'
        recommendation = 'Тиск стабільний - нормальна активність'
    
    log(f"Pressure delta: {delta_6h:.1f} hPa/6h, trend: {trend}")
    
    return {
        'delta_6h': round(delta_6h, 1),
        'trend': trend,
        'fishing_status': status,
        'recommendation': recommendation
    }
