"""
Physical Constants for Meteorology and Hydrobiology
===================================================

Unified constants from both meteorological and fishing modules.
Compatible with both CPython and MicroPython.
"""

try:
    from micropython import const
    MICROPYTHON = True
except ImportError:
    # For CPython compatibility
    def const(x):
        return x
    MICROPYTHON = False


class PhysicalConstants:
    """
    Physical constants for meteorological and hydrological calculations.
    Merged from both meteo_core.py and fishing.py.
    """
    
    # ========================================================================
    # ATMOSPHERIC CONSTANTS
    # ========================================================================
    
    # Gas constants
    R = const(287)  # Gas constant for dry air, J/(kg·K)
    g = const(9.81)  # Gravitational acceleration, m/s² (UNIFIED - was duplicated)
    cp = const(1005)  # Specific heat capacity at constant pressure, J/(kg·K)
    cv = const(718)  # Specific heat capacity at constant volume, J/(kg·K)
    gamma = const(1.4)  # Adiabatic index
    L = const(2500000)  # Specific heat of vaporization, J/kg (2.5e6)
    
    # Psychrometric constants
    A = 0.000662  # Psychrometric coefficient
    
    # Vertical gradients
    GAMMA_DRY = 1.0  # Dry adiabatic lapse rate, °C/100m
    GAMMA_WET = 0.5  # Saturated adiabatic lapse rate, °C/100m
    GAMMA_NORMAL = 0.6  # Normal temperature lapse rate, °C/100m
    
    # Standard conditions
    P0_HPA = 1013.25  # Standard atmospheric pressure, hPa
    P0_MMHG = const(760)  # Standard pressure, mmHg
    T0_CELSIUS = const(15)  # Standard temperature, °C
    T0_KELVIN = 273.15  # Absolute zero offset
    
    # Empirical coefficients
    BARIC_STEP_COEF = const(8000)  # For baric step calculations
    CONDENSATION_COEF = const(122)  # Condensation level coefficient, m/°C
    CONDENSATION_HEIGHT_COEF = const(122)  # Alternative name for same coefficient
    
    # Location-specific (default: Vinnytsia, Ukraine)
    ELEVATION = const(262)  # Elevation above sea level, meters
    EMA_ALPHA = 0.3  # Exponential smoothing coefficient for sensor noise (0.1 - very smooth, 1.0 - no smoothing)
    
    # Barometric changes
    BAROMETRIC_CRITICAL_CHANGE = 2.5  # Critical pressure change, mmHg/hour
    
    # ========================================================================
    # WATER PROPERTIES
    # ========================================================================
    
    # Physical properties of water
    WATER_DENSITY = const(1000)  # kg/m³
    WATER_HEAT_CAPACITY = const(4186)  # J/(kg·°C)
    WATER_PRESSURE_PER_METER = const(76)  # mmHg per 1 meter of depth
    
    # Gas exchange in water
    HENRY_CONSTANT_O2 = 1.3e-3  # mol/(L·atm) at 25°C
    O2_DIFFUSION_COEF = 2.0e-9  # m²/s
    
    # Optical properties
    WATER_ALBEDO = 0.06
    LIGHT_EXTINCTION_CLEAR = 0.1  # m⁻¹ for clear water
    LIGHT_EXTINCTION_TURBID = 5.0  # m⁻¹ for turbid water
    
    # ========================================================================
    # BIOLOGICAL CONSTANTS
    # ========================================================================
    
    # Temperature dependence
    Q10_FISH = 2.2  # Van't Hoff temperature coefficient for fish
    
    # Thermal inertia of water bodies
    THERMAL_INERTIA_SHALLOW = 0.15  # Shallow water
    THERMAL_INERTIA_MEDIUM = 0.08   # Medium depth
    THERMAL_INERTIA_DEEP = 0.05     # Deep water
    
    # Wind and aeration
    AERATION_COEFFICIENT = 0.001  # Wind aeration coefficient
    WIND_TURBULENCE_COEF = 0.001  # Wind turbulence coefficient


# For backward compatibility
g = PhysicalConstants.g
R = PhysicalConstants.R
cp = PhysicalConstants.cp
cv = PhysicalConstants.cv
gamma = PhysicalConstants.gamma
L = PhysicalConstants.L
