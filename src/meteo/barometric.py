"""
Barometric Calculations
=======================

Atmospheric pressure related calculations.
"""

import math
from typing import Dict
from ..core.constants import PhysicalConstants
from .psychrometry import saturation_pressure


def adjust_pressure_to_sea_level(p_station: float, t_celsius: float, elevation: float = None) -> float:
    """
    Adjust station pressure to mean sea level pressure (MSLP).
    Critical for accurate weather forecasting at elevation > 0m.
    
    Args:
        p_station: Station pressure in hPa
        t_celsius: Temperature in Celsius
        elevation: Elevation in meters (defaults to PhysicalConstants.ELEVATION)
        
    Returns:
        Sea level pressure in hPa
    """
    h = elevation if elevation is not None else PhysicalConstants.ELEVATION
    if h == 0:
        return p_station
    
    # Average temperature of air column (Kelvin) with lapse rate correction
    t_kelvin = t_celsius + 273.15 + (h * 0.0065 / 2)
    
    # Barometric formula
    # 0.034163 is a constant derived from g * M / R
    p_sea_level = p_station * math.exp((0.034163 * h) / t_kelvin)
    return p_sea_level


def adjust_pressure_to_sea_level_precise(p_station: float, t_celsius: float, 
                                          humidity_percent: float,
                                          elevation: float = None) -> float:
    """
    Precise pressure adjustment for Vinnytsia with humidity consideration.
    
    Uses modified barometric formula with virtual temperature correction.
    
    Source: WMO Guide to Meteorological Instruments and Methods of Observation (2018)
    Section 3.9.2: Pressure Reduction to Sea Level
    
    Args:
        p_station: Station pressure in hPa
        t_celsius: Temperature in Celsius
        humidity_percent: Relative humidity in percent
        elevation: Elevation in meters (defaults to PhysicalConstants.ELEVATION)
        
    Returns:
        Sea level pressure in hPa
    """
    h = elevation if elevation is not None else PhysicalConstants.ELEVATION
    if h == 0:
        return p_station
    
    # 1. Calculate saturation vapor pressure
    e = saturation_pressure(t_celsius) * (humidity_percent / 100.0)
    
    # 2. Virtual temperature (accounts for humidity)
    # T_v = T × (1 + 0.608 × (e/p))
    T_kelvin = t_celsius + 273.15
    mixing_ratio = 0.622 * e / (p_station - e)  # kg water vapor / kg dry air
    T_virtual = T_kelvin * (1 + 0.608 * mixing_ratio)
    
    # 3. Average virtual temperature of air column
    # Accounts for vertical temperature gradient (0.0065 K/m)
    T_avg = T_virtual + (h * 0.0065 / 2)
    
    # 4. Barometric formula with virtual temperature
    # Constant: g*M/R = 9.80665 * 0.0289644 / 8.31446 ≈ 0.034163
    exponent = (PhysicalConstants.g * 0.0289644 * h) / (8.31446 * T_avg)
    p_sea_level = p_station * math.exp(exponent)
    
    return p_sea_level


def baric_step(t_celsius: float) -> float:
    """
    Calculate baric step (m/hPa).
    
    Formula: Hб = 8000 × (1 + 0.004 × t) / 1000
    where t is air temperature in °C
    
    Shows how many meters you need to ascend/descend
    for pressure to change by 1 hPa.
    
    Args:
        t_celsius: Air temperature in Celsius
        
    Returns:
        Baric step in meters per hPa
    """
    Hb = (PhysicalConstants.BARIC_STEP_COEF * (1 + 0.004 * t_celsius)) / 1000
    return Hb


def pressure_tendency_to_height(delta_p: float, t_celsius: float) -> float:
    """
    Convert pressure change to height change.
    
    Uses baric step: Δh = Нб × Δp
    
    Args:
        delta_p: Pressure change in hPa
        t_celsius: Air temperature in Celsius
        
    Returns:
        Height change in meters
    """
    Hb = baric_step(t_celsius)
    delta_h = Hb * delta_p
    return delta_h


def air_density(pressure_hpa: float, t_celsius: float) -> float:
    """
    Calculate air density (kg/m³).
    
    Equation of state: ρ = p / (R × T)
    where p is pressure in Pa, R is gas constant, T is temperature in K
    
    Args:
        pressure_hpa: Pressure in hPa
        t_celsius: Temperature in Celsius
        
    Returns:
        Air density in kg/m³
    """
    p_pa = pressure_hpa * 100  # Convert hPa to Pa
    T_kelvin = celsius_to_kelvin(t_celsius)
    
    rho = p_pa / (PhysicalConstants.R * T_kelvin)
    return rho


def potential_temperature(t_celsius: float, pressure_hpa: float) -> float:
    """
    Calculate potential temperature (K).
    
    Formula: θ = T × (1000/p)^0.286
    where T is temperature in K, p is pressure in hPa
    
    Potential temperature is conserved in adiabatic processes.
    
    Args:
        t_celsius: Temperature in Celsius
        pressure_hpa: Pressure in hPa
        
    Returns:
        Potential temperature in Kelvin
    """
    T_kelvin = celsius_to_kelvin(t_celsius)
    theta = T_kelvin * math.pow(1000.0 / pressure_hpa, 0.286)
    return theta


def celsius_to_kelvin(t_celsius: float) -> float:
    """Convert Celsius to Kelvin."""
    return t_celsius + PhysicalConstants.T0_KELVIN


def kelvin_to_celsius(t_kelvin: float) -> float:
    """Convert Kelvin to Celsius."""
    return t_kelvin - PhysicalConstants.T0_KELVIN


def stability_index(t_surface: float, humidity: float) -> Dict[str, float]:
    """
    Calculate atmospheric instability indices considering humidity.
    
    Args:
        t_surface: Surface temperature in Celsius
        humidity: Relative humidity in percent
        
    Returns:
        Dictionary with Showalter index, lifted index, and parcel temperature at 500 hPa
    """
    # Determine actual lapse rate (temperature decrease rate)
    if humidity >= 90:
        gamma = 0.5  # Moist adiabat (air cools slowly)
    elif humidity <= 40:
        gamma = 0.98  # Dry adiabat (air cools quickly)
    else:
        # Smooth transition between 0.6 and 0.98
        gamma = 0.6 + (0.98 - 0.6) * ((70 - humidity) / 30)
    
    # Calculate temperatures at different heights (simulation)
    # 850 hPa ~ 1.5 km, 500 hPa ~ 5.5 km
    t_850_est = t_surface - (gamma * 15)
    t_500_est = t_surface - (gamma * 55)
    
    # Temperature of rising parcel (always along moist adiabat for thunderstorms)
    t_parcel_500 = t_surface - (0.5 * 55)
    
    # Showalter Index
    SI = t_500_est - t_parcel_500
    
    return {
        'showalter_index': round(SI, 1),
        'lifted_index': round(-SI, 1),
        'parcel_temp_500': round(t_parcel_500, 1)
    }
