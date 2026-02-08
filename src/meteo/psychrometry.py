"""
Psychrometric Calculations
==========================

Calculations related to humidity, water vapor, and condensation.
"""

import math
from ..core.constants import PhysicalConstants


def saturation_pressure(t_celsius: float) -> float:
    """
    Calculate saturation vapor pressure (hPa) by temperature.
    Uses Magnus formula for accurate calculations.
    
    Magnus formula: E = 6.112 × exp((17.67 × T)/(T + 243.5))
    where T is temperature in °C
    
    Args:
        t_celsius: Temperature in Celsius
        
    Returns:
        Saturation vapor pressure in hPa
    """
    if t_celsius < -40:
        # For very low temperatures (ice)
        return 0.1
    
    # Magnus formula (derived from Clausius-Clapeyron)
    E = 6.112 * math.exp((17.67 * t_celsius) / (t_celsius + 243.5))
    return E


def actual_vapor_pressure(t_celsius: float, humidity_percent: float) -> float:
    """
    Calculate actual vapor pressure.
    
    Formula: e = E × (f/100)
    where E is saturation pressure, f is relative humidity
    
    Args:
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        
    Returns:
        Actual vapor pressure in hPa
    """
    E = saturation_pressure(t_celsius)
    e = E * (humidity_percent / 100.0)
    return e


def dew_point(t_celsius: float, humidity_percent: float) -> float:
    """
    Calculate dew point temperature from temperature and humidity.
    
    Uses inverse Magnus formula:
    τ = (243.5 × ln(e/6.112)) / (17.67 - ln(e/6.112))
    
    Args:
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        
    Returns:
        Dew point temperature in Celsius
    """
    e = actual_vapor_pressure(t_celsius, humidity_percent)
    
    if e <= 0.1:
        return -40.0
    
    # Inverse Magnus formula
    ln_ratio = math.log(e / 6.112)
    dew_point_temp = (243.5 * ln_ratio) / (17.67 - ln_ratio)
    
    return dew_point_temp


def humidity_deficit(t_celsius: float, humidity_percent: float) -> float:
    """
    Calculate humidity deficit (vapor pressure deficit).
    
    Formula: d = E - e = E × (1 - f/100)
    
    Args:
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        
    Returns:
        Humidity deficit in hPa
    """
    E = saturation_pressure(t_celsius)
    e = actual_vapor_pressure(t_celsius, humidity_percent)
    return E - e


def condensation_level(t_celsius: float, humidity_percent: float) -> float:
    """
    Calculate lifting condensation level height (m).
    
    Formula: Hк = 122 × Δτ
    where Δτ = t - τ (dew point deficit)
    
    Args:
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        
    Returns:
        Condensation level height in meters
    """
    tau = dew_point(t_celsius, humidity_percent)
    delta_tau = t_celsius - tau
    
    Hk = PhysicalConstants.CONDENSATION_COEF * delta_tau
    return max(0, Hk)


def wet_bulb_temperature(t_celsius: float, humidity_percent: float, pressure_hpa: float = None) -> float:
    """
    Calculate wet bulb temperature (approximate).
    
    Args:
        t_celsius: Dry bulb temperature in Celsius
        humidity_percent: Relative humidity in percent
        pressure_hpa: Atmospheric pressure in hPa (optional)
        
    Returns:
        Wet bulb temperature in Celsius
    """
    if pressure_hpa is None:
        pressure_hpa = PhysicalConstants.P0_HPA
    
    # Simplified formula for wet bulb temperature
    e = actual_vapor_pressure(t_celsius, humidity_percent)
    E = saturation_pressure(t_celsius)
    
    # Psychrometric equation
    t_wet = t_celsius - ((E - e) / (PhysicalConstants.A * pressure_hpa))
    
    return t_wet


def relative_humidity_from_dewpoint(t_celsius: float, dew_point_celsius: float) -> float:
    """
    Calculate relative humidity from temperature and dew point.
    
    Args:
        t_celsius: Temperature in Celsius
        dew_point_celsius: Dew point temperature in Celsius
        
    Returns:
        Relative humidity in percent
    """
    E = saturation_pressure(t_celsius)
    e = saturation_pressure(dew_point_celsius)
    
    if E == 0:
        return 0.0
    
    rh = (e / E) * 100.0
    return min(100.0, max(0.0, rh))


def absolute_humidity(t_celsius: float, humidity_percent: float) -> float:
    """
    Calculate absolute humidity (water vapor density in g/m³).
    
    Args:
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        
    Returns:
        Absolute humidity in g/m³
    """
    e = actual_vapor_pressure(t_celsius, humidity_percent)
    T_kelvin = t_celsius + PhysicalConstants.T0_KELVIN
    
    # Formula: ρ_v = (e × 216.7) / T
    # where e is in hPa and T is in Kelvin
    abs_humidity = (e * 216.7) / T_kelvin
    
    return abs_humidity
