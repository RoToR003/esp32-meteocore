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
    
    # ========================================================================
    # LOCATION-SPECIFIC: VINNYTSIA, UKRAINE
    # ========================================================================
    
    # Geographic coordinates
    LATITUDE = 49.233  # degrees North
    LONGITUDE = 28.468  # degrees East
    ELEVATION = const(305)  # meters above sea level (CORRECTED from 262m)
    TIMEZONE = 'Europe/Kiev'
    
    # Climate of Vinnytsia (continental, temperate)
    # Average annual temperature: +7.3°C
    # Average annual precipitation: 595 mm
    # Average station pressure at 305m: 975-980 hPa
    # MSLP: 1010-1020 hPa (reduced to sea level)
    
    # Barometric formula correction for Vinnytsia (305m)
    # At T=15°C: p_station ≈ 976 hPa -> MSLP ≈ 1013 hPa
    # Correction coefficient: 1.038 (instead of universal)
    VINNYTSIA_MSLP_CORRECTION = 1.038
    
    # ========================================================================
    # SOUTHERN BUG RIVER (CENTER OF VINNYTSIA)
    # ========================================================================
    
    RIVER_NAME = "Південний Буг"
    RIVER_WIDTH = 80.0  # meters (in city center)
    RIVER_DEPTH_AVERAGE = 1.8  # meters (average depth)
    RIVER_DEPTH_MAX = 4.5  # meters (maximum depth)
    RIVER_CURRENT_SPEED = 0.3  # m/s (average current speed)
    RIVER_SUBSTRATE = "змішаний"  # sand, silt, stone
    
    # Thermal characteristics of the river
    RIVER_THERMAL_INERTIA = 0.12  # For river (fast response to weather)
    RIVER_TEMP_AMPLITUDE_SUMMER = 8.0  # °C (daily temperature range in summer)
    RIVER_TEMP_AMPLITUDE_WINTER = 2.0  # °C (lower amplitude in winter)
    
    # Ice regime of Southern Bug in Vinnytsia
    ICE_FORMATION_TEMP = -5.0  # °C (average temperature for ice formation)
    ICE_BREAKUP_TEMP = 3.0  # °C (average temperature for ice breakup)
    ICE_COVER_DAYS_AVG = 80  # days (average ice cover duration)
    
    # ========================================================================
    # WATER CHEMISTRY OF SOUTHERN BUG (GEO VINNYTSIA DATA)
    # ========================================================================
    
    WATER_PH_AVERAGE = 7.8  # slightly alkaline (typically 7.5-8.2)
    WATER_PH_MIN = 7.2
    WATER_PH_MAX = 8.5
    WATER_HARDNESS = 4.5  # mg-eq/L (moderately hard)
    WATER_OXYGEN_SATURATION_SUMMER = 7.5  # mg/L (decreases in summer)
    WATER_OXYGEN_SATURATION_WINTER = 12.0  # mg/L (increases in winter)
    WATER_TURBIDITY = "середня"  # NTU 10-25 (depends on flood)
    
    # Anthropogenic pollution (city center)
    POLLUTION_FACTOR = 1.2  # Pollution coefficient (1.0 = clean, >1.0 = polluted)
    EUTROPHICATION_LEVEL = "помірна"  # Eutrophication from urban runoff
    
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
